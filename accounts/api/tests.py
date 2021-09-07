from accounts.models import UserProfile
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from testing.TwitterTestCase import TwitterTestCase


LOGIN_ENDPOINT = '/api/accounts/login/'
LOGOUT_ENDPOINT = '/api/accounts/logout/'
SIGNUP_ENDPOINT = '/api/accounts/signup/'
LOGIN_STATUS_ENDPOINT = '/api/accounts/login_status/'
USER_PROFILE_DETAIL_URL = '/api/profiles/{}/'


class AccountsApiTest(TwitterTestCase):
    def setUp(self):
        self.clear_cache()
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
        self.assertEqual(response.data['user']['id'], self.user.id)

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
        
        
class UserProfileAPITests(TwitterTestCase):

    def test_update(self):
        user1, user1_client = self.create_user_and_client('user1')
        p = user1.profile
        p.nickname = 'old nickname'
        p.save()
        url = USER_PROFILE_DETAIL_URL.format(p.id)

        # test can only be updated by user himself.
        _, user2_client = self.create_user_and_client('user2')
        response = user2_client.put(url, {
            'nickname': 'a new nickname',
        })
        self.assertEqual(response.status_code, 403)
        p.refresh_from_db()
        self.assertEqual(p.nickname, 'old nickname')

        # update nickname
        response = user1_client.put(url, {
            'nickname': 'a new nickname',
        })
        self.assertEqual(response.status_code, 200)
        p.refresh_from_db()
        self.assertEqual(p.nickname, 'a new nickname')

        # update avatar
        response = user1_client.put(url, {
            'avatar': SimpleUploadedFile(
                name='my-avatar.jpg',
                content=str.encode('a fake image'),
                content_type='image/jpeg',
            ),
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual('my-avatar' in response.data['avatar'], True)
        p.refresh_from_db()
        self.assertIsNotNone(p.avatar)
