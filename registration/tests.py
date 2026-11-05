from django.test import TestCase

from .models import Student


class StudentRegistrationTests(TestCase):
    def create_student(self, student_id='S123', first_name='Alex', last_name='Rivera'):
        return Student.objects.create(
            student_id=student_id,
            first_name=first_name,
            last_name=last_name,
            gender='Female',
            date_of_birth='2005-04-12',
            contact_no='555-0100',
        )

    def test_registration_page_renders_form(self):
        response = self.client.get('/registration/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="student_id"')
        self.assertContains(response, 'name="first_name"')
        self.assertContains(response, 'name="date_of_birth"')
        self.assertContains(response, 'Student Directory')
        self.assertContains(response, 'registration/style.css')

    def test_valid_registration_saves_student_and_redirects(self):
        response = self.client.post(
            '/registration/',
            {
                'student_id': 'S123',
                'first_name': 'Alex',
                'last_name': 'Rivera',
                'gender': 'Female',
                'date_of_birth': '2005-04-12',
                'contact_no': '555-0100',
            },
        )

        self.assertRedirects(response, '/registration/success/')
        self.assertEqual(Student.objects.count(), 1)

    def test_invalid_registration_rerenders_form_without_saving(self):
        response = self.client.post(
            '/registration/',
            {
                'student_id': '',
                'first_name': 'Alex',
                'last_name': 'Rivera',
                'gender': 'Female',
                'date_of_birth': '2005-04-12',
                'contact_no': '555-0100',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')
        self.assertEqual(Student.objects.count(), 0)

    def test_student_list_searches_and_sorts_students(self):
        self.create_student('S124', 'Jamie', 'Brown')
        self.create_student('S125', 'Taylor', 'Adams')

        response = self.client.get('/registration/students/', {'q': 'jam'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'S124')
        self.assertNotContains(response, 'S125')

        response = self.client.get('/registration/students/')
        self.assertLess(
            response.content.index(b'Taylor'),
            response.content.index(b'Jamie'),
        )

    def test_student_detail_and_missing_record(self):
        student = self.create_student()

        response = self.client.get(f'/registration/students/{student.pk}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, student.student_id)
        self.assertEqual(
            self.client.get('/registration/students/9999/').status_code,
            404,
        )

    def test_student_create_and_update(self):
        create_response = self.client.post(
            '/registration/students/create/',
            {
                'student_id': 'S126',
                'first_name': 'Morgan',
                'last_name': 'Lee',
                'gender': 'Male',
                'date_of_birth': '2004-01-02',
                'contact_no': '555-0101',
            },
        )
        student = Student.objects.get(student_id='S126')
        self.assertRedirects(create_response, '/registration/students/')

        update_response = self.client.post(
            f'/registration/students/{student.pk}/edit/',
            {
                'student_id': 'S126',
                'first_name': 'Morgan',
                'last_name': 'Updated',
                'gender': 'Male',
                'date_of_birth': '2004-01-02',
                'contact_no': '555-0101',
            },
            follow=True,
        )
        self.assertRedirects(
            update_response,
            f'/registration/students/{student.pk}/',
        )
        self.assertContains(update_response, 'Student record updated successfully.')
        student.refresh_from_db()
        self.assertEqual(student.last_name, 'Updated')

    def test_shared_navigation_is_available_on_home_and_directory_pages(self):
        for url in ('/', '/Home/', '/registration/students/'):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'aria-label="Main navigation"')
                self.assertContains(response, 'Student Directory')

    def test_student_delete_requires_post(self):
        student = self.create_student()
        delete_url = f'/registration/students/{student.pk}/delete/'

        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Student.objects.filter(pk=student.pk).exists())

        response = self.client.post(delete_url)
        self.assertRedirects(response, '/registration/students/')
        self.assertFalse(Student.objects.filter(pk=student.pk).exists())
