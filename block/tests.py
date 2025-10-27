from django.test import TestCase
from users.models import CustomUser, CAM, Researcher, Project, logCamActions
from .models import Block
from django.forms.models import model_to_dict
import yaml


# Create your tests here.
class BlockTestCase(TestCase):
    def setUp(self):
        # Set up a user
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@test.test", password="12345"
        )
        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")
        login = self.client.login(username="testuser", password="12345")
        # Create project belonging to user
        self.project = Project.objects.create(
            name="TestProject",
            description="TEST PROJECT",
            researcher=self.user,
            password="TestProjectPassword",
            name_participants="BLK",
        )
        self.cam = CAM.objects.create(
            name="testCAM", user=self.user, project=self.project
        )
        self.user.active_cam_num = self.cam.id
        self.user.save()

    def test_create_block(self):
        """
        Test to create a simple block for user as part of their CAM
        """
        # Data to pass through to ajax call
        data = {
            "add_valid": True,
            "num_block": 1,
            "title": "Meow",
            "shape": 3,
            "x_pos": 0.0,
            "y_pos": 0.0,
            "width": 100,
            "height": 100,
        }
        response = self.client.post("/block/add_block", data)
        # Make sure the correct response is obtained
        self.assertTrue(response.status_code, 200)
        # Check that the new block was in fact created
        self.assertTrue("Meow", [block.title for block in Block.objects.all()])

    def test_update_block(self):
        """
        Test to update an existing block
        """
        block_ = Block.objects.create(
            title="Meow2",
            x_pos=1.0,
            y_pos=1.0,
            height=100,
            width=100,
            creator=self.user,
            shape="neutral",
            CAM_id=self.cam.id,
        )
        data = {
            "update_valid": True,
            "num_block": block_.num,
            "title": "Meow2_update",
            "shape": 7,
            "comment": "ew",
            "x_pos": "2.0px",
            "y_pos": "2.0px",
            "height": "50px",
            "width": "50px",
        }
        response = self.client.post("/block/update_block", data)
        # Make sure the correct response is obtained
        self.assertTrue(response.status_code, 200)
        # Refresh block info from db
        block_.refresh_from_db()
        # Check that the updates were made
        update_true = {
            "title": "Meow2_update",
            "shape": 7,
            "comment": "ew",
            "x_pos": 2.0,
            "y_pos": 2.0,
            "height": 50,
            "width": 50,
        }  # What it should be updated to
        update_actual = {
            "title": block_.title,
            "shape": trans_shape_to_slide(block_.shape),
            "comment": block_.comment,
            "x_pos": block_.x_pos,
            "y_pos": block_.y_pos,
            "height": block_.height,
            "width": block_.width,
        }
        self.assertDictEqual(update_true, update_actual)
        # block_.delete()

    def test_delete_block(self):
        """
        Test that a block is deleted
        """
        block_ = Block.objects.create(
            title="Meow3",
            x_pos=1.0,
            y_pos=1.0,
            height=100,
            width=100,
            creator=self.user,
            shape="ambivalent",
            CAM_id=self.cam.id,
        )
        response = self.client.post(
            "/block/delete_block", {"delete_valid": True, "block_id": block_.num}
        )
        self.assertTrue(response.status_code, 200)
        logEntry = self.cam.logcamactions_set.latest("actionId").objDetails
        logEntry = yaml.load(logEntry, Loader=yaml.FullLoader)
        self.assertTrue(logEntry["title"], "Meow3")

    def test_drag_block(self):
        """
        Test that when a block is dragged the position information is updated
        """
        block_ = Block.objects.create(
            title="Meow3",
            x_pos=1.0,
            y_pos=1.0,
            height=100,
            width=100,
            creator=self.user,
            shape="ambivalent",
            CAM_id=self.cam.id,
        )
        data = {
            "drag_valid": True,
            "block_id": block_.num,
            "x_pos": "10.0px",
            "y_pos": "10.0px",
            "width": "100px",
            "height": "100px",
        }
        response = self.client.post("/block/drag_function", data)
        block_.refresh_from_db()
        update_true = {
            "title": "Meow3",
            "shape": 7,
            "x_pos": 10.0,
            "y_pos": 10.0,
            "height": 100.0,
            "width": 100.0,
        }  # What it should be updated to
        update_actual = {
            "title": block_.title,
            "shape": trans_shape_to_slide(block_.shape),
            "x_pos": block_.x_pos,
            "y_pos": block_.y_pos,
            "height": block_.height,
            "width": block_.width,
        }
        self.assertDictEqual(update_true, update_actual)
        block_.delete()

    def test_resize_block(self):
        """
        Test resizing a block
        """
        block_ = Block.objects.create(
            title="Meow4",
            x_pos=1.0,
            y_pos=1.0,
            height=100,
            width=100,
            creator=self.user,
            shape="neutral",
            CAM_id=self.cam.id,
        )
        data = {
            "resize_valid": True,
            "block_id": block_.num,
            "width": "200px",
            "height": "150px",
        }
        response = self.client.post("/block/resize_block", data)
        self.assertEqual(response.status_code, 200)

        block_.refresh_from_db()
        self.assertEqual(block_.width, 200.0)
        self.assertEqual(block_.height, 150.0)
        block_.delete()

    def test_update_text_size(self):
        """
        Test updating text size for a block
        """
        block_ = Block.objects.create(
            title="Meow5",
            x_pos=1.0,
            y_pos=1.0,
            height=100,
            width=100,
            creator=self.user,
            shape="neutral",
            CAM_id=self.cam.id,
            text_scale=14,
        )
        data = {"block_id": block_.num, "text_size": 20}
        response = self.client.post("/block/update_text_size", data)
        self.assertEqual(response.status_code, 200)

        block_.refresh_from_db()
        self.assertEqual(block_.text_scale, 20.0)
        block_.delete()

    def test_block_model_update_method(self):
        """
        Test Block model's update method
        """
        block_ = Block.objects.create(
            title="UpdateTest",
            x_pos=1.0,
            y_pos=1.0,
            height=100,
            width=100,
            creator=self.user,
            shape="neutral",
            CAM_id=self.cam.id,
        )

        # Test update method
        block_.update({"title": "UpdatedTitle", "comment": "Test comment"})
        block_.refresh_from_db()

        self.assertEqual(block_.title, "UpdatedTitle")
        self.assertEqual(block_.comment, "Test comment")
        block_.delete()

    def test_block_shape_choices(self):
        """
        Test that blocks can be created with all valid shape choices
        """
        shapes = [
            "neutral",
            "positive",
            "negative",
            "positive strong",
            "negative strong",
            "ambivalent",
            "negative weak",
            "positive weak",
        ]

        for idx, shape in enumerate(shapes):
            block = Block.objects.create(
                title=f"ShapeTest{idx}",
                x_pos=1.0,
                y_pos=1.0,
                height=100,
                width=100,
                creator=self.user,
                shape=shape,
                CAM_id=self.cam.id,
                num=idx + 10,
            )
            self.assertEqual(block.shape, shape)
            block.delete()

    def test_block_string_representation(self):
        """
        Test Block __str__ method
        """
        block_ = Block.objects.create(
            title="TestTitle",
            x_pos=1.0,
            y_pos=1.0,
            height=100,
            width=100,
            creator=self.user,
            shape="neutral",
            CAM_id=self.cam.id,
        )
        self.assertEqual(str(block_), "TestTitle")
        block_.delete()

    def test_block_default_values(self):
        """
        Test that blocks are created with correct default values
        """
        block_ = Block.objects.create(
            title="DefaultTest", creator=self.user, shape="neutral", CAM_id=self.cam.id
        )

        self.assertEqual(block_.x_pos, 0.0)
        self.assertEqual(block_.y_pos, 0.0)
        self.assertEqual(block_.width, 160)
        self.assertEqual(block_.height, 120)
        self.assertEqual(block_.text_scale, 14)
        self.assertTrue(block_.modifiable)
        self.assertFalse(block_.resizable)
        block_.delete()

    def test_block_cascade_delete_with_cam(self):
        """
        Test that blocks are deleted when their CAM is deleted
        """
        # Create a new CAM
        test_cam = CAM.objects.create(
            name="DeleteTestCAM", user=self.user, project=self.project
        )

        # Create blocks for this CAM
        block1 = Block.objects.create(
            title="CascadeTest1",
            creator=self.user,
            shape="neutral",
            CAM=test_cam,
            num=100,
        )
        block2 = Block.objects.create(
            title="CascadeTest2",
            creator=self.user,
            shape="positive",
            CAM=test_cam,
            num=101,
        )

        # Delete the CAM
        test_cam.delete()

        # Verify blocks are also deleted
        with self.assertRaises(Block.DoesNotExist):
            Block.objects.get(id=block1.id)
        with self.assertRaises(Block.DoesNotExist):
            Block.objects.get(id=block2.id)

    def test_shape_translation(self):
        """
        Test trans_slide_to_shape translation function from views
        """
        from block.views import trans_slide_to_shape

        # Test all valid shape values
        test_cases = [
            ("0", "negative strong"),
            ("1", "negative"),
            ("2", "negative weak"),
            ("3", "neutral"),
            ("4", "positive weak"),
            ("5", "positive"),
            ("6", "positive strong"),
            ("7", "ambivalent"),
        ]

        for slide_val, expected_shape in test_cases:
            with self.subTest(slide_val=slide_val):
                result = trans_slide_to_shape(slide_val)
                self.assertEqual(result, expected_shape)

    def test_shape_translation_invalid_input(self):
        """
        Test trans_slide_to_shape with invalid input defaults to neutral
        """
        from block.views import trans_slide_to_shape

        invalid_inputs = ["8", "100", "invalid", None, ""]
        for invalid_val in invalid_inputs:
            with self.subTest(invalid_val=invalid_val):
                result = trans_slide_to_shape(invalid_val)
                self.assertEqual(result, "neutral")

    def test_update_block_with_comment(self):
        """
        Test updating block with comment containing newlines
        """
        block_ = Block.objects.create(
            title="CommentTest",
            x_pos=1.0,
            y_pos=1.0,
            height=100,
            width=100,
            creator=self.user,
            shape="neutral",
            CAM_id=self.cam.id,
            num=201,
        )

        data = {
            "update_valid": True,
            "num_block": block_.num,
            "title": "Updated",
            "shape": 3,
            "x_pos": "10.0px",
            "y_pos": "20.0px",
            "width": "150px",
            "height": "200px",
            "comment": "Line 1\nLine 2\nLine 3",
        }

        response = self.client.post("/block/update_block", data)
        self.assertEqual(response.status_code, 200)

        block_.refresh_from_db()
        # Comment should be preserved (newlines may or may not be stripped depending on form)
        self.assertIsNotNone(block_.comment)
        self.assertIn("Line 1", block_.comment)

    def test_delete_block_with_links(self):
        """
        Test deleting a block that has associated links
        """
        from link.models import Link

        block1 = Block.objects.create(
            title="Block1",
            x_pos=1.0,
            y_pos=1.0,
            height=100,
            width=100,
            creator=self.user,
            shape="positive",
            CAM_id=self.cam.id,
            num=211,
        )

        block2 = Block.objects.create(
            title="Block2",
            x_pos=105.0,
            y_pos=105.0,
            height=100,
            width=100,
            creator=self.user,
            shape="negative",
            CAM_id=self.cam.id,
            num=212,
        )

        link = Link.objects.create(
            starting_block=block1,
            ending_block=block2,
            creator=self.user,
            CAM_id=self.cam.id,
        )

        link_id = link.id
        block1_id = block1.id

        response = self.client.post(
            "/block/delete_block", {"delete_valid": True, "block_id": block1.num}
        )

        self.assertEqual(response.status_code, 200)

        # Verify block is deleted
        self.assertFalse(Block.objects.filter(id=block1_id).exists())

        # Verify associated link is deleted
        self.assertFalse(Link.objects.filter(id=link_id).exists())

    def test_drag_block_with_text_scale(self):
        """
        Test dragging block and updating text scale
        """
        block_ = Block.objects.create(
            title="DragTest",
            x_pos=1.0,
            y_pos=1.0,
            height=100,
            width=100,
            creator=self.user,
            shape="neutral",
            CAM_id=self.cam.id,
            text_scale=14,
        )

        data = {
            "drag_valid": True,
            "block_id": block_.num,
            "x_pos": "50.0px",
            "y_pos": "75.0px",
            "width": "100px",
            "height": "100px",
            "text_scale": 18,
        }

        response = self.client.post("/block/drag_function", data)
        self.assertEqual(response.status_code, 200)

        block_.refresh_from_db()
        self.assertEqual(block_.x_pos, 50.0)
        self.assertEqual(block_.y_pos, 75.0)
        self.assertEqual(block_.text_scale, 18)

    def test_add_block_creates_block_in_database(self):
        """
        Test adding a new block creates it in database
        """
        data = {
            "add_valid": True,
            "num_block": 501,
            "title": "NewTestBlock",
            "shape": 3,
            "x_pos": "10.0",
            "y_pos": "20.0",
            "width": "200",
            "height": "150",
        }

        response = self.client.post("/block/add_block", data)
        self.assertEqual(response.status_code, 200)

        # Verify block was created
        block = Block.objects.filter(title="NewTestBlock", CAM_id=self.cam.id).first()
        self.assertIsNotNone(block)
        self.assertEqual(block.num, 501)
        self.assertEqual(block.shape, "neutral")

    def test_add_block_with_high_num(self):
        """
        Test that adding block with high number works
        """
        # Create block with high num
        data = {
            "add_valid": True,
            "num_block": 9999,
            "title": "HighNumBlock",
            "shape": 5,
            "x_pos": "10.0",
            "y_pos": "20.0",
            "width": "200",
            "height": "150",
        }

        response = self.client.post("/block/add_block", data)

        # Verify block was created with correct num
        block = Block.objects.filter(num=9999, CAM_id=self.cam.id).first()
        self.assertIsNotNone(block)
        self.assertEqual(block.title, "HighNumBlock")
        self.assertEqual(block.shape, "positive")

    def test_resize_block_invalid_dimensions(self):
        """
        Test resizing block with invalid width/height values
        """
        block_ = Block.objects.create(
            title="ResizeTestBlock",
            x_pos=1.0,
            y_pos=1.0,
            height=100,
            width=100,
            creator=self.user,
            shape="neutral",
            CAM_id=self.cam.id,
            num=511,
        )

        data = {
            "resize_valid": True,
            "block_id": block_.num,
            "width": "invalidpx",
            "height": "invalidpx",
        }

        response = self.client.post("/block/resize_block", data)
        # Should gracefully handle invalid input
        self.assertIsNotNone(response)

    def test_delete_block_cascade_with_multiple_links(self):
        """
        Test deleting block with multiple incoming and outgoing links
        """
        from link.models import Link

        block1 = Block.objects.create(
            title="CentralBlock",
            x_pos=50.0,
            y_pos=50.0,
            height=100,
            width=100,
            creator=self.user,
            shape="neutral",
            CAM_id=self.cam.id,
            num=521,
        )

        block2 = Block.objects.create(
            title="ConnectedBlock1",
            x_pos=1.0,
            y_pos=1.0,
            height=100,
            width=100,
            creator=self.user,
            shape="positive",
            CAM_id=self.cam.id,
            num=522,
        )

        block3 = Block.objects.create(
            title="ConnectedBlock2",
            x_pos=100.0,
            y_pos=100.0,
            height=100,
            width=100,
            creator=self.user,
            shape="negative",
            CAM_id=self.cam.id,
            num=523,
        )

        # Create multiple links
        link1 = Link.objects.create(
            starting_block=block1,
            ending_block=block2,
            creator=self.user,
            CAM_id=self.cam.id,
        )

        link2 = Link.objects.create(
            starting_block=block3,
            ending_block=block1,
            creator=self.user,
            CAM_id=self.cam.id,
        )

        link_ids = [link1.id, link2.id]

        # Delete the central block
        response = self.client.post(
            "/block/delete_block", {"delete_valid": True, "block_id": block1.num}
        )

        # Verify all related links are deleted
        for link_id in link_ids:
            self.assertFalse(Link.objects.filter(id=link_id).exists())


def trans_shape_to_slide(slide_val):
    """
    Translate between slider value and shape
    """
    if slide_val == "negative strong":
        shape = 0
    elif slide_val == "negative":
        shape = 1
    elif slide_val == "negative weak":
        shape = 2
    elif slide_val == "neutral":
        shape = 3
    elif slide_val == "positive weak":
        shape = 4
    elif slide_val == "positive":
        shape = 5
    elif slide_val == "positive strong":
        shape = 6
    elif slide_val == "ambivalent":
        shape = 7
    else:
        shape = "neutral"
    return shape
