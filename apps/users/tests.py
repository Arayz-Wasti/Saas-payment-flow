from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class UserAuthTests(TestCase):
    """Test user registration and authentication."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.register_url = '/api/users/register/'
        self.token_url = '/api/users/token/'
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpassword123',
            'company_name': 'Test Labs'
        }

    def test_create_user_successful(self) -> None:
        """Test creating a new user."""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.company_name, self.user_data['company_name'])
        self.assertFalse(user.is_active_subscriber)

    def test_obtain_token_successful(self) -> None:
        """Test obtaining a JWT token."""
        User.objects.create_user(**self.user_data)
        
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.token_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
