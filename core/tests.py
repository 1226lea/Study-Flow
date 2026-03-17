from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, LearningResource, SavedResource
from django.core.files.uploadedfile import SimpleUploadedFile


class StudyFlowIntegratedTest(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username='testuser', password='password123')
        self.other_user = User.objects.create_user(
            username='otheruser', password='password123')
        self.category = Category.objects.create(name="Lecture Notes")

        self.resource = LearningResource.objects.create(
            title="Python Basics",
            description="Intro to Python",
            category=self.category,
            uploader=self.user
        )
        self.client = Client()

    def test_category_creation(self):
        self.assertEqual(str(self.category), "Lecture Notes")

    def test_resource_list_view(self):
        response = self.client.get(reverse('resource_list'))
        self.assertEqual(response.status_code, 200)

    def test_search_functionality(self):

        response = self.client.get(
            reverse('resource_list'), {'search': 'Python'})
        self.assertContains(response, "Python Basics")
        response = self.client.get(
            reverse('resource_list'), {'search': 'Java'})
        self.assertNotContains(response, "Python Basics")

    def test_upload_resource_post(self):
        self.client.force_login(self.user)
        fake_file = SimpleUploadedFile("test.txt", b"file_content")
        response = self.client.post(reverse('upload_resource'), {
            'title': 'New Resource',
            'description': 'Description',
            'category': self.category.id,
            'resource_file': fake_file
        })
        self.assertEqual(LearningResource.objects.count(), 2)
        self.assertRedirects(response, reverse('resource_list'))

    def test_toggle_save_resource(self):

        self.client.force_login(self.user)

        self.client.get(
            reverse('toggle_save_resource', args=[self.resource.id]))
        self.assertTrue(SavedResource.objects.filter(
            user=self.user, resource=self.resource).exists())

        self.client.get(
            reverse('toggle_save_resource', args=[self.resource.id]))
        self.assertFalse(SavedResource.objects.filter(
            user=self.user, resource=self.resource).exists())

    def test_delete_resource_security(self):

        self.client.force_login(self.other_user)
        response = self.client.get(
            reverse('delete_resource', args=[self.resource.id]))
        self.assertTrue(LearningResource.objects.filter(
            id=self.resource.id).exists())
        self.assertRedirects(response, reverse('profile'))

    def test_edit_resource_view_get(self):

        self.client.force_login(self.user)
        response = self.client.get(
            reverse('edit_resource', args=[self.resource.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Basics")
