from django.test import TestCase, override_settings
from users.models import CustomUser, Researcher
from django.urls import reverse
from .models import Project
# Create your tests here.


@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class ProjectTestCase(TestCase):
    def setUp(self):
        # Set up a user
        self.user = CustomUser.objects.create_user(username='testuser', email='test@test.test', password='12345')
        Researcher.objects.create(user=self.user, affiliation='UdeM')
        login = self.client.login(username='testuser', password='12345')

    def test_create_project(self):
        """
        Test the create project view
        """
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
        #print(len(projects))
        self.assertTrue(len(projects), 1)
        print(CustomUser.objects.get(username='T1'))
        self.assertTrue(CustomUser.objects.get(username='T1'), 'T1')
