from django.test import TestCase
from .models import Category


class CategoryModelTest(TestCase):
    def test_category_creation(self):

        cat = Category.objects.create(name="Lecture Notes")
        self.assertEqual(str(cat), "Lecture Notes")
