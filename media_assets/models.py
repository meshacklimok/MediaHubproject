from django.db import models
from django.conf import settings
import cloudinary # media management - files cloudinary - url - store to the db 
from cloudinary.models import CloudinaryField
# Create your models here.
class MediaAsset(models.Model):
    # class variable for media assets choices 
    CATEGORY_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
    )
    # object attributes / table field 
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="Uploaded and maintained by MediaHUB")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='image')
    media_file = CloudinaryField('media', resource_type='auto') # cloudinary in use
    # relationship attribute  # object relationship - 'has a' : one user can have many uploads 
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='media_assets')
    created_at =  models.DateTimeField(auto_now_add=True) # automatically capture the time when a record is inserted 
    updated_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    # always display my objects in the order of creation 
    class Meta:
        ordering = ['-created_at']   
    # editing rights 
    def can_edit(self,user):
        '''check if user can update this asset'''
        return user == self.uploaded_by or user.is_teacher() or user.is_superuser
    
    # delete 
    def can_delete(self,user):
        return user  == self.uploaded_by or user.is_teacher() or user.is_superuser
    
    # str 
    def __str__(self):
        return self.title