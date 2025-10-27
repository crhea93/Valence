from django.shortcuts import render, redirect
from users.forms import CustomUserCreationForm
from block.models import Block
from link.models import Link
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .forms import (
    ContactForm,
    ResearcherSignupForm,
    ParticipantSignupForm,
    CustomUserChangeForm,
)
from django.utils import translation
from django.conf import settings as settings_dj
from .resources import BlockResource, LinkResource
from zipfile import ZipFile, BadZipFile
from io import BytesIO
from tablib import Dataset
from PIL import Image, ImageOps
import pandas as pd
import numpy as np
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from users.models import CAM, Project, CustomUser
from .views_CAM import (
    upload_cam_participant,
    create_individual_cam,
    create_individual_cam_randomUser,
)
import datetime
from random_username.generate import generate_username
import re
import base64
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

User = get_user_model()
from django.conf import settings

media_url = settings.MEDIA_URL


def translate(request, user):
    translation.activate(user.language_preference)
    request.session[translation.LANGUAGE_SESSION_KEY] = user.language_preference
    response = HttpResponse(...)
    response.set_cookie(settings_dj.LANGUAGE_COOKIE_NAME, user.language_preference)


@login_required(login_url="loginpage")
def index(request):
    print(datetime.datetime.now())
    if request.method == "POST":
        print("nope!")
    else:  # request.method = "GET"
        user = User.objects.get(username=request.user.username)
        translation.activate(user.language_preference)
        request.session[translation.LANGUAGE_SESSION_KEY] = user.language_preference
        response = HttpResponse(...)
        response.set_cookie(settings_dj.LANGUAGE_COOKIE_NAME, user.language_preference)
        if user.is_authenticated:
            current_cam = CAM.objects.get(id=user.active_cam_num)
            blocks = current_cam.block_set.all()
            blocks_ = []
            for block in blocks:
                if block.comment is None:
                    block.comment = ""
                blocks_.append(block)
            lines = current_cam.link_set.all()
            lines_ = []
            for line in lines:
                lines_.append(line)
            content = {
                "user": user,
                "existing_blocks": blocks_,
                "existing_lines": lines_,
            }
            return render(request, "base/index.html", content)
        else:
            return redirect("loginpage")


@login_required(login_url="loginpage")
def dashboard(request):
    user = User.objects.get(username=request.user.username)
    translate(request, user)
    context = {"projects": Project.objects.all(), "user": user}
    return render(request, "dashboard.html", context=context)


@login_required(login_url="loginpage")
def tutorials(request):
    context = {}
    return render(request, "tutorials.html", context=context)


@login_required(login_url="loginpage")
def instructions(request):
    context = {}
    return render(request, "instructions.html", context=context)


@login_required(login_url="loginpage")
def contributors(request):
    context = {}
    return render(request, "contributors.html", context=context)


@login_required(login_url="loginpage")
def privacy(request):
    context = {}
    return render(request, "privacy.html", context=context)


@login_required(login_url="loginpage")
def FAQ(request):
    context = {}
    return render(request, "FAQ.html", context=context)


def background(request):
    context = {"user": request.user}
    if request.user.language_preference == "de":
        return render(request, "Background-Nav/Background_German.html", context=context)
    else:
        return render(request, "Background-Nav/Background.html", context=context)


def background_german(request):
    context = {"user": request.user}
    return render(request, "Background-Nav/Background_German.html", context=context)


def loginpage(request):
    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
        print(form)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                print(user.is_researcher)
                if user.is_researcher:
                    return redirect("dashboard")
                else:
                    return redirect("dashboard")
            else:
                pass
        else:
            message = ""
            username = form.data.get("username")
            password = form.data.get("password")
            if username not in User.objects.values_list("username", flat=True):
                message = _("Username does not exist")
            elif authenticate(username=username, password=password):
                message = _("Username or Password is incorrect")
            else:
                message = _(
                    "User is not authenticated. Check your emails to validate your account."
                )
            return render(
                request=request,
                template_name="registration/login.html",
                context={"form": form, "message": message},
            )
    form = AuthenticationForm()
    return render(
        request=request, template_name="registration/login.html", context={"form": form}
    )


def signup(request):
    """This view accept deals with the account creation form.
    In POST mode, it accepts the account creation form, validates it,
    create the user in the DB if the form is valid.
    In GET mode, it renders the form template for the account registration:
    'registration/register.html'.
    """
    from users.utils import create_user_from_signup_form

    formParticipant = ParticipantSignupForm()
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST or None)
        if form.is_valid():
            # Use extracted business logic
            user, success = create_user_from_signup_form(form)
            if success:
                login(request, user)
                return render(request, "index.html")

        context = {
            "message": form.errors,
            "form": form,
            "formParticipant": formParticipant,
            "projects": Project.objects.all(),
        }
        return render(request, "registration/register.html", context=context)
    else:
        form = CustomUserCreationForm()
    return render(
        request,
        "registration/register.html",
        context={"form": form, "projects": Project.objects.all()},
    )


def create_participant(request):
    """
    This function is called if a user tries to create a participant account
    The first thing is to create a participant account using the participant signup form. Then, we determine whether
    or not a user wishes to join a project.

    Functionality to create a user and assign them to a project.
    If the user wants to join a project and enters the correct password, then an account will be made with the following code:
    1. Call views_CAM/upload_cam_participant
    2. Call views_CAM/create_project_cam to create a CAM and associate it with a project
    3. views_CAM/upload_cam_participant continues with uploading the initial project CAM to the user's CAM if one exists
    """
    from users.utils import validate_project_password, create_participant_user

    if request.method == "POST":
        form = ParticipantSignupForm(request.POST)
        if form.is_valid():
            # Get project information from form
            project_name = request.POST.get("project_name", "")
            project_password = str(request.POST.get("project_password", ""))

            # Validate project - only if project_name is provided and non-empty
            project = None
            error_message = None
            if project_name:
                project, error_message = validate_project_password(
                    project_name, project_password
                )
                # If validation fails, still create user but without project affiliation
                # (project will be None)

            # Create participant user
            user, success = create_participant_user(
                form, project=project, request=request
            )
            if success:
                login(request, user)
                return redirect("index")
            else:
                # User creation failed
                context = {
                    "message": form.errors,
                    "form": form,
                    "projects": Project.objects.all(),
                    "password_message": "Failed to create user account",
                }
                return render(request, "registration/register.html", context=context)
        else:
            context = {
                "message": form.errors,
                "form": form,
                "projects": Project.objects.all(),
            }
            return render(request, "registration/register.html", context=context)


def create_researcher(request):
    """
    Basic functionality to create a researcher. This also creates a blank CAM for the researcher.This is only called if
    the user specifically signs up as a researcher.
    """
    from users.utils import create_researcher_user

    if request.method == "POST":
        form = ResearcherSignupForm(request.POST)
        if form.is_valid():
            user, success = create_researcher_user(form, request=request)
            if success:
                login(request, user)
                return redirect("index")

        context = {"message": form.errors, "form": form}
        return render(request, "registration/register.html", context=context)


def clear_CAM(request):
    """
    Function to clear a CAM. This function simply deletes all the blocks and links in a current CAM. After this function,
     the user's page will be refreshed and they will have a blank CAM. The CAM name/id does not change.
    """
    clear_cam_valid = request.POST.get("clear_cam_valid")  # clear cam
    if clear_cam_valid:
        # clear blocks associated with user
        user = CustomUser.objects.get(username=request.user.username)
        current_cam = CAM.objects.get(id=user.active_cam_num)
        blocks = current_cam.block_set.all()
        for block in blocks:
            block.delete()
        # clear links associated with user
        links = current_cam.link_set.all()
        for link in links:
            link.delete()
        return HttpResponse()


def remove_transparency(im, bg_color=(255, 255, 255)):
    """
    Taken from https://stackoverflow.com/a/35859141/7444782
    """
    # Only process if image has transparency (http://stackoverflow.com/a/1963146)
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
        alpha = im.convert("RGBA").split()[-1]

        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
        bg = Image.new("RGBA", im.size, bg_color + (255,))
        bg.paste(im, mask=alpha)
        return bg
    else:
        return im


from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from io import BytesIO


def Image_CAM(request):
    from users.utils import process_cam_image

    image_data = request.POST.get("html_to_convert")
    user = CustomUser.objects.get(username=request.user.username)

    # Use extracted business logic
    file_name, success = process_cam_image(image_data, user, media_url)

    if success:
        return JsonResponse({"file_name": file_name})
    else:
        return JsonResponse({"error": "Failed to process image"}, status=400)


def view_pdf(request):
    print("meow meow")
    User = get_user_model()
    user = User.objects.get(username=request.user.username)
    content = {
        "user": user,
    }
    return render(request, "Background-Nav/PDF_view.html", content)


def export_CAM(request):
    """
    Function to export CAM data. We export the block and link information (i.e. what's in the database) as individual csv
    files. The files are then zipped into a single file called username_CAM.zip.The file is then downloaded to the Downloads
    file via the Jquery/Ajax call that envokes this function.
    """
    user = CustomUser.objects.get(username=request.user.username)
    current_cam = CAM.objects.get(id=user.active_cam_num)
    block_resource = BlockResource().export(current_cam.block_set.all()).csv
    link_resource = LinkResource().export(current_cam.link_set.all()).csv
    outfile = BytesIO()  # io.BytesIO() for python 3
    names = ["blocks", "links"]
    ct = 0
    with ZipFile(outfile, "w") as zf:
        for resource in [block_resource, link_resource]:
            zf.writestr("{}.csv".format(names[ct]), resource)
            ct += 1
    response = HttpResponse(outfile.getvalue(), content_type="application/octet-stream")
    response["Content-Disposition"] = (
        'attachment; filename="' + request.user.username + '_CAM.zip"'
    )
    return response


def import_CAM(request):
    """
    Functionality to import a CAM. The workflos is as follows:
    1 - Read in file from Jquery/Ajax call. This file is in the format of a zip file containing csvs for both the
    blocks and links. The input here is the output of the export_CAM function.
    2 - Clear any blocks/links from the current CAM in case any exist
    3 -
    """
    from users.utils import process_cam_zip_import

    if request.method == "POST":
        try:
            uploaded_CAM = request.FILES["myfile"]
        except KeyError:
            return HttpResponse("No file provided", status=400)

        deletable = request.POST.get("Deletable")
        user = CustomUser.objects.get(username=request.user.username)
        current_cam = CAM.objects.get(id=user.active_cam_num)

        # Use extracted business logic
        success, error_message = process_cam_zip_import(
            uploaded_CAM, user, current_cam, deletable=bool(deletable)
        )

        if success:
            return redirect("/")
        else:
            return HttpResponse(error_message, status=400)


def contact_form(request):
    from users.utils import process_contact_form

    if request.method == "GET":
        contact_form = ContactForm()
        return render(request, "Admin/Contact_Form_2.html")
    if request.method == "POST":
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            # Use extracted business logic
            success, error_message = process_contact_form(contact_form)
            if success:
                return HttpResponse("done")
            else:
                return HttpResponse(error_message, status=400)
        else:
            # Form is invalid, return error response
            return HttpResponse("Invalid form data", status=400)


def send_cam(request):
    from users.utils import send_cam_email

    user_id = request.user.id
    username = request.user.username

    # Get recipient email from request, default to admin email if not provided
    recipient_email = request.POST.get("email", "thibeaultrheaprogramming@gmail.com")

    # Use extracted business logic
    success, error_message = send_cam_email(user_id, username, recipient_email)

    if success:
        return redirect("/")
    else:
        return HttpResponse(error_message, status=400)


def language_change(request):
    if request.method == "POST":
        # Change current language
        user_language = request.POST.get("language")
        print(user_language)
        if not user_language:
            user_language = "en"
        translation.activate(user_language)
        request.session[translation.LANGUAGE_SESSION_KEY] = user_language
        # Update users language preference
        if str(request.user) != "AnonymousUser":
            print(request.user)
            request.user.language_preference = user_language
            request.user.save()
        response = HttpResponse(...)
        response.set_cookie(settings_dj.LANGUAGE_COOKIE_NAME, user_language)
        message = _("Your language preferences have been updated!")
        print(message)
        print(request.user.language_preference)
        return JsonResponse({"message": message})
    else:
        return HttpResponse("Language successfully changed")


def language_change_anonymous(request):
    # Change current language
    user_language = request.LANGUAGE_CODE
    if user_language == "en":
        user_language = "de"
    elif user_language == "de":
        user_language = "en"
    translation.activate(user_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    # Update users language preference
    response = HttpResponse(...)
    response.set_cookie(settings_dj.LANGUAGE_COOKIE_NAME, user_language)
    return redirect(request.META["HTTP_REFERER"])


# @login_required(login_url='login')
@login_required
def settings(request):
    """This view is the user settings view.
    Depending of the request, we want to either show the user's settings
    or change them. In either case, we re-render the same page with
    the final settings.
    """
    user = request.user
    if request.method == "POST":
        avatar_ = request.FILES.get("id_image")
        print(avatar_)
        if avatar_:
            user.avatar = avatar_
        form = CustomUserChangeForm(request.POST, instance=user)
        # need to validate form before accessing cleaned data
        if form.is_valid():
            form.save()
        else:
            pass
    else:  # request.method == "GET"
        form = CustomUserChangeForm(instance=user)
    content = {"user": user, "form": form}
    return render(request, "settings_account.html", content)


def delete_user_cam(request):
    """
    Simple view to delete user
    """
    if request.method == "POST":
        cam_id = request.POST.get("cam_id")
    else:
        cam_id = request.GET.get("cam_id")
    cam = CAM.objects.get(id=cam_id)
    cam.delete()
    return HttpResponse("CAM Deleted")


def create_random(request):
    """
    Create user with randomized username and password
    """
    if request.method == "POST":
        username_ = generate_username(1)[0]
        print(username_)
        user = User.objects.create(
            username=username_, password=username_[::-1], random_user=True
        )
        login(request, user)
        create_individual_cam_randomUser(request, user)
        return redirect("index")
