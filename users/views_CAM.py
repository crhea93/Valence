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
import logging
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()


def create_individual_cam(request):
    """
    Create New CAM not tied to a project
    """
    user_ = request.user
    # Get current number of cams for user and add one to value
    num = user_.cam_set.count() + 1

    # Check if name is provided in POST request
    cam_name = request.POST.get("cam_name") if request.method == "POST" else None
    if not cam_name:
        cam_name = user_.username + str(num)

    form = IndividualCAMCreationForm(
        {"name": cam_name, "user": user_.id}
    )  # Fill in form
    if form.is_valid():
        cam = form.save()
        user_.active_cam_num = cam.id
        user_.save()
        cam.creation_date = datetime.datetime.now()
        cam.save()
    content = {
        "user": user_,
    }
    # Set user's current CAM to this newly created CAM
    return render(request, "base/index.html", content)


def create_project_cam(user, project):
    form = ProjectCAMCreationForm(
        {"name": user.username, "user": user.id, "project": project}
    )  # Fill in form
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
            project_cam_name = (
                project.Initial_CAM.name.split("/")[-2]
                + "/"
                + project.Initial_CAM.name.split("/")[-1]
            )
            with ZipFile(settings.MEDIA_ROOT + "/" + project_cam_name) as z:
                for filename in z.namelist():
                    if filename.endswith(".csv"):
                        data = z.extract(filename)
                        test = pd.read_csv(data)
                        # Set creator and CAM to the current user and their CAM
                        test["id"] = test["id"].apply(
                            lambda x: " "
                        )  # Must be empty to auto id
                        test["creator"] = test["creator"].apply(
                            lambda x: participant.id
                        )
                        test["CAM"] = test["CAM"].apply(lambda x: current_cam.id)
                        # Read in information from csvs
                        test.to_csv(data)
                        imported_data = dataset.load(open(data).read())
                        blocks_imported = current_cam.block_set.all()
                        logger.debug(
                            f"Imported blocks: {[block.id for block in blocks_imported]}"
                        )
                        if ct == 0:  # first csv is blocks.csv
                            result = block_resource.import_data(
                                imported_data, dry_run=True
                            )  # Test the data import
                            if not result.has_errors():
                                block_resource.import_data(
                                    imported_data, dry_run=False
                                )  # Actually import now
                            else:
                                logger.error(
                                    f"Error in reading in concepts: {result.row_errors()}"
                                )
                        else:  # Second csv is links.csv
                            result = link_resource.import_data(
                                imported_data, dry_run=True
                            )  # Test the data import
                            if not result.has_errors():
                                link_resource.import_data(
                                    imported_data, dry_run=False
                                )  # Actually import now
                            else:
                                logger.error(
                                    f"Error in reading in links: {result.row_errors()}"
                                )
                        ct += 1
                    else:
                        pass

                    # We now have to clean up the blocks' links...
            blocks_imported = cam.block_set.all()
            for block in blocks_imported:
                # Clean up Comments ('none' -> '')
                if block.comment == "None" or block.comment == "none":
                    block.comment = ""
                # if deletable is not None:
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
    """
    if request.method != "POST":
        return HttpResponse("Invalid request method", status=400)

    user_ = request.user
    cam_id = request.POST.get("cam_id")

    if not cam_id:
        return HttpResponse("No CAM ID provided", status=400)

    try:
        # Verify CAM exists
        CAM.objects.get(id=cam_id)
        user_.active_cam_num = cam_id
        user_.save()
        return HttpResponse("Success")
    except CAM.DoesNotExist:
        return HttpResponse("CAM not found", status=404)


def delete_cam(request):
    """
    Delete a CAM owned by the user
    """
    if request.method != "POST":
        return HttpResponse("Invalid request method", status=400)

    cam_id = request.POST.get("cam_id")
    if not cam_id:
        return HttpResponse("No CAM ID provided", status=400)

    try:
        curr_cam = CAM.objects.get(id=cam_id)
    except CAM.DoesNotExist:
        return HttpResponse("CAM not found", status=404)

    # Check if the user owns this CAM
    if curr_cam.user != request.user:
        return HttpResponse("Unauthorized", status=403)

    logger.debug(f"Deleting CAM: {curr_cam}")
    curr_cam.delete()
    return HttpResponse("Deleted")


def update_cam_name(request):
    """
    Update CAM name and description
    """
    if request.method != "POST":
        return HttpResponse("Invalid request method", status=400)

    cam_id = request.POST.get("cam_id")
    if not cam_id:
        return HttpResponse("No CAM ID provided", status=400)

    try:
        curr_cam = CAM.objects.get(id=cam_id)
    except CAM.DoesNotExist:
        return HttpResponse("CAM not found", status=404)

    new_name = request.POST.get("new_name")
    new_description = request.POST.get("description")

    if new_name:
        logger.debug(f"Updating CAM {curr_cam.id} with name: {new_name}")
        curr_cam.name = new_name

    if new_description is not None:  # Allow empty string
        curr_cam.description = new_description

    curr_cam.save()
    logger.debug(f"CAM updated: {curr_cam}")
    return HttpResponse("Name Updated")


def download_cam(request):
    """
    Download a CAM as a ZIP file containing blocks and links CSVs
    """
    if request.method != "GET":
        return HttpResponse("Invalid request method", status=400)

    cam_id = request.GET.get("pk") or request.GET.get("cam_id")
    if not cam_id:
        return HttpResponse("No CAM ID provided", status=400)

    try:
        current_cam = CAM.objects.get(id=cam_id)
    except CAM.DoesNotExist:
        return HttpResponse("CAM not found", status=404)

    # Export blocks and links
    block_resource = BlockResource().export(current_cam.block_set.all()).csv
    link_resource = LinkResource().export(current_cam.link_set.all()).csv
    outfile = BytesIO()
    names = ["blocks", "links"]
    ct = 0

    with ZipFile(outfile, "w") as zf:
        for resource in [block_resource, link_resource]:
            zf.writestr("{}.csv".format(names[ct]), resource)
            ct += 1
        # Optionally include CAM image if available
        if current_cam.cam_image:
            try:
                zf.write(str(current_cam.cam_image))
            except Exception as e:
                logger.warning(f"Could not include CAM image: {e}")

    response = HttpResponse(outfile.getvalue(), content_type="application/octet-stream")
    response["Content-Disposition"] = (
        'attachment; filename="' + current_cam.user.username + '_CAM.zip"'
    )
    return response


def initial_cam(request):
    """
    Download all CAMs for a project as a ZIP file
    """
    if request.method != "GET":
        return HttpResponse("Invalid request method", status=400)

    project_id = request.GET.get("pk")
    if not project_id:
        return HttpResponse("No project ID provided", status=400)

    try:
        current_project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return HttpResponse("Project not found", status=404)

    outfile = BytesIO()
    with ZipFile(outfile, "w") as zf:
        for current_cam in current_project.cam_set.all():
            block_resource = BlockResource().export(current_cam.block_set.all()).csv
            link_resource = LinkResource().export(current_cam.link_set.all()).csv
            names = ["blocks", "links"]
            ct = 0
            for resource in [block_resource, link_resource]:
                zf.writestr(
                    "{}.csv".format(current_cam.user.username + "_" + names[ct]),
                    resource,
                )
                ct += 1

    response = HttpResponse(outfile.getvalue(), content_type="application/octet-stream")
    response["Content-Disposition"] = (
        'attachment; filename="' + request.user.username + '_CAM.zip"'
    )
    return response


def create_individual_cam_randomUser(request, user_):
    """
    Create New CAM not tied to a project
    # TODO:TEST
    """
    # Get current number of cams for user and add one to value
    num = user_.cam_set.count() + 1
    form = IndividualCAMCreationForm(
        {"name": user_.username + str(num), "user": user_.id}
    )  # Fill in form
    if form.is_valid():
        cam = form.save()
        user_.active_cam_num = cam.id
        user_.save()
        cam.creation_date = datetime.datetime.now()
        cam.save()
    content = {
        "user": user_,
    }
    # Set user's current CAM to this newly created CAM
    return render(request, "base/index.html", content)


def clone_CAM(request):
    """
    Clone a CAM for a user
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    original_cam_id = request.POST.get("cam_id")
    if not original_cam_id:
        return JsonResponse({"error": "No CAM ID provided"}, status=400)

    try:
        user_ = User.objects.get(username=request.user.username)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    try:
        cam_ = CAM.objects.get(id=original_cam_id)
    except CAM.DoesNotExist:
        return JsonResponse({"error": "CAM not found"}, status=404)

    # Store original values before cloning
    original_user = cam_.user
    original_project = cam_.project
    original_description = cam_.description
    original_cam_image = cam_.cam_image
    original_name = cam_.name

    # Get blocks and links BEFORE modifying cam_ - force evaluation with list()
    blocks_ = list(cam_.block_set.all())
    links_ = list(cam_.link_set.all())
    link_dict = {}

    cam_.pk = None  # Give new primary key
    # Get current number of cams for user and add one to value
    num = user_.cam_set.count() + 1
    # Check if new name is provided in POST request
    new_name = request.POST.get("new_name")
    cam_.name = new_name if new_name else original_name + "_clone"
    cam_.user = original_user
    cam_.project = original_project
    cam_.description = original_description
    cam_.cam_image = original_cam_image
    cam_.save()  # Save new CAM
    logger.info(f"Cloning CAM {original_name} for user {user_.username}")
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
                # link_blocks[link_blocks == old_id] = block_.pk
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

    return JsonResponse({"message": "Success", "cloned_cam_id": cam_.id})


def clone_CAM_call(user, cam_id):
    """
    Clone a CAM for a user. This is called by join_project_link in views_Project.py
    """
    user_ = user
    cam_ = CAM.objects.get(id=cam_id)  # Get current CAM

    # Store original values before cloning
    original_user = cam_.user
    original_project = cam_.project
    original_description = cam_.description
    original_cam_image = cam_.cam_image
    original_name = cam_.name

    # Get blocks and links BEFORE modifying cam_ - force evaluation with list()
    blocks_ = list(cam_.block_set.all())
    links_ = list(cam_.link_set.all())
    link_dict = {}

    cam_.pk = None  # Give new primary key
    # Get current number of cams for user and add one to value
    num = user_.cam_set.count() + 1
    cam_.name = original_name + "_clone"
    cam_.user = original_user
    cam_.project = original_project
    cam_.description = original_description
    cam_.cam_image = original_cam_image
    cam_.save()  # Save new CAM
    logger.info(f"Cloning CAM {original_name} for user {user_.username}")
    # Create dictionary for links  {link: [start_concept_new, end_concept_new]}
    for link_ in links_:
        link_dict[link_.pk] = [link_.starting_block.id, link_.ending_block.id]
    # Add blocks and links
    for block_ in blocks_:
        logger.debug(f"Cloning block: {block_}")
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
                # link_blocks[link_blocks == old_id] = block_.pk
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

    return cam_  # Return the cloned CAM object
