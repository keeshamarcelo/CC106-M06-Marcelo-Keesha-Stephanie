from django.test import TestCase


class HomePageTests(TestCase):
    def test_landing_page_renders_home_link(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome to My Django Application')
        self.assertContains(response, 'href="/Home/"')

    def test_home_page_renders_message_and_landing_link(self):
        response = self.client.get('/Home/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<title>My Home Page</title>')
        self.assertContains(response, 'Welcome to my first Django application!')
        self.assertContains(response, 'href="/"')
