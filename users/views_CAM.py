from django.shortcuts import render
from .forms import IndividualCAMCreationForm, ProjectCAMCreationForm
from django.http import HttpResponse, JsonResponse
from users.models import CAM, Project
from block.models import Block
from .resources import BlockResource, LinkResource
from zipfile import ZipFile
from io import BytesIO
import pandas as pd
from tablib import Dataset
from django.forms.models import model_to_dict
from django.conf import settings
import datetime
from django.contrib.auth import get_user_model

User = get_user_model()



def create_individual_cam(request):
    """
    Create New CAM not tied to a project
    """
    user_ = request.user
    # Get current number of cams for user and add one to value
    num = len(user_.cam_set.all()) + 1
    form = IndividualCAMCreationForm({"name": user_.username+str(num), 'user': user_.id})  # Fill in form
    if form.is_valid():
        cam = form.save()
        user_.active_cam_num = cam.id
        user_.save()
        cam.creation_date = datetime.datetime.now()
        cam.save()
    content = {
        'user': user_,
    }
    # Set user's current CAM to this newly created CAM
    return render(request, 'base/index.html', content)




def create_project_cam(user, project):
    form = ProjectCAMCreationForm({"name": user.username, 'user': user.id, 'project': project})  # Fill in form
    # Initiate CAM
    cam = None
    project_name = Project.objects.get(id=project).name
    if form.is_valid():
        cam = form.save()
        user.active_cam_num = cam.id
        user.save()
        cam.name = project_name
        cam.creation_date = datetime.datetime.now()
        cam.save()

    return cam



def upload_cam_participant(participant, project):
    """
    Assign CAM to participant when they make a linked account
    """
    cam = create_project_cam(participant, project.id)
    try:
        # If we are given an initial import file add the concepts/links
        if project.Initial_CAM:
            # Save input file and set to Project
            block_resource = BlockResource()
            link_resource = LinkResource()
            dataset = Dataset()
            current_cam = CAM.objects.get(id=participant.active_cam_num)
            # Clear all current blocks and links
            blocks = current_cam.block_set.all()
            for block in blocks:
                block.delete()
            links = current_cam.link_set.all()
            for link in links:
                link.delete()
            ct = 0
            project_cam_name = project.Initial_CAM.name.split('/')[-2] + '/' + project.Initial_CAM.name.split('/')[-1]
            with ZipFile(settings.MEDIA_ROOT+'/'+project_cam_name) as z:
                for filename in z.namelist():
                    if filename.endswith('.csv'):
                        data = z.extract(filename)
                        test = pd.read_csv(data)
                        # Set creator and CAM to the current user and their CAM
                        test['id'] = test['id'].apply(lambda x: ' ')  # Must be empty to auto id
                        test['creator'] = test['creator'].apply(lambda x: participant.id)
                        test['CAM'] = test['CAM'].apply(lambda x: current_cam.id)
                        # Read in information from csvs
                        test.to_csv(data)
                        imported_data = dataset.load(open(data).read())
                        blocks_imported = current_cam.block_set.all()
                        print([block.id for block in blocks_imported])
                        if ct == 0:  # first csv is blocks.csv
                            result = block_resource.import_data(imported_data, dry_run=True)  # Test the data import
                            if not result.has_errors():
                                block_resource.import_data(imported_data, dry_run=False)  # Actually import now
                            else:
                                print('Error in reading in concepts')
                                print(result.row_errors())
                        else:  # Second csv is links.csv
                            result = link_resource.import_data(imported_data, dry_run=True)  # Test the data import
                            if not result.has_errors():
                                link_resource.import_data(imported_data, dry_run=False)  # Actually import now
                            else:
                                print('Error in reading in links')
                                print(result.row_errors())
                        ct += 1
                    else:
                        pass

                    # We now have to clean up the blocks' links...
            blocks_imported = cam.block_set.all()
            for block in blocks_imported:
                # Clean up Comments ('none' -> '')
                if block.comment == 'None' or block.comment == 'none':
                    block.comment = ''
                #if deletable is not None:
                #    block.modifiable = False
                # Change block creator to current user
                block.creator = participant
                block.save()
            links_imported = current_cam.link_set.all()
            for link in links_imported:
                link.creator = participant
                link.save()
    except:
        pass
    participant.save()


def load_cam(request):
    """
    Change user's current CAM and go to the CAM
    TODO: TEST
    """
    user_ = request.user
    # Get current CAM number
    curr_cam = request.POST.get('cam_id')
    user_.active_cam_num = curr_cam
    user_.save()
    return HttpResponse("Success")


def delete_cam(request):
    # Get current CAM
    # TODO: TEST
    curr_cam = CAM.objects.get(id=request.POST.get('cam_id'))
    print(curr_cam)
    curr_cam.delete()
    return HttpResponse('Deleted')


def update_cam_name(request):
    # Get current CAM
    # TODO: TEST
    curr_cam = CAM.objects.get(id=request.POST.get('cam_id'))
    new_name = request.POST.get('new_name')
    new_description = request.POST.get('description')
    print(new_name)
    curr_cam.name = new_name
    curr_cam.description = new_description
    curr_cam.save()
    print(curr_cam)
    return HttpResponse('Name Updated')


def download_cam(request):
    # TODO: TEST
    current_cam = CAM.objects.get(id=request.GET.get('pk'))
    block_resource = BlockResource().export(current_cam.block_set.all()).csv
    link_resource = LinkResource().export(current_cam.link_set.all()).csv
    outfile = BytesIO()  # io.BytesIO() for python 3
    names = ['blocks', 'links']
    ct = 0
    with ZipFile(outfile, 'w') as zf:
        for resource in [block_resource, link_resource]:
            zf.writestr("{}.csv".format(names[ct]), resource)
            ct += 1
        if current_cam.cam_image:
            try:
                zf.write(str(current_cam.cam_image))
            except:
                pass
    response = HttpResponse(outfile.getvalue(), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="' + current_cam.user.username + '_CAM.zip"'
    return response


def initial_cam(request):
    current_project = Project.objects.get(id=request.GET.get('pk'))
    outfile = BytesIO()  # io.BytesIO() for python 3
    with ZipFile(outfile, 'w') as zf:
        for current_cam in current_project.cam_set.all():
            block_resource = BlockResource().export(current_cam.block_set.all()).csv
            link_resource = LinkResource().export(current_cam.link_set.all()).csv
            names = ['blocks', 'links']
            ct = 0
            for resource in [block_resource, link_resource]:
                zf.writestr("{}.csv".format(current_cam.user.username + '_' + names[ct]), resource)
                ct += 1
    response = HttpResponse(outfile.getvalue(), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="' + request.user.username + '_CAM.zip"'
    return response


def create_individual_cam_randomUser(request, user_):
    """
    Create New CAM not tied to a project
    # TODO:TEST
    """
    # Get current number of cams for user and add one to value
    num = len(user_.cam_set.all()) + 1
    form = IndividualCAMCreationForm({"name": user_.username+str(num), 'user': user_.id})  # Fill in form
    if form.is_valid():
        cam = form.save()
        user_.active_cam_num = cam.id
        user_.save()
        cam.creation_date = datetime.datetime.now()
        cam.save()
    content = {
        'user': user_,
    }
    # Set user's current CAM to this newly created CAM
    return render(request, 'base/index.html', content)

def clone_CAM(request):
    """
    Clone a CAM for a user
    TODO: TEST
    """
    user_ = User.objects.get(username=request.user.username)
    cam_ = CAM.objects.get(id=request.POST.get('cam_id'))  # Get current CAM
    blocks_ = cam_.block_set.all()
    links_ = cam_.link_set.all()
    link_dict = {}
    cam_.pk = None  # Give new primary key
    # Get current number of cams for user and add one to value
    num = len(user_.cam_set.all()) + 1
    cam_.name = cam_.name + '_clone'
    cam_.save()  # Save new CAM
    print('Making new CAM')
    # Create dictionary for links  {link: [start_concept_new, end_concept_new]}
    for link_ in links_:
        link_dict[link_.pk] = [link_.starting_block.id, link_.ending_block.id]
    # Add blocks and links
    for block_ in blocks_:
        # Check if block is the starting block for some link
        old_id = block_.pk
        block_.pk = None
        block_.creator = user_
        block_.CAM = cam_
        block_.save()
        for link_id, link_blocks in link_dict.items():
            if old_id in link_blocks:  # need to update
                for ct, blk in enumerate(link_blocks):
                    if old_id == blk:
                        link_blocks[ct] = block_.pk
                #link_blocks[link_blocks == old_id] = block_.pk
                # Now update dictionary
                link_dict[link_id] = link_blocks
    for link_ in links_:
        old_id = link_.pk
        link_.pk = None
        link_.creator = user_
        link_.CAM = cam_
        link_.starting_block = Block.objects.get(id=link_dict[old_id][0])
        link_.ending_block = Block.objects.get(id=link_dict[old_id][1])
        link_.save()
        # Now update link starting and ending IDs with the new block ids

    return JsonResponse({'message':'Success'})

def clone_CAM_call(user, cam_id):
    """
    Clone a CAM for a user. This is called by join_project_link in views_Project.py
    TODO: TEST
    """
    user_ = user
    cam_ = CAM.objects.get(id=cam_id)  # Get current CAM
    blocks_ = cam_.block_set.all()
    links_ = cam_.link_set.all()
    link_dict = {}
    cam_.pk = None  # Give new primary key
    # Get current number of cams for user and add one to value
    num = len(user_.cam_set.all()) + 1
    cam_.name = cam_.name + '_clone'
    cam_.save()  # Save new CAM
    print('Making new CAM')
    # Create dictionary for links  {link: [start_concept_new, end_concept_new]}
    for link_ in links_:
        link_dict[link_.pk] = [link_.starting_block.id, link_.ending_block.id]
    # Add blocks and links
    for block_ in blocks_:
        print(block_)
        # Check if block is the starting block for some link
        old_id = block_.pk
        block_.pk = None
        block_.creator = user_
        block_.CAM = cam_
        block_.save()
        for link_id, link_blocks in link_dict.items():
            if old_id in link_blocks:  # need to update
                for ct, blk in enumerate(link_blocks):
                    if old_id == blk:
                        link_blocks[ct] = block_.pk
                #link_blocks[link_blocks == old_id] = block_.pk
                # Now update dictionary
                link_dict[link_id] = link_blocks
    for link_ in links_:
        old_id = link_.pk
        link_.pk = None
        link_.creator = user_
        link_.CAM = cam_
        link_.starting_block = Block.objects.get(id=link_dict[old_id][0])
        link_.ending_block = Block.objects.get(id=link_dict[old_id][1])
        link_.save()
        # Now update link starting and ending IDs with the new block ids


    return JsonResponse({'message':'Success'})
