from django.contrib.auth.decorators import login_required
from .models import Category, LearningResource
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import LearningResource


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
