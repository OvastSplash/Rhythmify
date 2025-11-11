from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class RedirectToProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(user_login="123", password="123")

    def test_redirects_to_profile(self):
        login_url = reverse('login')
        profile_url = reverse('profile', kwargs={'user_id': self.user.id})

        login_data = {
            'user_login': self.user.user_login,
            'password': '123'
        }

        response = self.client.post(
            login_url,
            data=login_data,
        )

        self.assertRedirects(response, profile_url)