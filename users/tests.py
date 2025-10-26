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
        self.assertEqual(response.status_code, 302)  # Should redirect after login

        # Test logout
        response = self.client.get("/users/logout")
        self.assertEqual(response.status_code, 302)  # Should redirect after logout

    def test_login_invalid_credentials(self):
        """
        Test login with invalid credentials
        """
        self.client.logout()
        response = self.client.post(
            "/users/loginpage", {"username": "testuser", "password": "wrongpassword"}
        )
        # Should stay on login page or show error
        self.assertContains(response, "loginpage", status_code=200)

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
        )

        response = self.client.post(
            "/users/project_settings",
            {
                "project_id": project.id,
                "description": "Updated description",
                "password": "newpassword",
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
            name="UpdateTest", description="Original", researcher=self.user
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


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class CAMOperationsTestCase(TestCase):
    def setUp(self):
        # Set up a user
        self.user = CustomUser.objects.create_user(username='testuser', email='test@test.test', password='12345')
        self.researcher = Researcher.objects.create(user=self.user, affiliation='UdeM')
        login = self.client.login(username='testuser', password='12345')
        
        # Create project
        self.project = Project.objects.create(
            name='TestProject',
            description='TEST PROJECT',
            researcher=self.user,
            password='TestProjectPassword'
        )
        
        # Create CAM
        self.cam = CAM.objects.create(name='testCAM', user=self.user, project=self.project)
        self.user.active_cam_num = self.cam.id
        self.user.save()
        
        # Create some blocks and links for testing
        self.block1 = Block.objects.create(
            title='Block1', x_pos=10.0, y_pos=10.0, height=100, width=100,
            creator=self.user, shape='neutral', CAM=self.cam, num=1
        )
        self.block2 = Block.objects.create(
            title='Block2', x_pos=150.0, y_pos=150.0, height=100, width=100,
            creator=self.user, shape='positive', CAM=self.cam, num=2
        )
        self.link = Link.objects.create(
            starting_block=self.block1, ending_block=self.block2,
            creator=self.user, CAM=self.cam, arrow_type='uni'
        )

    def test_create_individual_cam(self):
        """
        Test creating a new individual CAM
        """
        response = self.client.post('/users/create_individual_cam', {
            'cam_name': 'NewCAM',
            'cam_description': 'Test description'
        })
        
        # Check that new CAM was created
        new_cam = CAM.objects.filter(name='NewCAM').first()
        self.assertIsNotNone(new_cam)
        self.assertEqual(new_cam.user, self.user)

    def test_load_cam(self):
        """
        Test loading CAM data
        """
        response = self.client.post('/users/load_cam', {
            'cam_id': self.cam.id
        })
        
        self.assertEqual(response.status_code, 200)

    def test_delete_cam(self):
        """
        Test deleting a CAM
        """
        cam_to_delete = CAM.objects.create(
            name='DeleteMe',
            user=self.user,
            project=self.project
        )
        
        response = self.client.post('/users/delete_cam', {
            'cam_id': cam_to_delete.id
        })
        
        # Check that CAM is deleted
        with self.assertRaises(CAM.DoesNotExist):
            CAM.objects.get(id=cam_to_delete.id)

    def test_update_cam_name(self):
        """
        Test updating CAM name
        """
        response = self.client.post('/users/update_cam_name', {
            'cam_id': self.cam.id,
            'new_name': 'UpdatedCAMName'
        })
        
        self.cam.refresh_from_db()
        self.assertEqual(self.cam.name, 'UpdatedCAMName')

    def test_download_cam(self):
        """
        Test downloading CAM as JSON
        """
        response = self.client.get('/users/download_cam', {
            'cam_id': self.cam.id
        })
        
        self.assertEqual(response.status_code, 200)

    def test_clone_cam(self):
        """
        Test cloning a CAM with all its blocks and links
        """
        original_cam_id = self.cam.id
        
        response = self.client.post('/users/clone_cam', {
            'cam_id': self.cam.id,
            'new_name': 'ClonedCAM'
        })
        
        # Check that new CAM was created
        cloned_cam = CAM.objects.filter(name='ClonedCAM').first()
        self.assertIsNotNone(cloned_cam)
        self.assertNotEqual(cloned_cam.id, original_cam_id)

    def test_clear_cam(self):
        """
        Test clearing all blocks and links from a CAM
        """
        response = self.client.post('/users/clear_CAM', {
            'cam_id': self.cam.id
        })
        
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
        self.assertIn('testCAM', str(self.cam))
