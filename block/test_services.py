"""
Unit tests for block/services.py
Tests for all business logic functions extracted from views
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import CAM, Researcher, Project
from block.models import Block
from link.models import Link
from block.services import (
    trans_slide_to_shape,
    validate_block_number,
    validate_block_number_exists,
    parse_dimension_from_px,
    create_block,
    update_block_data,
    resize_block_dimensions,
    set_all_blocks_resizable,
    update_block_text_scale,
    get_next_action_id,
    log_block_deletion,
    cleanup_old_action_logs,
    delete_block_with_logging,
    get_links_for_block,
    get_links_data_for_block,
    update_block_position,
)

User = get_user_model()


class ShapeConversionTestCase(TestCase):
    """Test shape slider to name conversion"""

    def test_all_shape_mappings(self):
        """Test all shape value mappings"""
        mappings = {
            "0": "negative strong",
            "1": "negative",
            "2": "negative weak",
            "3": "neutral",
            "4": "positive weak",
            "5": "positive",
            "6": "positive strong",
            "7": "ambivalent",
        }

        for slider_val, expected_shape in mappings.items():
            with self.subTest(slider_val=slider_val):
                result = trans_slide_to_shape(slider_val)
                self.assertEqual(result, expected_shape)

    def test_invalid_shape_defaults_to_neutral(self):
        """Test invalid shape values default to neutral"""
        result = trans_slide_to_shape("99")
        self.assertEqual(result, "neutral")

    def test_non_string_shape_values(self):
        """Test conversion works with non-string values"""
        result = trans_slide_to_shape(3)
        self.assertEqual(result, "neutral")


class DimensionParsingTestCase(TestCase):
    """Test parsing of dimension strings with 'px' suffix"""

    def test_parse_dimension_with_px(self):
        """Test parsing dimension with px suffix"""
        value, success = parse_dimension_from_px("100px")
        self.assertTrue(success)
        self.assertEqual(value, 100.0)

    def test_parse_dimension_without_px(self):
        """Test parsing dimension without px suffix"""
        value, success = parse_dimension_from_px("100")
        self.assertTrue(success)
        self.assertEqual(value, 100.0)

    def test_parse_dimension_float(self):
        """Test parsing float dimension"""
        value, success = parse_dimension_from_px("100.5px")
        self.assertTrue(success)
        self.assertEqual(value, 100.5)

    def test_parse_dimension_invalid(self):
        """Test parsing invalid dimension"""
        value, success = parse_dimension_from_px("notanumber")
        self.assertFalse(success)
        self.assertIsNone(value)

    def test_parse_dimension_empty_string(self):
        """Test parsing empty string"""
        value, success = parse_dimension_from_px("")
        self.assertFalse(success)
        self.assertIsNone(value)


class BlockValidationTestCase(TestCase):
    """Test block number validation functions"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="pass123"
        )
        self.researcher = Researcher.objects.create(
            user=self.user, affiliation="Test Uni"
        )
        self.project = Project.objects.create(
            name="TestProject",
            description="Test",
            researcher=self.user,
            password="projpass",
            name_participants="TP",
        )
        self.cam = CAM.objects.create(user=self.user, project=self.project)

    def test_validate_block_number_new_block(self):
        """Test validation passes for new block numbers"""
        is_valid, error = validate_block_number(self.cam, 1)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_validate_block_number_duplicate(self):
        """Test validation fails for duplicate block numbers"""
        Block.objects.create(
            title="Block1",
            num=1,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
        )

        is_valid, error = validate_block_number(self.cam, 1)
        self.assertFalse(is_valid)
        self.assertIn("already exists", error)

    def test_validate_block_number_float_and_int(self):
        """Test validation handles both float and int block numbers"""
        Block.objects.create(
            title="Block1",
            num=1.0,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
        )

        # Should fail validation with both int and float
        is_valid, error = validate_block_number(self.cam, 1)
        self.assertFalse(is_valid)

        is_valid, error = validate_block_number(self.cam, 1.0)
        self.assertFalse(is_valid)

    def test_validate_block_number_exists_found(self):
        """Test validation finds existing block"""
        Block.objects.create(
            title="Block1",
            num=1,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
        )

        is_valid, error = validate_block_number_exists(self.cam, 1)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_validate_block_number_exists_not_found(self):
        """Test validation fails when block doesn't exist"""
        is_valid, error = validate_block_number_exists(self.cam, 999)
        self.assertFalse(is_valid)
        self.assertIn("does not exist", error)

    def test_validate_block_number_exists_string_input(self):
        """Test validation with string input"""
        Block.objects.create(
            title="Block1",
            num=1.0,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
        )

        is_valid, error = validate_block_number_exists(self.cam, "1")
        self.assertTrue(is_valid)


class BlockCreationTestCase(TestCase):
    """Test block creation service"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="pass123"
        )
        self.researcher = Researcher.objects.create(
            user=self.user, affiliation="Test Uni"
        )
        self.project = Project.objects.create(
            name="TestProject",
            description="Test",
            researcher=self.user,
            password="projpass",
            name_participants="TP",
        )
        self.cam = CAM.objects.create(user=self.user, project=self.project)

    def test_create_block_success(self):
        """Test successful block creation"""
        block_data = {
            "title": "Test Block",
            "shape": "neutral",
            "num": 1,
            "x_pos": 100.0,
            "y_pos": 200.0,
            "width": 150,
            "height": 100,
        }

        block, success, error = create_block(self.cam, self.user, block_data)

        self.assertTrue(success)
        self.assertIsNotNone(block)
        self.assertEqual(block.title, "Test Block")
        self.assertEqual(block.num, 1)
        self.assertEqual(block.creator, self.user)

    def test_create_block_duplicate_number(self):
        """Test block creation fails with duplicate number"""
        Block.objects.create(
            title="Block1",
            num=1,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
        )

        block_data = {
            "title": "Duplicate Block",
            "shape": "neutral",
            "num": 1,
            "x_pos": 100.0,
            "y_pos": 200.0,
            "width": 150,
            "height": 100,
        }

        block, success, error = create_block(self.cam, self.user, block_data)

        self.assertFalse(success)
        self.assertIsNone(block)
        self.assertIn("already exists", error)

    def test_create_block_with_comment(self):
        """Test block creation with comment"""
        block_data = {
            "title": "Block with Comment",
            "shape": "positive",
            "num": 2,
            "x_pos": 0.0,
            "y_pos": 0.0,
            "width": 150,
            "height": 100,
            "comment": "This is a test comment",
        }

        block, success, error = create_block(self.cam, self.user, block_data)

        self.assertTrue(success)
        self.assertEqual(block.comment, "This is a test comment")


class BlockUpdateTestCase(TestCase):
    """Test block update service"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="pass123"
        )
        self.researcher = Researcher.objects.create(
            user=self.user, affiliation="Test Uni"
        )
        self.project = Project.objects.create(
            name="TestProject",
            description="Test",
            researcher=self.user,
            password="projpass",
            name_participants="TP",
        )
        self.cam = CAM.objects.create(user=self.user, project=self.project)
        self.block = Block.objects.create(
            title="Original Block",
            num=1,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
            x_pos=100.0,
            y_pos=100.0,
            width=150,
            height=100,
        )

    def test_update_block_title(self):
        """Test updating block title"""
        block_data = {"title": "Updated Title"}

        block, success, error = update_block_data(self.block, block_data)

        self.assertTrue(success)
        self.assertEqual(block.title, "Updated Title")

    def test_update_block_position_with_px(self):
        """Test updating block position from string with px"""
        block_data = {
            "x_pos": "200.0px",
            "y_pos": "300.0px",
        }

        block, success, error = update_block_data(self.block, block_data)

        self.assertTrue(success)
        self.assertEqual(block.x_pos, 200.0)
        self.assertEqual(block.y_pos, 300.0)

    def test_update_block_dimensions(self):
        """Test updating block dimensions"""
        block_data = {
            "width": "200px",
            "height": "150px",
        }

        block, success, error = update_block_data(self.block, block_data)

        self.assertTrue(success)
        self.assertEqual(block.width, 200.0)
        self.assertEqual(block.height, 150.0)

    def test_update_block_comment_with_newlines(self):
        """Test updating block comment and stripping newlines"""
        block_data = {
            "comment": "Line 1\nLine 2\nLine 3\n",
        }

        block, success, error = update_block_data(self.block, block_data)

        self.assertTrue(success)
        self.assertEqual(block.comment, "Line 1\nLine 2\nLine 3")

    def test_update_block_shape(self):
        """Test updating block shape"""
        block_data = {"shape": "positive strong"}

        block, success, error = update_block_data(self.block, block_data)

        self.assertTrue(success)
        self.assertEqual(block.shape, "positive strong")


class BlockResizeTestCase(TestCase):
    """Test block resizing service"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="pass123"
        )
        self.researcher = Researcher.objects.create(
            user=self.user, affiliation="Test Uni"
        )
        self.project = Project.objects.create(
            name="TestProject",
            description="Test",
            researcher=self.user,
            password="projpass",
            name_participants="TP",
        )
        self.cam = CAM.objects.create(user=self.user, project=self.project)
        self.block = Block.objects.create(
            title="Block",
            num=1,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
            width=150,
            height=100,
        )

    def test_resize_block_width(self):
        """Test resizing block width"""
        block, success, message = resize_block_dimensions(self.block, width="200px")

        self.assertTrue(success)
        self.assertEqual(block.width, 200.0)

    def test_resize_block_height(self):
        """Test resizing block height"""
        block, success, message = resize_block_dimensions(self.block, height="150px")

        self.assertTrue(success)
        self.assertEqual(block.height, 150.0)

    def test_resize_block_both_dimensions(self):
        """Test resizing both dimensions"""
        block, success, message = resize_block_dimensions(self.block, "250px", "180px")

        self.assertTrue(success)
        self.assertEqual(block.width, 250.0)
        self.assertEqual(block.height, 180.0)

    def test_resize_block_invalid_dimension(self):
        """Test resizing with invalid dimension - silently ignores invalid values"""
        # The service silently ignores invalid dimensions and returns success
        block, success, message = resize_block_dimensions(
            self.block, width="notanumber"
        )

        # Even with invalid input, it returns success (doesn't update anything)
        self.assertTrue(success)
        # Width should remain unchanged
        self.assertEqual(block.width, 150)


class ResizablePropertyTestCase(TestCase):
    """Test setting resizable property for all blocks"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="pass123"
        )
        self.researcher = Researcher.objects.create(
            user=self.user, affiliation="Test Uni"
        )
        self.project = Project.objects.create(
            name="TestProject",
            description="Test",
            researcher=self.user,
            password="projpass",
            name_participants="TP",
        )
        self.cam = CAM.objects.create(user=self.user, project=self.project)

        # Create multiple blocks
        for i in range(3):
            Block.objects.create(
                title=f"Block {i}",
                num=i,
                creator=self.user,
                shape="neutral",
                CAM=self.cam,
                resizable=False,
            )

    def test_set_all_blocks_resizable_true(self):
        """Test setting all blocks to resizable"""
        count, success, message = set_all_blocks_resizable(self.cam, True)

        self.assertTrue(success)
        self.assertEqual(count, 3)

        # Verify all blocks are resizable
        for block in self.cam.block_set.all():
            self.assertTrue(block.resizable)

    def test_set_all_blocks_resizable_false(self):
        """Test setting all blocks to non-resizable"""
        # First make them resizable
        self.cam.block_set.all().update(resizable=True)

        count, success, message = set_all_blocks_resizable(self.cam, False)

        self.assertTrue(success)
        self.assertEqual(count, 3)

        # Verify all blocks are not resizable
        for block in self.cam.block_set.all():
            self.assertFalse(block.resizable)


class TextScaleTestCase(TestCase):
    """Test text scale update service"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="pass123"
        )
        self.researcher = Researcher.objects.create(
            user=self.user, affiliation="Test Uni"
        )
        self.project = Project.objects.create(
            name="TestProject",
            description="Test",
            researcher=self.user,
            password="projpass",
            name_participants="TP",
        )
        self.cam = CAM.objects.create(user=self.user, project=self.project)
        self.block = Block.objects.create(
            title="Block",
            num=1,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
            text_scale=14,
        )

    def test_update_text_scale_valid(self):
        """Test updating text scale with valid value"""
        block, success, message = update_block_text_scale(self.block, "18")

        self.assertTrue(success)
        self.assertEqual(block.text_scale, 18.0)

    def test_update_text_scale_float(self):
        """Test updating text scale with float value"""
        block, success, message = update_block_text_scale(self.block, "16.5")

        self.assertTrue(success)
        self.assertEqual(block.text_scale, 16.5)

    def test_update_text_scale_invalid_defaults(self):
        """Test invalid text scale defaults to 14"""
        block, success, message = update_block_text_scale(self.block, "notanumber")

        self.assertTrue(success)
        self.assertEqual(block.text_scale, 14)


class BlockDeletionTestCase(TestCase):
    """Test block deletion with logging"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="pass123"
        )
        self.researcher = Researcher.objects.create(
            user=self.user, affiliation="Test Uni"
        )
        self.project = Project.objects.create(
            name="TestProject",
            description="Test",
            researcher=self.user,
            password="projpass",
            name_participants="TP",
        )
        self.cam = CAM.objects.create(user=self.user, project=self.project)

    def test_delete_block_without_links(self):
        """Test deleting a block with no links"""
        block = Block.objects.create(
            title="Block",
            num=1,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
        )

        deleted_links, success, error = delete_block_with_logging(self.cam, block)

        self.assertTrue(success)
        self.assertEqual(deleted_links, [])
        self.assertFalse(Block.objects.filter(id=block.id).exists())

    def test_delete_block_with_links(self):
        """Test deleting a block with associated links"""
        block1 = Block.objects.create(
            title="Block 1",
            num=1,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
        )
        block2 = Block.objects.create(
            title="Block 2",
            num=2,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
        )

        link = Link.objects.create(
            starting_block=block1,
            ending_block=block2,
            creator=self.user,
            CAM=self.cam,
        )

        deleted_links, success, error = delete_block_with_logging(self.cam, block1)

        self.assertTrue(success)
        self.assertEqual(len(deleted_links), 1)
        self.assertFalse(Block.objects.filter(id=block1.id).exists())
        self.assertFalse(Link.objects.filter(id=link.id).exists())

    def test_delete_block_with_multiple_links(self):
        """Test deleting a block involved in multiple links"""
        block1 = Block.objects.create(
            title="Block 1", num=1, creator=self.user, shape="neutral", CAM=self.cam
        )
        block2 = Block.objects.create(
            title="Block 2", num=2, creator=self.user, shape="neutral", CAM=self.cam
        )
        block3 = Block.objects.create(
            title="Block 3", num=3, creator=self.user, shape="neutral", CAM=self.cam
        )

        link1 = Link.objects.create(
            starting_block=block1, ending_block=block2, creator=self.user, CAM=self.cam
        )
        link2 = Link.objects.create(
            starting_block=block3, ending_block=block1, creator=self.user, CAM=self.cam
        )

        deleted_links, success, error = delete_block_with_logging(self.cam, block1)

        self.assertTrue(success)
        self.assertEqual(len(deleted_links), 2)
        self.assertFalse(Link.objects.filter(id=link1.id).exists())
        self.assertFalse(Link.objects.filter(id=link2.id).exists())

    def test_delete_block_non_modifiable(self):
        """Test that non-modifiable blocks cannot be deleted"""
        block = Block.objects.create(
            title="Non-modifiable Block",
            num=1,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
            modifiable=False,
        )

        deleted_links, success, error = delete_block_with_logging(self.cam, block)

        self.assertFalse(success)
        self.assertEqual(error, "This block cannot be deleted")
        self.assertEqual(deleted_links, [])
        # Block should still exist
        self.assertTrue(Block.objects.filter(id=block.id).exists())


class BlockPositionTestCase(TestCase):
    """Test block position update service"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="pass123"
        )
        self.researcher = Researcher.objects.create(
            user=self.user, affiliation="Test Uni"
        )
        self.project = Project.objects.create(
            name="TestProject",
            description="Test",
            researcher=self.user,
            password="projpass",
            name_participants="TP",
        )
        self.cam = CAM.objects.create(user=self.user, project=self.project)
        self.block = Block.objects.create(
            title="Block",
            num=1,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
            x_pos=100.0,
            y_pos=100.0,
            width=150,
            height=100,
        )

    def test_update_block_position(self):
        """Test updating block position"""
        block, success, error = update_block_position(self.block, "200.0px", "300.0px")

        self.assertTrue(success)
        self.assertEqual(block.x_pos, 200.0)
        self.assertEqual(block.y_pos, 300.0)

    def test_update_block_position_with_dimensions(self):
        """Test updating position and dimensions"""
        block, success, error = update_block_position(
            self.block, "200px", "300px", "200px", "150px"
        )

        self.assertTrue(success)
        self.assertEqual(block.x_pos, 200.0)
        self.assertEqual(block.y_pos, 300.0)
        self.assertEqual(block.width, 200.0)
        self.assertEqual(block.height, 150.0)

    def test_update_block_position_with_text_scale(self):
        """Test updating position and text scale"""
        block, success, error = update_block_position(
            self.block, "200px", "300px", text_scale="18"
        )

        self.assertTrue(success)
        self.assertEqual(block.x_pos, 200.0)
        self.assertEqual(block.y_pos, 300.0)
        self.assertEqual(block.text_scale, 18.0)

    def test_update_block_position_invalid_position(self):
        """Test updating with invalid position"""
        block, success, error = update_block_position(self.block, "invalid", "300px")

        self.assertFalse(success)


class LinksDataTestCase(TestCase):
    """Test getting links data for blocks"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="pass123"
        )
        self.researcher = Researcher.objects.create(
            user=self.user, affiliation="Test Uni"
        )
        self.project = Project.objects.create(
            name="TestProject",
            description="Test",
            researcher=self.user,
            password="projpass",
            name_participants="TP",
        )
        self.cam = CAM.objects.create(user=self.user, project=self.project)
        self.block1 = Block.objects.create(
            title="Block 1",
            num=1,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
            x_pos=100.0,
            y_pos=100.0,
        )
        self.block2 = Block.objects.create(
            title="Block 2",
            num=2,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
            x_pos=200.0,
            y_pos=200.0,
        )

    def test_get_links_for_block_no_links(self):
        """Test getting links for block with no links"""
        links = get_links_for_block(self.cam, self.block1)
        self.assertEqual(links.count(), 0)

    def test_get_links_for_block_with_links(self):
        """Test getting links for block with associated links"""
        Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
        )

        links = get_links_for_block(self.cam, self.block1)
        self.assertEqual(links.count(), 1)

    def test_get_links_data_for_block(self):
        """Test getting formatted links data"""
        link = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
            line_style="dashed",
        )

        link_data = get_links_data_for_block(self.cam, self.block1)

        self.assertEqual(len(link_data["id"]), 1)
        self.assertEqual(link_data["id"][0], link.id)
        self.assertEqual(link_data["start_x"][0], 100.0)
        self.assertEqual(link_data["start_y"][0], 100.0)
        self.assertEqual(link_data["end_x"][0], 200.0)
        self.assertEqual(link_data["end_y"][0], 200.0)
        self.assertEqual(link_data["starting_block"][0], 1)
        self.assertEqual(link_data["ending_block"][0], 2)
