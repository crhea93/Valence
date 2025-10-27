from .forms import BlockForm
from .models import Block
from django.http import JsonResponse
from django.template.defaulttags import register
from datetime import datetime
from django.forms.models import model_to_dict
from users.models import CAM, logCamActions
from django.contrib.auth import get_user_model
import numpy as np

from .services import (
    trans_slide_to_shape,
    validate_block_number,
    validate_block_number_exists,
    create_block,
    update_block_data,
    resize_block_dimensions,
    set_all_blocks_resizable,
    update_block_text_scale,
    delete_block_with_logging,
    get_links_data_for_block,
    update_block_position,
)

User = get_user_model()


@register.filter
def get_range(value):
    return range(value)


@register.filter
def get_links(link_set):
    link_ids = [link.id for link in link_set.all()]
    return link_ids


@register.filter
def integer(val):
    return int(val)


def add_block(request):
    """
    Add a block to the CAM. Block data is passed via AJAX from the frontend,
    created in the database, and returned with additional metadata for the canvas.
    """
    response_data = {}

    # Check authentication
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=403)

    if request.method != "POST":
        return JsonResponse(response_data)

    add_valid = request.POST.get("add_valid")
    if not add_valid:
        return JsonResponse(response_data)

    try:
        cam = CAM.objects.get(id=request.user.active_cam_num)

        # Prepare block data from request
        block_data = {
            "title": request.POST.get("title", ""),
            "shape": trans_slide_to_shape(request.POST.get("shape")),
            "num": request.POST.get("num_block"),
            "x_pos": request.POST.get("x_pos", 0),
            "y_pos": request.POST.get("y_pos", 0),
            "width": request.POST.get("width", 150),
            "height": request.POST.get("height", 100),
            "comment": "",  # Initially no comment
        }

        # Create block using service
        block, success, error = create_block(cam, request.user, block_data)

        if not success:
            return JsonResponse({"error": error}, status=400)

        # Prepare response
        response_data["id"] = block.id
        response_data["title"] = block.title
        response_data["shape"] = (
            "rounded-circle" if block.shape == "circle" else block.shape
        )
        response_data["num"] = block.num
        response_data["x_pos"] = block.x_pos
        response_data["y_pos"] = block.y_pos
        response_data["width"] = block.width
        response_data["height"] = block.height
        response_data["comment"] = block.comment
        response_data["links"] = block.links if hasattr(block, "links") else []

    except CAM.DoesNotExist:
        return JsonResponse({"error": "CAM not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(response_data)


def update_block(request):
    """
    Update block information. Validates block exists and updates all provided fields.
    Returns updated block data for the canvas.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    update_valid = request.POST.get("update_valid")
    if not update_valid:
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        cam = CAM.objects.get(id=request.user.active_cam_num)
        block_num = request.POST.get("num_block")

        # Validate block number exists
        is_valid, error = validate_block_number_exists(cam, block_num)
        if not is_valid:
            return JsonResponse({"error": error}, status=404)

        block = cam.block_set.get(num=block_num)

        # Prepare update data
        block_data = {
            "title": request.POST.get("title"),
            "shape": trans_slide_to_shape(request.POST.get("shape")),
            "comment": request.POST.get("comment"),
            "x_pos": request.POST.get("x_pos"),
            "y_pos": request.POST.get("y_pos"),
            "width": request.POST.get("width"),
            "height": request.POST.get("height"),
        }

        # Update block using service
        block, success, error = update_block_data(block, block_data)

        if not success:
            return JsonResponse({"error": error}, status=400)

        # Return updated data
        return JsonResponse(
            {
                "title": block.title,
                "shape": block.shape,
                "comment": block.comment,
                "x_pos": block.x_pos,
                "y_pos": block.y_pos,
                "width": block.width,
                "height": block.height,
            }
        )

    except CAM.DoesNotExist:
        return JsonResponse({"error": "CAM not found"}, status=404)
    except Block.DoesNotExist:
        return JsonResponse({"error": "Block not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def resize_block(request):
    """
    Resize a block's dimensions or toggle resizable property for all blocks in CAM.
    """
    if request.method != "POST":
        return JsonResponse({"resize_message": "Invalid request"}, status=400)

    try:
        cam = CAM.objects.get(id=request.user.active_cam_num)

        # Check if this is a dimension resize
        resize_valid = request.POST.get("resize_valid")
        if resize_valid:
            block_id = request.POST.get("block_id")
            width = request.POST.get("width")
            height = request.POST.get("height")

            block = cam.block_set.get(num=block_id)
            block, success, message = resize_block_dimensions(block, width, height)

            if not success:
                return JsonResponse({"resize_message": message}, status=400)

            return JsonResponse({"resize_message": message})

        # Otherwise toggle resizable for all blocks
        update_valid = request.POST.get("update_valid")
        if not update_valid:
            return JsonResponse({"resize_message": "Invalid request"}, status=400)

        resize_bool_str = request.POST.get("resize")
        resizable = resize_bool_str == "True"

        count, success, message = set_all_blocks_resizable(cam, resizable)

        return JsonResponse({"resize_message": message})

    except CAM.DoesNotExist:
        return JsonResponse({"resize_message": "CAM not found"}, status=404)
    except Block.DoesNotExist:
        return JsonResponse({"resize_message": "Block not found"}, status=404)
    except Exception as e:
        return JsonResponse({"resize_message": str(e)}, status=500)


def delete_block(request):
    """
    Delete a block from the CAM. Also deletes all associated links and logs the deletion.
    Returns list of deleted links for the frontend to update the canvas.
    """
    if request.method != "POST":
        return JsonResponse({"links": []})

    delete_valid = request.POST.get("delete_valid")
    if not delete_valid:
        return JsonResponse({"links": []})

    try:
        cam = CAM.objects.get(id=request.user.active_cam_num)
        block_id = request.POST.get("block_id")
        block = cam.block_set.get(num=block_id)

        # Check if block is modifiable (can be deleted)
        if block.modifiable is False:
            return JsonResponse({"error": "This block cannot be deleted"}, status=403)

        # Delete block with logging (handles links and action logs)
        deleted_links, success, error = delete_block_with_logging(cam, block)

        if not success:
            return JsonResponse({"error": error}, status=400)

        return JsonResponse({"links": deleted_links})

    except CAM.DoesNotExist:
        return JsonResponse({"error": "CAM not found"}, status=404)
    except Block.DoesNotExist:
        return JsonResponse({"error": "Block not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def drag_function(request):
    """
    Update block position when dragged on canvas. Returns updated link data for
    all links connected to the block so the frontend can update them visually.
    """
    if request.method != "POST":
        return JsonResponse({})

    drag_valid = request.POST.get("drag_valid")
    if not drag_valid:
        return JsonResponse({})

    try:
        cam = CAM.objects.get(id=request.user.active_cam_num)
        block_id = request.POST.get("block_id")
        block = cam.block_set.get(num=block_id)

        # Get position and dimension data
        x_pos = request.POST.get("x_pos")
        y_pos = request.POST.get("y_pos")
        width = request.POST.get("width")
        height = request.POST.get("height")
        text_scale = request.POST.get("text_scale")

        # Update block position using service
        block, success, error = update_block_position(
            block, x_pos, y_pos, width, height, text_scale
        )

        if not success:
            return JsonResponse({"error": error}, status=400)

        # Get link data for all related links
        link_data = get_links_data_for_block(cam, block)

        return JsonResponse(link_data)

    except CAM.DoesNotExist:
        return JsonResponse({"error": "CAM not found"}, status=404)
    except Block.DoesNotExist:
        return JsonResponse({"error": "Block not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def update_text_size(request):
    """
    Update the text scale/size of a block.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        # Accept both text_scale and text_size parameter names
        new_text_scale = request.POST.get("text_scale") or request.POST.get("text_size")
        block_id = request.POST.get("block_id")

        cam = CAM.objects.get(id=request.user.active_cam_num)
        block = cam.block_set.get(num=block_id)

        # Update text scale using service
        block, success, message = update_block_text_scale(block, new_text_scale)

        if not success:
            return JsonResponse({"error": message}, status=400)

        return JsonResponse({"message": message})

    except CAM.DoesNotExist:
        return JsonResponse({"error": "CAM not found"}, status=404)
    except Block.DoesNotExist:
        return JsonResponse({"error": "Block not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
