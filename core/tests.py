from django.test import TestCase, Client
from django.urls import reverse
from .models import Category, LearningResource


class StudyFlowTest(TestCase):
    def setUp(self):

        self.category = Category.objects.create(name="Lecture Notes")
        self.client = Client()

    def test_category_creation(self):

        self.assertEqual(str(self.category), "Lecture Notes")

    def test_resource_list_view(self):

        response = self.client.get(reverse('resource_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/resource_list.html')

    def test_upload_redirect_if_not_logged_in(self):

        response = self.client.get(reverse('upload_resource'))
        self.assertEqual(response.status_code, 302)
