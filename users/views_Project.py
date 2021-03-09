from django.shortcuts import render
from .forms import ProjectCreationForm
from .create_users import create_users
from django.http import HttpResponse
from .models import Project
from .resources import BlockResource, LinkResource
from zipfile import ZipFile
from io import BytesIO


def project_page(request):
    user_ = request.user
    project = Project.objects.get(id=user_.active_project_num)
    context = {
        'user': user_,
        'active_project': project
    }
    return render(request, "project_page.html", context=context)


def create_project(request):
    form = ProjectCreationForm()
    if request.method == "POST":
        user_ = request.user
        # Get information to pass to Project Form
        project_info = {
            'name': request.POST.get('label'),
            'researcher': user_.id,
            'num_part': request.POST.get('num_participants'),
            'description': request.POST.get('description'),
            'name_participants': request.POST.get('name_participants'),
            'password': request.POST.get('password')
        }
        # Now pass to Project Form
        form = ProjectCreationForm(project_info)
        # Check if we have an input file
        try:
            input_file = request.FILES['myfile']
        except:
            input_file = False
        if form.is_valid():
            project = form.save()
            project.Initial_CAM = input_file
            project.save()

            print(project.Initial_CAM)
            # Check if we need to create users
            if request.POST.get('participantType') == 'auto_participants':
                # Call creation function found in create_users.py
                create_users(project, user_.researcher, project.num_part, request.POST.get('name_participants'),
                             request.POST.get('languagePreference'), input_file,
                             request.POST.get('conceptDelete'))
            context = {
                'user': user_,
                'active_project': project
                }

            return render(request, "project_page.html", context=context)
        else:
            context = {
                'message': form.errors,
                "form": form
            }
            return render(request, "create_project.html", context=context)
    else:
        return render(request, "create_project.html", context={"form": form})


def load_project(request):
    """
    Change user's current CAM and go to the CAM
    """
    user_ = request.user
    # Get current CAM number
    curr_project = request.POST.get('project_id')
    user_.active_project_num = curr_project
    user_.save()
    return HttpResponse("Success")


def delete_project(request):
    # Get current CAM
    curr_project = Project.objects.get(id=request.POST.get('project_id'))
    curr_project.delete()
    return HttpResponse('Deleted')


def download_project(request):
    current_project = Project.objects.get(id=request.GET.get('pk'))
    outfile = BytesIO()  # io.BytesIO() for python 3
    with ZipFile(outfile, 'w') as zf:
        for current_cam in current_project.cam_set.all():
            block_resource = BlockResource().export(current_cam.block_set.all()).csv
            link_resource = LinkResource().export(current_cam.link_set.all()).csv
            names = ['blocks', 'links']
            ct = 0
            for resource in [block_resource, link_resource]:
                zf.writestr("{}.csv".format(current_cam.user.username+'_'+str(current_cam.id)+'_'+names[ct]), resource)
                ct += 1
            if current_cam.cam_image:
                try:
                    zf.write(str(current_cam.cam_image))
                except:
                    pass
    response = HttpResponse(outfile.getvalue(), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="' + current_project.name + '_CAM.zip"'
    return response
