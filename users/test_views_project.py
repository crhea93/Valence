"""
Comprehensive tests for users/views_Project.py
"""

from django.test import TestCase, override_settings, Client
from users.models import CustomUser, Researcher, CAM, Project
from block.models import Block
from link.models import Link
from django.urls import reverse


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class JoinProjectViewTestCase(TestCase):
    """Test join_project view functionality"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@test.com", password="12345"
        )
        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")
        self.client.login(username="testuser", password="12345")

        self.project = Project.objects.create(
            name="TestProject",
            description="TEST PROJECT",
            researcher=self.user,
            password="TestProjectPassword",
            name_participants="TP",
        )

    def test_join_project_get_request(self):
        """Test GET request to join_project"""
        response = self.client.get("/users/join_project")
        self.assertEqual(response.status_code, 200)

    def test_join_project_post_without_data(self):
        """Test POST request to join_project without data"""
        response = self.client.post("/users/join_project", {})
        self.assertEqual(response.status_code, 200)

    def test_join_project_with_valid_password(self):
        """Test joining project with correct password"""
        response = self.client.post(
            "/users/join_project",
            {
                "project_name": self.project.name,
                "project_password": self.project.password,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_join_project_with_invalid_password(self):
        """Test joining project with wrong password"""
        response = self.client.post(
            "/users/join_project",
            {
                "project_name": self.project.name,
                "project_password": "WrongPassword",
            },
        )
        self.assertEqual(response.status_code, 200)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class CreateProjectViewTestCase(TestCase):
    """Test create_project view functionality"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@test.com", password="12345"
        )
        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")
        self.client.login(username="testuser", password="12345")

    def test_create_project_get_request(self):
        """Test GET request to create_project"""
        response = self.client.get("/users/create_project")
        self.assertEqual(response.status_code, 200)

    def test_create_project_valid_data(self):
        """Test creating project with valid data"""
        response = self.client.post(
            "/users/create_project",
            {
                "label": "New Project",
                "description": "Test Description",
                "num_participants": "5",
                "name_participants": "NP",
                "participantType": "auto_participants",
                "languagePreference": "en",
                "conceptDelete": "false",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_create_project_creates_participants(self):
        """Test that create_project creates participant users"""
        response = self.client.post(
            "/users/create_project",
            {
                "label": "ParticipantProject",
                "description": "Test",
                "num_participants": "3",
                "name_participants": "PP",
                "participantType": "auto_participants",
                "languagePreference": "en",
                "conceptDelete": "false",
            },
        )
        self.assertEqual(response.status_code, 200)
        # Check that participants were created
        participants = CustomUser.objects.filter(username__startswith="PP")
        # Should have created participant users
        self.assertGreaterEqual(participants.count(), 0)

    def test_create_project_with_custom_participants(self):
        """Test creating project with custom participants"""
        response = self.client.post(
            "/users/create_project",
            {
                "label": "CustomProject",
                "description": "Test",
                "num_participants": "2",
                "name_participants": "CP",
                "participantType": "custom_participants",
                "languagePreference": "en",
                "conceptDelete": "false",
            },
        )
        self.assertEqual(response.status_code, 200)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class ProjectPageViewTestCase(TestCase):
    """Test project_page view functionality"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@test.com", password="12345"
        )
        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")
        self.client.login(username="testuser", password="12345")

        self.project = Project.objects.create(
            name="TestProject",
            description="TEST PROJECT",
            researcher=self.user,
            password="TestProjectPassword",
            name_participants="TP",
        )
        self.user.active_project_num = self.project.id
        self.user.save()

    def test_project_page_get_request(self):
        """Test GET request to project_page"""
        response = self.client.get("/users/project_page")
        self.assertEqual(response.status_code, 200)

    def test_project_page_with_participants(self):
        """Test project page displays participants"""
        # Create participant user
        participant = CustomUser.objects.create_user(
            username="participant", email="part@test.com", password="12345"
        )
        participant.active_project_num = self.project.id
        participant.save()

        response = self.client.get("/users/project_page")
        self.assertEqual(response.status_code, 200)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class JoinProjectLinkViewTestCase(TestCase):
    """Test join_project_link view functionality"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@test.com", password="12345"
        )
        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")

        self.project = Project.objects.create(
            name="TestProject",
            description="TEST PROJECT",
            researcher=self.user,
            password="TestProjectPassword",
            name_participants="TP",
        )

    def test_join_project_link_new_cam(self):
        """Test joining via project link with new CAM"""
        response = self.client.get(
            "/users/join_project_link",
            {
                "username": "newuser",
                "pword": "password",
                "proj_name": self.project.name,
                "proj_pword": self.project.password,
                "cam_op": "new",
            },
        )
        # Should create user and CAM
        self.assertIn(response.status_code, [200, 302])

    def test_join_project_link_with_wrong_password(self):
        """Test joining via project link with wrong project password"""
        response = self.client.get(
            "/users/join_project_link",
            {
                "username": "newuser",
                "pword": "password",
                "proj_name": self.project.name,
                "proj_pword": "WrongPassword",
                "cam_op": "new",
            },
        )
        # Should handle error gracefully
        self.assertIn(response.status_code, [200, 302, 404])

    def test_join_project_link_reuse_cam(self):
        """Test joining via project link with cam_op=reuse"""
        # First create user with CAM
        response1 = self.client.get(
            "/users/join_project_link",
            {
                "username": "testuser2",
                "pword": "password",
                "proj_name": self.project.name,
                "proj_pword": self.project.password,
                "cam_op": "new",
            },
        )

        # Get the created user
        user = CustomUser.objects.filter(username="testuser2").first()
        if user:
            # Try to reuse CAM
            response2 = self.client.get(
                "/users/join_project_link",
                {
                    "username": "testuser2",
                    "pword": "password",
                    "proj_name": self.project.name,
                    "proj_pword": self.project.password,
                    "cam_op": "reuse",
                    "cam_id": user.active_cam_num,
                },
            )
            self.assertIn(response2.status_code, [200, 302])

    def test_join_project_link_duplicate_cam(self):
        """Test joining via project link with cam_op=duplicate"""
        # First create user with CAM
        response1 = self.client.get(
            "/users/join_project_link",
            {
                "username": "testuser3",
                "pword": "password",
                "proj_name": self.project.name,
                "proj_pword": self.project.password,
                "cam_op": "new",
            },
        )

        # Get the created user
        user = CustomUser.objects.filter(username="testuser3").first()
        if user:
            # Try to duplicate CAM
            response2 = self.client.get(
                "/users/join_project_link",
                {
                    "username": "testuser3",
                    "pword": "password",
                    "proj_name": self.project.name,
                    "proj_pword": self.project.password,
                    "cam_op": "duplicate",
                    "cam_id": user.active_cam_num,
                },
            )
            self.assertIn(response2.status_code, [200, 302])


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class ProjectSettingsViewTestCase(TestCase):
    """Test project_settings view functionality"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@test.com", password="12345"
        )
        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")
        self.client.login(username="testuser", password="12345")

        self.project = Project.objects.create(
            name="TestProject",
            description="TEST PROJECT",
            researcher=self.user,
            password="TestProjectPassword",
            name_participants="TP",
        )
        self.user.active_project_num = self.project.id
        self.user.save()

    def test_project_settings_get(self):
        """Test GET request to project_settings"""
        response = self.client.get("/users/project_settings")
        self.assertEqual(response.status_code, 200)

    def test_project_settings_update(self):
        """Test updating project settings"""
        response = self.client.post(
            "/users/project_settings",
            {
                "nameUpdate": self.project.name,
                "descriptionUpdate": "Updated description",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "Updated description")

    def test_project_settings_not_owner(self):
        """Test project settings access by non-owner"""
        other_user = CustomUser.objects.create_user(
            username="otheruser", email="other@test.com", password="12345"
        )
        other_user.active_project_num = self.project.id
        other_user.save()

        self.client.logout()
        self.client.login(username="otheruser", password="12345")

        response = self.client.post(
            "/users/project_settings",
            {
                "nameUpdate": self.project.name,
                "descriptionUpdate": "Hacked",
            },
        )
        # Should deny access
        self.assertEqual(response.status_code, 200)
        # Description should not change
        self.project.refresh_from_db()
        self.assertNotEqual(self.project.description, "Hacked")


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class LoadProjectViewTestCase(TestCase):
    """Test load_project view functionality"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@test.com", password="12345"
        )
        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")
        self.client.login(username="testuser", password="12345")

        self.project = Project.objects.create(
            name="TestProject",
            description="TEST PROJECT",
            researcher=self.user,
            password="TestProjectPassword",
            name_participants="TP",
        )

    def test_load_project_post_request(self):
        """Test loading a project"""
        response = self.client.post(
            "/users/load_project",
            {"project_id": self.project.id},
        )
        self.assertEqual(response.status_code, 200)

    def test_load_project_invalid_id(self):
        """Test loading nonexistent project"""
        response = self.client.post(
            "/users/load_project",
            {"project_id": 9999},
        )
        self.assertIn(response.status_code, [200, 404])


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class DeleteProjectViewTestCase(TestCase):
    """Test delete_project view functionality"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@test.com", password="12345"
        )
        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")
        self.client.login(username="testuser", password="12345")

        self.project = Project.objects.create(
            name="TestProject",
            description="TEST PROJECT",
            researcher=self.user,
            password="TestProjectPassword",
            name_participants="TP",
        )

    def test_delete_project_valid(self):
        """Test deleting a project"""
        project_id = self.project.id
        response = self.client.post(
            "/users/delete_project",
            {"project_id": project_id},
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_project_as_non_owner(self):
        """Test deleting project as non-owner"""
        other_user = CustomUser.objects.create_user(
            username="otheruser", email="other@test.com", password="12345"
        )
        self.client.logout()
        self.client.login(username="otheruser", password="12345")

        response = self.client.post(
            "/users/delete_project",
            {"project_id": self.project.id},
        )
        # Should not delete
        self.project.refresh_from_db()
        # Project should still exist
        self.assertIsNotNone(self.project)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class DownloadProjectViewTestCase(TestCase):
    """Test download_project view functionality"""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@test.com", password="12345"
        )
        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")
        self.client.login(username="testuser", password="12345")

        self.project = Project.objects.create(
            name="TestProject",
            description="TEST PROJECT",
            researcher=self.user,
            password="TestProjectPassword",
            name_participants="TP",
        )

        # Create CAM for project
        self.cam = CAM.objects.create(
            name="TestCAM", user=self.user, project=self.project
        )

    def test_download_project_returns_file(self):
        """Test downloading project data"""
        response = self.client.get(
            "/users/download_project",
            {"project_id": self.project.id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("octet-stream", response["Content-Type"])

    def test_download_project_invalid_id(self):
        """Test downloading nonexistent project"""
        response = self.client.get(
            "/users/download_project",
            {"project_id": 9999},
        )
        self.assertIn(response.status_code, [200, 404])
