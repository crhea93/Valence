from django.test import TestCase
from users.models import CustomUser, CAM, Researcher, Project, logCamActions
from .models import Block
from django.forms.models import model_to_dict
import yaml

# Create your tests here.
class BlockTestCase(TestCase):
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

    def test_create_block(self):
        """
        Test to create a simple block for user as part of their CAM
        """
        # Data to pass through to ajax call
        data = {'add_valid': True, 'num_block': 1, 'title': 'Meow', 'shape': 3, 'x_pos': 0.0, 'y_pos': 0.0,
               'width': 100, 'height': 100}
        response = self.client.post('/block/add_block', data)
        # Make sure the correct response is obtained
        self.assertTrue(response.status_code, 200)
        # Check that the new block was in fact created
        self.assertTrue('Meow', [block.title for block in Block.objects.all()])

    def test_update_block(self):
        """
        Test to update an existing block
        """
        block_ = Block.objects.create(title='Meow2', x_pos=1.0, y_pos=1.0, height=100, width=100, creator=self.user,
                                      shape='neutral', CAM_id=self.cam.id)
        data = {'update_valid': True, 'num_block': block_.num, 'title': 'Meow2_update', 'shape': 7, 'comment': 'ew',
                'x_pos': '2.0px', 'y_pos': '2.0px', 'height':'50px', 'width': '50px'}
        response = self.client.post('/block/update_block', data)
        # Make sure the correct response is obtained
        self.assertTrue(response.status_code, 200)
        # Refresh block info from db
        block_.refresh_from_db()
        # Check that the updates were made
        update_true = {'title': 'Meow2_update', 'shape': 7, 'comment': 'ew',
                       'x_pos': 2.0, 'y_pos': 2.0, 'height':50, 'width': 50}  # What it should be updated to
        update_actual = {'title': block_.title, 'shape': trans_shape_to_slide(block_.shape), 'comment': block_.comment,
                         'x_pos': block_.x_pos, 'y_pos': block_.y_pos, 'height': block_.height,
                         'width': block_.width}
        self.assertDictEqual(update_true, update_actual)
        #block_.delete()


    def test_delete_block(self):
        """
        Test that a block is deleted
        """
        block_ = Block.objects.create(title='Meow3', x_pos=1.0, y_pos=1.0, height=100, width=100, creator=self.user,
                                      shape='ambivalent', CAM_id=self.cam.id)
        response = self.client.post('/block/delete_block', {'delete_valid': True, 'block_id': block_.num})
        self.assertTrue(response.status_code, 200)
        logEntry = self.cam.logcamactions_set.latest('actionId').objDetails
        logEntry = yaml.load(logEntry)
        self.assertTrue(logEntry['title'], 'Meow3')

    def test_drag_block(self):
        """
        Test that when a block is dragged the position information is updated
        """
        block_ = Block.objects.create(title='Meow3', x_pos=1.0, y_pos=1.0, height=100, width=100, creator=self.user,
                                      shape='ambivalent', CAM_id=self.cam.id)
        data = {
            'drag_valid': True, 'block_id': block_.num, 'x_pos': '10.0px', 'y_pos': '10.0px', 'width': '100px',
            'height': '100px'
        }
        response = self.client.post('/block/drag_function', data)
        block_.refresh_from_db()
        update_true = {'title': 'Meow3', 'shape': 7,
                       'x_pos': 10.0, 'y_pos': 10.0, 'height':100.0, 'width': 100.0}  # What it should be updated to
        update_actual = {'title': block_.title, 'shape': trans_shape_to_slide(block_.shape),
                         'x_pos': block_.x_pos, 'y_pos': block_.y_pos, 'height': block_.height,
                         'width': block_.width}
        self.assertDictEqual(update_true, update_actual)
        block_.delete()


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
