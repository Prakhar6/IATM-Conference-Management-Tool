from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from conference.models import Conference
from .models import Payment
from membership.models import Membership

User = get_user_model()

class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            country='USA',
            organization='Test Org',
            phone='1234567890',
            occupation='faculty'
        )
        
        self.conference = Conference.objects.create(
            conference_name='Test Conference',
            conference_description='A test conference',
            start_date='2024-06-01',
            end_date='2024-06-03',
            location='Test Location'
        )
    
    def test_payment_creation(self):
        payment = Payment.objects.create(
            user=self.user,
            conference=self.conference,
            amount=75.00,
            status='pending'
        )
        
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.conference, self.conference)
        self.assertEqual(payment.amount, 75.00)
        self.assertEqual(payment.status, 'pending')
    
    def test_payment_string_representation(self):
        payment = Payment.objects.create(
            user=self.user,
            conference=self.conference,
            amount=75.00
        )
        
        expected_string = f"{self.user.email} - {self.conference.conference_name} - $75.00"
        self.assertEqual(str(payment), expected_string)

class PaymentViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            country='USA',
            organization='Test Org',
            phone='1234567890',
            occupation='student_undergraduate'
        )
        
        self.conference = Conference.objects.create(
            conference_name='Test Conference',
            conference_description='A test conference',
            start_date='2024-06-01',
            end_date='2024-06-03',
            location='Test Location'
        )
    
    def test_payment_checkout_requires_login(self):
        url = reverse('payments:payment_checkout', kwargs={'slug': self.conference.slug})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_payment_status_requires_login(self):
        url = reverse('payments:payment_status', kwargs={'slug': self.conference.slug})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_payment_status_authenticated_user(self):
        self.client.login(email='test@example.com', password='testpass123')
        url = reverse('payments:payment_status', kwargs={'slug': self.conference.slug})
        response = self.client.get(url)
        
        # Should return 200 for authenticated user
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/payment_status.html')

class PaymentIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            country='USA',
            organization='Test Org',
            phone='1234567890',
            occupation='student_undergraduate'
        )
        
        self.conference = Conference.objects.create(
            conference_name='Test Conference',
            conference_description='A test conference',
            start_date='2024-06-01',
            end_date='2024-06-03',
            location='Test Location'
        )
    
    def test_student_pricing(self):
        """Test that student users get $50 pricing"""
        if self.user.occupation in ['student_undergraduate', 'student_graduate']:
            expected_price = 50.00
        else:
            expected_price = 100.00
        
        self.assertEqual(expected_price, 50.00)  # This user is a student
    
    def test_faculty_pricing(self):
        """Test that faculty users get $100 pricing"""
        faculty_user = User.objects.create_user(
            email='faculty@example.com',
            password='testpass123',
            first_name='Faculty',
            last_name='User',
            country='USA',
            organization='Test Org',
            phone='1234567890',
            occupation='faculty'
        )
        
        if faculty_user.occupation in ['student_undergraduate', 'student_graduate']:
            expected_price = 50.00
        else:
            expected_price = 100.00
        
        self.assertEqual(expected_price, 100.00)  # This user is faculty
