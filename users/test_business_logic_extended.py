"""
Extended Business Logic Tests with Mocking
Tests for image processing, ZIP import, and email functionality
with proper mocking of external dependencies
"""

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from unittest.mock import patch, MagicMock
from PIL import Image
from zipfile import ZipFile
import csv
import io
import base64

from users.models import CustomUser, Researcher, CAM
from users.forms import (
    ContactForm,
    CustomUserCreationForm,
    ParticipantSignupForm,
    ResearcherSignupForm,
)
from .models import Project
from block.models import Block


class ImageProcessingTestCase(TestCase):
    """Test image processing error cases"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
        )
        self.cam = CAM.objects.create(user=self.user)
        self.user.active_cam_num = self.cam.id
        self.user.save()

    def test_process_cam_image_invalid_base64_padding(self):
        """Test image processing with invalid base64 padding"""
        from users.utils import process_cam_image
        from django.conf import settings

        # Malformed base64 (incorrect padding)
        invalid_data = "data:image/png;base64,this_is_not_valid_base64!!!"

        file_name, success = process_cam_image(
            invalid_data, self.user, settings.MEDIA_URL
        )

        self.assertFalse(success)
        self.assertIsNone(file_name)

    def test_process_cam_image_empty_data(self):
        """Test image processing with empty data"""
        from users.utils import process_cam_image
        from django.conf import settings

        file_name, success = process_cam_image("", self.user, settings.MEDIA_URL)

        self.assertFalse(success)
        self.assertIsNone(file_name)

    def test_process_cam_image_malformed_header(self):
        """Test image processing with malformed data URI header"""
        from users.utils import process_cam_image
        from django.conf import settings

        # Missing base64 keyword
        malformed = "data:image/png;unknown,ABCDEF"

        file_name, success = process_cam_image(malformed, self.user, settings.MEDIA_URL)

        self.assertFalse(success)


class ZIPImportTestCase(TestCase):
    """Test ZIP import with mocked data"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
        )
        self.researcher = CustomUser.objects.create_user(
            username="researcher",
            email="researcher@test.com",
            password="researchpass123",
        )
        Researcher.objects.create(user=self.researcher, affiliation="Test Uni")
        self.project = Project.objects.create(
            name="TestProject",
            description="Test",
            researcher=self.researcher,
            password="ProjectPass123",
            name_participants="TP",
        )
        self.cam = CAM.objects.create(user=self.user, project=self.project)

    def _create_valid_zip_with_csv(self):
        """Helper to create a valid ZIP file with CSV data"""
        zip_buffer = io.BytesIO()

        with ZipFile(zip_buffer, "w") as z:
            # Create blocks.csv
            blocks_csv = io.StringIO()
            blocks_writer = csv.writer(blocks_csv)
            blocks_writer.writerow(
                ["id", "creator", "title", "shape", "CAM", "text_scale", "comment"]
            )
            blocks_writer.writerow(
                [
                    "",
                    str(self.user.id),
                    "Test Block 1",
                    "positive",
                    str(self.cam.id),
                    "14",
                    "Test comment",
                ]
            )
            blocks_writer.writerow(
                [
                    "",
                    str(self.user.id),
                    "Test Block 2",
                    "negative",
                    str(self.cam.id),
                    "12",
                    "",
                ]
            )
            z.writestr("blocks.csv", blocks_csv.getvalue())

            # Create links.csv
            links_csv = io.StringIO()
            links_writer = csv.writer(links_csv)
            links_writer.writerow(["source_id", "target_id", "creator", "CAM"])
            z.writestr("links.csv", links_csv.getvalue())

        zip_buffer.seek(0)
        return SimpleUploadedFile(
            "valid.zip", zip_buffer.getvalue(), content_type="application/zip"
        )

    @patch("users.utils.BlockResource")
    @patch("users.utils.LinkResource")
    def test_process_cam_zip_import_valid_zip(
        self, mock_link_resource, mock_block_resource
    ):
        """Test successful ZIP import with valid CSV data"""
        from users.utils import process_cam_zip_import

        # Setup resource mocks
        mock_block_resource_instance = MagicMock()
        mock_link_resource_instance = MagicMock()
        mock_block_resource.return_value = mock_block_resource_instance
        mock_link_resource.return_value = mock_link_resource_instance

        # Mock import_data to return success
        mock_result = MagicMock()
        mock_result.has_errors.return_value = False
        mock_block_resource_instance.import_data.return_value = mock_result
        mock_link_resource_instance.import_data.return_value = mock_result

        # Create valid ZIP
        valid_zip = self._create_valid_zip_with_csv()

        # Test import
        success, error = process_cam_zip_import(valid_zip, self.user, self.cam)

        self.assertTrue(success)
        self.assertEqual(error, "")

    def test_process_cam_zip_import_empty_zip(self):
        """Test ZIP import with empty ZIP file"""
        from users.utils import process_cam_zip_import

        # Create empty ZIP
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, "w") as z:
            pass  # Empty ZIP

        zip_buffer.seek(0)
        empty_zip = SimpleUploadedFile(
            "empty.zip", zip_buffer.getvalue(), content_type="application/zip"
        )

        success, error = process_cam_zip_import(empty_zip, self.user, self.cam)

        # Empty ZIP should succeed (no data to import)
        self.assertTrue(success)

    def test_process_cam_zip_import_missing_blocks_csv(self):
        """Test ZIP import with missing blocks.csv"""
        from users.utils import process_cam_zip_import

        # Create ZIP without blocks.csv
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, "w") as z:
            links_csv = io.StringIO()
            links_writer = csv.writer(links_csv)
            links_writer.writerow(["source_id", "target_id", "creator"])
            z.writestr("links.csv", links_csv.getvalue())

        zip_buffer.seek(0)
        incomplete_zip = SimpleUploadedFile(
            "incomplete.zip", zip_buffer.getvalue(), content_type="application/zip"
        )

        # Should succeed but only process links
        success, error = process_cam_zip_import(incomplete_zip, self.user, self.cam)
        self.assertTrue(success)

    def test_process_cam_zip_import_corrupted_csv(self):
        """Test ZIP import with corrupted CSV data"""
        from users.utils import process_cam_zip_import

        # Create ZIP with invalid CSV
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, "w") as z:
            z.writestr("blocks.csv", "This is not valid CSV\n\x00\x01\x02")
            z.writestr("links.csv", "Also invalid")

        zip_buffer.seek(0)
        corrupted_zip = SimpleUploadedFile(
            "corrupted.zip", zip_buffer.getvalue(), content_type="application/zip"
        )

        success, error = process_cam_zip_import(corrupted_zip, self.user, self.cam)

        # Should handle error gracefully
        self.assertFalse(success)
        self.assertIsNotNone(error)


class EmailSendingTestCase(TestCase):
    """Test email sending with proper assertions"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
        )
        self.cam = CAM.objects.create(user=self.user)

    @patch("users.utils.render_to_string")
    def test_process_contact_form_calls_render_template(self, mock_render):
        """Test that contact form renders email template"""
        from users.utils import process_contact_form

        mock_render.return_value = "<html>Test Email</html>"

        form = ContactForm(
            data={
                "contacter": "Test User",
                "email": "test@example.com",
                "message": "Test message",
            }
        )

        self.assertTrue(form.is_valid())
        success, error = process_contact_form(form)

        # Verify template was rendered
        self.assertTrue(success)
        mock_render.assert_called_once()
        call_args = mock_render.call_args
        self.assertEqual(call_args[0][0], "Admin/email_contact_us.html")

    def test_process_contact_form_sends_email_with_correct_data(self):
        """Test contact form sends email with form data"""
        from users.utils import process_contact_form

        form = ContactForm(
            data={
                "contacter": "John Doe",
                "email": "john@example.com",
                "message": "Important message",
            }
        )

        self.assertTrue(form.is_valid())
        success, error = process_contact_form(form)

        self.assertTrue(success)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertEqual(email.from_email, "john@example.com")
        self.assertIn("thibeaultrheaprogramming@gmail.com", email.to)
        self.assertEqual(email.subject, "CAM")

    @patch("users.utils.render_to_string")
    def test_send_cam_email_renders_template(self, mock_render):
        """Test send_cam_email renders template"""
        from users.utils import send_cam_email

        mock_render.return_value = "<html>CAM Email</html>"

        success, error = send_cam_email(
            self.user.id, self.user.username, "recipient@example.com"
        )

        self.assertTrue(success)
        mock_render.assert_called_once()
        call_args = mock_render.call_args
        self.assertEqual(call_args[0][0], "Admin/send_CAM.html")

    @patch("users.utils.render_to_string")
    def test_send_cam_email_attaches_csv_files(self, mock_render):
        """Test send_cam_email attaches CSV files"""
        from users.utils import send_cam_email

        mock_render.return_value = "<html>CAM Email</html>"

        success, error = send_cam_email(
            self.user.id, self.user.username, "recipient@example.com"
        )

        self.assertTrue(success)
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        # Should have attachments (blocks and links CSV)
        self.assertGreater(len(email.attachments), 0)

    def test_send_cam_email_with_custom_recipient(self):
        """Test send_cam_email with custom recipient"""
        from users.utils import send_cam_email

        custom_email = "custom@example.com"
        success, error = send_cam_email(self.user.id, self.user.username, custom_email)

        self.assertTrue(success)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(custom_email, mail.outbox[0].to)

    def test_send_cam_email_default_recipient(self):
        """Test send_cam_email uses default recipient"""
        from users.utils import send_cam_email

        success, error = send_cam_email(self.user.id, self.user.username)

        self.assertTrue(success)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("thibeaultrheaprogramming@gmail.com", mail.outbox[0].to)


class ParticipantUserCreationTestCase(TestCase):
    """Test participant user creation with project affiliation"""

    def setUp(self):
        self.researcher = CustomUser.objects.create_user(
            username="researcher",
            email="researcher@test.com",
            password="pass123",
        )
        Researcher.objects.create(user=self.researcher, affiliation="Test Uni")
        self.project = Project.objects.create(
            name="TestProject",
            description="Test",
            researcher=self.researcher,
            password="ProjectPass123",
            name_participants="TP",
        )

    @patch("users.utils.upload_cam_participant")
    def test_create_participant_user_with_project(self, mock_upload_cam):
        """Test participant creation with project affiliation"""
        from users.utils import create_participant_user
        from users.forms import ParticipantSignupForm

        form = ParticipantSignupForm(
            data={
                "project_name": self.project.name,
                "project_password": self.project.password,
                "username": "participant1",
                "password1": "PartPass123!",
                "password2": "PartPass123!",
                "language_preference": "en",
            }
        )

        self.assertTrue(form.is_valid())

        # Create request mock
        mock_request = MagicMock()

        user, success = create_participant_user(
            form, project=self.project, request=mock_request
        )

        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "participant1")
        self.assertEqual(user.active_project_num, self.project.id)
        # Verify CAM upload was called
        mock_upload_cam.assert_called_once()

    @patch("users.utils.create_individual_cam")
    def test_create_participant_user_without_project(self, mock_create_cam):
        """Test participant creation without project affiliation"""
        from users.utils import create_participant_user
        from users.forms import ParticipantSignupForm

        form = ParticipantSignupForm(
            data={
                "project_name": "",
                "project_password": "",
                "username": "participant2",
                "password1": "PartPass123!",
                "password2": "PartPass123!",
                "language_preference": "en",
            }
        )

        self.assertTrue(form.is_valid())

        mock_request = MagicMock()
        user, success = create_participant_user(
            form, project=None, request=mock_request
        )

        self.assertTrue(success)
        self.assertIsNotNone(user)
        # Verify individual CAM was created
        mock_create_cam.assert_called_once()


class FormValidationComprehensiveTestCase(TestCase):
    """Comprehensive form validation tests"""

    def test_custom_user_creation_form_passwords_must_match(self):
        """Test form validation rejects mismatched passwords"""
        form = CustomUserCreationForm(
            data={
                "username": "testuser",
                "email": "test@test.com",
                "first_name": "Test",
                "last_name": "User",
                "password1": "Pass123!",
                "password2": "Different123!",  # Mismatch
                "language_preference": "en",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_custom_user_creation_valid_form(self):
        """Test valid custom user creation form"""
        form = CustomUserCreationForm(
            data={
                "username": "testuser",
                "email": "test@test.com",
                "first_name": "Test",
                "last_name": "User",
                "password1": "Pass123!test",
                "password2": "Pass123!test",
                "language_preference": "en",
            }
        )
        self.assertTrue(form.is_valid())

    def test_participant_form_blank_project_allowed(self):
        """Test participant form allows blank project"""
        form = ParticipantSignupForm(
            data={
                "project_name": "",
                "project_password": "",
                "username": "participant",
                "email": "part@test.com",
                "first_name": "Part",
                "last_name": "Icipant",
                "password1": "Pass123!test",
                "password2": "Pass123!test",
                "language_preference": "en",
            }
        )
        self.assertTrue(form.is_valid())

    def test_researcher_form_valid_with_affiliation(self):
        """Test researcher form with affiliation"""
        form = ResearcherSignupForm(
            data={
                "username": "researcher",
                "email": "research@test.com",
                "first_name": "Res",
                "last_name": "Earcher",
                "password1": "Pass123!test",
                "password2": "Pass123!test",
                "affiliation": "Test University",
                "language_preference": "en",
            }
        )
        self.assertTrue(form.is_valid())

    def test_contact_form_long_message(self):
        """Test contact form with long message"""
        long_message = "x" * 1000
        form = ContactForm(
            data={
                "contacter": "Test User",
                "email": "test@example.com",
                "message": long_message,
            }
        )
        self.assertTrue(form.is_valid())
