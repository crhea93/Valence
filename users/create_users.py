"""
Create list of users with a specific imported CAM
"""
from .forms import ParticipantSignupForm
from users.models import CustomUser, Participant
from .resources import BlockResource, LinkResource
from zipfile import ZipFile
from tablib import Dataset
from block.models import Block
from link.models import Link
import pandas as pd
from .views_CAM import create_project_cam
from django.core.files.storage import default_storage
from django.forms.models import model_to_dict


def create_users(project, researcher, num_part, call_id, language_pref, input_file, deletable):
    """
    Create a new set of users for a project
    :param project: Project ID
    :param num_par: Number of Participants
    :param call_id: Naming convention --> username = call_id+num and password = call_id+num+call_id
    :param language_pref: Language Preference for users
    :param input_file: Name of input zip file
    :param deletable: Can the users delete the existing concepts
    :return:
    """
    for user_num in range(num_part):
        # Delete user if currently exists
        try:
            user = CustomUser.objects.get(username=call_id+str(user_num))
            user.delete()
        except:
            pass
        # Create new user
        participant_info = {
            'username': call_id + str(user_num),
            'email': call_id + str(user_num) + '@test.com',  # Give fake emails
            'password1': call_id + str(user_num) + call_id,
            'password2': call_id + str(user_num) + call_id,
            'first_name': '',
            'last_name': '',
            'language_preference': language_pref
        }
        form = ParticipantSignupForm(participant_info)
        if form.is_valid():
            participant = form.save()
            participant.researcher = researcher
            participant.project = project
            participant.save()
            cam = create_project_cam(participant, project.id)
            # If we are given an initial import file add the concepts/links
            if input_file:
                # Save input file and set to Project
                filename = default_storage.save(input_file.name, input_file)
                project.Initial_CAM = filename
                project.save()
                print(model_to_dict(project))
                block_resource = BlockResource()
                link_resource = LinkResource()
                dataset = Dataset()
                ct = 0
                #try:
                with ZipFile(input_file) as z:
                    for filename in z.namelist():
                        data = z.extract(filename)
                        test = pd.read_csv(data)
                        test['id'] = test['id'].apply(lambda x: '')  # Must be empty to auto id
                        test['creator'] = test['creator'].apply(lambda x: participant.id)
                        test['CAM'] = test['CAM'].apply(lambda x: cam.id)
                        test.to_csv(data)
                        imported_data = dataset.load(open(data).read())
                        if ct == 0:
                            result = block_resource.import_data(imported_data, dry_run=True)  # Test the data import
                            if not result.has_errors():
                                block_resource.import_data(imported_data, dry_run=False)  # Actually import now
                            else:
                                print('error block')
                        else:
                            result = link_resource.import_data(imported_data, dry_run=True)  # Test the data import
                            if not result.has_errors():
                                link_resource.import_data(imported_data, dry_run=False)  # Actually import now
                            else:
                                print('error link')
                        ct += 1
                #except:
                    #print('didnt work')
                # We now have to clean up the blocks' links...
                blocks_imported = cam.block_set.all()
                for block in blocks_imported:
                    # Clean up Comments ('none' -> '')
                    if block.comment == 'None' or block.comment == 'none':
                        block.comment = ''
                    if deletable is not None:
                        block.modifiable = False
                    # Change block creator to current user
                    #block.creator = participant
                    block.save()
                links_imported = cam.link_set.all()
                for link in links_imported:
                    #link.creator = participant
                    link.save()
            participant.save()
