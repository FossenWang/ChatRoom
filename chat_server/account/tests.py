from django.test import TestCase
from django.test import Client


class AccountTestCase(TestCase):
    def test_login(self):
        c = Client(enforce_csrf_checks=True)

        rsp = c.post('/api/account/login/',
                     {'username': 'Fossen', 'password': '123456'})
        self.assertEqual(rsp.status_code, 403)

        # post request need csrf token
        rsp = c.get('/api/csrf/')
        self.assertEqual(rsp.status_code, 200)
        csrftoken = rsp.json()['csrftoken']

        rsp = c.post('/api/account/login/',
                     {'username': 'Fossen', 'password': '123456'},
                     HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(rsp.status_code, 200)
        self.assertTrue(rsp.json()['login'])

        # fail login
        rsp = c.get('/api/csrf/')
        self.assertEqual(rsp.status_code, 200)
        csrftoken = rsp.json()['csrftoken']
        rsp = c.post('/api/account/login/',
                     {'username': 'Fossen', 'password': '1'},
                     HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(rsp.status_code, 403)
        self.assertFalse(rsp.json()['login'])

        rsp = c.get('/api/account/logout/')
        self.assertEqual(rsp.status_code, 200)
        self.assertTrue(rsp.json()['logout'])
