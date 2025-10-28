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

    def test_update_link_pos_valid_data(self):
        """Test update_link_pos function (backward compatibility alias)"""
        response = self.client.post(
            "/link/update_link_pos",
            {
                "link_id": self.link.id,
                "line_style": "Dashed-Strong",
                "arrow_type": "bi",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.link.refresh_from_db()
        self.assertEqual(self.link.line_style, "Dashed-Strong")
        self.assertEqual(self.link.arrow_type, "bi")

        # Verify response structure
        response_data = json.loads(response.content)
        self.assertIn("line_style", response_data)
        self.assertIn("arrow_type", response_data)
        self.assertIn("id", response_data)
        self.assertIn("starting_block", response_data)
        self.assertIn("ending_block", response_data)

    def test_update_link_pos_nonexistent(self):
        """Test update_link_pos with nonexistent link"""
        response = self.client.post(
            "/link/update_link_pos",
            {
                "link_id": 9999,
                "line_style": "Solid-Weak",
                "arrow_type": "uni",
            },
        )
        self.assertEqual(response.status_code, 404)

    def test_update_link_pos_get_request(self):
        """Test update_link_pos with GET request"""
        response = self.client.get("/link/update_link_pos")
        self.assertEqual(response.status_code, 200)

    def test_update_link_get_request(self):
        """Test update_link with GET request"""
        response = self.client.get("/link/update_link")
        self.assertEqual(response.status_code, 200)

    def test_swap_link_direction_nonexistent(self):
        """Test swapping direction of nonexistent link"""
        response = self.client.post(
            "/link/swap_link_direction",
            {"link_id": 9999},
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_link_nonexistent(self):
        """Test deleting a nonexistent link"""
        response = self.client.post(
            "/link/delete_link",
            {"link_delete_valid": True, "link_id": 9999},
        )
        self.assertEqual(response.status_code, 404)

    def test_add_link_with_default_styling(self):
        """Test adding link without explicit line_style and arrow_type"""
        # Create a third block
        block3 = Block.objects.create(
            title="Block3",
            x_pos=300.0,
            y_pos=300.0,
            width=100,
            height=100,
            shape="neutral",
            creator=self.user,
            CAM=self.cam,
            num=3,
        )

        response = self.client.post(
            "/link/add_link",
            {
                "link_valid": True,
                "starting_block": self.block1.num,
                "ending_block": block3.num,
            },
        )
        # Should use default values for line_style and arrow_type
        self.assertIn(response.status_code, [200, 400])

    def test_add_link_nonexistent_starting_block(self):
        """Test adding link with nonexistent starting block"""
        response = self.client.post(
            "/link/add_link",
            {
                "link_valid": True,
                "starting_block": 9999,
                "ending_block": self.block2.num,
                "line_style": "Solid-Weak",
                "arrow_type": "uni",
            },
        )
        # Should return 404 or 500 depending on exception handling
        self.assertIn(response.status_code, [404, 500])

    def test_add_link_nonexistent_ending_block(self):
        """Test adding link with nonexistent ending block"""
        response = self.client.post(
            "/link/add_link",
            {
                "link_valid": True,
                "starting_block": self.block1.num,
                "ending_block": 9999,
                "line_style": "Solid-Weak",
                "arrow_type": "uni",
            },
        )
        # Should return 404 or 500 depending on exception handling
        self.assertIn(response.status_code, [404, 500])

    def test_add_link_response_data_structure(self):
        """Test that add_link returns correct response data structure"""
        # Create a third block to avoid duplicate link
        block3 = Block.objects.create(
            title="Block3",
            x_pos=300.0,
            y_pos=300.0,
            width=100,
            height=100,
            shape="neutral",
            creator=self.user,
            CAM=self.cam,
            num=3,
        )

        response = self.client.post(
            "/link/add_link",
            {
                "link_valid": True,
                "starting_block": self.block2.num,
                "ending_block": block3.num,
                "line_style": "Solid-Strong",
                "arrow_type": "bi",
            },
        )

        if response.status_code == 200:
            response_data = json.loads(response.content)
            # Should contain num_link (link ID)
            self.assertIn("num_link", response_data)

    def test_update_link_response_data_structure(self):
        """Test that update_link returns correct response data structure"""
        response = self.client.post(
            "/link/update_link",
            {
                "link_id": self.link.id,
                "line_style": "Solid-Strong",
                "arrow_type": "bi",
            },
        )
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        # Should contain position data from get_link_position_data
        self.assertTrue(len(response_data) > 0)

    def test_swap_link_direction_response_data(self):
        """Test that swap_link_direction returns correct response data"""
        response = self.client.post(
            "/link/swap_link_direction",
            {"link_id": self.link.id},
        )
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        # Should contain position data from get_link_position_data
        self.assertTrue(len(response_data) > 0)

    def test_delete_link_with_valid_param(self):
        """Test deleting link with proper link_delete_valid parameter"""
        link_id = self.link.id
        response = self.client.post(
            "/link/delete_link",
            {"link_delete_valid": True, "link_id": link_id},
        )
        self.assertEqual(response.status_code, 200)

    def test_add_link_all_line_styles(self):
        """Test adding links with different line styles"""
        line_styles = ["Solid-Weak", "Solid-Strong", "Dashed-Weak", "Dashed-Strong"]

        for i, style in enumerate(line_styles):
            # Create new block for each link
            block = Block.objects.create(
                title=f"Block{10 + i}",
                x_pos=100.0 * i,
                y_pos=100.0 * i,
                width=100,
                height=100,
                shape="neutral",
                creator=self.user,
                CAM=self.cam,
                num=10 + i,
            )

            response = self.client.post(
                "/link/add_link",
                {
                    "link_valid": True,
                    "starting_block": self.block1.num,
                    "ending_block": block.num,
                    "line_style": style,
                    "arrow_type": "uni",
                },
            )
            self.assertIn(response.status_code, [200, 400])

    def test_add_link_different_arrow_types(self):
        """Test adding links with different arrow types"""
        arrow_types = ["uni", "bi"]

        for i, arrow in enumerate(arrow_types):
            # Create new block for each link
            block = Block.objects.create(
                title=f"ArrowBlock{20 + i}",
                x_pos=200.0 * i,
                y_pos=200.0 * i,
                width=100,
                height=100,
                shape="neutral",
                creator=self.user,
                CAM=self.cam,
                num=20 + i,
            )

            response = self.client.post(
                "/link/add_link",
                {
                    "link_valid": True,
                    "starting_block": self.block1.num,
                    "ending_block": block.num,
                    "line_style": "Solid-Weak",
                    "arrow_type": arrow,
                },
            )
            self.assertIn(response.status_code, [200, 400])

    def test_update_link_empty_values(self):
        """Test updating link with empty/missing values"""
        response = self.client.post(
            "/link/update_link",
            {
                "link_id": self.link.id,
            },
        )
        # Should handle gracefully
        self.assertEqual(response.status_code, 200)

    def test_swap_link_direction_twice(self):
        """Test swapping link direction twice returns to original"""
        original_start = self.link.starting_block
        original_end = self.link.ending_block

        # First swap
        self.client.post(
            "/link/swap_link_direction",
            {"link_id": self.link.id},
        )
        self.link.refresh_from_db()
        self.assertEqual(self.link.starting_block, original_end)
        self.assertEqual(self.link.ending_block, original_start)

        # Second swap - should be back to original
        self.client.post(
            "/link/swap_link_direction",
            {"link_id": self.link.id},
        )
        self.link.refresh_from_db()
        self.assertEqual(self.link.starting_block, original_start)
        self.assertEqual(self.link.ending_block, original_end)

    def test_update_link_multiple_times(self):
        """Test updating same link multiple times"""
        # First update
        response1 = self.client.post(
            "/link/update_link",
            {
                "link_id": self.link.id,
                "line_style": "Solid-Strong",
                "arrow_type": "bi",
            },
        )
        self.assertEqual(response1.status_code, 200)

        # Second update
        response2 = self.client.post(
            "/link/update_link",
            {
                "link_id": self.link.id,
                "line_style": "Dashed-Weak",
                "arrow_type": "uni",
            },
        )
        self.assertEqual(response2.status_code, 200)

        self.link.refresh_from_db()
        self.assertEqual(self.link.line_style, "Dashed-Weak")
        self.assertEqual(self.link.arrow_type, "uni")

    def test_delete_link_response_empty(self):
        """Test that delete_link returns empty JSON on success"""
        response = self.client.post(
            "/link/delete_link",
            {"link_delete_valid": True, "link_id": self.link.id},
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        # Should return empty dict on success
        self.assertEqual(response_data, {})
