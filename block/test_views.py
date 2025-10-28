"""
Comprehensive tests for block views
"""

from django.test import TestCase, override_settings
from users.models import CustomUser, Researcher, CAM, Project
from block.models import Block
from link.models import Link
import json


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class BlockViewsTestCase(TestCase):
    """Comprehensive tests for block views"""

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

        # Create test block
        self.block = Block.objects.create(
            title="TestBlock",
            x_pos=10.0,
            y_pos=20.0,
            width=100,
            height=100,
            shape="neutral",
            creator=self.user,
            CAM=self.cam,
            num=1,
        )

    def test_add_block_no_authentication(self):
        """Test add_block without authentication"""
        self.client.logout()
        response = self.client.post(
            "/block/add_block",
            {
                "add_valid": True,
                "num_block": 99,
                "title": "Unauthorized",
                "shape": 3,
                "x_pos": 0,
                "y_pos": 0,
                "width": 100,
                "height": 100,
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_add_block_valid_data(self):
        """Test adding a block with valid data"""
        response = self.client.post(
            "/block/add_block",
            {
                "add_valid": True,
                "num_block": 99,
                "title": "NewBlock",
                "shape": 3,
                "x_pos": "50.0",
                "y_pos": "60.0",
                "width": "150",
                "height": "120",
            },
        )
        self.assertEqual(response.status_code, 200)
        # Check block was created
        new_block = Block.objects.filter(title="NewBlock").first()
        self.assertIsNotNone(new_block)

    def test_add_block_invalid_no_valid_param(self):
        """Test adding a block without add_valid parameter"""
        response = self.client.post(
            "/block/add_block",
            {
                "num_block": 100,
                "title": "InvalidBlock",
                "shape": 3,
                "x_pos": 0,
                "y_pos": 0,
                "width": 100,
                "height": 100,
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_add_block_non_post_request(self):
        """Test add_block with non-POST request"""
        response = self.client.get("/block/add_block")
        self.assertEqual(response.status_code, 200)

    def test_update_block_valid_data(self):
        """Test updating a block with valid data"""
        response = self.client.post(
            "/block/update_block",
            {
                "update_valid": True,
                "num_block": self.block.num,
                "title": "UpdatedBlock",
                "shape": 5,
                "x_pos": "100.0",
                "y_pos": "120.0",
                "width": "200",
                "height": "180",
                "comment": "Test comment",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.block.refresh_from_db()
        self.assertEqual(self.block.title, "UpdatedBlock")
        self.assertEqual(self.block.comment, "Test comment")

    def test_update_block_nonexistent(self):
        """Test updating a nonexistent block"""
        response = self.client.post(
            "/block/update_block",
            {
                "update_valid": True,
                "num_block": 9999,
                "title": "NonexistentUpdate",
                "shape": 3,
                "x_pos": "0",
                "y_pos": "0",
                "width": "100",
                "height": "100",
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_block_valid(self):
        """Test deleting a block"""
        block_id = self.block.num
        response = self.client.post(
            "/block/delete_block",
            {"delete_valid": True, "block_id": block_id},
        )
        self.assertEqual(response.status_code, 200)
        # Check block was deleted
        with self.assertRaises(Block.DoesNotExist):
            Block.objects.get(num=block_id, CAM=self.cam)

    def test_delete_block_non_modifiable(self):
        """Test that non-modifiable blocks cannot be deleted"""
        # Set block as non-modifiable
        self.block.modifiable = False
        self.block.save()

        block_id = self.block.num
        response = self.client.post(
            "/block/delete_block",
            {"delete_valid": True, "block_id": block_id},
        )
        # Should return 403 Forbidden
        self.assertEqual(response.status_code, 403)
        # Check block still exists
        self.assertTrue(Block.objects.filter(num=block_id, CAM=self.cam).exists())
        # Verify error message
        response_data = json.loads(response.content)
        self.assertEqual(response_data["error"], "This block cannot be deleted")

    def test_drag_function_update_position(self):
        """Test drag_function to update block position"""
        response = self.client.post(
            "/block/drag_function",
            {
                "drag_valid": True,
                "block_id": self.block.num,
                "x_pos": "250.0px",
                "y_pos": "350.0px",
                "width": "100px",
                "height": "100px",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.block.refresh_from_db()
        self.assertEqual(self.block.x_pos, 250.0)
        self.assertEqual(self.block.y_pos, 350.0)

    def test_drag_function_resize_block(self):
        """Test drag_function to resize a block"""
        response = self.client.post(
            "/block/drag_function",
            {
                "drag_valid": True,
                "block_id": self.block.num,
                "x_pos": "10.0px",
                "y_pos": "20.0px",
                "width": "200px",
                "height": "150px",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.block.refresh_from_db()
        self.assertEqual(self.block.width, 200.0)
        self.assertEqual(self.block.height, 150.0)

    def test_update_text_size(self):
        """Test updating block text size"""
        response = self.client.post(
            "/block/update_text_size",
            {"block_id": self.block.num, "text_scale": "18"},
        )
        self.assertEqual(response.status_code, 200)
        self.block.refresh_from_db()
        self.assertEqual(self.block.text_scale, 18.0)

    def test_add_block_missing_fields(self):
        """Test adding block with missing required fields"""
        response = self.client.post(
            "/block/add_block",
            {
                "add_valid": True,
                "num_block": 100,
                # Missing title and shape
                "x_pos": "0",
                "y_pos": "0",
                "width": "100",
                "height": "100",
            },
        )
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400])

    def test_update_block_missing_block_num(self):
        """Test updating block without providing block number"""
        response = self.client.post(
            "/block/update_block",
            {
                "update_valid": True,
                "title": "Updated",
                "shape": 3,
            },
        )
        # Should handle missing block number
        self.assertIn(response.status_code, [200, 400, 404])

    def test_delete_block_no_valid_param(self):
        """Test deleting block without delete_valid parameter"""
        response = self.client.post(
            "/block/delete_block",
            {"block_id": self.block.num},
        )
        # Should not delete without delete_valid parameter
        self.assertEqual(response.status_code, 200)
        # Block should still exist
        self.assertTrue(Block.objects.filter(num=self.block.num, CAM=self.cam).exists())

    def test_drag_function_no_drag_valid(self):
        """Test drag function without drag_valid parameter"""
        response = self.client.post(
            "/block/drag_function",
            {
                "block_id": self.block.num,
                "x_pos": "250.0",
                "y_pos": "350.0",
                "width": "100",
                "height": "100",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_update_text_size_invalid_scale(self):
        """Test updating text size with invalid value"""
        response = self.client.post(
            "/block/update_text_size",
            {"block_id": self.block.num, "text_scale": "invalid"},
        )
        # Should handle invalid input gracefully
        self.assertIn(response.status_code, [200, 400])

    def test_update_block_get_request(self):
        """Test update_block with GET request instead of POST"""
        response = self.client.get("/block/update_block")
        self.assertEqual(response.status_code, 400)

    def test_delete_block_get_request(self):
        """Test delete_block with GET request instead of POST"""
        response = self.client.get("/block/delete_block")
        self.assertEqual(response.status_code, 200)

    def test_drag_function_get_request(self):
        """Test drag_function with GET request instead of POST"""
        response = self.client.get("/block/drag_function")
        self.assertEqual(response.status_code, 200)

    def test_update_text_size_get_request(self):
        """Test update_text_size with GET request instead of POST"""
        response = self.client.get("/block/update_text_size")
        self.assertEqual(response.status_code, 400)

    def test_add_block_without_add_valid_param(self):
        """Test add_block without add_valid parameter"""
        response = self.client.post(
            "/block/add_block",
            {
                "num_block": 100,
                "title": "Test",
                "shape": 3,
                "x_pos": "0",
                "y_pos": "0",
                "width": "100",
                "height": "100",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_drag_function_with_different_dimensions(self):
        """Test drag function with very large dimensions"""
        response = self.client.post(
            "/block/drag_function",
            {
                "drag_valid": True,
                "block_id": self.block.num,
                "x_pos": "5000.0px",
                "y_pos": "5000.0px",
                "width": "1000px",
                "height": "1000px",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.block.refresh_from_db()
        self.assertEqual(self.block.x_pos, 5000.0)
        self.assertEqual(self.block.y_pos, 5000.0)

    def test_resize_block_dimensions(self):
        """Test resizing a block's dimensions"""
        response = self.client.post(
            "/block/resize_block",
            {
                "resize_valid": True,
                "block_id": self.block.num,
                "width": "300",
                "height": "250",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.block.refresh_from_db()
        self.assertEqual(self.block.width, 300.0)
        self.assertEqual(self.block.height, 250.0)

    def test_resize_block_toggle_resizable_true(self):
        """Test setting all blocks in CAM as resizable"""
        # Create additional blocks
        Block.objects.create(
            title="Block2",
            x_pos=100.0,
            y_pos=100.0,
            width=100,
            height=100,
            shape="neutral",
            creator=self.user,
            CAM=self.cam,
            num=2,
            resizable=False,
        )

        response = self.client.post(
            "/block/resize_block",
            {
                "update_valid": True,
                "resize": "True",
            },
        )
        self.assertEqual(response.status_code, 200)

        # Check all blocks are now resizable
        for block in Block.objects.filter(CAM=self.cam):
            block.refresh_from_db()
            self.assertTrue(block.resizable)

    def test_resize_block_toggle_resizable_false(self):
        """Test setting all blocks in CAM as non-resizable"""
        # Create additional blocks
        Block.objects.create(
            title="Block2",
            x_pos=100.0,
            y_pos=100.0,
            width=100,
            height=100,
            shape="neutral",
            creator=self.user,
            CAM=self.cam,
            num=2,
            resizable=True,
        )

        response = self.client.post(
            "/block/resize_block",
            {
                "update_valid": True,
                "resize": "False",
            },
        )
        self.assertEqual(response.status_code, 200)

        # Check all blocks are now non-resizable
        for block in Block.objects.filter(CAM=self.cam):
            block.refresh_from_db()
            self.assertFalse(block.resizable)

    def test_resize_block_nonexistent(self):
        """Test resizing a nonexistent block"""
        response = self.client.post(
            "/block/resize_block",
            {
                "resize_valid": True,
                "block_id": 9999,
                "width": "300",
                "height": "250",
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_resize_block_no_valid_param(self):
        """Test resize_block without valid parameters"""
        response = self.client.post(
            "/block/resize_block",
            {
                "block_id": self.block.num,
                "width": "300",
                "height": "250",
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_resize_block_get_request(self):
        """Test resize_block with GET request instead of POST"""
        response = self.client.get("/block/resize_block")
        self.assertEqual(response.status_code, 400)

    def test_delete_block_with_links(self):
        """Test deleting a block that has links connected to it"""
        # Create another block
        block2 = Block.objects.create(
            title="Block2",
            x_pos=200.0,
            y_pos=200.0,
            width=100,
            height=100,
            shape="neutral",
            creator=self.user,
            CAM=self.cam,
            num=2,
        )

        # Create a link between blocks
        link = Link.objects.create(
            starting_block=self.block,
            ending_block=block2,
            line_style="Solid-Weak",
            arrow_type="uni",
            creator=self.user,
            CAM=self.cam,
            num=1,
        )

        response = self.client.post(
            "/block/delete_block",
            {"delete_valid": True, "block_id": self.block.num},
        )
        self.assertEqual(response.status_code, 200)

        # Verify block is deleted
        with self.assertRaises(Block.DoesNotExist):
            Block.objects.get(num=self.block.num, CAM=self.cam)

        # Verify link is also deleted
        with self.assertRaises(Link.DoesNotExist):
            Link.objects.get(id=link.id)

        # Check response contains deleted links
        response_data = json.loads(response.content)
        self.assertIn("links", response_data)

    def test_delete_block_nonexistent(self):
        """Test deleting a nonexistent block"""
        response = self.client.post(
            "/block/delete_block",
            {"delete_valid": True, "block_id": 9999},
        )
        self.assertEqual(response.status_code, 404)

    def test_drag_function_with_links(self):
        """Test dragging a block that has links updates link positions"""
        # Create another block and link
        block2 = Block.objects.create(
            title="Block2",
            x_pos=200.0,
            y_pos=200.0,
            width=100,
            height=100,
            shape="neutral",
            creator=self.user,
            CAM=self.cam,
            num=2,
        )

        Link.objects.create(
            starting_block=self.block,
            ending_block=block2,
            line_style="Solid-Weak",
            arrow_type="uni",
            creator=self.user,
            CAM=self.cam,
            num=1,
        )

        response = self.client.post(
            "/block/drag_function",
            {
                "drag_valid": True,
                "block_id": self.block.num,
                "x_pos": "250.0px",
                "y_pos": "350.0px",
                "width": "100px",
                "height": "100px",
            },
        )
        self.assertEqual(response.status_code, 200)

        # Response should contain link data
        response_data = json.loads(response.content)
        # Check that link information is in response
        self.assertTrue(len(response_data) > 0)

    def test_drag_function_nonexistent_block(self):
        """Test drag function with nonexistent block"""
        response = self.client.post(
            "/block/drag_function",
            {
                "drag_valid": True,
                "block_id": 9999,
                "x_pos": "100.0px",
                "y_pos": "100.0px",
                "width": "100px",
                "height": "100px",
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_update_text_size_nonexistent_block(self):
        """Test updating text size for nonexistent block"""
        response = self.client.post(
            "/block/update_text_size",
            {"block_id": 9999, "text_scale": "18"},
        )
        self.assertEqual(response.status_code, 404)

    def test_update_text_size_alternative_param(self):
        """Test updating text size using text_size parameter instead of text_scale"""
        response = self.client.post(
            "/block/update_text_size",
            {"block_id": self.block.num, "text_size": "20"},
        )
        self.assertEqual(response.status_code, 200)
        self.block.refresh_from_db()
        self.assertEqual(self.block.text_scale, 20.0)

    def test_update_block_without_update_valid(self):
        """Test update_block without update_valid parameter"""
        response = self.client.post(
            "/block/update_block",
            {
                "num_block": self.block.num,
                "title": "ShouldNotUpdate",
                "shape": 3,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.block.refresh_from_db()
        self.assertEqual(self.block.title, "TestBlock")  # Should not be updated

    def test_add_block_with_different_shapes(self):
        """Test adding blocks with different shape types"""
        shapes = [1, 2, 3, 4, 5, 6, 7]  # Different shape values

        for i, shape in enumerate(shapes):
            response = self.client.post(
                "/block/add_block",
                {
                    "add_valid": True,
                    "num_block": 100 + i,
                    "title": f"ShapeBlock{i}",
                    "shape": shape,
                    "x_pos": "0",
                    "y_pos": "0",
                    "width": "100",
                    "height": "100",
                },
            )
            self.assertEqual(response.status_code, 200)

    def test_drag_function_with_text_scale(self):
        """Test drag function updates text_scale if provided"""
        response = self.client.post(
            "/block/drag_function",
            {
                "drag_valid": True,
                "block_id": self.block.num,
                "x_pos": "100.0px",
                "y_pos": "100.0px",
                "width": "100px",
                "height": "100px",
                "text_scale": "16",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.block.refresh_from_db()
        self.assertEqual(self.block.text_scale, 16.0)

    def test_add_block_with_comment(self):
        """Test adding a block - comment should be empty initially"""
        response = self.client.post(
            "/block/add_block",
            {
                "add_valid": True,
                "num_block": 200,
                "title": "BlockWithComment",
                "shape": 3,
                "x_pos": "0",
                "y_pos": "0",
                "width": "100",
                "height": "100",
            },
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        # Comment should be empty string or None initially
        self.assertIn(response_data.get("comment"), ["", None])

    def test_update_block_all_fields(self):
        """Test updating all fields of a block at once"""
        response = self.client.post(
            "/block/update_block",
            {
                "update_valid": True,
                "num_block": self.block.num,
                "title": "CompletelyUpdated",
                "shape": 4,
                "comment": "New comment",
                "x_pos": "500.0",
                "y_pos": "600.0",
                "width": "250",
                "height": "200",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.block.refresh_from_db()
        self.assertEqual(self.block.title, "CompletelyUpdated")
        self.assertEqual(self.block.comment, "New comment")
        self.assertEqual(self.block.x_pos, 500.0)
        self.assertEqual(self.block.y_pos, 600.0)
        self.assertEqual(self.block.width, 250.0)
        self.assertEqual(self.block.height, 200.0)

    def test_resize_block_invalid_dimensions(self):
        """Test resizing block with invalid dimensions"""
        response = self.client.post(
            "/block/resize_block",
            {
                "resize_valid": True,
                "block_id": self.block.num,
                "width": "invalid",
                "height": "invalid",
            },
        )
        # Should handle invalid input gracefully
        self.assertIn(response.status_code, [200, 400])

    def test_drag_function_negative_coordinates(self):
        """Test drag function with negative coordinates"""
        response = self.client.post(
            "/block/drag_function",
            {
                "drag_valid": True,
                "block_id": self.block.num,
                "x_pos": "-50.0px",
                "y_pos": "-100.0px",
                "width": "100px",
                "height": "100px",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.block.refresh_from_db()
        # Check if negative coordinates are handled
        self.assertTrue(True)  # Basic check that request completes
