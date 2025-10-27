"""
Business logic services for block operations.
Extracted from views.py to improve testability and separation of concerns.
"""

from django.forms.models import model_to_dict
from datetime import datetime
import numpy as np

from users.models import CAM, logCamActions
from .models import Block
from .forms import BlockForm


# ==================== Shape Constants ====================

SHAPE_MAPPING = {
    "0": "negative strong",
    "1": "negative",
    "2": "negative weak",
    "3": "neutral",
    "4": "positive weak",
    "5": "positive",
    "6": "positive strong",
    "7": "ambivalent",
}


def trans_slide_to_shape(slide_val):
    """
    Translate between slider value and shape name.

    Args:
        slide_val (str): Slider value (0-7)

    Returns:
        str: Shape name
    """
    return SHAPE_MAPPING.get(str(slide_val), "neutral")


# ==================== Block Validation ====================


def validate_block_number(cam, block_num):
    """
    Validate that a block number doesn't already exist in the CAM.

    Args:
        cam (CAM): The CAM object
        block_num (str/int): Block number to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Convert block_num to float for comparison (num field is a FloatField)
        try:
            block_num_float = float(block_num)
        except (ValueError, TypeError):
            return False, "Invalid block number format"

        blocks_existing = cam.block_set.all().values_list("num", flat=True)
        if block_num_float in blocks_existing:
            return False, "Block number already exists"
        return True, ""
    except Exception as e:
        return False, str(e)


def validate_block_number_exists(cam, block_num):
    """
    Validate that a block number exists in the CAM.

    Args:
        cam (CAM): The CAM object
        block_num (str/int): Block number to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Convert block_num to float for comparison (num field is a FloatField)
        try:
            block_num_float = float(block_num)
        except (ValueError, TypeError):
            return False, "Invalid block number format"

        blocks_existing = cam.block_set.all().values_list("num", flat=True)
        if block_num_float not in blocks_existing:
            return False, "Block number does not exist"
        return True, ""
    except Exception as e:
        return False, str(e)


def parse_dimension_from_px(dimension_str):
    """
    Parse a dimension string that may contain 'px' suffix.

    Args:
        dimension_str (str): Dimension string (e.g., "100px" or "100")

    Returns:
        tuple: (value, success) where value is float or None
    """
    try:
        if isinstance(dimension_str, str):
            dimension_str = dimension_str.rstrip("px")
        return float(dimension_str), True
    except (ValueError, TypeError):
        return None, False


# ==================== Block CRUD Operations ====================


def create_block(cam, user, block_data):
    """
    Create a new block in the CAM.

    Args:
        cam (CAM): The CAM object
        user (User): The user creating the block
        block_data (dict): Block data with keys:
            - title (str)
            - shape (str): Shape name (e.g., "positive")
            - num (str): Block number
            - x_pos (float)
            - y_pos (float)
            - width (float)
            - height (float)
            - comment (str, optional)

    Returns:
        tuple: (block, success, error_message)
    """
    try:
        # Validate block number doesn't exist
        is_valid, error = validate_block_number(cam, block_data.get("num"))
        if not is_valid:
            return None, False, error

        # Prepare block data
        form_data = {
            "title": block_data.get("title", ""),
            "shape": block_data.get("shape", "neutral"),
            "num": block_data.get("num"),
            "x_pos": block_data.get("x_pos", 0),
            "y_pos": block_data.get("y_pos", 0),
            "width": block_data.get("width", 150),
            "height": block_data.get("height", 100),
            "comment": block_data.get("comment", ""),
            "CAM": cam.id,
            "creator": user.id if user.is_authenticated else 1,
        }

        form_block = BlockForm(form_data)
        if not form_block.is_valid():
            return None, False, str(form_block.errors)

        block = form_block.save()
        return block, True, ""
    except Exception as e:
        return None, False, str(e)


def update_block_data(block, block_data):
    """
    Update an existing block with new data.

    Args:
        block (Block): The block to update
        block_data (dict): Block data with keys:
            - title (str, optional)
            - shape (str, optional)
            - comment (str, optional)
            - x_pos (float, optional)
            - y_pos (float, optional)
            - width (float, optional)
            - height (float, optional)

    Returns:
        tuple: (block, success, error_message)
    """
    try:
        update_fields = {}

        # Process each field
        if "title" in block_data:
            update_fields["title"] = block_data["title"]

        if "shape" in block_data:
            update_fields["shape"] = block_data["shape"]

        if "comment" in block_data:
            # Strip newlines from comment
            comment = block_data["comment"]
            if isinstance(comment, str):
                comment = comment.strip("\n")
            update_fields["comment"] = comment

        # Parse position and dimension data
        for field in ["x_pos", "y_pos", "width", "height"]:
            if field in block_data:
                value, success = parse_dimension_from_px(block_data[field])
                if success:
                    update_fields[field] = value

        # Add timestamp
        if update_fields:
            update_fields["timestamp"] = datetime.now()

        # Update using model's update method
        block.update(update_fields)
        return block, True, ""
    except Exception as e:
        return None, False, str(e)


def resize_block_dimensions(block, width=None, height=None):
    """
    Resize a block's dimensions.

    Args:
        block (Block): The block to resize
        width (str/float, optional): New width (may contain 'px')
        height (str/float, optional): New height (may contain 'px')

    Returns:
        tuple: (block, success, error_message)
    """
    try:
        if width:
            width_val, success = parse_dimension_from_px(width)
            if success:
                block.width = width_val

        if height:
            height_val, success = parse_dimension_from_px(height)
            if success:
                block.height = height_val

        block.save()
        return block, True, "Block resized successfully"
    except Exception as e:
        return None, False, str(e)


def set_all_blocks_resizable(cam, resizable):
    """
    Set the resizable property for all blocks in a CAM.

    Args:
        cam (CAM): The CAM object
        resizable (bool): Whether blocks should be resizable

    Returns:
        tuple: (count, success, error_message)
    """
    try:
        blocks = cam.block_set.all()
        for block in blocks:
            block.resizable = resizable
            block.save()
        return blocks.count(), True, "Blocks resizable status updated"
    except Exception as e:
        return 0, False, str(e)


def update_block_text_scale(block, text_scale):
    """
    Update the text scale of a block.

    Args:
        block (Block): The block to update
        text_scale (str/float): New text scale value

    Returns:
        tuple: (block, success, error_message)
    """
    try:
        try:
            text_scale = float(text_scale)
        except (ValueError, TypeError):
            text_scale = 14  # Default value

        block.update({"text_scale": text_scale})
        return block, True, f"Text scale updated to {text_scale}"
    except Exception as e:
        return None, False, str(e)


# ==================== Block Deletion ====================


def get_next_action_id(cam):
    """
    Get the next action ID for logging in a CAM.

    Args:
        cam (CAM): The CAM object

    Returns:
        int: Next action ID
    """
    try:
        latest = cam.logcamactions_set.latest("actionId")
        return latest.actionId + 1
    except:
        return 0


def log_block_deletion(cam, block, action_id):
    """
    Log a block deletion to the action history.

    Args:
        cam (CAM): The CAM object
        block (Block): The deleted block
        action_id (int): Action ID for logging

    Returns:
        tuple: (log_entry, success, error_message)
    """
    try:
        log_entry = logCamActions(
            camId=cam,
            actionId=action_id,
            actionType=0,  # 0 = deleting
            objType=1,  # 1 = block
            objDetails=model_to_dict(block),
        )
        log_entry.save()
        return log_entry, True, ""
    except Exception as e:
        return None, False, str(e)


def log_link_deletion(cam, link, action_id):
    """
    Log a link deletion to the action history.

    Args:
        cam (CAM): The CAM object
        link (Link): The deleted link
        action_id (int): Action ID for logging

    Returns:
        tuple: (log_entry, success, error_message)
    """
    try:
        log_entry = logCamActions(
            camId=cam,
            actionId=action_id,
            actionType=0,  # 0 = deleting
            objType=0,  # 0 = link
            objDetails=model_to_dict(link),
        )
        log_entry.save()
        return log_entry, True, ""
    except Exception as e:
        return None, False, str(e)


def cleanup_old_action_logs(cam, keep_count=10):
    """
    Remove oldest action logs, keeping only the most recent ones.

    Args:
        cam (CAM): The CAM object
        keep_count (int): Number of distinct action IDs to keep

    Returns:
        tuple: (deleted_count, success, error_message)
    """
    try:
        action_ids = (
            cam.logcamactions_set.order_by()
            .values_list("actionId", flat=True)
            .distinct()
        )

        if action_ids.count() > keep_count:
            min_action_id = int(np.amin(list(action_ids)))
            deleted_count, _ = logCamActions.objects.filter(
                actionId=min_action_id
            ).delete()
            return deleted_count, True, f"Deleted {deleted_count} old action logs"

        return 0, True, "No cleanup needed"
    except Exception as e:
        return 0, False, str(e)


def delete_block_with_logging(cam, block):
    """
    Delete a block and its related links, with full action logging.

    Args:
        cam (CAM): The CAM object
        block (Block): The block to delete

    Returns:
        tuple: (deleted_links, success, error_message)
    """
    try:
        # Check if block can be deleted (modifiable field)
        if block.modifiable is False:
            return [], False, "This block cannot be deleted"

        # Get related links
        related_links = cam.link_set.filter(
            starting_block=block.id
        ) | cam.link_set.filter(ending_block=block.id)
        deleted_links = [model_to_dict(link) for link in related_links]

        # Get next action ID
        action_id = get_next_action_id(cam)

        # Log block deletion
        log_block_deletion(cam, block, action_id)

        # Log each link deletion
        for link in related_links:
            log_link_deletion(cam, link, action_id)

        # Delete the block (links will cascade due to DB relations)
        block.delete()

        # Cleanup old logs
        cleanup_old_action_logs(cam)

        return deleted_links, True, ""
    except Exception as e:
        return [], False, str(e)


# ==================== Block Position & Link Data ====================


def get_links_for_block(cam, block):
    """
    Get all links associated with a block (both starting and ending).

    Args:
        cam (CAM): The CAM object
        block (Block): The block

    Returns:
        QuerySet: Links related to the block
    """
    return cam.link_set.filter(starting_block=block.id) | cam.link_set.filter(
        ending_block=block.id
    )


def get_links_data_for_block(cam, block):
    """
    Get formatted link data for a block that was moved (for UI update).

    Args:
        cam (CAM): The CAM object
        block (Block): The moved block

    Returns:
        dict: Link data with positions and styles
    """
    links = get_links_for_block(cam, block)

    link_data = {
        "id": [],
        "start_x": [],
        "start_y": [],
        "end_x": [],
        "end_y": [],
        "style": [],
        "width": [],
        "starting_block": [],
        "ending_block": [],
    }

    for link in links:
        link_data["id"].append(link.id)
        link_data["start_x"].append(link.starting_block.x_pos)
        link_data["start_y"].append(link.starting_block.y_pos)
        link_data["end_x"].append(link.ending_block.x_pos)
        link_data["end_y"].append(link.ending_block.y_pos)
        link_data["style"].append(link.line_style)
        link_data["starting_block"].append(link.starting_block.num)
        link_data["ending_block"].append(link.ending_block.num)

    return link_data


def update_block_position(
    block, x_pos, y_pos, width=None, height=None, text_scale=None
):
    """
    Update block position and optionally dimensions and text scale.

    Args:
        block (Block): The block to update
        x_pos (str/float): New X position (may contain 'px')
        y_pos (str/float): New Y position (may contain 'px')
        width (str/float, optional): New width
        height (str/float, optional): New height
        text_scale (str/float, optional): New text scale

    Returns:
        tuple: (block, success, error_message)
    """
    try:
        x_val, x_ok = parse_dimension_from_px(x_pos)
        y_val, y_ok = parse_dimension_from_px(y_pos)

        if not (x_ok and y_ok):
            return None, False, "Invalid position values"

        block.x_pos = x_val
        block.y_pos = y_val

        if width:
            w_val, w_ok = parse_dimension_from_px(width)
            if w_ok:
                block.width = w_val

        if height:
            h_val, h_ok = parse_dimension_from_px(height)
            if h_ok:
                block.height = h_val

        if text_scale:
            try:
                block.text_scale = float(text_scale)
            except (ValueError, TypeError):
                pass

        block.save()
        return block, True, ""
    except Exception as e:
        return None, False, str(e)
