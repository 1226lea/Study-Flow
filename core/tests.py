from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, LearningResource, SavedResource
from django.core.files.uploadedfile import SimpleUploadedFile


class StudyFlowIntegratedTest(TestCase):
    """
    Integrated test suite for Study-Flow core functionality.
    Covers User Stories C2, S2, and security access controls.
    """

    def setUp(self):
        # 1. Initialize test data: Users and Categories
        self.user = User.objects.create_user(
            username='testuser', password='password123')
        self.other_user = User.objects.create_user(
            username='otheruser', password='password123')
        self.category = Category.objects.create(name="Lecture Notes")

        # 2. Create an initial resource for testing search and delete logic
        self.resource = LearningResource.objects.create(
            title="Python Basics",
            description="Intro to Python",
            category=self.category,
            uploader=self.user
        )
        self.client = Client()

    def test_category_creation(self):
        """Verify that categories are correctly instantiated and represented."""
        self.assertEqual(str(self.category), "Lecture Notes")

    def test_resource_list_view(self):
        """Ensure the main resource list page loads successfully (Status 200)."""
        response = self.client.get(reverse('resource_list'))
        self.assertEqual(response.status_code, 200)

    def test_search_functionality(self):
        """
        Verify Keyword Search (User Story C2).
        Checks if the filter correctly includes/excludes resources based on titles.
        """
        # Case: Search for an existing keyword
        response = self.client.get(
            reverse('resource_list'), {'search': 'Python'})
        self.assertContains(response, "Python Basics")
        response = self.client.get(
            reverse('resource_list'), {'search': 'Java'})
        self.assertNotContains(response, "Python Basics")

    def test_upload_resource_post(self):
        """
        Verify Resource Upload (User Story C1).
        Ensures authenticated users can successfully upload files to the database.
        """
        self.client.force_login(self.user)
        # Simulate a small text file upload
        fake_file = SimpleUploadedFile("test.txt", b"file_content")
        response = self.client.post(reverse('upload_resource'), {
            'title': 'New Resource',
            'description': 'Description',
            'category': self.category.id,
            'resource_file': fake_file
        })

        # Check if the resource count in DB increased to 2
        self.assertEqual(LearningResource.objects.count(), 2)
        self.assertRedirects(response, reverse('resource_list'))

    def test_toggle_save_resource(self):
        """
        Verify Save/Unsave toggle logic.
        Ensures a single view can handle both adding and removing bookmarks.
        """
        self.client.force_login(self.user)

        # Step 1: Save the resource
        self.client.get(
            reverse('toggle_save_resource', args=[self.resource.id]))
        self.assertTrue(SavedResource.objects.filter(
            user=self.user, resource=self.resource).exists())
        # Step 2: Unsave the same resource
        self.client.get(
            reverse('toggle_save_resource', args=[self.resource.id]))
        self.assertFalse(SavedResource.objects.filter(
            user=self.user, resource=self.resource).exists())

    def test_delete_resource_security(self):
        """
        Verify Security & Access Control.
        Ensures users CANNOT delete resources uploaded by others.
        """
        # Login as a user who IS NOT the uploader
        self.client.force_login(self.other_user)
        response = self.client.get(
            reverse('delete_resource', args=[self.resource.id]))

        # Resource should still exist in the database
        self.assertTrue(LearningResource.objects.filter(
            id=self.resource.id).exists())
        # User should be redirected with an error message
        self.assertRedirects(response, reverse('profile'))

    def test_edit_resource_view_get(self):
        """Verify the edit page populates existing data correctly for the uploader."""
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('edit_resource', args=[self.resource.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python Basics")
