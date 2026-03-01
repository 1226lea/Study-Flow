from django.shortcuts import render, redirect
from .models import LearningResource


def resource_list(request):

    query = request.GET.get('search')
    if query:
        resources = LearningResource.objects.filter(title__icontains=query)
    else:
        resources = LearningResource.objects.all().order_by('-upload_time')

    return render(request, 'core/resource_list.html', {'resources': resources})
