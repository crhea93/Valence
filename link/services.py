"""
Business logic services for link operations.
Extracted from views.py to improve testability and separation of concerns.
"""

from datetime import datetime
from django.forms.models import model_to_dict

from users.models import CAM
from .models import Link
from .forms import LinkForm


# ==================== Link Validation ====================


def check_link_exists(cam, starting_block_num, ending_block_num):
    """
    Check if a link already exists between two blocks.

    Args:
        cam (CAM): The CAM object
        starting_block_num (str/int): Starting block number
        ending_block_num (str/int): Ending block number

    Returns:
        tuple: (exists, link_or_none)
    """
    try:
        existing_link = (
            cam.link_set.filter(starting_block__num=starting_block_num)
            .filter(ending_block__num=ending_block_num)
            .first()
        )

        return existing_link is not None, existing_link
    except Exception as e:
        return False, None


# ==================== Link CRUD Operations ====================


def create_link(
    cam, user, starting_block, ending_block, line_style="solid", arrow_type="->"
):
    """
    Create a new link between two blocks.

    Args:
        cam (CAM): The CAM object
        user (User): The user creating the link
        starting_block (Block): Starting block
        ending_block (Block): Ending block
        line_style (str): Line style (default: "solid")
        arrow_type (str): Arrow type (default: "->")

    Returns:
        tuple: (link, success, error_message)
    """
    try:
        # Check if link already exists
        exists, _ = check_link_exists(cam, starting_block.num, ending_block.num)
        if exists:
            return None, False, "Link already exists between these blocks"

        # Prepare link data
        link_data = {
            "starting_block": starting_block.id,
            "ending_block": ending_block.id,
            "line_style": line_style,
            "arrow_type": arrow_type,
            "CAM": cam.id,
            "creator": user.id if user.is_authenticated else 1,
        }

        form_link = LinkForm(link_data)
        if not form_link.is_valid():
            return None, False, str(form_link.errors)

        link = form_link.save()
        link.timestamp = datetime.now()
        link.save()

        return link, True, ""
    except Exception as e:
        return None, False, str(e)


def update_link_style(link, line_style=None, arrow_type=None):
    """
    Update link styling properties.

    Args:
        link (Link): The link to update
        line_style (str, optional): New line style
        arrow_type (str, optional): New arrow type

    Returns:
        tuple: (link, success, error_message)
    """
    try:
        update_data = {}

        if line_style is not None:
            update_data["line_style"] = line_style

        if arrow_type is not None:
            update_data["arrow_type"] = arrow_type

        if update_data:
            link.update(update_data)

        link.timestamp = datetime.now()
        link.save()

        return link, True, ""
    except Exception as e:
        return None, False, str(e)


def delete_link(link):
    """
    Delete a link.

    Args:
        link (Link): The link to delete

    Returns:
        tuple: (success, error_message)
    """
    try:
        link_id = link.id
        link.delete()
        return True, f"Link {link_id} deleted"
    except Exception as e:
        return False, str(e)


# ==================== Link Position & Direction ====================


def swap_link_direction(link):
    """
    Reverse the direction of a link (swap starting and ending blocks).

    Args:
        link (Link): The link to reverse

    Returns:
        tuple: (link, success, error_message)
    """
    try:
        # Swap the blocks
        new_starting_block = link.ending_block
        new_ending_block = link.starting_block

        link.starting_block = new_starting_block
        link.ending_block = new_ending_block
        link.timestamp = datetime.now()
        link.save()

        return link, True, ""
    except Exception as e:
        return None, False, str(e)


def get_link_position_data(link):
    """
    Get formatted position data for a link (for UI rendering).

    Args:
        link (Link): The link

    Returns:
        dict: Position and metadata for the link
    """
    return {
        "id": link.id,
        "start_x": link.starting_block.x_pos,
        "start_y": link.starting_block.y_pos,
        "end_x": link.ending_block.x_pos,
        "end_y": link.ending_block.y_pos,
        "line_style": link.line_style,
        "arrow_type": link.arrow_type,
        "starting_block": link.starting_block.num,
        "ending_block": link.ending_block.num,
    }


def get_multiple_links_position_data(links):
    """
    Get formatted position data for multiple links.

    Args:
        links (QuerySet): Links to format

    Returns:
        dict: Aggregated position data for multiple links
    """
    link_data = {
        "id": [],
        "start_x": [],
        "start_y": [],
        "end_x": [],
        "end_y": [],
        "line_style": [],
        "arrow_type": [],
        "starting_block": [],
        "ending_block": [],
    }

    for link in links:
        link_data["id"].append(link.id)
        link_data["start_x"].append(link.starting_block.x_pos)
        link_data["start_y"].append(link.starting_block.y_pos)
        link_data["end_x"].append(link.ending_block.x_pos)
        link_data["end_y"].append(link.ending_block.y_pos)
        link_data["line_style"].append(link.line_style)
        link_data["arrow_type"].append(link.arrow_type)
        link_data["starting_block"].append(link.starting_block.num)
        link_data["ending_block"].append(link.ending_block.num)

    return link_data


# ==================== Link Retrieval Helpers ====================


def get_block_links_by_id(cam, block_id):
    """
    Get all links connected to a block by block ID.

    Args:
        cam (CAM): The CAM object
        block_id (int): Block ID

    Returns:
        QuerySet: Links connected to the block
    """
    return cam.link_set.filter(starting_block=block_id) | cam.link_set.filter(
        ending_block=block_id
    )


def get_block_links_by_num(cam, block_num):
    """
    Get all links connected to a block by block number.

    Args:
        cam (CAM): The CAM object
        block_num (str/int): Block number

    Returns:
        QuerySet: Links connected to the block
    """
    try:
        block = cam.block_set.get(num=block_num)
        return get_block_links_by_id(cam, block.id)
    except Exception:
        return cam.link_set.none()
