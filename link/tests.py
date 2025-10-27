from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from users.models import CustomUser, CAM, Researcher, Project
from .models import Link
from block.models import Block
from django.forms.models import model_to_dict


# Create your tests here.
class LinkTestCase(TestCase):
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
            name_participants="LINK",
        )
        self.cam = CAM.objects.create(
            name="testCAM", user=self.user, project=self.project
        )
        self.user.active_cam_num = self.cam.id
        self.user.save()
        self.block1 = Block.objects.create(
            title="Meow1",
            x_pos=1.0,
            y_pos=1.0,
            height=100,
            width=100,
            creator=self.user,
            shape="negative",
            CAM_id=self.cam.id,
            num=1,
        )
        self.block2 = Block.objects.create(
            title="Meow2",
            x_pos=105.0,
            y_pos=105.0,
            height=100,
            width=100,
            creator=self.user,
            shape="positive",
            CAM_id=self.cam.id,
            num=2,
        )

    def test_create_link(self):
        """
        Test to create a simple link for user as part of their CAM
        """
        # Data to pass through to ajax call
        data = {
            "link_valid": True,
            "starting_block": self.block1.id,
            "ending_block": self.block2.id,
            "line_style": "Solid-Weak",
            "arrow_type": "uni",
        }
        response = self.client.post("/link/add_link", data)
        # Make sure the correct response is obtained
        self.assertTrue(response.status_code, 200)
        # Check that the new block was in fact created
        self.assertTrue("uni", [link.arrow_type for link in Link.objects.all()])
        link = Link.objects.filter(starting_block=self.block1.num).get(
            ending_block=self.block2.num
        )
        self.assertTrue(link)

    def test_update_link(self):
        """
        Test to update link
        """
        link_ = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM_id=self.cam.id,
        )
        data = {"link_id": link_.id, "line_style": "Dashed", "arrow_type": "uni"}
        response = self.client.post("/link/update_link", data)
        link_.refresh_from_db()
        update_true = {"line_style": "Dashed", "arrow_type": "uni"}
        update_actual = {"line_style": link_.line_style, "arrow_type": link_.arrow_type}
        self.assertDictEqual(update_true, update_actual)

    def test_swap_link_direction(self):
        """
        Test to swap the direction of a link
        """
        link_ = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM_id=self.cam.id,
            arrow_type="uni",
        )
        response = self.client.post("/link/swap_link_direction", {"link_id": link_.id})
        link_.refresh_from_db()
        # True order of links after swap
        true_order = {"starting_block": self.block2, "ending_block": self.block1}
        # Actual order of links after swap
        actual_order = {
            "starting_block": link_.starting_block,
            "ending_block": link_.ending_block,
        }
        # Check to make sure the orders are correct
        self.assertDictEqual(true_order, actual_order)

    def test_delete_link(self):
        """
        Test to delete link
        """
        link_ = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM_id=self.cam.id,
            arrow_type="uni",
        )
        response = self.client.post(
            "/link/delete_link", {"delete_link_valid": True, "link_id": link_.id}
        )
        self.assertTrue(response, 200)

    def test_update_link_position(self):
        """
        Test updating link position
        """
        link_ = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM_id=self.cam.id,
            arrow_type="uni",
        )

        # Update link position (this endpoint might store position data or update link properties)
        response = self.client.post(
            "/link/update_link_pos",
            {"link_id": link_.id, "position_data": "updated_position"},
        )

        self.assertEqual(response.status_code, 200)

    def test_link_model_update_method(self):
        """
        Test Link model's update method
        """
        link_ = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM_id=self.cam.id,
            arrow_type="uni",
            line_style="Solid-Weak",
        )

        # Test update method
        link_.update({"arrow_type": "bi", "line_style": "Dashed-Strong"})
        link_.refresh_from_db()

        self.assertEqual(link_.arrow_type, "bi")
        self.assertEqual(link_.line_style, "Dashed-Strong")

    def test_link_line_style_choices(self):
        """
        Test that links can be created with all valid line style choices
        """
        line_styles = [
            "Solid",
            "Solid-Strong",
            "Solid-Weak",
            "Dashed",
            "Dashed-Strong",
            "Dashed-Weak",
        ]

        for idx, line_style in enumerate(line_styles):
            link = Link.objects.create(
                starting_block=self.block1,
                ending_block=self.block2,
                creator=self.user,
                CAM_id=self.cam.id,
                line_style=line_style,
                num=idx + 10,
            )
            self.assertEqual(link.line_style, line_style)
            link.delete()

    def test_link_arrow_type_choices(self):
        """
        Test that links can be created with all valid arrow type choices
        """
        arrow_types = ["none", "uni", "bi"]

        for idx, arrow_type in enumerate(arrow_types):
            link = Link.objects.create(
                starting_block=self.block1,
                ending_block=self.block2,
                creator=self.user,
                CAM_id=self.cam.id,
                arrow_type=arrow_type,
                num=idx + 20,
            )
            self.assertEqual(link.arrow_type, arrow_type)
            link.delete()

    def test_link_string_representation(self):
        """
        Test Link __str__ method
        """
        link_ = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM_id=self.cam.id,
            num=999,
        )
        self.assertEqual(str(link_), "999")

    def test_link_default_values(self):
        """
        Test that links are created with correct default values
        """
        link_ = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM_id=self.cam.id,
        )

        self.assertEqual(link_.line_style, "Solid-Weak")
        self.assertEqual(link_.arrow_type, "none")
        self.assertEqual(link_.num, 0)

    def test_link_cascade_delete_with_block(self):
        """
        Test that links are deleted when one of their blocks is deleted
        """
        link_ = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM_id=self.cam.id,
        )
        link_id = link_.id

        # Delete starting block
        self.block1.delete()

        # Verify link is also deleted
        with self.assertRaises(Link.DoesNotExist):
            Link.objects.get(id=link_id)

    def test_link_cascade_delete_with_cam(self):
        """
        Test that links are deleted when their CAM is deleted
        """
        # Create a new CAM
        test_cam = CAM.objects.create(
            name="LinkDeleteTestCAM", user=self.user, project=self.project
        )

        # Create blocks
        block1 = Block.objects.create(
            title="LinkBlock1",
            creator=self.user,
            shape="neutral",
            CAM=test_cam,
            num=200,
        )
        block2 = Block.objects.create(
            title="LinkBlock2",
            creator=self.user,
            shape="positive",
            CAM=test_cam,
            num=201,
        )

        # Create link
        link = Link.objects.create(
            starting_block=block1, ending_block=block2, creator=self.user, CAM=test_cam
        )
        link_id = link.id

        # Delete the CAM
        test_cam.delete()

        # Verify link is also deleted
        with self.assertRaises(Link.DoesNotExist):
            Link.objects.get(id=link_id)

    def test_bidirectional_link(self):
        """
        Test creating and working with bidirectional links
        """
        link_ = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM_id=self.cam.id,
            arrow_type="bi",
        )

        self.assertEqual(link_.arrow_type, "bi")

        # Bidirectional links should maintain both start and end blocks
        self.assertEqual(link_.starting_block, self.block1)
        self.assertEqual(link_.ending_block, self.block2)

    def test_add_link_missing_blocks(self):
        """
        Test adding link with missing blocks - view raises exception
        """
        # Create blocks first to establish the CAM context
        block_start = Block.objects.create(
            title="StartBlock",
            x_pos=1.0,
            y_pos=1.0,
            height=100,
            width=100,
            creator=self.user,
            shape="neutral",
            CAM_id=self.cam.id,
            num=500,
        )

        # Try to add link with non-existent ending block
        # The view will raise Block.DoesNotExist exception
        try:
            response = self.client.post(
                "/link/add_link",
                {
                    "link_valid": True,
                    "starting_block": 500,
                    "ending_block": 9999,  # This block doesn't exist
                    "line_style": "Solid-Weak",
                    "arrow_type": "uni",
                },
            )
        except Exception:
            # Expected - the view raises exception for missing block
            pass

        # Verify link wasn't created
        self.assertFalse(Link.objects.filter(starting_block__num=500).exists())

    def test_update_link_properties(self):
        """
        Test updating link properties
        """
        link_ = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM_id=self.cam.id,
            arrow_type="uni",
            line_style="Solid-Weak",
        )

        response = self.client.post(
            "/link/update_link",
            {
                "link_id": link_.id,
                "line_style": "Dashed-Strong",
                "arrow_type": "bi",
            },
        )

        self.assertEqual(response.status_code, 200)

        link_.refresh_from_db()
        self.assertEqual(link_.line_style, "Dashed-Strong")
        self.assertEqual(link_.arrow_type, "bi")

    def test_swap_link_changes_direction(self):
        """
        Test swapping link direction
        """
        link_ = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM_id=self.cam.id,
        )

        original_start = link_.starting_block
        original_end = link_.ending_block

        response = self.client.post("/link/swap_link_direction", {"link_id": link_.id})

        self.assertEqual(response.status_code, 200)

        link_.refresh_from_db()
        # After swap, start and end should be reversed
        self.assertEqual(link_.starting_block, original_end)
        self.assertEqual(link_.ending_block, original_start)

    def test_delete_link_removes_from_database(self):
        """
        Test deleting link removes it completely
        """
        link_ = Link.objects.create(
            starting_block=self.block1,
            ending_block=self.block2,
            creator=self.user,
            CAM_id=self.cam.id,
        )

        link_id = link_.id

        response = self.client.post(
            "/link/delete_link", {"link_delete_valid": True, "link_id": link_id}
        )

        # Verify link is deleted
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
