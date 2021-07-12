from django.test import TestCase, override_settings
from users.models import CustomUser, Researcher
from django.urls import reverse
from .models import Project
# Create your tests here.


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class UserTestCase(TestCase):
    def setUp(self):
        # Set up a user
        self.user = CustomUser.objects.create_user(username='testuser', email='test@test.test', password='12345')
        self.user2 = CustomUser.objects.create_user(username='testuse2r', email='test2@test.test', password='12345')
        self.researcher = Researcher.objects.create(user=self.user, affiliation='UdeM')
        login = self.client.login(username='testuser', password='12345')
        # Create project belonging to user 2
        self.project = Project.objects.create(name='TestProject', description='TEST PROJECT', researcher=self.user2,
                                              password='TestProjectPassword')

    def test_user_creation_nonAff(self):
        """
        Test to make sure when a participant user is created and not affiliated with a project. We
        assume the participant does not enter a password (though by html design they "select" a project by default)
        """
        # Create new user with create_participant view
        response = self.client.post('/users/create_participant',
                                    {'project_name': self.project.name, 'project_password': '', 'username': 'newUser',
                                     'password1':'MEOWMEOW2', 'password2':'MEOWMEOW2', 'language_preference': 'en'})
        # Check that user is created
        new_part = CustomUser.objects.get(username='newUser')
        self.assertTrue(new_part)
        # Check that user has a CAM
        #new_part.refresh_from_db()
        #self.assertEqual(len(new_part.cam_set.all()), 1)
        # Check that user is not affiliated with a project
        #self.assertEqual(len(new_part.project_set.all()), 0)

    def test_user_creation_aff(self):
        """
        Test to make sure when a participant user is created and is affiliated with a project.
        """
        # Create new user with create_participant view
        response = self.client.post('/users/create_participant',
                                    {'project_name': self.project.name, 'project_password': self.project.password, 'username': 'newUser',
                                     'password1':'MEOWMEOW2', 'password2':'MEOWMEOW2', 'language_preference': 'en'})
        # Check that user is created
        new_part = CustomUser.objects.get(username='newUser')
        self.assertTrue(new_part)
        new_part.refresh_from_db()
        # Check that user has a CAM
        self.assertEqual(len(new_part.cam_set.all()), 1)
        # Check that user is now affiliated with a project
        #self.assertEqual(new_part.active_project_num, 1)
        #self.project.refresh_from_db()
        #self.assertTrue(False)

    def test_create_project(self):
        project_data = {
            'label': 'Test Project',
            'description': 'Test Description',
            'num_participants': 2,
            'name_participants': 'T',
            'participantType': 'auto_participants',
            'languagePreference': 'en',
            'conceptDelete': False
        }
        response = self.client.post(reverse('create_project'), project_data)
        # Check that the project is created
        projects = Project.objects.filter(researcher= self.user.id)
        self.assertTrue(len(projects), 1)
        self.assertTrue(CustomUser.objects.get(username='T1'), 'T1')


    #def test_user_creation_aff_init(self):