from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):
    def test_user_str(self):
        user = User.objects.create_user(username="test@test.com", email="test@test.com")
        self.assertEqual(str(user), "test@test.com")

    def test_user_email_unique(self):
        User.objects.create_user(username="a@a.com", email="a@a.com")
        with self.assertRaises(Exception):
            User.objects.create_user(username="b@b.com", email="a@a.com")

    def test_user_date_of_birth_optional(self):
        user = User.objects.create_user(username="test@test.com", email="test@test.com")
        self.assertIsNone(user.date_of_birth)
