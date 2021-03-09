from django.shortcuts import render
from .forms import IndividualCAMCreationForm, ProjectCAMCreationForm
from django.http import HttpResponse, JsonResponse
from users.models import CAM, Project
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

from block.models import Block
from link.models import Link

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
    if form.is_valid():
        cam = form.save()
        user.active_cam_num = cam.id
        user.save()
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
            ct = 0
            print(project.Initial_CAM.name.split('/'))
            project_cam_name = project.Initial_CAM.name.split('/')[-2] + '/' + project.Initial_CAM.name.split('/')[-1]
            print(project_cam_name)
            with ZipFile(settings.MEDIA_ROOT+'/'+project_cam_name) as z:
                for filename in z.namelist():
                    if filename.endswith('.csv'):
                        data = z.extract(filename)
                        test = pd.read_csv(data)
                        test['id'] = test['id'].apply(lambda x: ' ')  # Must be empty to auto id
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
                    else:
                        pass
                    ct += 1
                    # We now have to clean up the blocks' links...
            blocks_imported = cam.block_set.all()
            for block in blocks_imported:
                # Clean up Comments ('none' -> '')
                if block.comment == 'None' or block.comment == 'none':
                    block.comment = ''
                    block.modifiable = False
                block.save()
            links_imported = cam.link_set.all()
            for link in links_imported:
                link.save()
    except:
        pass
    participant.save()

def load_cam(request):
    """
    Change user's current CAM and go to the CAM
    """
    user_ = request.user
    # Get current CAM number
    curr_cam = request.POST.get('cam_id')
    user_.active_cam_num = curr_cam
    user_.save()
    return HttpResponse("Success")


def delete_cam(request):
    # Get current CAM
    curr_cam = CAM.objects.get(id=request.POST.get('cam_id'))
    print(curr_cam)
    curr_cam.delete()
    return HttpResponse('Deleted')


def update_cam_name(request):
    # Get current CAM
    curr_cam = CAM.objects.get(id=request.POST.get('cam_id'))
    new_name = request.POST.get('new_name')
    print(new_name)
    curr_cam.name = new_name
    curr_cam.save()
    return HttpResponse('Name Updated')


def download_cam(request):
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
    """
    user_ = User.objects.get(username=request.user.username)
    cam_ = CAM.objects.get(id=request.POST.get('cam_id'))  # Get current CAM
    blocks_ = cam_.block_set.all()
    links_ = cam_.link_set.all()
    cam_.pk = None  # Give new primary key
    # Get current number of cams for user and add one to value
    num = len(user_.cam_set.all()) + 1
    cam_.name = cam_.name + '_clone'
    cam_.save()  # Save new CAM
    # Add blocks and links
    for block_ in blocks_:
        block_.pk = None
        block_.creator = user_
        block_.CAM = cam_
        block_.save()
    for link_ in links_:
        link_.pk = None
        link_.creator = user_
        link_.CAM = cam_
        link_.save()
    return JsonResponse({'message':'Success'})
