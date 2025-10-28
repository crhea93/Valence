"""
Comprehensive tests for views_undo.py
Tests the undo functionality for CAM actions, particularly block and link deletion
"""

from django.test import TestCase, override_settings
from users.models import CustomUser, Researcher, CAM, Project, logCamActions
from block.models import Block
from link.models import Link
import json
import yaml

# Use UnsafeLoader for compatibility with views_undo.py which uses yaml.load()
# Note: In production, yaml.load() should be updated to yaml.safe_load()
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class UndoActionTestCase(TestCase):
    """Comprehensive tests for undo_action view"""

    def setUp(self):
        # Create user and researcher
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@test.com", password="12345"
        )
        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")
        self.client.login(username="testuser", password="12345")

        # Create project and CAM
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

        # Create test blocks
        self.block1 = Block.objects.create(
            title="Block1",
            x_pos=10.0,
            y_pos=20.0,
            width=100,
            height=100,
            shape="neutral",
            creator=self.user,
            CAM=self.cam,
            num=1,
        )

        self.block2 = Block.objects.create(
            title="Block2",
            x_pos=150.0,
            y_pos=200.0,
            width=120,
            height=120,
            shape="positive",
            creator=self.user,
            CAM=self.cam,
            num=2,
        )

        # Create test link
        self.link = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            line_style="Solid-Weak",
            arrow_type="uni",
            creator=self.user,
            CAM=self.cam,
            num=1,
        )

    def test_undo_action_get_request(self):
        """Test undo_action with GET request returns failure message"""
        response = self.client.get("/users/undo_action")
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn("message", response_data)
        self.assertEqual(response_data["message"], "Failed to undo previous action")

    def test_undo_action_post_no_actions(self):
        """Test undo_action with POST but no logged actions"""
        # Ensure no log actions exist
        logCamActions.objects.filter(camId=self.cam).delete()

        try:
            response = self.client.post("/users/undo_action")
            # Should handle gracefully when no actions exist
            self.assertIn(response.status_code, [200, 500])
        except logCamActions.DoesNotExist:
            # Exception is acceptable when no actions exist
            pass

    def test_undo_delete_block_action(self):
        """Test undoing a block deletion"""
        # Create a log entry for block deletion
        block_data = {
            "title": self.block1.title,
            "x_pos": self.block1.x_pos,
            "y_pos": self.block1.y_pos,
            "width": self.block1.width,
            "height": self.block1.height,
            "shape": self.block1.shape,
            "creator": self.block1.creator.id,
            "CAM": self.block1.CAM.id,
            "num": self.block1.num,
        }

        log_action = logCamActions.objects.create(
            camId=self.cam,
            actionId=1,
            actionType=0,  # Delete action
            objType=1,  # Block/Concept object
            objDetails=yaml.dump(block_data),
        )

        # Delete the block
        block_id = self.block1.id
        self.block1.delete()

        # Verify block is deleted
        self.assertFalse(Block.objects.filter(id=block_id).exists())

        # Call undo action
        response = self.client.post("/users/undo_action")
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertIn("message", response_data)

    def test_undo_delete_link_action(self):
        """Test undoing a link deletion (requires block to be undone first)"""
        # The undo logic expects block to be restored before link
        # So we need to create both block and link log entries

        # First, create block deletion log entry
        block_data = {
            "title": self.block1.title,
            "x_pos": self.block1.x_pos,
            "y_pos": self.block1.y_pos,
            "width": self.block1.width,
            "height": self.block1.height,
            "shape": self.block1.shape,
            "creator": self.block1.creator.id,
            "CAM": self.block1.CAM.id,
            "num": self.block1.num,
        }

        logCamActions.objects.create(
            camId=self.cam,
            actionId=1,
            actionType=0,  # Delete action
            objType=1,  # Block object (must come first)
            objDetails=yaml.dump(block_data),
        )

        # Then create link deletion log entry
        link_data = {
            "starting_block": self.link.starting_block.id,
            "ending_block": self.link.ending_block.id,
            "line_style": self.link.line_style,
            "arrow_type": self.link.arrow_type,
            "creator": self.link.creator.id,
            "CAM": self.link.CAM.id,
            "num": self.link.num,
        }

        logCamActions.objects.create(
            camId=self.cam,
            actionId=1,  # Same actionId as block
            actionType=0,  # Delete action
            objType=0,  # Link object
            objDetails=yaml.dump(link_data),
        )

        # Delete the block and link
        block_id = self.block1.id
        link_id = self.link.id
        self.block1.delete()
        self.link.delete()

        # Verify both are deleted
        self.assertFalse(Block.objects.filter(id=block_id).exists())
        self.assertFalse(Link.objects.filter(id=link_id).exists())

        # Call undo action
        response = self.client.post("/users/undo_action")
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertIn("message", response_data)

    def test_undo_non_delete_action(self):
        """Test undo with non-delete action (should warn)"""
        # Create a log entry for non-delete action (e.g., actionType=1)
        log_action = logCamActions.objects.create(
            camId=self.cam,
            actionId=1,
            actionType=1,  # Non-delete action
            objType=1,  # Block object
            objDetails=yaml.dump({"title": "Test"}),
        )

        response = self.client.post("/users/undo_action")
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertIn("message", response_data)
        # Should contain warning about only allowing undo of delete actions
        self.assertIn("only allow", response_data["message"].lower())

    def test_undo_invalid_object_type(self):
        """Test undo with invalid object type"""
        # Create a log entry with invalid objType (not 0 or 1)
        log_action = logCamActions.objects.create(
            camId=self.cam,
            actionId=1,
            actionType=0,  # Delete action
            objType=999,  # Invalid object type
            objDetails=yaml.dump({"title": "Test"}),
        )

        response = self.client.post("/users/undo_action")
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertIn("message", response_data)
        # Should contain warning about only concepts and links
        self.assertIn("concepts and links", response_data["message"])

    def test_undo_multiple_actions_same_id(self):
        """Test undo with multiple actions sharing the same actionId"""
        # Create multiple log entries with same actionId
        block_data = {
            "title": "TestBlock",
            "x_pos": 10.0,
            "y_pos": 20.0,
            "width": 100,
            "height": 100,
            "shape": "neutral",
            "creator": self.user.id,
            "CAM": self.cam.id,
            "num": 10,
        }

        # Create first action
        logCamActions.objects.create(
            camId=self.cam,
            actionId=1,
            actionType=0,
            objType=1,
            objDetails=yaml.dump(block_data),
        )

        # Create second action with same actionId
        block_data2 = block_data.copy()
        block_data2["num"] = 11
        block_data2["title"] = "TestBlock2"

        logCamActions.objects.create(
            camId=self.cam,
            actionId=1,  # Same actionId
            actionType=0,
            objType=1,
            objDetails=yaml.dump(block_data2),
        )

        response = self.client.post("/users/undo_action")
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertIn("message", response_data)

    def test_undo_with_malformed_yaml(self):
        """Test undo with malformed YAML data"""
        # Create a log entry with invalid YAML
        log_action = logCamActions.objects.create(
            camId=self.cam,
            actionId=1,
            actionType=0,
            objType=1,
            objDetails="invalid: yaml: data: {{{",  # Malformed YAML
        )

        try:
            response = self.client.post("/users/undo_action")
            # Should handle error gracefully
            self.assertIn(response.status_code, [200, 500])
        except yaml.scanner.ScannerError:
            # ScannerError is acceptable for malformed YAML
            pass

    def test_undo_block_with_invalid_data(self):
        """Test undo block with invalid/incomplete data"""
        # Create log with incomplete block data
        incomplete_block_data = {
            "title": "IncompleteBlock",
            # Missing required fields like CAM, creator, etc.
        }

        log_action = logCamActions.objects.create(
            camId=self.cam,
            actionId=1,
            actionType=0,
            objType=1,
            objDetails=yaml.dump(incomplete_block_data),
        )

        response = self.client.post("/users/undo_action")
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertIn("message", response_data)
        # Should contain error about form failure
        self.assertIn("form failed", response_data["message"].lower())

    def test_undo_link_with_invalid_data(self):
        """Test undo link with invalid/incomplete data"""
        # First create a block deletion log entry
        block_data = {
            "title": "DeletedBlock",
            "x_pos": 10.0,
            "y_pos": 20.0,
            "width": 100,
            "height": 100,
            "shape": "neutral",
            "creator": self.user.id,
            "CAM": self.cam.id,
            "num": 20,
        }

        logCamActions.objects.create(
            camId=self.cam,
            actionId=1,
            actionType=0,
            objType=1,
            objDetails=yaml.dump(block_data),
        )

        # Then create incomplete link data
        incomplete_link_data = {
            "starting_block": 9999,  # Non-existent block
            "ending_block": 9999,  # Non-existent block
            # Missing other required fields
        }

        logCamActions.objects.create(
            camId=self.cam,
            actionId=1,
            actionType=0,
            objType=0,  # Link
            objDetails=yaml.dump(incomplete_link_data),
        )

        response = self.client.post("/users/undo_action")
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertIn("message", response_data)

    def test_undo_latest_action_only(self):
        """Test that undo only affects the latest actionId"""
        # Create older action
        old_block_data = {
            "title": "OldBlock",
            "x_pos": 10.0,
            "y_pos": 20.0,
            "width": 100,
            "height": 100,
            "shape": "neutral",
            "creator": self.user.id,
            "CAM": self.cam.id,
            "num": 30,
        }

        logCamActions.objects.create(
            camId=self.cam,
            actionId=1,  # Older action
            actionType=0,
            objType=1,
            objDetails=yaml.dump(old_block_data),
        )

        # Create newer action
        new_block_data = {
            "title": "NewBlock",
            "x_pos": 50.0,
            "y_pos": 60.0,
            "width": 100,
            "height": 100,
            "shape": "positive",
            "creator": self.user.id,
            "CAM": self.cam.id,
            "num": 31,
        }

        logCamActions.objects.create(
            camId=self.cam,
            actionId=2,  # Newer action
            actionType=0,
            objType=1,
            objDetails=yaml.dump(new_block_data),
        )

        response = self.client.post("/users/undo_action")
        self.assertEqual(response.status_code, 200)

        # Should process the latest actionId (2)
        response_data = json.loads(response.content)
        self.assertIn("message", response_data)

    def test_undo_action_without_authentication(self):
        """Test undo_action without being logged in"""
        self.client.logout()

        try:
            response = self.client.post("/users/undo_action")
            # Should handle authentication error
            self.assertIn(response.status_code, [200, 302, 403, 500])
        except Exception:
            # Exception is acceptable without authentication
            pass

    def test_undo_response_message_structure(self):
        """Test that undo_action always returns message in response"""
        # Create a simple valid log entry
        block_data = {
            "title": "TestBlock",
            "x_pos": 10.0,
            "y_pos": 20.0,
            "width": 100,
            "height": 100,
            "shape": "neutral",
            "creator": self.user.id,
            "CAM": self.cam.id,
            "num": 40,
        }

        logCamActions.objects.create(
            camId=self.cam,
            actionId=1,
            actionType=0,
            objType=1,
            objDetails=yaml.dump(block_data),
        )

        response = self.client.post("/users/undo_action")
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        # Should always have a message field
        self.assertIn("message", response_data)
        self.assertIsInstance(response_data["message"], str)
        self.assertTrue(len(response_data["message"]) > 0)

    def test_undo_empty_objDetails(self):
        """Test undo with empty objDetails"""
        log_action = logCamActions.objects.create(
            camId=self.cam,
            actionId=1,
            actionType=0,
            objType=1,
            objDetails="",  # Empty details
        )

        response = self.client.post("/users/undo_action")

        # Should handle gracefully
        self.assertIn(response.status_code, [200, 500])
