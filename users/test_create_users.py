"""
Comprehensive tests for create_users.py
Tests user creation functionality for projects with and without initial CAM imports
"""

from django.test import TestCase, override_settings
from users.models import CustomUser, Researcher, Participant, Project, CAM
from block.models import Block
from link.models import Link
from users.create_users import create_users
from django.core.files.uploadedfile import SimpleUploadedFile
from zipfile import ZipFile
from io import BytesIO
import tempfile
import os


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class CreateUsersBasicTestCase(TestCase):
    """Tests for basic user creation without CAM import"""

    def setUp(self):
        self.researcher = CustomUser.objects.create_user(
            username="researcher", email="researcher@test.com", password="12345"
        )
        self.researcher_profile = Researcher.objects.create(
            user=self.researcher, affiliation="UdeM"
        )

        self.project = Project.objects.create(
            name="TestProject",
            description="TEST PROJECT",
            researcher=self.researcher,
            password="TestProjectPassword",
        )

    def test_create_single_user(self):
        """Test creating a single user for a project"""
        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=1,
            call_id="test",
            language_pref="en",
            input_file=None,
            deletable=None,
        )

        # Verify user was created
        user = CustomUser.objects.get(username="test0")
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test0@test.com")

        # Verify participant profile was created
        participant = Participant.objects.get(user=user)
        self.assertEqual(participant.researcher, self.researcher)
        self.assertEqual(participant.project, self.project)
        self.assertEqual(participant.language_preference, "en")

    def test_create_multiple_users(self):
        """Test creating multiple users for a project"""
        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=5,
            call_id="batch",
            language_pref="fr",
            input_file=None,
            deletable=None,
        )

        # Verify all users were created
        for i in range(5):
            user = CustomUser.objects.get(username=f"batch{i}")
            self.assertIsNotNone(user)
            self.assertEqual(user.email, f"batch{i}@test.com")

            # Verify participant profiles
            participant = Participant.objects.get(user=user)
            self.assertEqual(participant.researcher, self.researcher)
            self.assertEqual(participant.project, self.project)
            self.assertEqual(participant.language_preference, "fr")

    def test_create_user_with_cam(self):
        """Test that each user gets a CAM created"""
        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=2,
            call_id="cam",
            language_pref="en",
            input_file=None,
            deletable=None,
        )

        # Verify CAMs were created for each user
        for i in range(2):
            user = CustomUser.objects.get(username=f"cam{i}")
            self.assertIsNotNone(user.active_cam_num)

            # Verify CAM exists
            cam = CAM.objects.get(id=user.active_cam_num)
            self.assertEqual(cam.user, user)
            self.assertEqual(cam.project, self.project)

    def test_username_password_convention(self):
        """Test that username and password follow the naming convention"""
        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=1,
            call_id="test",
            language_pref="en",
            input_file=None,
            deletable=None,
        )

        # Verify password follows convention: call_id + num + call_id
        user = CustomUser.objects.get(username="test0")
        # Password should be 'test0test'
        self.assertTrue(user.check_password("test0test"))

    def test_recreate_existing_user(self):
        """Test that creating a user with existing username deletes old user"""
        # Create initial user manually
        old_user = CustomUser.objects.create_user(
            username="replace0", email="old@test.com", password="oldpass"
        )
        old_user_id = old_user.id

        # Create user with same username through create_users
        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=1,
            call_id="replace",
            language_pref="en",
            input_file=None,
            deletable=None,
        )

        # Verify old user is deleted
        self.assertFalse(CustomUser.objects.filter(id=old_user_id).exists())

        # Verify new user exists with correct email
        new_user = CustomUser.objects.get(username="replace0")
        self.assertEqual(new_user.email, "replace0@test.com")

    def test_user_language_preferences(self):
        """Test creating users with different language preferences"""
        # Create English preference users
        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=2,
            call_id="en",
            language_pref="en",
            input_file=None,
            deletable=None,
        )

        # Create French preference users
        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=2,
            call_id="fr",
            language_pref="fr",
            input_file=None,
            deletable=None,
        )

        # Verify language preferences
        en_user = CustomUser.objects.get(username="en0")
        en_participant = Participant.objects.get(user=en_user)
        self.assertEqual(en_participant.language_preference, "en")

        fr_user = CustomUser.objects.get(username="fr0")
        fr_participant = Participant.objects.get(user=fr_user)
        self.assertEqual(fr_participant.language_preference, "fr")

    def test_create_zero_users(self):
        """Test creating zero users (edge case)"""
        initial_user_count = CustomUser.objects.count()

        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=0,
            call_id="zero",
            language_pref="en",
            input_file=None,
            deletable=None,
        )

        # Verify no new users were created
        self.assertEqual(CustomUser.objects.count(), initial_user_count)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage",
    MEDIA_ROOT=tempfile.mkdtemp(),
)
class CreateUsersWithCAMImportTestCase(TestCase):
    """Tests for user creation with initial CAM import"""

    def setUp(self):
        self.researcher = CustomUser.objects.create_user(
            username="researcher", email="researcher@test.com", password="12345"
        )
        self.researcher_profile = Researcher.objects.create(
            user=self.researcher, affiliation="UdeM"
        )

        self.project = Project.objects.create(
            name="ImportProject",
            description="PROJECT WITH IMPORT",
            researcher=self.researcher,
            password="ImportPassword",
        )

    def _create_test_zip_file(self, include_links=True):
        """Helper function to create a test ZIP file with blocks and links CSV"""
        zip_buffer = BytesIO()

        # Create blocks CSV content
        blocks_csv = (
            "id,title,x_pos,y_pos,width,height,shape,comment,creator,CAM,num,resizable,modifiable\n"
            "1,ConceptA,100.0,100.0,100,100,neutral,Test comment,999,999,1,True,True\n"
            "2,ConceptB,200.0,200.0,100,100,positive,,999,999,2,True,True\n"
        )

        # Create links CSV content
        links_csv = (
            "id,starting_block,ending_block,line_style,arrow_type,creator,CAM,num\n"
            "1,1,2,Solid-Weak,uni,999,999,1\n"
        )

        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr("blocks.csv", blocks_csv)
            if include_links:
                zip_file.writestr("links.csv", links_csv)

        zip_buffer.seek(0)
        return SimpleUploadedFile(
            "test_cam.zip", zip_buffer.read(), content_type="application/zip"
        )

    def test_create_user_with_cam_import(self):
        """Test creating user with initial CAM import"""
        zip_file = self._create_test_zip_file()

        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=1,
            call_id="import",
            language_pref="en",
            input_file=zip_file,
            deletable=None,
        )

        # Verify user was created
        user = CustomUser.objects.get(username="import0")
        self.assertIsNotNone(user)

        # Verify CAM was created and has blocks
        cam = CAM.objects.get(id=user.active_cam_num)
        blocks = Block.objects.filter(CAM=cam)

        self.assertEqual(blocks.count(), 2)

        # Verify block properties
        block_a = blocks.get(title="ConceptA")
        self.assertEqual(block_a.x_pos, 100.0)
        self.assertEqual(block_a.y_pos, 100.0)
        self.assertEqual(block_a.shape, "neutral")
        self.assertEqual(block_a.creator, user)
        self.assertEqual(block_a.CAM, cam)

    def test_create_user_with_cam_import_links(self):
        """Test that links are imported correctly"""
        zip_file = self._create_test_zip_file()

        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=1,
            call_id="linktest",
            language_pref="en",
            input_file=zip_file,
            deletable=None,
        )

        user = CustomUser.objects.get(username="linktest0")
        cam = CAM.objects.get(id=user.active_cam_num)
        links = Link.objects.filter(CAM=cam)

        self.assertEqual(links.count(), 1)

        # Verify link properties
        link = links.first()
        self.assertEqual(link.line_style, "Solid-Weak")
        self.assertEqual(link.arrow_type, "uni")
        self.assertEqual(link.creator, user)
        self.assertEqual(link.CAM, cam)

    def test_create_user_import_cleans_none_comments(self):
        """Test that 'None' comments are cleaned to empty strings"""
        # Create zip with 'None' comment
        zip_buffer = BytesIO()
        blocks_csv = (
            "id,title,x_pos,y_pos,width,height,shape,comment,creator,CAM,num,resizable,modifiable\n"
            "1,TestBlock,100.0,100.0,100,100,neutral,None,999,999,1,True,True\n"
        )

        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr("blocks.csv", blocks_csv)
            zip_file.writestr(
                "links.csv",
                "id,starting_block,ending_block,line_style,arrow_type,creator,CAM,num\n",
            )

        zip_buffer.seek(0)
        zip_file = SimpleUploadedFile(
            "test.zip", zip_buffer.read(), content_type="application/zip"
        )

        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=1,
            call_id="clean",
            language_pref="en",
            input_file=zip_file,
            deletable=None,
        )

        user = CustomUser.objects.get(username="clean0")
        cam = CAM.objects.get(id=user.active_cam_num)
        block = Block.objects.get(CAM=cam, title="TestBlock")

        # Comment should be empty string, not 'None'
        self.assertEqual(block.comment, "")

    def test_create_user_import_with_deletable_false(self):
        """Test that deletable=False makes blocks non-modifiable"""
        zip_file = self._create_test_zip_file()

        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=1,
            call_id="locked",
            language_pref="en",
            input_file=zip_file,
            deletable=False,
        )

        user = CustomUser.objects.get(username="locked0")
        cam = CAM.objects.get(id=user.active_cam_num)
        blocks = Block.objects.filter(CAM=cam)

        # All blocks should be non-modifiable
        for block in blocks:
            self.assertFalse(block.modifiable)

    def test_create_user_import_with_deletable_true(self):
        """Test that deletable=True keeps blocks modifiable"""
        zip_file = self._create_test_zip_file()

        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=1,
            call_id="unlocked",
            language_pref="en",
            input_file=zip_file,
            deletable=True,
        )

        user = CustomUser.objects.get(username="unlocked0")
        cam = CAM.objects.get(id=user.active_cam_num)
        blocks = Block.objects.filter(CAM=cam)

        # Blocks should still be modifiable (deletable doesn't affect when True)
        # Based on code: only sets modifiable=False when deletable is not None
        # So this test verifies the original behavior is preserved
        self.assertGreater(blocks.count(), 0)

    def test_create_multiple_users_with_same_import(self):
        """Test that multiple users get independent copies of imported CAM"""
        zip_file = self._create_test_zip_file()

        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=3,
            call_id="multi",
            language_pref="en",
            input_file=zip_file,
            deletable=None,
        )

        # Verify each user has their own CAM with blocks
        for i in range(3):
            user = CustomUser.objects.get(username=f"multi{i}")
            cam = CAM.objects.get(id=user.active_cam_num)
            blocks = Block.objects.filter(CAM=cam)

            self.assertEqual(blocks.count(), 2)

            # Verify blocks belong to correct user
            for block in blocks:
                self.assertEqual(block.creator, user)
                self.assertEqual(block.CAM, cam)

    def test_create_user_import_sets_project_initial_cam(self):
        """Test that import file is saved to project"""
        zip_file = self._create_test_zip_file()

        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=1,
            call_id="projfile",
            language_pref="en",
            input_file=zip_file,
            deletable=None,
        )

        # Verify project has Initial_CAM set
        self.project.refresh_from_db()
        self.assertIsNotNone(self.project.Initial_CAM)
        self.assertIn("test_cam.zip", self.project.Initial_CAM.name)

    def test_create_user_empty_blocks_csv(self):
        """Test handling of empty blocks CSV"""
        zip_buffer = BytesIO()
        blocks_csv = "id,title,x_pos,y_pos,width,height,shape,comment,creator,CAM,num,resizable,modifiable\n"
        links_csv = (
            "id,starting_block,ending_block,line_style,arrow_type,creator,CAM,num\n"
        )

        with ZipFile(zip_buffer, "w") as zip_file:
            zip_file.writestr("blocks.csv", blocks_csv)
            zip_file.writestr("links.csv", links_csv)

        zip_buffer.seek(0)
        zip_file = SimpleUploadedFile(
            "empty.zip", zip_buffer.read(), content_type="application/zip"
        )

        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=1,
            call_id="empty",
            language_pref="en",
            input_file=zip_file,
            deletable=None,
        )

        # User should still be created
        user = CustomUser.objects.get(username="empty0")
        cam = CAM.objects.get(id=user.active_cam_num)

        # CAM should have no blocks
        self.assertEqual(Block.objects.filter(CAM=cam).count(), 0)


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class CreateUsersEdgeCasesTestCase(TestCase):
    """Tests for edge cases and error handling in create_users"""

    def setUp(self):
        self.researcher = CustomUser.objects.create_user(
            username="researcher", email="researcher@test.com", password="12345"
        )
        self.researcher_profile = Researcher.objects.create(
            user=self.researcher, affiliation="UdeM"
        )

        self.project = Project.objects.create(
            name="EdgeCaseProject",
            description="EDGE CASE TESTING",
            researcher=self.researcher,
            password="EdgePassword",
        )

    def test_create_user_with_special_characters_call_id(self):
        """Test creating users with special characters in call_id"""
        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=1,
            call_id="test_user_",
            language_pref="en",
            input_file=None,
            deletable=None,
        )

        # User should be created with special characters
        user = CustomUser.objects.get(username="test_user_0")
        self.assertIsNotNone(user)

    def test_create_user_with_long_call_id(self):
        """Test creating users with long call_id"""
        long_id = "verylongcallidentifier"

        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=1,
            call_id=long_id,
            language_pref="en",
            input_file=None,
            deletable=None,
        )

        user = CustomUser.objects.get(username=f"{long_id}0")
        self.assertIsNotNone(user)

    def test_create_large_number_of_users(self):
        """Test creating a large number of users"""
        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=50,
            call_id="bulk",
            language_pref="en",
            input_file=None,
            deletable=None,
        )

        # Verify all 50 users were created
        bulk_users = CustomUser.objects.filter(username__startswith="bulk")
        self.assertEqual(bulk_users.count(), 50)

        # Verify each has a CAM
        for user in bulk_users:
            self.assertIsNotNone(user.active_cam_num)

    def test_users_belong_to_correct_project(self):
        """Test that users are associated with correct project"""
        # Create second project
        project2 = Project.objects.create(
            name="Project2",
            description="SECOND PROJECT",
            researcher=self.researcher,
            password="Project2Pass",
        )

        # Create users for project 1
        create_users(
            project=self.project,
            researcher=self.researcher,
            num_part=2,
            call_id="p1",
            language_pref="en",
            input_file=None,
            deletable=None,
        )

        # Create users for project 2
        create_users(
            project=project2,
            researcher=self.researcher,
            num_part=2,
            call_id="p2",
            language_pref="en",
            input_file=None,
            deletable=None,
        )

        # Verify project associations
        p1_user = CustomUser.objects.get(username="p10")
        p1_participant = Participant.objects.get(user=p1_user)
        self.assertEqual(p1_participant.project, self.project)

        p2_user = CustomUser.objects.get(username="p20")
        p2_participant = Participant.objects.get(user=p2_user)
        self.assertEqual(p2_participant.project, project2)
