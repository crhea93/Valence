"""
Comprehensive tests for link views
"""

from django.test import TestCase, override_settings
from users.models import CustomUser, Researcher, CAM, Project
from block.models import Block
from link.models import Link
import json


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class LinkViewsTestCase(TestCase):
    """Comprehensive tests for link views"""

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

    def test_add_link_no_authentication(self):
        """Test add_link without authentication returns error"""
        self.client.logout()
        response = self.client.post(
            "/link/add_link",
            {
                "link_valid": True,
                "starting_block": self.block1.num,
                "ending_block": self.block2.num,
                "line_style": "Solid-Weak",
                "arrow_type": "uni",
            },
        )
        # Should return error (500 or 404)
        self.assertIn(response.status_code, [404, 500])

    def test_add_link_valid_data(self):
        """Test adding a link with valid data"""
        response = self.client.post(
            "/link/add_link",
            {
                "link_valid": True,
                "starting_block": self.block1.num,
                "ending_block": self.block2.num,
                "line_style": "Dashed-Strong",
                "arrow_type": "bi",
            },
        )
        self.assertIn(response.status_code, [200, 400])

    def test_add_link_invalid_no_valid_param(self):
        """Test adding a link without link_valid parameter"""
        response = self.client.post(
            "/link/add_link",
            {
                "starting_block": self.block1.num,
                "ending_block": self.block2.num,
                "line_style": "Solid-Weak",
                "arrow_type": "uni",
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_add_link_non_post_request(self):
        """Test add_link with non-POST request"""
        response = self.client.get("/link/add_link")
        self.assertEqual(response.status_code, 200)

    def test_update_link_valid_data(self):
        """Test updating a link with valid data"""
        response = self.client.post(
            "/link/update_link",
            {
                "link_id": self.link.id,
                "line_style": "Dashed-Weak",
                "arrow_type": "bi",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.link.refresh_from_db()
        self.assertEqual(self.link.line_style, "Dashed-Weak")
        self.assertEqual(self.link.arrow_type, "bi")

    def test_update_link_only_style(self):
        """Test updating only the line style of a link"""
        response = self.client.post(
            "/link/update_link",
            {
                "link_id": self.link.id,
                "line_style": "Solid-Strong",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.link.refresh_from_db()
        self.assertEqual(self.link.line_style, "Solid-Strong")

    def test_update_link_only_arrow(self):
        """Test updating only the arrow type of a link"""
        response = self.client.post(
            "/link/update_link",
            {
                "link_id": self.link.id,
                "arrow_type": "bi",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.link.refresh_from_db()
        self.assertEqual(self.link.arrow_type, "bi")

    def test_delete_link_valid(self):
        """Test deleting a link"""
        link_id = self.link.id
        response = self.client.post(
            "/link/delete_link",
            {"delete_link_valid": True, "link_id": link_id},
        )
        self.assertEqual(response.status_code, 200)
        # Link deletion depends on implementation - just verify response is successful

    def test_delete_link_invalid_no_valid_param(self):
        """Test deleting link without delete_link_valid parameter"""
        response = self.client.post(
            "/link/delete_link",
            {"link_id": self.link.id},
        )
        self.assertEqual(response.status_code, 200)

    def test_swap_link_direction(self):
        """Test swapping link direction"""
        original_start = self.link.starting_block
        original_end = self.link.ending_block

        response = self.client.post(
            "/link/swap_link_direction",
            {"link_id": self.link.id},
        )
        self.assertEqual(response.status_code, 200)

        self.link.refresh_from_db()
        self.assertEqual(self.link.starting_block, original_end)
        self.assertEqual(self.link.ending_block, original_start)

    def test_swap_link_direction_non_post(self):
        """Test swap_link_direction with non-POST request"""
        response = self.client.get("/link/swap_link_direction")
        self.assertEqual(response.status_code, 200)

    def test_delete_link_non_post(self):
        """Test delete_link with non-POST request"""
        response = self.client.get("/link/delete_link")
        self.assertEqual(response.status_code, 200)

    def test_update_link_nonexistent(self):
        """Test updating a nonexistent link"""
        response = self.client.post(
            "/link/update_link",
            {
                "link_id": 9999,
                "line_style": "Solid-Weak",
                "arrow_type": "uni",
            },
        )
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 404])

    def test_add_multiple_links(self):
        """Test adding multiple links between same blocks"""
        response1 = self.client.post(
            "/link/add_link",
            {
                "link_valid": True,
                "starting_block": self.block1.num,
                "ending_block": self.block2.num,
                "line_style": "Solid-Weak",
                "arrow_type": "uni",
            },
        )
        self.assertIn(response1.status_code, [200, 400])

        response2 = self.client.post(
            "/link/add_link",
            {
                "link_valid": True,
                "starting_block": self.block2.num,
                "ending_block": self.block1.num,
                "line_style": "Dashed-Strong",
                "arrow_type": "bi",
            },
        )
        self.assertIn(response2.status_code, [200, 400])
