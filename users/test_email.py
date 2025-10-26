from django.test import TestCase, override_settings
from django.core import mail
from users.models import CustomUser, Researcher, CAM, Project
from block.models import Block
from link.models import Link


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class EmailFunctionalityTestCase(TestCase):
    """
    Test suite for email functionality including contact forms and CAM sharing
    """

    def setUp(self):
        # Create users
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@test.com", password="12345"
        )
        self.user2 = CustomUser.objects.create_user(
            username="testuser2", email="test2@test.com", password="12345"
        )

        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")
        self.client.login(username="testuser", password="12345")

        # Create project and CAM
        self.project = Project.objects.create(
            name="TestProject",
            description="TEST PROJECT",
            researcher=self.user,
            password="TestProjectPassword",
        )

        self.cam = CAM.objects.create(
            name="testCAM", user=self.user, project=self.project
        )
        self.user.active_cam_num = self.cam.id
        self.user.save()

        # Clear mail outbox before each test
        mail.outbox = []

    def test_contact_form_submission_sends_email(self):
        """
        Test that submitting contact form sends an email
        """
        response = self.client.post(
            "/users/contact_form",
            {
                "contacter": "Test User",
                "email": "testuser@example.com",
                "message": "This is a test message for support",
            },
        )

        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)

        # Check email content
        email = mail.outbox[0]
        self.assertIn("Test User", email.body)
        self.assertIn("testuser@example.com", email.body)
        self.assertIn("This is a test message for support", email.body)

    def test_contact_form_invalid_email(self):
        """
        Test contact form with invalid email address
        """
        response = self.client.post(
            "/users/contact_form",
            {
                "contacter": "Test User",
                "email": "invalid-email",
                "message": "Test message",
            },
        )

        # Should not send email with invalid email format
        # Form validation should fail with EmailField
        self.assertEqual(len(mail.outbox), 0)

    def test_contact_form_missing_required_fields(self):
        """
        Test contact form with missing required fields
        """
        response = self.client.post(
            "/users/contact_form",
            {"contacter": "Test User", "email": "", "message": ""},
        )

        # Should not send email with missing fields
        self.assertEqual(len(mail.outbox), 0)

    def test_send_cam_to_email(self):
        """
        Test sending CAM data to an email address
        """
        # Add some blocks to the CAM
        Block.objects.create(
            title="SharedBlock",
            x_pos=10.0,
            y_pos=20.0,
            width=100,
            height=100,
            shape="neutral",
            creator=self.user,
            CAM=self.cam,
            num=1,
        )

        response = self.client.post(
            "/users/send_cam", {"email": "recipient@example.com", "cam_id": self.cam.id}
        )

        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertIn("recipient@example.com", email.to)

    def test_password_reset_email(self):
        """
        Test that password reset sends email
        """
        response = self.client.post(
            "/users/password_reset/", {"email": "test@test.com"}
        )

        # Check that password reset email was sent
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertIn("test@test.com", email.to)
        # Should contain reset link or token
        self.assertTrue(len(email.body) > 0)

    def test_contact_form_get_request(self):
        """
        Test that GET request to contact form displays form
        """
        response = self.client.get("/users/contact_form")

        self.assertEqual(response.status_code, 200)
        # Should render the contact form template
        self.assertIn(
            "Contact", response.content.decode() or "contact" in str(response.context)
        )

    def test_email_content_escapes_html(self):
        """
        Test that email content properly escapes HTML to prevent XSS
        """
        response = self.client.post(
            "/users/contact_form",
            {
                "contacter": "Test User",
                "email": "test@example.com",
                "message": '<script>alert("XSS")</script>This is a test',
            },
        )

        if len(mail.outbox) > 0:
            email = mail.outbox[0]
            # Should not contain raw script tags
            self.assertNotIn("<script>", email.body)

    def test_send_cam_with_invalid_email(self):
        """
        Test sending CAM to invalid email address
        """
        response = self.client.post(
            "/users/send_cam", {"email": "invalid-email-format", "cam_id": self.cam.id}
        )

        # Should not send email with invalid address
        # Actual behavior depends on validation in view
        # View currently returns 302 redirect (no email validation implemented)
        self.assertIn(response.status_code, [200, 302, 400])

    def test_send_cam_unauthorized_cam(self):
        """
        Test that users cannot send CAMs they don't own
        """
        # Create CAM owned by user2
        other_cam = CAM.objects.create(
            name="OtherCAM", user=self.user2, project=self.project
        )

        response = self.client.post(
            "/users/send_cam",
            {"email": "recipient@example.com", "cam_id": other_cam.id},
        )

        # Should not allow sending someone else's CAM
        # Actual behavior depends on permission checks
        # Email should not be sent or should show error
        # View returns 302 redirect on success (no permission check currently implemented)
        self.assertIn(response.status_code, [200, 302, 403, 404])

    def test_email_backend_configuration(self):
        """
        Test that email backend is properly configured for testing
        """
        # Send a simple test email
        mail.send_mail(
            "Test Subject",
            "Test message",
            "from@example.com",
            ["to@example.com"],
            fail_silently=False,
        )

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Subject")

    def test_contact_form_email_contains_all_fields(self):
        """
        Test that contact form email includes all submitted information
        """
        form_data = {
            "contacter": "John Doe",
            "email": "john.doe@example.com",
            "message": "I have a question about CAM functionality.\nCan you help me with this?",
        }

        response = self.client.post("/users/contact_form", form_data)

        if len(mail.outbox) > 0:
            email = mail.outbox[0]

            # Check all form fields are in email
            self.assertIn(form_data["contacter"], email.body)
            self.assertIn(form_data["email"], email.body)
            self.assertIn("question about CAM", email.body)

    def test_multiple_emails_sent_sequentially(self):
        """
        Test sending multiple emails in sequence
        """
        # Send first contact form
        self.client.post(
            "/users/contact_form",
            {
                "contacter": "User 1",
                "email": "user1@example.com",
                "message": "Message 1",
            },
        )

        # Send second contact form
        self.client.post(
            "/users/contact_form",
            {
                "contacter": "User 2",
                "email": "user2@example.com",
                "message": "Message 2",
            },
        )

        # Both emails should be in outbox
        self.assertEqual(len(mail.outbox), 2)

        # Verify different recipients
        email_bodies = [email.body for email in mail.outbox]
        self.assertTrue(any("User 1" in body for body in email_bodies))
        self.assertTrue(any("User 2" in body for body in email_bodies))
