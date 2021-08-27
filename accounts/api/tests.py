from accounts.models import UserProfile
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient


LOGIN_ENDPOINT = '/api/accounts/login/'
LOGOUT_ENDPOINT = '/api/accounts/logout/'
SIGNUP_ENDPOINT = '/api/accounts/signup/'
LOGIN_STATUS_ENDPOINT = '/api/accounts/login_status/'


class AccountsApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = self.createUser(
            username='testuser',
            password='correctpassword',
            email='test@fake.com'
        )

    def createUser(self, username, password, email):
        return User.objects.create_user(username=username, password=password, email=email)

    def test_login(self):
        # case 1: send GET request
        response = self.client.get(LOGIN_ENDPOINT, {
                'username': self.user.username,
                'password': 'correctpassword',
            })
        self.assertEqual(response.status_code, 405)

        # case 2: wrong password
        response = self.client.post(LOGIN_ENDPOINT, {
                'username': self.user.username,
                'password': 'wrongpassword',
            })
        self.assertEqual(response.status_code, 400)

        # case 3: success
        response = self.client.get(LOGIN_STATUS_ENDPOINT)
        self.assertFalse(response.data['has_logged_in'])

        response = self.client.post(LOGIN_ENDPOINT, {
            'username': self.user.username,
            'password': 'correctpassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['user'])
        self.assertEqual(response.data['user']['email'], self.user.email)

        response = self.client.get(LOGIN_STATUS_ENDPOINT)
        self.assertTrue(response.data['has_logged_in'])

    def test_logout(self):
        self.client.post(LOGIN_ENDPOINT, {
            'username': self.user.username,
            'password': 'correctpassword',
        })
        response = self.client.get(LOGIN_STATUS_ENDPOINT)
        self.assertTrue(response.data['has_logged_in'])

        # case 1: send GET request
        response = self.client.get(LOGOUT_ENDPOINT)
        self.assertEqual(response.status_code, 405)

        # case 2: success
        response = self.client.post(LOGOUT_ENDPOINT)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(LOGIN_STATUS_ENDPOINT)
        self.assertFalse(response.data['has_logged_in'])

    def test_signup(self):
        # case 1: send GET request
        data = {
            'username': 'newuser',
            'password': 'anewpassword',
            'email': 'newuser@fake.com'
        }
        response = self.client.get(SIGNUP_ENDPOINT, data)
        self.assertEqual(response.status_code, 405)

        # case 2: invalid email
        data = {
            'username': 'newuser',
            'password': 'anewpassword',
            'email': '123'
        }
        response = self.client.post(SIGNUP_ENDPOINT, data)
        self.assertEqual(response.status_code, 400)

        # case 3: password is too short
        data = {
            'username': 'newuser',
            'password': '1234',
            'email': 'newuser@fake.com'
        }
        response = self.client.post(SIGNUP_ENDPOINT, data)
        self.assertEqual(response.status_code, 400)

        # case 4: user name is too long
        data = {
            'username': 'aloooooooooooooooooooooooogusername',
            'password': 'anewpassword',
            'email': 'newuser@fake.com'
        }
        response = self.client.post(SIGNUP_ENDPOINT, data)
        self.assertEqual(response.status_code, 400)

        # case 5: success
        data = {
            'username': 'newuser',
            'password': 'anewpassword',
            'email': 'newuser@fake.com'
        }
        response = self.client.post(SIGNUP_ENDPOINT, data)
        self.assertEqual(response.status_code, 201)
        created_user_id = response.data['user']['id']
        profile = UserProfile.objects.filter(user_id=created_user_id).first()
        self.assertNotEqual(profile, None)
        response = self.client.get(LOGIN_STATUS_ENDPOINT)
        self.assertTrue(response.data['has_logged_in'])
