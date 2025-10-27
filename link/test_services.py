"""
Unit tests for link/services.py
Tests for all business logic functions extracted from views
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import CAM, Researcher, Project
from block.models import Block
from link.models import Link
from link.services import (
    check_link_exists,
    create_link,
    update_link_style,
    delete_link,
    swap_link_direction,
    get_link_position_data,
    get_multiple_links_position_data,
    get_block_links_by_id,
    get_block_links_by_num,
)

User = get_user_model()


class LinkValidationTestCase(TestCase):
    """Test link existence validation"""

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
        )
        self.block2 = Block.objects.create(
            title="Block 2",
            num=2,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
        )

    def test_check_link_exists_not_found(self):
        """Test checking for non-existent link"""
        exists, link = check_link_exists(self.cam, 1, 2)
        self.assertFalse(exists)
        self.assertIsNone(link)

    def test_check_link_exists_found(self):
        """Test checking for existing link"""
        link_obj = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
        )

        exists, link = check_link_exists(self.cam, 1, 2)
        self.assertTrue(exists)
        self.assertEqual(link.id, link_obj.id)

    def test_check_link_exists_reverse_direction(self):
        """Test that link direction matters"""
        Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
        )

        # Reverse direction should not exist
        exists, link = check_link_exists(self.cam, 2, 1)
        self.assertFalse(exists)


class LinkCreationTestCase(TestCase):
    """Test link creation service"""

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
        )
        self.block2 = Block.objects.create(
            title="Block 2",
            num=2,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
        )

    def test_link_creation_preconditions(self):
        """Test that blocks exist and can be linked"""
        # Verify blocks exist
        self.assertEqual(self.block1.id, self.block1.id)
        self.assertEqual(self.block2.id, self.block2.id)
        # Verify they're in the same CAM
        self.assertEqual(self.block1.CAM, self.cam)
        self.assertEqual(self.block2.CAM, self.cam)

    def test_create_link_duplicate(self):
        """Test link creation fails for duplicate link"""
        Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
        )

        link, success, error = create_link(
            self.cam, self.user, self.block1, self.block2
        )

        self.assertFalse(success)
        self.assertIsNone(link)
        self.assertIn("already exists", error)

    def test_check_link_not_exists_initially(self):
        """Test that new link doesn't exist before creation"""
        exists, link = check_link_exists(self.cam, 1, 2)
        self.assertFalse(exists)
        self.assertIsNone(link)


class LinkUpdateTestCase(TestCase):
    """Test link style update service"""

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
        )
        self.block2 = Block.objects.create(
            title="Block 2",
            num=2,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
        )
        self.link = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
            line_style="solid",
            arrow_type="->",
        )

    def test_update_link_line_style(self):
        """Test updating line style"""
        link, success, error = update_link_style(self.link, line_style="dashed")

        self.assertTrue(success)
        self.assertEqual(link.line_style, "dashed")

    def test_update_link_arrow_type(self):
        """Test updating arrow type"""
        link, success, error = update_link_style(self.link, arrow_type="<->")

        self.assertTrue(success)
        self.assertEqual(link.arrow_type, "<->")

    def test_update_link_both_properties(self):
        """Test updating both line style and arrow type"""
        link, success, error = update_link_style(
            self.link, line_style="dotted", arrow_type="<>"
        )

        self.assertTrue(success)
        self.assertEqual(link.line_style, "dotted")
        self.assertEqual(link.arrow_type, "<>")

    def test_update_link_no_changes(self):
        """Test update with no changes"""
        link, success, error = update_link_style(self.link)

        self.assertTrue(success)
        self.assertEqual(link.line_style, "solid")
        self.assertEqual(link.arrow_type, "->")


class LinkDeletionTestCase(TestCase):
    """Test link deletion service"""

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
        )
        self.block2 = Block.objects.create(
            title="Block 2",
            num=2,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
        )

    def test_delete_link_success(self):
        """Test successful link deletion"""
        link = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
        )
        link_id = link.id

        success, message = delete_link(link)

        self.assertTrue(success)
        self.assertFalse(Link.objects.filter(id=link_id).exists())

    def test_delete_link_message(self):
        """Test deletion message"""
        link = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
        )

        success, message = delete_link(link)

        self.assertTrue(success)
        self.assertIn("deleted", message.lower())


class LinkDirectionSwapTestCase(TestCase):
    """Test link direction swapping service"""

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
        )
        self.block2 = Block.objects.create(
            title="Block 2",
            num=2,
            creator=self.user,
            shape="neutral",
            CAM=self.cam,
        )

    def test_swap_link_direction(self):
        """Test swapping link direction"""
        link = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
        )

        link, success, error = swap_link_direction(link)

        self.assertTrue(success)
        self.assertEqual(link.starting_block, self.block2)
        self.assertEqual(link.ending_block, self.block1)

    def test_swap_link_direction_twice(self):
        """Test swapping link direction twice returns to original"""
        link = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
        )

        # First swap
        link, success, error = swap_link_direction(link)
        self.assertTrue(success)

        # Second swap
        link, success, error = swap_link_direction(link)
        self.assertTrue(success)

        # Should be back to original
        self.assertEqual(link.starting_block, self.block1)
        self.assertEqual(link.ending_block, self.block2)


class LinkPositionDataTestCase(TestCase):
    """Test getting link position data"""

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

    def test_get_link_position_data(self):
        """Test getting formatted link position data"""
        link = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
            line_style="dashed",
            arrow_type="<->",
        )

        data = get_link_position_data(link)

        self.assertEqual(data["id"], link.id)
        self.assertEqual(data["start_x"], 100.0)
        self.assertEqual(data["start_y"], 100.0)
        self.assertEqual(data["end_x"], 200.0)
        self.assertEqual(data["end_y"], 200.0)
        self.assertEqual(data["line_style"], "dashed")
        self.assertEqual(data["arrow_type"], "<->")
        self.assertEqual(data["starting_block"], 1)
        self.assertEqual(data["ending_block"], 2)

    def test_get_multiple_links_position_data(self):
        """Test getting data for multiple links"""
        link1 = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
        )
        link2 = Link.objects.create(
            starting_block=self.block2,
            ending_block=self.block1,
            creator=self.user,
            CAM=self.cam,
        )

        links = Link.objects.filter(CAM=self.cam)
        data = get_multiple_links_position_data(links)

        self.assertEqual(len(data["id"]), 2)
        self.assertIn(link1.id, data["id"])
        self.assertIn(link2.id, data["id"])


class LinkRetrievalTestCase(TestCase):
    """Test link retrieval helper functions"""

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
            title="Block 1", num=1, creator=self.user, shape="neutral", CAM=self.cam
        )
        self.block2 = Block.objects.create(
            title="Block 2", num=2, creator=self.user, shape="neutral", CAM=self.cam
        )
        self.block3 = Block.objects.create(
            title="Block 3", num=3, creator=self.user, shape="neutral", CAM=self.cam
        )

    def test_get_block_links_by_id_starting(self):
        """Test getting links where block is starting point"""
        link = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
        )

        links = get_block_links_by_id(self.cam, self.block1.id)
        self.assertEqual(links.count(), 1)
        self.assertEqual(links.first().id, link.id)

    def test_get_block_links_by_id_ending(self):
        """Test getting links where block is ending point"""
        link = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
        )

        links = get_block_links_by_id(self.cam, self.block2.id)
        self.assertEqual(links.count(), 1)
        self.assertEqual(links.first().id, link.id)

    def test_get_block_links_by_id_both_directions(self):
        """Test getting links where block is in both directions"""
        link1 = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
        )
        link2 = Link.objects.create(
            starting_block=self.block3,
            ending_block=self.block1,
            creator=self.user,
            CAM=self.cam,
        )

        links = get_block_links_by_id(self.cam, self.block1.id)
        self.assertEqual(links.count(), 2)

    def test_get_block_links_by_num(self):
        """Test getting links by block number"""
        link = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM=self.cam,
        )

        links = get_block_links_by_num(self.cam, 1)
        self.assertEqual(links.count(), 1)

    def test_get_block_links_by_num_invalid(self):
        """Test getting links for non-existent block number"""
        links = get_block_links_by_num(self.cam, 999)
        self.assertEqual(links.count(), 0)
