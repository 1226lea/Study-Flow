from django.contrib.auth.decorators import login_required
from .models import Category, LearningResource, SavedResource
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages


def resource_list(request):
    # Fetch all resources (newest first) and all categories
    resources = LearningResource.objects.all().order_by('-upload_time')
    categories = Category.objects.all()

    # Handle keyword search (User Story C2)
    search_query = request.GET.get('search')
    if search_query:
        resources = resources.filter(title__icontains=search_query)

    # Handle category filtering (User Story S2)
    category_id = request.GET.get('category')
    if category_id:
        resources = resources.filter(category_id=category_id)

    # Pass the data to the frontend template
    context = {
        'resources': resources,
        'categories': categories,
    }
    return render(request, 'core/resource_list.html', context)


def register_view(request):

    if request.user.is_authenticated:
        return redirect('resource_list')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, f"Welcome {user.username}! Account created.")

            return redirect('resource_list')
    else:
        form = UserCreationForm()

    return render(request, 'core/register.html', {'form': form})


@login_required
def upload_resource(request):
    if request.method == 'POST':

        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')

        resource_file = request.FILES.get('resource_file')

        if title and resource_file:

            LearningResource.objects.create(
                title=title,
                description=description,
                category_id=category_id,
                file=resource_file,
                uploader=request.user
            )
            messages.success(request, "Resource uploaded successfully!")
            return redirect('resource_list')
        else:
            messages.error(request, "Title and File are required.")

    categories = Category.objects.all()
    return render(request, 'core/upload.html', {'categories': categories})

# User Profile and Save Resource Logic

@login_required
def profile_view(request):
    # 1. Get resources uploaded by the current user
    uploaded_resources = LearningResource.objects.filter(uploader=request.user).order_by('-upload_time')
    
    # 2. Get resources saved by the current user
    saved_items = SavedResource.objects.filter(user=request.user).order_by('-saved_at')
    
    # 3. Pass data to the template
    context = {
        'uploaded_resources': uploaded_resources,
        'saved_items': saved_items,
    }
    return render(request, 'core/profile.html', context)


@login_required
def toggle_save_resource(request, resource_id):
    # Find the requested resource or return 404
    resource = get_object_or_404(LearningResource, id=resource_id)
    
    # Check if the user has already saved this resource
    saved_item = SavedResource.objects.filter(user=request.user, resource=resource).first()
    
    if saved_item:
        # If already saved, clicking again removes it (Unsave)
        saved_item.delete()
        messages.success(request, f"Removed '{resource.title}' from your saved items.")
    else:
        # If not saved, create a new save record
        SavedResource.objects.create(user=request.user, resource=resource)
        messages.success(request, f"Saved '{resource.title}' to your profile!")
        
    # Redirect the user back to the page they were just on
    return redirect(request.META.get('HTTP_REFERER', 'resource_list'))

# Delete Resource Logic (with security check)

@login_required
def delete_resource(request, resource_id):
    # 1. Try to find the resource (return 404 if not found)
    resource = get_object_or_404(LearningResource, id=resource_id)
    
    # 2. Security Check
    if resource.uploader != request.user:
        # If not, show an error message and refuse deletion
        messages.error(request, "Permission denied. You can only delete your own resources.")
        return redirect('profile')
        
    # 3. If the user owns it, proceed with deletion
    resource.delete()
    
    # Show a success message
    messages.success(request, f"Successfully deleted '{resource.title}'.")
    
    # Redirect back to the user's profile page
    return redirect('profile')

def resource_detail(request, resource_id):
    # Retrieve the resource by ID, and return a 404 error if it is not found
    resource = get_object_or_404(LearningResource, id=resource_id)
    
    context = {
        'resource': resource,
    }
    return render(request, 'core/resource_detail.html', context)

@login_required
def edit_resource(request, resource_id):
    # Fetch the resource object
    resource = get_object_or_404(LearningResource, id=resource_id)
    
    # Security check: Deny access if the user is not the uploader
    if request.user != resource.uploader:
        messages.error(request, "Access Denied: You can only edit your own resources.")
        return redirect('resource_detail', resource_id=resource.id)

    # Process the submitted form data
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        resource_file = request.FILES.get('resource_file')

        if title:
            # Update resource attributes
            resource.title = title
            resource.description = description
            if category_id:
                resource.category_id = category_id
            
            # Only replace the old file if the user actually uploaded a new one
            if resource_file:
                resource.file = resource_file
                
            resource.save()
            messages.success(request, "Resource updated successfully!")
            return redirect('resource_detail', resource_id=resource.id)
        else:
            messages.error(request, "Title is required.")

    # GET request: Prepare category data for the frontend dropdown menu
    categories = Category.objects.all()
    context = {
        'resource': resource,
        'categories': categories,
    }
    return render(request, 'core/edit_resource.html', context)