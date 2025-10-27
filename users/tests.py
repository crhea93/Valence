from django.test import TestCase, override_settings
from users.models import CustomUser, Researcher, CAM
from django.urls import reverse
from .models import Project
from block.models import Block
from link.models import Link
import requests
import json
# Create your tests here.


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class UserTestCase(TestCase):
    def setUp(self):
        # Set up a user
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@test.test", password="12345"
        )
        self.user2 = CustomUser.objects.create_user(
            username="testuser2", email="test2@test.test", password="12345"
        )
        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")
        login = self.client.login(username="testuser", password="12345")
        # Create project belonging to user 2
        self.project = Project.objects.create(
            name="TestProject",
            description="TEST PROJECT",
            researcher=self.user2,
            password="TestProjectPassword",
        )

    def test_user_creation_nonAff(self):
        """
        Test to make sure when a participant user is created and not affiliated with a project. We
        assume the participant does not enter a password (though by html design they "select" a project by default)
        """
        # Create new user with create_participant view
        response = self.client.post(
            "/users/create_participant",
            {
                "project_name": self.project.name,
                "project_password": "",
                "username": "newUser",
                "password1": "MEOWMEOW2",
                "password2": "MEOWMEOW2",
                "language_preference": "en",
            },
        )
        # Check that user is created
        new_part = CustomUser.objects.get(username="newUser")
        self.assertTrue(new_part)
        # Check that user has a CAM
        # new_part.refresh_from_db()
        # self.assertEqual(len(new_part.cam_set.all()), 1)
        # Check that user is not affiliated with a project
        # self.assertEqual(len(new_part.project_set.all()), 0)

    def test_user_creation_aff(self):
        """
        Test to make sure when a participant user is created and is affiliated with a project.
        """
        # Create new user with create_participant view
        response = self.client.post(
            "/users/create_participant",
            {
                "project_name": self.project.name,
                "project_password": self.project.password,
                "username": "newUser",
                "password1": "MEOWMEOW2",
                "password2": "MEOWMEOW2",
                "language_preference": "en",
            },
        )
        # Check that user is created
        new_part = CustomUser.objects.get(username="newUser")
        self.assertTrue(new_part)
        new_part.refresh_from_db()
        # Check that user has a CAM
        self.assertEqual(len(new_part.cam_set.all()), 1)
        # Check that user is now affiliated with a project
        # self.assertEqual(new_part.active_project_num, 1)
        # self.project.refresh_from_db()
        # self.assertTrue(False)

    def test_create_project(self):
        project_data = {
            "label": "Test Project",
            "description": "Test Description",
            "num_participants": 2,
            "name_participants": "T",
            "participantType": "auto_participants",
            "languagePreference": "en",
            "conceptDelete": False,
        }
        response = self.client.post(reverse("create_project"), project_data)
        # Check that the project is created
        projects = Project.objects.filter(researcher=self.user.id)
        self.assertTrue(len(projects), 1)
        self.assertTrue(CustomUser.objects.get(username="T1"), "T1")

    def test_project_link_test_1(self):
        """
        Test that a user is created with a new cam when using the project login link with cam_op=new
        """
        cam_op = "new"  # Creating new CAM for a new user
        # Create user called cmeow_test with the password meow_test for the project TestProject with the password TestProjectPassword
        url = (
            "/users/join_project_link?username=cmeow_test&pword=meow_test&"
            "proj_name=TestProject&proj_pword=TestProjectPassword&cam_op=" + cam_op
        )
        response = self.client.get(url)
        # Check that user is created
        new_part = CustomUser.objects.get(username="cmeow_test")
        self.assertTrue(new_part)
        new_part.refresh_from_db()
        # Check that user has a CAM
        self.assertEqual(len(new_part.cam_set.all()), 1)

    def test_project_link_test_2(self):
        """
        Test that a user which is already created gets a new cam when using the project login link with cam_op=new

        We first create a new user and then we create a second CAM for him
        """
        cam_op = "new"  # Creating new CAM for a new user
        # Create user called cmeow_test with the password meow_test for the project TestProject with the password TestProjectPassword
        url = (
            "/users/join_project_link?username=cmeow_test&pword=meow_test&"
            "proj_name=TestProject&proj_pword=TestProjectPassword&cam_op=" + cam_op
        )
        response = self.client.get(url)
        # Now create new CAM for user
        response = self.client.get(url)
        participant = CustomUser.objects.get(username="cmeow_test")
        participant.refresh_from_db()
        # Check that user has a CAM
        self.assertEqual(len(participant.cam_set.all()), 2)

    def test_project_link_test_3(self):
        """
        Test that a user which is already created gets a new cam when using the project login link with cam_op=reuse

        We first create a new user and then we create a second CAM for him
        """
        cam_op = "new"  # Creating new CAM for a new user
        # Create user called cmeow_test with the password meow_test for the project TestProject with the password TestProjectPassword
        url = (
            "/users/join_project_link?username=cmeow_test&pword=meow_test&"
            "proj_name=TestProject&proj_pword=TestProjectPassword&cam_op=" + cam_op
        )
        response = self.client.get(url)
        participant = CustomUser.objects.get(username="cmeow_test")
        # Now reuse CAM for user
        cam_op = "reuse"
        url = (
            "/users/join_project_link?username=cmeow_test&pword=meow_test&"
            "proj_name=TestProject&proj_pword=TestProjectPassword&cam_op=%s&cam_id=%s"
            % (cam_op, participant.active_cam_num)
        )
        response = self.client.get(url)
        self.assertEqual(response.url, "/users/index/")
        participant.refresh_from_db()
        # Check that user has only one CAM
        self.assertEqual(len(participant.cam_set.all()), 1)

    def test_project_link_test_4(self):
        """
        Test that a user which is already created gets a duplicate cam when using the project login link with cam_op=duplicate

        We first create a new user and then we clone the CAM
        """
        cam_op = "new"  # Creating new CAM for a new user
        # Create user called cmeow_test with the password meow_test for the project TestProject with the password TestProjectPassword
        url = (
            "/users/join_project_link?username=cmeow_test&pword=meow_test&"
            "proj_name=TestProject&proj_pword=TestProjectPassword&cam_op=" + cam_op
        )
        response = self.client.get(url)
        participant = CustomUser.objects.get(username="cmeow_test")
        # Now duplicate CAM for user
        cam_op = "duplicate"
        url = (
            "/users/join_project_link?username=cmeow_test&pword=meow_test&"
            "proj_name=TestProject&proj_pword=TestProjectPassword&cam_op=%s&cam_id=%s"
            % (cam_op, participant.active_cam_num)
        )
        response = self.client.get(url)
        self.assertEqual(response.url, "/users/index/")
        participant.refresh_from_db()
        # Check that user has only one CAM
        self.assertEqual(len(participant.cam_set.all()), 2)

    def test_login_logout(self):
        """
        Test user login and logout functionality
        """
        # Logout first
        self.client.logout()

        # Test login with correct credentials
        response = self.client.post(
            "/users/loginpage", {"username": "testuser", "password": "12345"}
        )
        self.assertIn(response.status_code, [301, 302])  # Should redirect after login

        # Test logout
        response = self.client.get("/users/logout")
        self.assertIn(response.status_code, [301, 302])  # Should redirect after logout

    def test_login_invalid_credentials(self):
        """
        Test login with invalid credentials
        """
        self.client.logout()
        response = self.client.post(
            "/users/loginpage", {"username": "testuser", "password": "wrongpassword"}
        )
        # Should stay on login page (status 200) and show error message
        self.assertEqual(response.status_code, 200)

    def test_create_researcher(self):
        """
        Test researcher account creation
        """
        response = self.client.post(
            "/users/create_researcher",
            {
                "username": "newresearcher",
                "password1": "ResearchPass123!",
                "password2": "ResearchPass123!",
                "email": "researcher@test.com",
                "affiliation": "Test University",
                "language_preference": "en",
            },
        )

        # Check that researcher user is created
        new_researcher = CustomUser.objects.get(username="newresearcher")
        self.assertTrue(new_researcher)
        self.assertTrue(new_researcher.is_researcher)

        # Check that Researcher profile is created
        researcher_profile = Researcher.objects.get(user=new_researcher)
        self.assertEqual(researcher_profile.affiliation, "Test University")

    def test_language_change(self):
        """
        Test language preference change
        """
        response = self.client.post("/users/language_change", {"language": "de"})

        self.user.refresh_from_db()
        self.assertEqual(self.user.language_preference, "de")

    def test_project_deletion(self):
        """
        Test that a project can be deleted by its owner
        """
        # Create a new project owned by logged-in user
        new_project = Project.objects.create(
            name="DeleteTest",
            description="Test project for deletion",
            researcher=self.user,
            password="testpass",
            name_participants="DT",
        )

        response = self.client.post(
            "/users/delete_project", {"project_id": new_project.id}
        )

        # Check that project is deleted
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=new_project.id)

    def test_project_settings_update(self):
        """
        Test updating project settings
        """
        project = Project.objects.create(
            name="SettingsTest",
            description="Original description",
            researcher=self.user,
            password="originalpass",
            name_participants="ST",
        )

        # Set the user's active project
        self.user.active_project_num = project.id
        self.user.save()

        response = self.client.post(
            "/users/project_settings",
            {
                "nameUpdate": project.name,
                "descriptionUpdate": "Updated description",
            },
        )

        project.refresh_from_db()
        self.assertEqual(project.description, "Updated description")

    def test_create_random_user(self):
        """
        Test creation of random anonymous users
        """
        response = self.client.post(
            "/users/create_random", {"language_preference": "en"}
        )

        # Check that a random user was created
        random_users = CustomUser.objects.filter(random_user=True)
        self.assertTrue(random_users.exists())

    def test_model_cam_update(self):
        """
        Test CAM model update method
        """
        from users.models import CAM

        cam = CAM.objects.create(
            name="TestCAM",
            user=self.user,
            project=self.project,
            description="Original description",
        )

        # Test update method
        cam.update({"description": "Updated description"})
        cam.refresh_from_db()

        self.assertEqual(cam.description, "Updated description")

    def test_model_project_update(self):
        """
        Test Project model update method
        """
        project = Project.objects.create(
            name="UpdateTest",
            description="Original",
            researcher=self.user,
            name_participants="UT",
        )

        # Test update method
        project.update({"description": "Modified"})
        project.refresh_from_db()

        self.assertEqual(project.description, "Modified")

    def test_user_string_representation(self):
        """
        Test model __str__ methods
        """
        self.assertEqual(str(self.user), "testuser")
        self.assertEqual(str(self.researcher), "testuser")
        self.assertTrue("TestProject" in str(self.project))

    def test_project_unique_name_constraint(self):
        """
        Test that project names must be unique
        """
        from django.db import IntegrityError

        # Try to create another project with same name
        with self.assertRaises(IntegrityError):
            Project.objects.create(
                name="TestProject",  # Same as self.project
                description="Duplicate name",
                researcher=self.user,
            )


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class CAMOperationsTestCase(TestCase):
    def setUp(self):
        # Set up a user
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@test.test", password="12345"
        )
        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")
        login = self.client.login(username="testuser", password="12345")

        # Create project
        self.project = Project.objects.create(
            name="TestProject",
            description="TEST PROJECT",
            researcher=self.user,
            password="TestProjectPassword",
        )

        # Create CAM
        self.cam = CAM.objects.create(
            name="testCAM", user=self.user, project=self.project
        )
        self.user.active_cam_num = self.cam.id
        self.user.save()

        # Create some blocks and links for testing
        self.block1 = Block.objects.create(
            title="Block1",
            x_pos=10.0,
            y_pos=10.0,
            height=100,
            width=100,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
            num=1,
        )
        self.block2 = Block.objects.create(
            title="Block2",
            x_pos=150.0,
            y_pos=150.0,
            height=100,
            width=100,
            creator=self.user,
            shape="positive",
            CAM=self.cam,
            num=2,
        )
        self.link = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
            arrow_type="uni",
        )

    def test_create_individual_cam(self):
        """
        Test creating a new individual CAM
        """
        response = self.client.post(
            "/users/create_individual_cam",
            {"cam_name": "NewCAM", "cam_description": "Test description"},
        )

        # Check that new CAM was created
        new_cam = CAM.objects.filter(name="NewCAM").first()
        self.assertIsNotNone(new_cam)
        self.assertEqual(new_cam.user, self.user)

    def test_load_cam(self):
        """
        Test loading CAM data
        """
        response = self.client.post("/users/load_cam", {"cam_id": self.cam.id})

        self.assertEqual(response.status_code, 200)

    def test_delete_cam(self):
        """
        Test deleting a CAM
        """
        cam_to_delete = CAM.objects.create(
            name="DeleteMe", user=self.user, project=self.project
        )

        response = self.client.post("/users/delete_cam", {"cam_id": cam_to_delete.id})

        # Check that CAM is deleted
        with self.assertRaises(CAM.DoesNotExist):
            CAM.objects.get(id=cam_to_delete.id)

    def test_update_cam_name(self):
        """
        Test updating CAM name
        """
        response = self.client.post(
            "/users/update_cam_name",
            {"cam_id": self.cam.id, "new_name": "UpdatedCAMName"},
        )

        self.cam.refresh_from_db()
        self.assertEqual(self.cam.name, "UpdatedCAMName")

    def test_download_cam(self):
        """
        Test downloading CAM as JSON
        """
        response = self.client.get("/users/download_cam", {"cam_id": self.cam.id})

        self.assertEqual(response.status_code, 200)

    def test_clone_cam(self):
        """
        Test cloning a CAM with all its blocks and links
        """
        original_cam_id = self.cam.id

        response = self.client.post(
            "/users/clone_cam", {"cam_id": self.cam.id, "new_name": "ClonedCAM"}
        )

        # Check that new CAM was created
        cloned_cam = CAM.objects.filter(name="ClonedCAM").first()
        self.assertIsNotNone(cloned_cam)
        self.assertNotEqual(cloned_cam.id, original_cam_id)

    def test_clear_cam(self):
        """
        Test clearing all blocks and links from a CAM
        """
        response = self.client.post("/users/clear_CAM", {"clear_cam_valid": True})

        # Check that all blocks are deleted
        remaining_blocks = Block.objects.filter(CAM=self.cam)
        self.assertEqual(remaining_blocks.count(), 0)

        # Check that all links are deleted
        remaining_links = Link.objects.filter(CAM=self.cam)
        self.assertEqual(remaining_links.count(), 0)

    def test_cam_with_project_association(self):
        """
        Test that CAM is properly associated with a project
        """
        self.assertEqual(self.cam.project, self.project)

        # Test that project can access its CAMs
        project_cams = CAM.objects.filter(project=self.project)
        self.assertIn(self.cam, project_cams)

    def test_cam_string_representation(self):
        """
        Test CAM model __str__ method
        """
        self.assertIn("testCAM", str(self.cam))


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
        from users.forms import CustomUserCreationForm

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
        from users.forms import CustomUserCreationForm

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
        from users.forms import CustomUserCreationForm

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
        from users.forms import CustomUserCreationForm

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
        from users.forms import ContactForm

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
        from users.forms import ResearcherSignupForm

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

    def test_participant_form_password_mismatch(self):
        """Test participant form with mismatched passwords"""
        from users.forms import ParticipantSignupForm

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
        from users.forms import ResearcherSignupForm

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
        from users.forms import ResearcherSignupForm

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
        from users.forms import ContactForm

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
        from users.forms import ContactForm

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
        from users.forms import ContactForm

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
        from users.forms import ContactForm

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


class CreateParticipantUserComprehensiveTestCase(TestCase):
    """Comprehensive tests for create_participant_user business logic"""

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

    def test_create_participant_without_project(self):
        """Test creating a participant user without project affiliation"""
        from users.utils import create_participant_user
        from users.forms import ParticipantSignupForm

        form = ParticipantSignupForm(
            data={
                "project_name": "",
                "project_password": "",
                "username": "participant1",
                "password1": "PartPass123!",
                "password2": "PartPass123!",
                "language_preference": "en",
            }
        )
        self.assertTrue(form.is_valid())
        user, success = create_participant_user(form, project=None, request=None)
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "participant1")
        self.assertTrue(user.is_participant)

    def test_create_participant_with_project(self):
        """Test creating a participant user with project affiliation"""
        from users.utils import create_participant_user
        from users.forms import ParticipantSignupForm

        form = ParticipantSignupForm(
            data={
                "project_name": self.project.name,
                "project_password": self.project.password,
                "username": "participant2",
                "password1": "PartPass123!",
                "password2": "PartPass123!",
                "language_preference": "en",
            }
        )
        self.assertTrue(form.is_valid())
        user, success = create_participant_user(
            form, project=self.project, request=None
        )
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "participant2")
        self.assertTrue(user.is_participant)
        self.assertEqual(user.active_project_num, self.project.id)

    def test_create_participant_handles_form_save_exception(self):
        """Test that create_participant_user handles form save exceptions"""
        from users.utils import create_participant_user

        # Create a mock form that raises exception on save
        class FailingForm:
            def save(self):
                raise Exception("Form save failed")

        user, success = create_participant_user(
            FailingForm(), project=None, request=None
        )
        self.assertFalse(success)
        self.assertIsNone(user)


class CreateResearcherUserComprehensiveTestCase(TestCase):
    """Comprehensive tests for create_researcher_user business logic"""

    def test_create_researcher_user_success(self):
        """Test successful researcher user creation"""
        from users.utils import create_researcher_user
        from users.forms import ResearcherSignupForm

        form = ResearcherSignupForm(
            data={
                "username": "researcher1",
                "email": "researcher1@test.com",
                "password1": "ResearchPass123!",
                "password2": "ResearchPass123!",
                "affiliation": "Test University",
                "language_preference": "en",
            }
        )
        self.assertTrue(form.is_valid())
        user, success = create_researcher_user(form, request=None)
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "researcher1")
        self.assertTrue(user.is_researcher)

    def test_create_researcher_user_handles_exception(self):
        """Test that create_researcher_user handles exceptions"""
        from users.utils import create_researcher_user

        # Create a mock form that raises exception
        class FailingForm:
            def save(self):
                raise Exception("Form save failed")

            cleaned_data = {"username": "fail", "password1": "pass"}

        user, success = create_researcher_user(FailingForm(), request=None)
        self.assertFalse(success)
        self.assertIsNone(user)


class RemoveTransparencyComprehensiveTestCase(TestCase):
    """Comprehensive tests for remove_transparency function"""

    def test_remove_transparency_rgba_image(self):
        """Test removing transparency from RGBA image"""
        from users.utils import remove_transparency
        from PIL import Image

        # Create RGBA image with transparency
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        result = remove_transparency(img)
        self.assertIsNotNone(result)
        self.assertIn(result.mode, ("RGBA", "RGB"))

    def test_remove_transparency_la_image(self):
        """Test removing transparency from LA (grayscale+alpha) image"""
        from users.utils import remove_transparency
        from PIL import Image

        # Create LA image
        img = Image.new("LA", (100, 100), (255, 128))
        result = remove_transparency(img)
        self.assertIsNotNone(result)

    def test_remove_transparency_rgb_unchanged(self):
        """Test that RGB image is returned unchanged"""
        from users.utils import remove_transparency
        from PIL import Image

        img = Image.new("RGB", (100, 100), (255, 0, 0))
        result = remove_transparency(img)
        self.assertEqual(result, img)

    def test_remove_transparency_custom_background(self):
        """Test removing transparency with custom background color"""
        from users.utils import remove_transparency
        from PIL import Image

        img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        result = remove_transparency(img, bg_color=(0, 255, 0))
        self.assertIsNotNone(result)


class ProcessCamImageComprehensiveTestCase(TestCase):
    """Comprehensive tests for process_cam_image function"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
        )
        self.cam = CAM.objects.create(user=self.user)
        self.user.active_cam_num = self.cam.id
        self.user.save()

    def test_process_cam_image_invalid_format(self):
        """Test process_cam_image with invalid format"""
        from users.utils import process_cam_image
        from django.conf import settings

        invalid_data = "invalid_data_format"
        file_name, success = process_cam_image(
            invalid_data, self.user, settings.MEDIA_URL
        )
        self.assertFalse(success)
        self.assertIsNone(file_name)

    def test_process_cam_image_missing_user_cam(self):
        """Test process_cam_image when user has no active CAM"""
        from users.utils import process_cam_image
        from django.conf import settings

        # Create user without active CAM
        user_no_cam = CustomUser.objects.create_user(
            username="nocam",
            email="nocam@test.com",
            password="pass123",
        )
        user_no_cam.active_cam_num = None
        user_no_cam.save()

        invalid_data = "invalid"
        file_name, success = process_cam_image(
            invalid_data, user_no_cam, settings.MEDIA_URL
        )
        self.assertFalse(success)
        self.assertIsNone(file_name)

    def test_process_cam_image_invalid_base64_content(self):
        """Test process_cam_image with invalid base64 content"""
        from users.utils import process_cam_image
        from django.conf import settings

        # Valid data URL format but invalid base64
        invalid_data = "data:image/png;base64,!!!"
        file_name, success = process_cam_image(
            invalid_data, self.user, settings.MEDIA_URL
        )
        self.assertFalse(success)
        self.assertIsNone(file_name)


class ValidateProjectPasswordComprehensiveTestCase(TestCase):
    """Comprehensive tests for validate_project_password function"""

    def setUp(self):
        self.researcher = CustomUser.objects.create_user(
            username="researcher",
            email="researcher@test.com",
            password="pass123",
        )
        Researcher.objects.create(user=self.researcher, affiliation="Test Uni")
        self.project_with_password = Project.objects.create(
            name="ProtectedProject",
            description="Test",
            researcher=self.researcher,
            password="SecurePassword123",
            name_participants="PP",
        )
        self.project_no_password = Project.objects.create(
            name="OpenProject",
            description="Test",
            researcher=self.researcher,
            password="",
            name_participants="OP",
        )

    def test_validate_project_with_correct_password(self):
        """Test validating a project with correct password"""
        from users.utils import validate_project_password

        project, error = validate_project_password(
            self.project_with_password.name, "SecurePassword123"
        )
        self.assertIsNotNone(project)
        self.assertIsNone(error)
        self.assertEqual(project.id, self.project_with_password.id)

    def test_validate_project_with_incorrect_password(self):
        """Test validating a project with incorrect password"""
        from users.utils import validate_project_password

        project, error = validate_project_password(
            self.project_with_password.name, "WrongPassword"
        )
        self.assertIsNone(project)
        self.assertIsNotNone(error)
        self.assertIn("Incorrect", error)

    def test_validate_project_no_password_required(self):
        """Test validating a project with no password requirement"""
        from users.utils import validate_project_password

        project, error = validate_project_password(self.project_no_password.name, "")
        self.assertIsNotNone(project)
        self.assertIsNone(error)
        self.assertEqual(project.id, self.project_no_password.id)

    def test_validate_project_no_password_any_input(self):
        """Test validating a no-password project with any input"""
        from users.utils import validate_project_password

        project, error = validate_project_password(
            self.project_no_password.name, "SomePassword"
        )
        self.assertIsNotNone(project)
        self.assertIsNone(error)

    def test_validate_project_nonexistent(self):
        """Test validating a nonexistent project"""
        from users.utils import validate_project_password

        project, error = validate_project_password("NonExistentProject", "password")
        self.assertIsNone(project)
        self.assertIsNotNone(error)
        self.assertIn("does not exist", error)

    def test_validate_project_empty_name_and_password(self):
        """Test validating with empty project name"""
        from users.utils import validate_project_password

        project, error = validate_project_password("", "")
        self.assertIsNone(project)
        self.assertIsNone(error)


class ProcessContactFormComprehensiveTestCase(TestCase):
    """Comprehensive tests for process_contact_form function"""

    def test_process_contact_form_success(self):
        """Test successful contact form processing"""
        from users.utils import process_contact_form
        from users.forms import ContactForm
        from django.core.mail import outbox

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
        self.assertEqual(len(outbox), 1)

    def test_process_contact_form_with_html_content(self):
        """Test contact form with HTML-like content"""
        from users.utils import process_contact_form
        from users.forms import ContactForm
        from django.core.mail import outbox

        form = ContactForm(
            data={
                "contacter": "Test User",
                "email": "test@example.com",
                "message": "<script>alert('xss')</script>",
            }
        )
        self.assertTrue(form.is_valid())
        success, error = process_contact_form(form)
        self.assertTrue(success)
        self.assertEqual(len(outbox), 1)


class SendCamEmailComprehensiveTestCase(TestCase):
    """Comprehensive tests for send_cam_email function"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
        )
        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")

    def test_send_cam_email_success(self):
        """Test successful CAM email sending"""
        from users.utils import send_cam_email
        from django.core.mail import outbox

        success, error = send_cam_email(
            self.user.id, self.user.username, "recipient@example.com"
        )
        self.assertTrue(success)
        self.assertEqual(error, "")
        self.assertEqual(len(outbox), 1)

    def test_send_cam_email_to_default_address(self):
        """Test CAM email sent to default address when not specified"""
        from users.utils import send_cam_email
        from django.core.mail import outbox

        success, error = send_cam_email(self.user.id, self.user.username)
        self.assertTrue(success)
        self.assertEqual(len(outbox), 1)

    def test_send_cam_email_contains_csv_attachments(self):
        """Test that CAM email contains CSV attachments"""
        from users.utils import send_cam_email
        from django.core.mail import outbox

        success, error = send_cam_email(
            self.user.id, self.user.username, "test@example.com"
        )
        self.assertTrue(success)
        self.assertEqual(len(outbox), 1)
        email = outbox[0]
        # Check attachments exist
        self.assertGreater(len(email.attachments), 0)

    def test_send_cam_email_invalid_user_id(self):
        """Test send_cam_email with invalid user ID"""
        from users.utils import send_cam_email

        success, error = send_cam_email(99999, "nonexistent", "test@example.com")
        # Should still succeed but with no blocks/links
        self.assertTrue(success)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class LoginpageViewTestCase(TestCase):
    """Test loginpage view functionality"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
        )
        self.inactive_user = CustomUser.objects.create_user(
            username="inactive",
            email="inactive@test.com",
            password="inactivepass",
        )
        self.inactive_user.is_active = False
        self.inactive_user.save()

    def test_loginpage_valid_credentials(self):
        """Test login with valid credentials"""
        response = self.client.post(
            "/users/loginpage",
            {"username": "testuser", "password": "testpass123"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_loginpage_nonexistent_user(self):
        """Test login with nonexistent username"""
        response = self.client.post(
            "/users/loginpage",
            {"username": "nonexistent", "password": "somepass"},
        )
        self.assertEqual(response.status_code, 200)

    def test_loginpage_wrong_password(self):
        """Test login with wrong password"""
        response = self.client.post(
            "/users/loginpage",
            {"username": "testuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 200)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class SignupViewTestCase(TestCase):
    """Test signup view functionality"""

    def test_signup_duplicate_username(self):
        """Test signup with duplicate username"""
        CustomUser.objects.create_user(
            username="existing", email="existing@test.com", password="pass123"
        )

        response = self.client.post(
            "/users/signup",
            {
                "username": "existing",
                "email": "newemail@test.com",
                "first_name": "New",
                "last_name": "User",
                "password1": "SecurePass123!",
                "password2": "SecurePass123!",
                "language_preference": "en",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_signup_password_mismatch(self):
        """Test signup with mismatched passwords"""
        response = self.client.post(
            "/users/signup",
            {
                "username": "newuser2",
                "email": "newuser2@test.com",
                "first_name": "New",
                "last_name": "User",
                "password1": "SecurePass123!",
                "password2": "DifferentPass123!",
                "language_preference": "en",
            },
        )
        self.assertEqual(response.status_code, 200)


class ClearCAMViewTestCase(TestCase):
    """Test clear_CAM view functionality"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
        )
        Researcher.objects.create(user=self.user, affiliation="UdeM")
        self.client.login(username="testuser", password="testpass123")

        self.project = Project.objects.create(
            name="TestProject",
            description="TEST PROJECT",
            researcher=self.user,
            password="TestProjectPassword",
            name_participants="TP",
        )

        self.cam = CAM.objects.create(
            name="testCAM", user=self.user, project=self.project
        )
        self.user.active_cam_num = self.cam.id
        self.user.save()

        # Create test blocks and links
        self.block1 = Block.objects.create(
            title="Block1",
            x_pos=10.0,
            y_pos=10.0,
            height=100,
            width=100,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
            num=1,
        )
        self.link = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block1,
            creator=self.user,
            CAM=self.cam,
        )

    def test_clear_cam_valid_request(self):
        """Test clearing CAM with valid request"""
        response = self.client.post("/users/clear_CAM", {"clear_cam_valid": True})
        self.assertEqual(response.status_code, 200)

        # Check that blocks and links are deleted
        self.assertEqual(Block.objects.filter(CAM=self.cam).count(), 0)
        self.assertEqual(Link.objects.filter(CAM=self.cam).count(), 0)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class CreateRandomUserViewTestCase(TestCase):
    """Test create_random view functionality"""

    def test_create_random_user_response(self):
        """Test creating a random anonymous user returns successful response"""
        response = self.client.post(
            "/users/create_random", {"language_preference": "en"}
        )
        # Should return successful response
        self.assertIn(response.status_code, [200, 302])


class LanguageChangeViewTestCase(TestCase):
    """Test language_change view functionality"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            language_preference="en",
        )
        self.client.login(username="testuser", password="testpass123")

    def test_language_change_english_to_german(self):
        """Test changing language from English to German"""
        response = self.client.post("/users/language_change", {"language": "de"})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.language_preference, "de")

    def test_language_change_german_to_english(self):
        """Test changing language from German to English"""
        self.user.language_preference = "de"
        self.user.save()

        response = self.client.post("/users/language_change", {"language": "en"})
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.language_preference, "en")


class ExportCAMViewTestCase(TestCase):
    """Test export_CAM view functionality"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
        )
        Researcher.objects.create(user=self.user, affiliation="UdeM")
        self.client.login(username="testuser", password="testpass123")

        self.cam = CAM.objects.create(name="testCAM", user=self.user)
        self.user.active_cam_num = self.cam.id
        self.user.save()

        # Create test block
        self.block = Block.objects.create(
            title="ExportBlock",
            x_pos=10.0,
            y_pos=10.0,
            height=100,
            width=100,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
            num=1,
        )

    def test_export_cam_returns_zip(self):
        """Test export_CAM returns a ZIP file"""
        response = self.client.get("/users/export_CAM")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/octet-stream")
        self.assertIn("attachment", response["Content-Disposition"])

    def test_export_cam_contains_csv_files(self):
        """Test exported ZIP contains CSV files"""
        response = self.client.get("/users/export_CAM")
        from zipfile import ZipFile
        from io import BytesIO

        zip_file = ZipFile(BytesIO(response.content))
        file_list = zip_file.namelist()
        self.assertIn("blocks.csv", file_list)
        self.assertIn("links.csv", file_list)
