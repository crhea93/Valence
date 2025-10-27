from django.http import JsonResponse
from link.models import Link
from link.forms import LinkForm
from datetime import datetime
from users.models import CAM

from .services import (
    check_link_exists,
    create_link as create_link_service,
    update_link_style,
    delete_link as delete_link_service,
    swap_link_direction as swap_direction_service,
    get_link_position_data,
    get_block_links_by_num,
)


def add_link(request):
    """
    Create a new link between two blocks. Validates that the link doesn't already exist
    and returns link data for the frontend.
    """
    if request.method != "POST":
        return JsonResponse({})

    link_valid = request.POST.get("link_valid")
    if not link_valid:
        return JsonResponse({})

    try:
        cam = CAM.objects.get(id=request.user.active_cam_num)
        start_block = cam.block_set.get(num=request.POST.get("starting_block"))
        end_block = cam.block_set.get(num=request.POST.get("ending_block"))

        # Get link styling
        line_style = request.POST.get("line_style", "solid")
        arrow_type = request.POST.get("arrow_type", "->")

        # Create link using service
        link, success, error = create_link_service(
            cam, request.user, start_block, end_block, line_style, arrow_type
        )

        if not success:
            return JsonResponse({"error": error}, status=400)

        # Return link data for frontend
        response_data = get_link_position_data(link)
        response_data["num_link"] = link.id

        return JsonResponse(response_data)

    except CAM.DoesNotExist:
        return JsonResponse({"error": "CAM not found"}, status=404)
    except Link.DoesNotExist:
        return JsonResponse({"error": "Block not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def update_link(request):
    """
    Update link styling properties (line style and arrow type).
    Returns updated link data for the frontend.
    """
    if request.method != "POST":
        return JsonResponse({})

    try:
        link_id = request.POST.get("link_id")
        link = Link.objects.get(id=link_id)

        # Get updated styling
        line_style = request.POST.get("line_style")
        arrow_type = request.POST.get("arrow_type")

        # Update link using service
        link, success, error = update_link_style(link, line_style, arrow_type)

        if not success:
            return JsonResponse({"error": error}, status=400)

        # Return updated link data
        return JsonResponse(get_link_position_data(link))

    except Link.DoesNotExist:
        return JsonResponse({"error": "Link not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def update_link_pos(request):
    """
    Update link styling properties. Alias for update_link for backwards compatibility.
    """
    if request.method != "POST":
        return JsonResponse({})

    try:
        link_id = request.POST.get("link_id")
        link = Link.objects.get(id=link_id)

        # Get updated styling
        line_style = request.POST.get("line_style")
        arrow_type = request.POST.get("arrow_type")

        # Update link using service
        link, success, error = update_link_style(link, line_style, arrow_type)

        if not success:
            return JsonResponse({"error": error}, status=400)

        # Return link data
        return JsonResponse(
            {
                "line_style": link.line_style,
                "arrow_type": link.arrow_type,
                "id": link.id,
                "starting_block": link.starting_block.id,
                "ending_block": link.ending_block.id,
            }
        )

    except Link.DoesNotExist:
        return JsonResponse({"error": "Link not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def swap_link_direction(request):
    """
    Reverse the direction of a link (swap starting and ending blocks).
    Returns updated link data for the frontend.
    """
    if request.method != "POST":
        return JsonResponse({})

    try:
        link_id = request.POST.get("link_id")
        link = Link.objects.get(id=link_id)

        # Swap direction using service
        link, success, error = swap_direction_service(link)

        if not success:
            return JsonResponse({"error": error}, status=400)

        # Return updated link data
        return JsonResponse(get_link_position_data(link))

    except Link.DoesNotExist:
        return JsonResponse({"error": "Link not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def delete_link(request):
    """
    Delete a link from the CAM.
    """
    if request.method != "POST":
        return JsonResponse({})

    link_delete_valid = request.POST.get("link_delete_valid")
    if not link_delete_valid:
        return JsonResponse({})

    try:
        link_id = request.POST.get("link_id")
        link = Link.objects.get(id=link_id)

        # Delete link using service
        success, error = delete_link_service(link)

        if not success:
            return JsonResponse({"error": error}, status=400)

        return JsonResponse({})

    except Link.DoesNotExist:
        return JsonResponse({"error": "Link not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
