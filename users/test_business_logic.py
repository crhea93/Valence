"""
Business Logic Tests for users/views.py
Tests the extracted utility functions from users/utils.py
"""

from django.test import TestCase
from users.models import CustomUser, Researcher, CAM
from users.forms import (
    CustomUserCreationForm,
    ParticipantSignupForm,
    ResearcherSignupForm,
    ContactForm,
)
from .models import Project


class SignupTestCase(TestCase):
    """Test coverage for signup() function - business logic tests"""

    def setUp(self):
        # Create a researcher user for the project
        researcher_user = CustomUser.objects.create_user(
            username="signup_researcher",
            email="signup_research@test.com",
            password="pass123",
        )
        Researcher.objects.create(user=researcher_user, affiliation="Test Uni")

        # Create some projects for the signup form
        self.project1 = Project.objects.create(
            name="SignupProject1",
            description="Test Project",
            researcher=researcher_user,
            password="TestPass123",
            name_participants="SP1",
        )

    def test_signup_form_valid(self):
        """Test signup form validation with valid data"""
        form = CustomUserCreationForm(
            data={
                "username": "newuser",
                "email": "newuser@test.com",
                "first_name": "New",
                "last_name": "User",
                "password1": "SecurePass123!",
                "password2": "SecurePass123!",
                "language_preference": "en",
            }
        )
        self.assertTrue(form.is_valid())

    def test_signup_form_invalid_password_mismatch(self):
        """Test signup form validation with mismatched passwords"""
        form = CustomUserCreationForm(
            data={
                "username": "newuser2",
                "email": "newuser2@test.com",
                "first_name": "New",
                "last_name": "User",
                "password1": "SecurePass123!",
                "password2": "DifferentPass123!",
                "language_preference": "en",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_signup_form_invalid_duplicate_username(self):
        """Test signup form validation with duplicate username"""
        # Create first user
        CustomUser.objects.create_user(
            username="duplicate", email="first@test.com", password="pass123"
        )

        # Try with duplicate username
        form = CustomUserCreationForm(
            data={
                "username": "duplicate",
                "email": "duplicate@test.com",
                "first_name": "Duplicate",
                "last_name": "User",
                "password1": "SecurePass123!",
                "password2": "SecurePass123!",
                "language_preference": "en",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)


class BusinessLogicTestCase(TestCase):
    """Test extracted business logic functions from utils.py"""

    def setUp(self):
        # Create test users
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
        )
        self.researcher_user = CustomUser.objects.create_user(
            username="researcher",
            email="researcher@test.com",
            password="researchpass123",
        )
        Researcher.objects.create(user=self.researcher_user, affiliation="Test Uni")

        # Create test project
        self.project = Project.objects.create(
            name="TestProject",
            description="Test Project",
            researcher=self.researcher_user,
            password="ProjectPass123",
            name_participants="TP",
        )

        # Create test CAM
        self.cam = CAM.objects.create(user=self.user)
        self.user.active_cam_num = self.cam.id
        self.user.save()

    def test_validate_project_password_valid(self):
        """Test project validation with correct password"""
        from users.utils import validate_project_password

        project, error = validate_project_password(
            self.project.name, self.project.password
        )
        self.assertIsNotNone(project)
        self.assertIsNone(error)
        self.assertEqual(project.id, self.project.id)

    def test_validate_project_password_invalid(self):
        """Test project validation with incorrect password"""
        from users.utils import validate_project_password

        project, error = validate_project_password(self.project.name, "WrongPassword")
        self.assertIsNone(project)
        self.assertIsNotNone(error)
        self.assertIn("Incorrect", error)

    def test_validate_project_not_exists(self):
        """Test project validation with non-existent project"""
        from users.utils import validate_project_password

        project, error = validate_project_password("NonExistent", "")
        self.assertIsNone(project)
        self.assertIsNotNone(error)
        self.assertIn("does not exist", error)

    def test_validate_project_empty_name(self):
        """Test project validation with empty project name"""
        from users.utils import validate_project_password

        project, error = validate_project_password("", "")
        self.assertIsNone(project)
        self.assertIsNone(error)  # Empty project name is not an error

    def test_create_user_from_signup_form_valid(self):
        """Test user creation from valid signup form"""
        from users.utils import create_user_from_signup_form

        form = CustomUserCreationForm(
            data={
                "username": "newuser",
                "email": "newuser@test.com",
                "first_name": "New",
                "last_name": "User",
                "password1": "SecurePass123!",
                "password2": "SecurePass123!",
                "language_preference": "en",
            }
        )
        self.assertTrue(form.is_valid())
        user, success = create_user_from_signup_form(form)
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "newuser")
        self.assertFalse(user.is_active)  # Users start inactive

    def test_process_contact_form_valid(self):
        """Test contact form processing with valid data"""
        from users.utils import process_contact_form

        form = ContactForm(
            data={
                "contacter": "Test User",
                "email": "test@example.com",
                "message": "Test message",
            }
        )
        self.assertTrue(form.is_valid())
        success, error = process_contact_form(form)
        self.assertTrue(success)
        self.assertEqual(error, "")

    def test_send_cam_email_valid(self):
        """Test CAM email sending"""
        from users.utils import send_cam_email
        from django.core.mail import outbox

        success, error = send_cam_email(
            self.user.id,
            self.user.username,
            "recipient@example.com",
        )
        self.assertTrue(success)
        self.assertEqual(error, "")
        # Email should be sent
        self.assertEqual(len(outbox), 1)

    def test_process_cam_image_invalid_base64(self):
        """Test image processing with invalid base64 data"""
        from users.utils import process_cam_image
        from django.conf import settings

        invalid_data = "not_valid_base64_data"
        file_name, success = process_cam_image(
            invalid_data, self.user, settings.MEDIA_URL
        )
        self.assertFalse(success)
        self.assertIsNone(file_name)

    def test_process_cam_zip_import_invalid_zip(self):
        """Test ZIP import with invalid ZIP file"""
        from users.utils import process_cam_zip_import
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create fake ZIP file
        fake_zip = SimpleUploadedFile(
            "notazip.zip", b"This is not a ZIP file", content_type="application/zip"
        )

        success, error = process_cam_zip_import(fake_zip, self.user, self.cam)
        self.assertFalse(success)
        self.assertIn("not a zip file", error.lower())

    def test_validate_project_empty_password(self):
        """Test project validation with empty password when password not set"""
        from users.utils import validate_project_password

        # Create project without password requirement
        no_password_project = Project.objects.create(
            name="NoPasswordProject",
            description="Project without password",
            researcher=self.researcher_user,
            password="",
            name_participants="NP",
        )

        project, error = validate_project_password(no_password_project.name, "")
        self.assertIsNotNone(project)
        self.assertIsNone(error)

    def test_create_researcher_user_valid(self):
        """Test researcher creation"""
        from users.utils import create_researcher_user

        form = ResearcherSignupForm(
            data={
                "username": "newresearcher",
                "email": "newresearch@test.com",
                "password1": "ResearchPass123!",
                "password2": "ResearchPass123!",
                "affiliation": "Test University",
                "language_preference": "en",
            }
        )
        self.assertTrue(form.is_valid())
        user, success = create_researcher_user(form)
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "newresearcher")
        self.assertTrue(user.is_researcher)


class ParticipantSignupFormTestCase(TestCase):
    """Test ParticipantSignupForm validation"""

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

    def test_participant_form_valid(self):
        """Test valid participant signup form"""
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

    def test_participant_form_password_mismatch(self):
        """Test participant form with mismatched passwords"""
        form = ParticipantSignupForm(
            data={
                "project_name": "",
                "project_password": "",
                "username": "participant2",
                "password1": "Pass123!",
                "password2": "DifferentPass123!",
                "language_preference": "en",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


class ResearcherSignupFormTestCase(TestCase):
    """Test ResearcherSignupForm validation"""

    def test_researcher_form_valid(self):
        """Test valid researcher signup form"""
        form = ResearcherSignupForm(
            data={
                "username": "newresearcher",
                "email": "research@test.com",
                "password1": "ResearchPass123!",
                "password2": "ResearchPass123!",
                "affiliation": "Test University",
                "language_preference": "en",
            }
        )
        self.assertTrue(form.is_valid())

    def test_researcher_form_password_mismatch(self):
        """Test researcher form with mismatched passwords"""
        form = ResearcherSignupForm(
            data={
                "username": "researcher3",
                "email": "research3@test.com",
                "password1": "ResearchPass123!",
                "password2": "DifferentPass123!",
                "affiliation": "Test University",
                "language_preference": "en",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


class ContactFormTestCase(TestCase):
    """Test ContactForm validation"""

    def test_contact_form_valid(self):
        """Test valid contact form"""
        form = ContactForm(
            data={
                "contacter": "Test User",
                "email": "test@example.com",
                "message": "Test message",
            }
        )
        self.assertTrue(form.is_valid())

    def test_contact_form_invalid_email(self):
        """Test contact form with invalid email"""
        form = ContactForm(
            data={
                "contacter": "Test User",
                "email": "not_an_email",
                "message": "Test message",
            }
        )
        self.assertFalse(form.is_valid())

    def test_contact_form_missing_fields(self):
        """Test contact form with missing required fields"""
        form = ContactForm(data={"contacter": "Test User"})
        self.assertFalse(form.is_valid())


class UtilsFunctionEdgeCasesTestCase(TestCase):
    """Test edge cases in extracted utils functions"""

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
        self.cam = CAM.objects.create(user=self.user)

    def test_validate_project_password_case_sensitive(self):
        """Test that project password is case-sensitive"""
        from users.utils import validate_project_password

        # Should fail with different case
        project, error = validate_project_password(self.project.name, "projectpass123")
        self.assertIsNone(project)
        self.assertIsNotNone(error)

    def test_remove_transparency_rgb_image(self):
        """Test remove_transparency with non-transparent image"""
        from users.utils import remove_transparency
        from PIL import Image

        # Create RGB image (no transparency)
        img = Image.new("RGB", (100, 100), (255, 0, 0))
        result = remove_transparency(img)
        self.assertEqual(result, img)

    def test_process_contact_form_with_special_characters(self):
        """Test contact form with special characters"""
        from users.utils import process_contact_form

        form = ContactForm(
            data={
                "contacter": "Test User <>&\"'",
                "email": "test@example.com",
                "message": 'Message with <special> &characters& and "quotes"',
            }
        )
        self.assertTrue(form.is_valid())
        success, error = process_contact_form(form)
        self.assertTrue(success)

    def test_send_cam_email_with_valid_user(self):
        """Test send_cam_email successfully sends email"""
        from users.utils import send_cam_email
        from django.core.mail import outbox

        success, error = send_cam_email(
            self.user.id, self.user.username, "recipient@example.com"
        )
        # Should succeed
        self.assertTrue(success)
        # Email should be sent
        self.assertEqual(len(outbox), 1)
