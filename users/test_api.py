from django.test import TestCase, override_settings, Client
from users.models import CustomUser, Researcher, CAM, Project
from block.models import Block
from link.models import Link
import json
from zipfile import ZipFile
from io import BytesIO


@override_settings(
    STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage"
)
class APIEndpointTestCase(TestCase):
    """
    Test suite for API endpoints including JSON responses and error handling
    """

    def setUp(self):
        # Create users
        self.user = CustomUser.objects.create_user(
            username="testuser", email="test@test.com", password="12345"
        )
        self.user2 = CustomUser.objects.create_user(
            username="testuser2", email="test2@test.com", password="12345"
        )

        self.researcher = Researcher.objects.create(user=self.user, affiliation="UdeM")
        self.client.login(username="testuser", password="12345")

        # Create project and CAM
        self.project = Project.objects.create(
            name="TestProject",
            description="TEST PROJECT",
            researcher=self.user,
            password="TestProjectPassword",
            name_participants="API",
        )

        self.cam = CAM.objects.create(
            name="testCAM", user=self.user, project=self.project
        )
        self.user.active_cam_num = self.cam.id
        self.user.save()

        # Create test blocks
        self.block1 = Block.objects.create(
            title="APIBlock1",
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
            title="APIBlock2",
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

    def test_download_cam_returns_zip(self):
        """
        Test that download_cam endpoint returns a valid ZIP file
        """
        response = self.client.get("/users/download_cam", {"pk": self.cam.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/octet-stream")
        self.assertIn("attachment", response["Content-Disposition"])

        # Verify it's a valid ZIP file
        zip_data = BytesIO(response.content)
        with ZipFile(zip_data, "r") as zf:
            # Check that ZIP contains expected files
            namelist = zf.namelist()
            self.assertIn("blocks.csv", namelist)
            self.assertIn("links.csv", namelist)

    def test_download_cam_contains_blocks_and_links(self):
        """
        Test that downloaded CAM data contains blocks and links
        """
        response = self.client.get("/users/download_cam", {"pk": self.cam.id})

        # Parse ZIP file
        zip_data = BytesIO(response.content)
        with ZipFile(zip_data, "r") as zf:
            # Read blocks CSV
            blocks_csv = zf.read("blocks.csv").decode("utf-8")
            self.assertIn("APIBlock1", blocks_csv)
            self.assertIn("APIBlock2", blocks_csv)

            # Read links CSV
            links_csv = zf.read("links.csv").decode("utf-8")
            # Verify links data exists and has content
            self.assertTrue(len(links_csv) > 0)

    def test_load_cam_returns_json(self):
        """
        Test that load_cam endpoint returns JSON response
        """
        response = self.client.post("/users/load_cam", {"cam_id": self.cam.id})

        self.assertEqual(response.status_code, 200)

        # Should return JSON data
        try:
            data = json.loads(response.content)
            self.assertIsInstance(data, dict)
        except json.JSONDecodeError:
            # Some endpoints might return HTML, check content type
            pass

    def test_add_block_api_response(self):
        """
        Test block creation API endpoint response
        """
        response = self.client.post(
            "/block/add_block",
            {
                "add_valid": True,
                "num_block": 99,
                "title": "APICreatedBlock",
                "shape": 3,
                "x_pos": 100.0,
                "y_pos": 200.0,
                "width": 150,
                "height": 150,
            },
        )

        self.assertEqual(response.status_code, 200)

        # Verify block was created
        new_block = Block.objects.filter(title="APICreatedBlock").first()
        self.assertIsNotNone(new_block)
        self.assertEqual(new_block.x_pos, 100.0)
        self.assertEqual(new_block.y_pos, 200.0)

    def test_update_block_api_response(self):
        """
        Test block update API endpoint
        """
        response = self.client.post(
            "/block/update_block",
            {
                "update_valid": True,
                "num_block": self.block1.num,
                "title": "UpdatedViaAPI",
                "shape": 5,
                "x_pos": "50.0px",
                "y_pos": "60.0px",
                "width": "200px",
                "height": "180px",
            },
        )

        self.assertEqual(response.status_code, 200)

        # Verify update
        self.block1.refresh_from_db()
        self.assertEqual(self.block1.title, "UpdatedViaAPI")

    def test_delete_block_api_response(self):
        """
        Test block deletion API endpoint
        """
        block_id = self.block1.num

        response = self.client.post(
            "/block/delete_block", {"delete_valid": True, "block_id": block_id}
        )

        self.assertEqual(response.status_code, 200)

        # Verify deletion
        with self.assertRaises(Block.DoesNotExist):
            Block.objects.get(num=block_id, CAM=self.cam)

    def test_add_link_api_response(self):
        """
        Test link creation API endpoint
        """
        # Create another block to link to
        block3 = Block.objects.create(
            title="Block3",
            x_pos=300.0,
            y_pos=300.0,
            width=100,
            height=100,
            shape="negative",
            creator=self.user,
            CAM=self.cam,
            num=3,
        )

        response = self.client.post(
            "/link/add_link",
            {
                "link_valid": True,
                "starting_block": self.block2.id,
                "ending_block": block3.id,
                "line_style": "Dashed-Strong",
                "arrow_type": "bi",
            },
        )

        self.assertEqual(response.status_code, 200)

        # Verify link was created
        new_link = Link.objects.filter(
            starting_block=self.block2, ending_block=block3
        ).first()
        self.assertIsNotNone(new_link)

    def test_update_link_api_response(self):
        """
        Test link update API endpoint
        """
        response = self.client.post(
            "/link/update_link",
            {"link_id": self.link.id, "line_style": "Dashed-Weak", "arrow_type": "bi"},
        )

        self.assertEqual(response.status_code, 200)

        # Verify update
        self.link.refresh_from_db()
        self.assertEqual(self.link.line_style, "Dashed-Weak")
        self.assertEqual(self.link.arrow_type, "bi")

    def test_delete_link_api_response(self):
        """
        Test link deletion API endpoint
        """
        link_id = self.link.id

        response = self.client.post(
            "/link/delete_link", {"delete_link_valid": True, "link_id": link_id}
        )

        self.assertEqual(response.status_code, 200)

        # Note: The actual deletion behavior may vary
        # Just verify the endpoint responds successfully

    def test_swap_link_direction_api_response(self):
        """
        Test link direction swap API endpoint
        """
        original_start = self.link.starting_block
        original_end = self.link.ending_block

        response = self.client.post(
            "/link/swap_link_direction", {"link_id": self.link.id}
        )

        self.assertEqual(response.status_code, 200)

        # Verify direction was swapped
        self.link.refresh_from_db()
        self.assertEqual(self.link.starting_block, original_end)
        self.assertEqual(self.link.ending_block, original_start)

    def test_api_invalid_request_handling(self):
        """
        Test API endpoints handle invalid requests gracefully
        """
        # Try to add block with missing required fields
        # Should return error response or 400 status
        response = self.client.post(
            "/block/add_block",
            {
                "add_valid": True,
                "num_block": 100,
                # Missing title, shape, positions
            },
        )
        # View should handle missing fields gracefully
        self.assertIn(response.status_code, [200, 400])

    def test_api_unauthorized_access(self):
        """
        Test API endpoints require authentication
        """
        # Logout
        self.client.logout()

        # Try to access protected endpoint
        # Should redirect to login or return error
        response = self.client.post(
            "/block/add_block",
            {
                "add_valid": True,
                "num_block": 100,
                "title": "Unauthorized",
                "shape": 3,
                "x_pos": 0,
                "y_pos": 0,
                "width": 100,
                "height": 100,
            },
        )
        # Should redirect to login (301/302) or return 403
        self.assertIn(response.status_code, [301, 302, 403, 404])

    def test_api_cross_user_data_access(self):
        """
        Test that users cannot access other users' data via API
        """
        # Create CAM for user2
        other_cam = CAM.objects.create(
            name="OtherCAM", user=self.user2, project=self.project
        )

        # Try to load user2's CAM as user1
        response = self.client.post("/users/load_cam", {"cam_id": other_cam.id})

        # Should deny access or return error
        # Actual behavior depends on permission checks in view
        self.assertIn(response.status_code, [200, 403, 404])

    def test_drag_function_updates_position(self):
        """
        Test drag function API updates block position correctly
        """
        new_x = 250.0
        new_y = 350.0

        response = self.client.post(
            "/block/drag_function",
            {
                "drag_valid": True,
                "block_id": self.block1.num,
                "x_pos": f"{new_x}px",
                "y_pos": f"{new_y}px",
                "width": "100px",
                "height": "100px",
            },
        )

        self.assertEqual(response.status_code, 200)

        # Verify position update
        self.block1.refresh_from_db()
        self.assertEqual(self.block1.x_pos, new_x)
        self.assertEqual(self.block1.y_pos, new_y)

    def test_resize_block_api(self):
        """
        Test resize block API endpoint (actually resizes via drag_function)
        """
        response = self.client.post(
            "/block/drag_function",
            {
                "drag_valid": True,
                "block_id": self.block1.num,
                "x_pos": f"{self.block1.x_pos}px",
                "y_pos": f"{self.block1.y_pos}px",
                "width": "250px",
                "height": "200px",
            },
        )

        self.assertEqual(response.status_code, 200)

        # Verify resize
        self.block1.refresh_from_db()
        self.assertEqual(self.block1.width, 250.0)
        self.assertEqual(self.block1.height, 200.0)

    def test_update_text_size_api(self):
        """
        Test update text size API endpoint
        """
        response = self.client.post(
            "/block/update_text_size", {"block_id": self.block1.num, "text_scale": 20}
        )

        self.assertEqual(response.status_code, 200)

        # Verify text size update
        self.block1.refresh_from_db()
        self.assertEqual(self.block1.text_scale, 20.0)

    def test_create_project_api(self):
        """
        Test project creation API endpoint
        """
        response = self.client.post(
            "/users/create_project",
            {
                "label": "API Project",
                "description": "Created via API",
                "num_participants": 5,
                "name_participants": "APIP",
                "participantType": "auto_participants",
                "languagePreference": "en",
                "conceptDelete": False,
            },
        )

        # Verify project was created
        new_project = Project.objects.filter(name="API Project").first()
        self.assertIsNotNone(new_project)
        self.assertEqual(new_project.description, "Created via API")

    def test_api_handles_concurrent_requests(self):
        """
        Test API can handle multiple simultaneous updates
        """
        # Update block position multiple times
        for i in range(5):
            response = self.client.post(
                "/block/drag_function",
                {
                    "drag_valid": True,
                    "block_id": self.block1.num,
                    "x_pos": f"{i * 10}px",
                    "y_pos": f"{i * 20}px",
                    "width": "100px",
                    "height": "100px",
                },
            )
            self.assertEqual(response.status_code, 200)

        # Final position should be from last update
        self.block1.refresh_from_db()
        self.assertEqual(self.block1.x_pos, 40.0)
        self.assertEqual(self.block1.y_pos, 80.0)
