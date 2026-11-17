from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from labs.models import Lab, Flag, Submission, Solve


class LabInterfaceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='hacker1', password='password123')
        self.author = User.objects.create_user(username='author1', password='password123')

        self.lab = Lab.objects.create(
            author=self.author,
            title='ESP32 UART Exploit & Bus Snooping',
            slug='esp32-uart-exploit-01',
            description='Test challenge description',
            category='Firmware',
            points=500,
            wokwi_url='https://wokwi.com/projects/344606822858064466',
            is_published=True
        )

        self.flag = Flag.objects.create(
            lab=self.lab,
            flag_hash='FLAG{UART_B4UD_R4T3_PWN3D_7331}',
            is_case_sensitive=True
        )

    def test_lab_list_view(self):
        response = self.client.get(reverse('labs:lab_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ESP32 UART Exploit &amp; Bus Snooping')
        self.assertContains(response, '500 PTS')

    def test_lab_interface_view_renders_design_elements(self):
        response = self.client.get(reverse('labs:lab_interface', kwargs={'slug': self.lab.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ESP32 UART Exploit &amp; Bus Snooping')
        self.assertContains(response, 'WOKWI SIMULATION CANVAS')
        self.assertContains(response, 'FIRMWARE SOURCE')
        self.assertContains(response, 'UART SERIAL TELEMETRY')
        self.assertContains(response, 'FLAG{')
        self.assertContains(response, 'INJECT PAYLOAD / SUBMIT')

    def test_flag_submission_correct_standard_post(self):
        self.client.login(username='hacker1', password='password123')
        response = self.client.post(
            reverse('labs:lab_interface', kwargs={'slug': self.lab.slug}),
            {'flag': 'FLAG{UART_B4UD_R4T3_PWN3D_7331}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Submission.objects.filter(player=self.user, lab=self.lab, is_correct=True).exists())
        self.assertTrue(Solve.objects.filter(player=self.user, lab=self.lab, points_awarded=500).exists())
        self.assertContains(response, '+500 PTS Awarded!')
        self.assertContains(response, 'SOLVED')

    def test_flag_submission_inner_payload_normalized(self):
        # User types only the inner content inside the FLAG{ } box
        self.client.login(username='hacker1', password='password123')
        response = self.client.post(
            reverse('labs:lab_interface', kwargs={'slug': self.lab.slug}),
            {'flag': 'UART_B4UD_R4T3_PWN3D_7331'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Submission.objects.filter(player=self.user, lab=self.lab, is_correct=True).exists())
        self.assertTrue(Solve.objects.filter(player=self.user, lab=self.lab).exists())

    def test_flag_submission_incorrect(self):
        self.client.login(username='hacker1', password='password123')
        response = self.client.post(
            reverse('labs:lab_interface', kwargs={'slug': self.lab.slug}),
            {'flag': 'FLAG{WRONG_PAYLOAD}'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Submission.objects.filter(player=self.user, lab=self.lab, is_correct=False).exists())
        self.assertFalse(Solve.objects.filter(player=self.user, lab=self.lab).exists())
        self.assertContains(response, 'Checksum mismatch or invalid payload')

    def test_flag_submission_unauthenticated(self):
        response = self.client.post(
            reverse('labs:lab_interface', kwargs={'slug': self.lab.slug}),
            {'flag': 'FLAG{UART_B4UD_R4T3_PWN3D_7331}'}
        )
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
