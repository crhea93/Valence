from django.shortcuts import render, redirect
from .forms import ProjectCreationForm
from .create_users import create_users
from django.http import HttpResponse, JsonResponse
from .models import Project, CAM
from .resources import BlockResource, LinkResource
from zipfile import ZipFile
from io import BytesIO
from .views_CAM import upload_cam_participant, create_individual_cam, clone_CAM_call
from django.contrib.auth import login, authenticate
from .forms import ParticipantSignupForm
from users.forms import CustomUserCreationForm
from users.models import CustomUser
from django.utils import translation
from django.conf import settings as settings_dj
from django.http import HttpResponse
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


def translate(request, user):
    translation.activate(user.language_preference)
    request.session[translation.LANGUAGE_SESSION_KEY] = user.language_preference
    response = HttpResponse(...)
    response.set_cookie(settings_dj.LANGUAGE_COOKIE_NAME, user.language_preference)


def project_page(request):
    user_ = request.user
    translate(request, user_)
    project = Project.objects.get(id=user_.active_project_num)
    context = {"user": user_, "active_project": project}
    return render(request, "project_page.html", context=context)


def create_project(request):
    form = ProjectCreationForm()
    if request.method == "POST":
        user_ = request.user

        # Check if user has researcher profile
        if not hasattr(user_, "researcher") or user_.researcher is None:
            context = {
                "message": "Only researchers can create projects. Please contact an administrator.",
                "form": form,
            }
            return render(request, "create_project.html", context=context)

        # Get information to pass to Project Form
        project_info = {
            "name": request.POST.get("label"),
            "researcher": user_.id,
            "num_part": request.POST.get("num_participants"),
            "description": request.POST.get("description"),
            "name_participants": request.POST.get("name_participants"),
            "password": request.POST.get("password"),
        }
        # Now pass to Project Form
        form = ProjectCreationForm(project_info)
        # Check if we have an input file
        try:
            input_file = request.FILES["myfile"]
        except:
            input_file = False
        if form.is_valid():
            project = form.save()
            project.Initial_CAM = input_file
            project.save()
            logger.debug(f"Project Initial CAM: {project.Initial_CAM}")
            # Check if we need to create users
            if request.POST.get("participantType") == "auto_participants":
                # Call creation function found in create_users.py
                create_users(
                    project,
                    user_.researcher,
                    project.num_part,
                    request.POST.get("name_participants"),
                    request.POST.get("languagePreference"),
                    input_file,
                    request.POST.get("conceptDelete"),
                )
            context = {
                "user": user_,
                "active_project": project,
                "form": form,
            }

            return render(request, "project_page.html", context=context)
        else:
            context = {
                "message": form.errors,
                "form": form,
                "project_info": project_info,
            }
            return render(request, "create_project.html", context=context)
    else:
        return render(request, "create_project.html", context={"form": form})


def join_project(request):
    """
    View called when a participant joins a new project from the dashboard. The mecahnism is identical to the create_participant
    view above.

    Functionality to create a user and assign them to a project.
    If the user wants to join a project and enters the correct password, then an account will be made with the following code:
    1. Call views_CAM/upload_cam_participant
    2. Call views_CAM/create_project_cam to create a CAM and associate it with a project
    3. views_CAM/upload_cam_participant continues with uploading the initial project CAM to the user's CAM if one exists
    """
    project_name = request.POST.get("project_name")
    # Check if project exists
    if request.POST.get("project_checked") == "true":
        try:  # If project exists
            project = Project.objects.get(name=project_name)
            if request.POST.get("project_password") == project.password:
                upload_cam_participant(request.user, project)
                return JsonResponse({"message": "Success"})
            else:  # Password incorrect
                return JsonResponse(
                    data={
                        "error_message": "Please enter the correct password!",
                        "message": "Failure",
                    }
                )
        except Project.DoesNotExist:  # Project does not exist
            project_names = [project.name for project in Project.objects.all()]
            return JsonResponse(
                data={
                    "error_message": "Project does not exist. Please select from the following options: \n"
                    + ", ".join(project_names)
                }
            )
        except Exception as e:  # Other errors
            return JsonResponse(
                data={
                    "error_message": f"An error occurred: {str(e)}",
                    "message": "Failure",
                }
            )
    else:
        create_individual_cam(request)
        return JsonResponse({"message": "Success"})


def join_project_link(request):
    """
    View to create a participant and assign them a project. This is used when a participant is given a signup link. The information
    for the user and project is all pulled directly from the url in a GET.

    The mechanism is identical to the create_participant view above.

    Functionality to create a user and assign them to a project.
    If the user wants to join a project and enters the correct password, then an account will be made with the following code:
    1. Call views_CAM/upload_cam_participant
    2. Call views_CAM/create_project_cam to create a CAM and associate it with a project
    3. views_CAM/upload_cam_participant continues with uploading the initial project CAM to the user's CAM if one exists

    We have added the functionality to simply send a user directly to their CAM (reuse), duplicate their CAM and then
    direct them to the duplicate (duplicate), and create a new CAM (new)

    Example link: http://127.0.0.1:8000/users/join_project_link?username=cmeow&pword=meow&proj_name=Carter2&proj_pword=Carter
    """
    # Step 1: Create User
    formParticipant = ParticipantSignupForm()
    # Read in information from url: users/join_project_link?username=&pword=&lang=&proj_name=&proj_pword=
    username = request.GET.get("username")
    pword1 = request.GET.get("pword")
    pword2 = pword1  # Make sure the passwords are equal for authentification
    lang = request.GET.get("lang", "en")
    user_info = {
        "username": username,
        "password1": pword1,
        "password2": pword2,
        "language_preference": lang,
    }
    # Determine what kind of action to do
    cam_op = request.GET.get(
        "cam_op", "new"
    )  # Either new, reuse, or duplicate (default: new)
    if request.method == "GET":
        if (
            cam_op == "new"
        ):  # Now we have two cases: 1 - user doesn't exist or 2 - user already exists
            if CustomUser.objects.filter(
                username=username
            ):  # Case 2: User already exists
                logger.info(f"User {username} already exists, logging in")
                # Step 1: Login as user
                user = authenticate(username=username, password=pword1)
                login(request, user)
                user = CustomUser.objects.get(username=username)
                # Step 2: Assign User to Project
                project_name = request.GET.get("proj_name")
                project = Project.objects.get(name=project_name)
                if request.GET.get("proj_pword") == project.password:
                    user.active_project_num = project.id
                    user.save()
                    upload_cam_participant(user, project)
                    return redirect("index")
                else:  # Password incorrect  (SHOULD NOT HAPPEN)
                    return JsonResponse(
                        data={
                            "error_message": "Please enter the correct password!",
                            "message": "Failure",
                        }
                    )
            else:  # Case 1: User does not exist
                logger.info(f"Creating new user {username}")
                form = ParticipantSignupForm(user_info)
                if form.is_valid():
                    form.save()
                    user = authenticate(username=username, password=pword1)
                    login(request, user)
                    user = CustomUser.objects.get(username=username)
                    # Step 2: Assign User to Project
                    project_name = request.GET.get("proj_name")
                    project = Project.objects.get(name=project_name)
                    if request.GET.get("proj_pword") == project.password:
                        user.active_project_num = project.id
                        user.save()
                        upload_cam_participant(user, project)
                        return redirect("index")
                    else:  # Password incorrect  (SHOULD NOT HAPPEN)
                        return JsonResponse(
                            data={
                                "error_message": "Please enter the correct password!",
                                "message": "Failure",
                            }
                        )
                else:
                    return redirect("login")
        elif cam_op == "reuse":  # Simply log user in and redirect to CAM
            # TODO: Test if CAM doesn't exist
            cam_id = request.GET.get("cam_id")  # Get CAM id
            # Check that CAM exists
            try:
                cam = CAM.objects.get(pk=cam_id)
            except:
                return JsonResponse(
                    data={
                        "error_message": "This CAM doesn't exist! Please contact the leader of the study.",
                        "message": "Failure",
                    }
                )
            # Step 1: Login as user
            user = authenticate(username=username, password=pword1)
            login(request, user)
            user = CustomUser.objects.get(username=username)
            # Step 2: Set CAM id to the correct CAM
            user.active_cam_num = cam_id
            user.save()
            # Step 3: Redirect user to CAM
            return redirect("index")
        elif cam_op == "duplicate":  # Create duplicate CAM and redirect user to it
            cam_id = request.GET.get("cam_id")  # Get CAM id
            # Check that CAM exists
            try:
                cam = CAM.objects.get(pk=cam_id)
            except:
                return JsonResponse(
                    data={
                        "error_message": "This CAM doesn't exist! Please contact the leader of the study.",
                        "message": "Failure",
                    }
                )
            # Step 1: Sign in as user
            user = authenticate(username=username, password=pword1)
            login(request, user)
            user = CustomUser.objects.get(username=username)
            # Step 2: Clone CAM
            clone = clone_CAM_call(
                user, cam_id
            )  # Get cloned CAM directly from function
            # Step 3: Set user's current cam to the clone
            user.active_cam_num = clone.id
            user.save()
            # Step 4: Redirect user to cloned CAM
            return redirect("index")

    """except:  # Project does not exist
        project_names = [project.name for project in Project.objects.all()]
        return JsonResponse(data={
            'error_message': "Project does not exist. Please select from the following options: \n" + ', '.join(
                project_names)})
        create_individual_cam(request)
        return redirect('index')
    else:
        create_individual_cam(request)
        return redirect('index')"""


def load_project(request):
    """
    Change user's current CAM and go to the CAM
    """
    user_ = request.user
    # Get current CAM number
    curr_project = request.POST.get("project_id")
    user_.active_project_num = curr_project
    user_.save()
    return HttpResponse("Success")


def delete_project(request):
    # Get current project
    project_id = request.POST.get("project_id")
    try:
        curr_project = Project.objects.get(id=project_id)

        # Check if user is the owner of the project
        if curr_project.researcher != request.user:
            return HttpResponse("Unauthorized", status=403)

        curr_project.delete()
        return HttpResponse("Deleted")
    except Project.DoesNotExist:
        return HttpResponse("Project not found", status=404)


def download_project(request):
    pk = request.GET.get("pk")

    # If no pk provided, try to use user's active project
    if not pk:
        if (
            hasattr(request.user, "active_project_num")
            and request.user.active_project_num
        ):
            pk = request.user.active_project_num
        else:
            return HttpResponse("Project ID is required", status=400)

    try:
        current_project = Project.objects.get(id=pk)
    except Project.DoesNotExist:
        return HttpResponse("Project not found", status=404)

    outfile = BytesIO()  # io.BytesIO() for python 3
    with ZipFile(outfile, "w") as zf:
        for current_cam in current_project.cam_set.all():
            block_resource = BlockResource().export(current_cam.block_set.all()).csv
            link_resource = LinkResource().export(current_cam.link_set.all()).csv
            names = ["blocks", "links"]
            ct = 0
            for resource in [block_resource, link_resource]:
                zf.writestr(
                    "{}.csv".format(
                        current_cam.user.username
                        + "_"
                        + str(current_cam.id)
                        + "_"
                        + names[ct]
                    ),
                    resource,
                )
                ct += 1
            if current_cam.cam_image:
                try:
                    zf.write(str(current_cam.cam_image))
                except:
                    pass
    response = HttpResponse(outfile.getvalue(), content_type="application/octet-stream")
    response["Content-Disposition"] = (
        'attachment; filename="' + current_project.name + '_CAM.zip"'
    )
    return response


def project_settings(request):
    if request.method == "GET":
        user_ = request.user
        project = Project.objects.get(id=user_.active_project_num)
        context = {"user": user_, "active_project": project}
        return render(request, "project_settings.html", context=context)
    if request.method == "POST":
        user_ = request.user
        project = Project.objects.get(id=user_.active_project_num)
        # Get information to pass to Project Form
        project_info = {
            "name": request.POST.get("nameUpdate"),
            "description": request.POST.get("descriptionUpdate"),
        }
        project.update(project_info)
        context = {"user": user_, "active_project": project}
        return render(request, "project_settings.html", context=context)
