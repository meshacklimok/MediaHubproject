import json
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse

from .models import Transactions
from .views import normalize_phone


class NormalizePhoneTests(TestCase):
    def test_accepts_common_formats(self):
        for phone in ['0712345678', '254712345678', '+254712345678', '0712 345 678']:
            self.assertEqual(normalize_phone(phone), '254712345678')

    def test_rejects_invalid(self):
        for phone in ['', '12345', '254abc345678', None]:
            self.assertIsNone(normalize_phone(phone))


class StkPushTests(TestCase):
    form = {'phone': '0712345678', 'amount': '10', 'name': 'Jane', 'email': 'jane@example.com'}

    def test_invalid_input_rerenders_form(self):
        response = self.client.post(reverse('mediampesa:stk_push'), {**self.form, 'phone': '123'})
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'valid Safaricom number', status_code=400)
        self.assertFalse(Transactions.objects.exists())

    @patch('mediampesa.views.requests')
    def test_successful_push_redirects_to_waiting_page(self, mock_requests):
        mock_requests.get.return_value = MagicMock(json=lambda: {'access_token': 'token'})
        mock_requests.post.return_value = MagicMock(json=lambda: {
            'CheckoutRequestID': 'ws_CO_123', 'ResponseDescription': 'Success'})

        response = self.client.post(reverse('mediampesa:stk_push'), self.form)

        transaction = Transactions.objects.get()
        self.assertRedirects(response, reverse('mediampesa:waiting_page', args=[transaction.id]))
        self.assertEqual(transaction.transaction_id, 'ws_CO_123')
        self.assertEqual(transaction.phone_number, '254712345678')
        self.assertEqual(mock_requests.post.call_args.kwargs['json']['Amount'], 10)

    @patch('mediampesa.views.requests')
    def test_rejected_push_marks_failed(self, mock_requests):
        mock_requests.get.return_value = MagicMock(json=lambda: {'access_token': 'token'})
        mock_requests.post.return_value = MagicMock(json=lambda: {'errorMessage': 'Invalid Access Token'})

        response = self.client.post(reverse('mediampesa:stk_push'), self.form)

        self.assertRedirects(response, reverse('mediampesa:payment_failed'))
        self.assertEqual(Transactions.objects.get().status, 'Failed')


class CallbackTests(TestCase):
    def setUp(self):
        self.transaction = Transactions.objects.create(
            transaction_id='ws_CO_123', phone_number='254712345678', amount=10,
            status='Pending', email='jane@example.com', name='Jane')

    def post_callback(self, result_code, metadata=None):
        stk_callback = {'CheckoutRequestID': 'ws_CO_123', 'ResultCode': result_code, 'ResultDesc': 'desc'}
        if metadata:
            stk_callback['CallbackMetadata'] = {'Item': metadata}
        return self.client.post(reverse('mediampesa:callback'),
                                json.dumps({'Body': {'stkCallback': stk_callback}}),
                                content_type='application/json')

    def status(self):
        return self.client.get(reverse('mediampesa:check_status', args=[self.transaction.id])).json()['status']

    def test_success(self):
        self.assertEqual(self.status(), 'Pending')
        response = self.post_callback(0, [
            {'Name': 'Amount', 'Value': 10},
            {'Name': 'MpesaReceiptNumber', 'Value': 'NLJ7RT61SV'},
            {'Name': 'TransactionDate', 'Value': 20251130101530},
        ])
        self.assertEqual(response.status_code, 200)
        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.mpesa_receipt_number, 'NLJ7RT61SV')
        self.assertEqual(self.status(), 'Success')

    def test_cancelled(self):
        self.post_callback(1032)
        self.assertEqual(self.status(), 'Cancelled')

    def test_other_error_codes_fail(self):
        self.post_callback(2001)  # wrong PIN
        self.assertEqual(self.status(), 'Failed')
