"""
Business logic utilities for user-related operations.
These functions contain testable business logic separated from HTTP request handling.
"""

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from zipfile import ZipFile, BadZipFile
from io import BytesIO
from tablib import Dataset
from PIL import Image, ImageOps
import pandas as pd
import numpy as np
import base64
import re
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from users.models import CAM, Project, CustomUser
from users.resources import BlockResource, LinkResource
from .views_CAM import upload_cam_participant, create_individual_cam


# ==================== Signup Business Logic ====================


def create_user_from_signup_form(form):
    """
    Create a new user from a validated signup form.

    Args:
        form: A validated CustomUserCreationForm instance

    Returns:
        tuple: (user, success) where user is the created CustomUser instance
               and success is a boolean indicating if creation was successful
    """
    try:
        user = form.save(commit=False)
        user.is_active = False  # Users start inactive until verified
        user.save()
        return user, True
    except Exception as e:
        return None, False


# ==================== Create Participant Business Logic ====================


def validate_project_password(project_name, project_password):
    """
    Validate that a project exists and has the correct password.

    Args:
        project_name: Name of the project to validate
        project_password: Password to verify

    Returns:
        tuple: (project, error_message) where project is the Project object
               or None, and error_message is a string describing any error
    """
    if not project_name:
        return None, None  # No project requested is not an error

    # Check if project exists
    try:
        project = Project.objects.get(name=project_name)
    except Project.DoesNotExist:
        project_names = [p.name for p in Project.objects.all()]
        error_msg = (
            "Project does not exist. Please select from the following options: "
            + ", ".join(project_names)
        )
        return None, error_msg

    # Check password if project has one
    if project.password and project_password != project.password:
        return None, "Incorrect Project Password"

    return project, None


def create_participant_user(form, project=None, request=None):
    """
    Create a new participant user with optional project affiliation.

    Args:
        form: A validated ParticipantSignupForm instance
        project: Optional Project instance to affiliate with
        request: Optional HTTP request object for login/CAM creation

    Returns:
        tuple: (user, success) where user is the created CustomUser instance
               and success is a boolean
    """
    try:
        user = form.save()

        if project:
            user.active_project_num = project.id
            user.save()
            if request:
                upload_cam_participant(user, project)
        else:
            # Create individual CAM for user without project
            if request:
                create_individual_cam(request)

        return user, True
    except Exception as e:
        return None, False


# ==================== Create Researcher Business Logic ====================


def create_researcher_user(form, request=None):
    """
    Create a new researcher user and initialize their CAM.

    Args:
        form: A validated ResearcherSignupForm instance
        request: Optional HTTP request object for CAM creation

    Returns:
        tuple: (user, success) where user is the created CustomUser instance
               and success is a boolean
    """
    try:
        form.save()
        username = form.cleaned_data.get("username")
        raw_password = form.cleaned_data.get("password1")
        user = authenticate(username=username, password=raw_password)

        if request:
            create_individual_cam(request)

        return user, True
    except Exception as e:
        return None, False


# ==================== Image CAM Business Logic ====================


def remove_transparency(im, bg_color=(255, 255, 255)):
    """
    Remove transparency from an image by adding a white background.

    Taken from https://stackoverflow.com/a/35859141/7444782
    """
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        alpha = im.convert("RGBA").split()[-1]
        bg = Image.new("RGBA", im.size, bg_color + (255,))
        bg.paste(im, mask=alpha)
        return bg
    else:
        return im


def process_cam_image(html_to_convert, user, media_url):
    """
    Process and save CAM image from base64 encoded data.

    Args:
        html_to_convert: Base64 encoded image data string
        user: CustomUser instance
        media_url: Media URL setting from Django configuration

    Returns:
        tuple: (file_name, success) where file_name is the saved filename
               and success is a boolean
    """
    try:
        # Extract base64 image data
        dataUrlPattern = re.compile(r"data:image/(png|jpeg);base64,(.*)$")
        match = dataUrlPattern.match(html_to_convert)
        if not match:
            return None, False

        image_data = match.group(2)
        image_data = image_data.encode()
        image_data = base64.b64decode(image_data)

        file_name = (
            media_url[1:]
            + "CAMS/"
            + user.username
            + "_"
            + str(user.active_cam_num)
            + ".png"
        )

        # Process image
        im = Image.open(BytesIO(image_data))
        if im.mode in ("RGBA", "LA"):
            im = remove_transparency(im)
            im = im.convert("RGB")
        im = im.resize((im.width * 5, im.height * 5), Image.ANTIALIAS)

        # Save color image
        color_buffer = BytesIO()
        im.save(color_buffer, "PNG", quality=1000)
        color_buffer.seek(0)
        default_storage.save(file_name, ContentFile(color_buffer.read()))

        # Save grayscale image
        gray_image = ImageOps.grayscale(im)
        gray_buffer = BytesIO()
        gray_image.save(gray_buffer, "PNG")
        gray_buffer.seek(0)
        gray_file_name = (
            media_url[1:]
            + "CAMS/"
            + user.username
            + "_"
            + str(user.active_cam_num)
            + "_grayscale.png"
        )
        default_storage.save(gray_file_name, ContentFile(gray_buffer.read()))

        # Update database
        current_cam = CAM.objects.get(id=user.active_cam_num)
        current_cam.cam_image = file_name
        current_cam.save()

        return file_name, True
    except Exception as e:
        return None, False


# ==================== Import CAM Business Logic ====================


def process_cam_zip_import(uploaded_cam, user, current_cam, deletable=False):
    """
    Process and import CAM data from a ZIP file.

    Args:
        uploaded_cam: File object containing ZIP data
        user: CustomUser instance
        current_cam: CAM instance to import into
        deletable: Boolean indicating if imported blocks should be non-modifiable

    Returns:
        tuple: (success, error_message) where success is a boolean
               and error_message is a string (empty if successful)
    """
    try:
        block_resource = BlockResource()
        link_resource = LinkResource()
        dataset = Dataset()

        # Clear existing blocks and links
        current_cam.block_set.all().delete()
        current_cam.link_set.all().delete()

        # Process ZIP file
        with ZipFile(uploaded_cam) as z:
            for filename in z.namelist():
                if filename.endswith(".csv"):
                    data = z.extract(filename)
                    test = pd.read_csv(data)

                    # Update creator and CAM references
                    if "creator" in test.columns:
                        test["creator"] = test["creator"].apply(lambda x: user.id)
                    if "CAM" in test.columns:
                        test["CAM"] = test["CAM"].apply(lambda x: current_cam.id)

                    # Handle text_scale for blocks
                    if "blocks" in filename:
                        test["text_scale"] = test["text_scale"].apply(
                            lambda x: x if ~np.isnan(x) else 14
                        )

                    # Import data
                    test.to_csv(data)
                    imported_data = dataset.load(open(data).read())

                    if "blocks" in filename:
                        result = block_resource.import_data(imported_data, dry_run=True)
                        if not result.has_errors():
                            block_resource.import_data(imported_data, dry_run=False)
                        else:
                            return (
                                False,
                                f"Error importing blocks: {result.row_errors()}",
                            )
                    else:
                        result = link_resource.import_data(imported_data, dry_run=True)
                        if not result.has_errors():
                            link_resource.import_data(imported_data, dry_run=False)
                        else:
                            return (
                                False,
                                f"Error importing links: {result.row_errors()}",
                            )

        # Post-import cleanup
        for block in current_cam.block_set.all():
            if block.comment in ("None", "none"):
                block.comment = ""
            if deletable:
                block.modifiable = False
            block.creator = user
            block.save()

        for link in current_cam.link_set.all():
            link.creator = user
            link.save()

        return True, ""
    except BadZipFile:
        return False, "File is not a zip file"
    except KeyError as e:
        return False, f"Missing file in ZIP: {str(e)}"
    except Exception as e:
        return False, f"Import failed: {str(e)}"


# ==================== Contact Form Business Logic ====================


def process_contact_form(contact_form):
    """
    Process and send a contact form submission email.

    Args:
        contact_form: A validated ContactForm instance

    Returns:
        tuple: (success, error_message) where success is a boolean
               and error_message is a string (empty if successful)
    """
    try:
        html_content = render_to_string(
            "Admin/email_contact_us.html",
            {
                "contacter": contact_form.cleaned_data["contacter"],
                "email": contact_form.cleaned_data["email"],
                "message": contact_form.cleaned_data["message"],
            },
        )
        text_content = strip_tags(html_content)
        email_subject = "CAM"
        email_from = contact_form.cleaned_data["email"]
        message = EmailMultiAlternatives(
            email_subject,
            text_content,
            email_from,
            ["thibeaultrheaprogramming@gmail.com"],
        )
        message.attach_alternative(html_content, "text/html")
        message.send()
        return True, ""
    except Exception as e:
        return False, str(e)


# ==================== Send CAM Business Logic ====================


def send_cam_email(
    user_id, username, recipient_email="thibeaultrheaprogramming@gmail.com"
):
    """
    Compose and send a CAM export email with CSV attachments.

    Args:
        user_id: ID of the user whose CAM to send
        username: Username of the user
        recipient_email: Email address to send to

    Returns:
        tuple: (success, error_message) where success is a boolean
               and error_message is a string (empty if successful)
    """
    try:
        from block.models import Block
        from link.models import Link
        import os

        html_content = render_to_string("Admin/send_CAM.html", {"contacter": username})
        text_content = strip_tags(html_content)
        email_subject = username + "'s CAM"
        email_from = "thibeaultrheaprogramming@gmail.com"
        message = EmailMultiAlternatives(
            email_subject, text_content, email_from, [recipient_email]
        )
        message.attach_alternative(html_content, "text/html")

        # Attach CSV files
        block_resource = (
            BlockResource().export(Block.objects.filter(creator=user_id)).csv
        )
        link_resource = LinkResource().export(Link.objects.filter(creator=user_id)).csv
        message.attach(username + "_blocks.csv", block_resource, "text/csv")
        message.attach(username + "_links.csv", link_resource, "text/csv")

        # Attach PDF if it exists
        pdf_path = "media/" + username + ".pdf"
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as pdf_file:
                message.attach(username + "_CAM.pdf", pdf_file.read())

        message.send()
        return True, ""
    except Exception as e:
        return False, str(e)
