from django.contrib.auth.decorators import login_required
from .models import Category, LearningResource, SavedResource
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages


def resource_list(request):

    query = request.GET.get('search')
    if query:
        resources = LearningResource.objects.filter(title__icontains=query)
    else:
        resources = LearningResource.objects.all().order_by('-upload_time')

    return render(request, 'core/resource_list.html', {'resources': resources})


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