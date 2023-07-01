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
        self.user = CustomUser.objects.create_user(username='testuser', email='test@test.test', password='12345')
        self.researcher = Researcher.objects.create(user=self.user, affiliation='UdeM')
        login = self.client.login(username='testuser', password='12345')
        # Create project belonging to user
        self.project = Project.objects.create(name='TestProject', description='TEST PROJECT', researcher=self.user,
                                              password='TestProjectPassword')
        self.cam = CAM.objects.create(name='testCAM', user=self.user, project=self.project)
        self.user.active_cam_num = self.cam.id
        self.block1 = Block.objects.create(title='Meow1', x_pos=1.0, y_pos=1.0, height=100, width=100, creator=self.user,
                                           shape='negative', CAM_id=self.cam.id, num=1)
        self.block2 = Block.objects.create(title='Meow2', x_pos=105.0, y_pos=105.0, height=100, width=100, creator=self.user,
                                           shape='positive', CAM_id=self.cam.id, num=2)

    def test_create_link(self):
        """
        Test to create a simple link for user as part of their CAM
        """
        # Data to pass through to ajax call
        data = {'link_valid': True, 'starting_block': self.block1.id, 'ending_block': self.block2.id,
                'line_style': 'Solid-Weak', 'arrow_type': 'uni'}
        response = self.client.post('/link/add_link', data)
        # Make sure the correct response is obtained
        self.assertTrue(response.status_code, 200)
        # Check that the new block was in fact created
        self.assertTrue('uni', [link.arrow_type for link in Link.objects.all()])
        link = Link.objects.filter(starting_block=self.block1.num).get(ending_block=self.block2.num)
        self.assertTrue(link)

    def test_update_link(self):
        """
        Test to update link
        """
        link_ = Link.objects.create(starting_block=self.block1, ending_block=self.block2, creator=self.user,
                                    CAM_id=self.cam.id)
        data = {
            'link_id': link_.id, 'line_style': 'Dashed', 'arrow_type': 'uni'
        }
        response = self.client.post('/link/update_link', data)
        link_.refresh_from_db()
        update_true = {'line_style': 'Dashed', 'arrow_type': 'uni'}
        update_actual = {'line_style': link_.line_style, 'arrow_type': link_.arrow_type}
        self.assertDictEqual(update_true, update_actual)

    def test_swap_link_direction(self):
        """
        Test to swap the direction of a link
        """
        link_ = Link.objects.create(starting_block=self.block1, ending_block=self.block2, creator=self.user,
                                    CAM_id=self.cam.id, arrow_type='uni')
        response = self.client.post('/link/swap_link_direction', {'link_id':link_.id})
        link_.refresh_from_db()
        # True order of links after swap
        true_order = {'starting_block': self.block2, 'ending_block':self.block1}
        # Actual order of links after swap
        actual_order = {'starting_block': link_.starting_block, 'ending_block': link_.ending_block}
        # Check to make sure the orders are correct
        self.assertDictEqual(true_order, actual_order)

    def test_delete_link(self):
        """
        Test to delete link
        """
        link_ = Link.objects.create(starting_block=self.block1, ending_block=self.block2, creator=self.user,
                                    CAM_id=self.cam.id, arrow_type='uni')
        response = self.client.post('/link/delete_link', {"delete_link_valid": True, 'link_id': link_.id})
        self.assertTrue(response, 200)


def trans_shape_to_slide(slide_val):
    """
    Translate between slider value and shape
    """
    if slide_val == 'negative strong':
        shape = 0
    elif slide_val == 'negative':
        shape = 1
    elif slide_val == 'negative weak':
        shape = 2
    elif slide_val == 'neutral':
        shape = 3
    elif slide_val == 'positive weak':
        shape = 4
    elif slide_val == 'positive':
        shape = 5
    elif slide_val == 'positive strong':
        shape = 6
    elif slide_val == 'ambivalent':
        shape = 7
    else:
        shape = 'neutral'
    return shape
