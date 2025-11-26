from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import MediaAsset
from .forms import MediaAssetForm
# Create your views here.
@login_required
def dashboard_view(request):
    '''main dashboard : show all public media assets '''
    # capture all assets 
    media_list = MediaAsset.objects.filter(is_public=True)
    # power search functionality for my user 
    query = request.GET.get('q') # get data from a form using the name attribute 
    if query:
        media_list = media_list.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    # content pagination 
    paginator = Paginator(media_list, 12)
    # request template for more records 
    page_number = request.GET.get('page')
    media_assets = paginator.get_page(page_number)
    return render(request, 'media_assets/dashboard.html',{
        'media_assets' : media_assets,
        'query' : query
    })
    
@login_required
def my_media_view(request):
    '''user own media assets'''
    media_list = MediaAsset.objects.filter(uploaded_by=request.user)
    paginator = Paginator(media_list,12)
    page_number = request.GET.get('page')
    media_assets = paginator.get_page(page_number)
    
    return render(request, 'media_assets/my_media.html',{
        'media_assets': media_assets
    })

@login_required
def upload_view(request):
    '''upload media asset'''
    if request.method == "POST":
        form = MediaAssetForm(request.POST, request.FILES)
        if form.is_valid():
            media = form.save(commit=False)
            media.uploaded_by = request.user
            media.save()
            messages.success(request , 'Media Uploaded Successfully!!')
            return redirect('media_assets:my_media')
    else:
        form = MediaAssetForm()
    
    return render(request, 'media_assets/upload_media.html',
                  {'form' : form})
    
    

@login_required
def media_detail_view(request,pk):
    '''showcases full media details'''
    media = get_object_or_404(MediaAsset, pk=pk)
    # app specifications 
    if not media.is_public and media.uploaded_by != request.user and not request.user.is_teacher() and not request.user.is_superuser:
        messages.error(request, "This is media is private")
        return redirect('media_assets:dashboard')
    
    # Increment the view counts 
    media.views_count += 1
    media.save(update_fields=['views_count'])
    
    # compute permissions for template (template can't call methods with args)
    can_edit = media.can_edit(request.user)
    can_delete = media.can_delete(request.user)

    return render(request, 'media_assets/media_detail.html' , {
        'media' : media,
        'can_edit': can_edit,
        'can_delete': can_delete,
    })

### edit and delete views 
@login_required
def edit_media_view(request,pk):
    '''edit media assets based off pk'''
    media = get_object_or_404(MediaAsset, pk=pk)
    if not media.can_edit(request.user):
        messages.error(request, "You cannot edit this file.")
        return redirect('media_assets:dashboard')
    if request.method  == "POST":
        form = MediaAssetForm(request.POST, request.FILES, instance=media)
        if form.is_valid():
            form.save()
            messages.success(request, "Media Asset Updated Successfully")
            return redirect("media_assets:media_detail", pk=pk)
    else:
        form = MediaAssetForm(instance=media)
        
    return render(request, 'media_assets/edit_media.html', {'form' : form, 'media' : media})
        


@login_required
def delete_media_view(request,pk):
    '''Delete media assets based of pk'''
    media = get_object_or_404(MediaAsset,pk=pk)
    if not media.can_delete(request.user):
        messages.error(request, "You cannot delete this media")
        return redirect("media_assets:dashboard")
    
    if request.method == "POST":
        media.delete()
        messages.success(request,"Deleted Successfully")
        return redirect("media_assets:my_media")
    
    return render(request, 'media_assets/delete_media.html', {
        'media': media
    })