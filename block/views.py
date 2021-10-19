from .forms import BlockForm
from django.http import JsonResponse
from django.template.defaulttags import register
from datetime import datetime
from django.forms.models import model_to_dict
from users.models import CAM


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
    Functionality to add a block to the databaase. This functionality is called from templates/Concept/concept_placement.html
    or templates/Concept/Initial_Placement. The Jquery/Ajax call passes all block information to django. The information is
    augmented to include any other relavent features (i.e. creator id). The block is then created in the database
    via the BlockForm form defined in block/forms.py. The complete block data is then passed back to the drawing canvas.
    """
    block_data = {}
    if request.method == 'POST':
        add_valid = request.POST.get('add_valid')
        cam = CAM.objects.get(id=request.user.active_cam_num)
        blocks_existing = cam.block_set.all().values_list('num', flat=True)
        if add_valid and request.POST.get('num_block') not in blocks_existing:
            # If we are only adding a new element
            # Getting basic block information
            block_data['title'] = request.POST.get('title')
            block_data['shape'] = trans_slide_to_shape(request.POST.get('shape'))
            block_data['num'] = request.POST.get('num_block')
            block_data['x_pos'] = request.POST.get('x_pos')
            block_data['y_pos'] = request.POST.get('y_pos')
            block_data['width'] = request.POST.get('width')
            block_data['height'] = request.POST.get('height')
            block_data['comment'] = ''  # Initially no comment
            block_data['CAM'] = request.user.active_cam_num
            if request.user.is_authenticated:  # Making sure we have an authenticated user
                block_data['creator'] = request.user.id
            else:
                block_data['creator'] = 1
            form_block = BlockForm(block_data)  # Getting our block form
            block = form_block.save()  # Saving the form and getting the block
            block_data['id'] = block.id  # Additional information about block
            if block_data['shape'] == 'circle':
                block_data['shape'] = 'rounded-circle'
            block_data['links'] = []  # Need associated links for JQuery purposes
            if cam.link_set.filter(starting_block=block.id)|cam.link_set.filter(ending_block=block.id):
                block_data['links'] = block.links
    return JsonResponse(block_data)


def update_block(request):
    """
    Function to update the information associated with a block. This is called whenever a block is modified (with
    the exception of being moved/dragged -- See below for that function). This can be invoked either from templates/Concept/concept_placement.html
    or templates/Concept/Initial_Placement or templates/Concept/resize_function.html. The block data is taken from the Jquery/Ajax
    call. The block is updated using the block.update() command defined in block/model.py. The block data is returned to
    the Jquery call to update the drawing canvas.
    """
    block_data = {}
    if request.method == 'POST':
        update_valid = request.POST.get('update_valid')
        cam = CAM.objects.get(id=request.user.active_cam_num)
        blocks_existing = cam.block_set.all().values_list('num', flat=True)
        if update_valid and (request.POST.get('num_block') not in blocks_existing):
            block_num = request.POST.get('num_block')
            block = cam.block_set.all().get(num=block_num)  # Get block number
            # Fill in basic information for the block form
            block_data['title'] = request.POST.get('title')
            block_data['shape'] = trans_slide_to_shape(request.POST.get('shape'))
            block_data['num'] = block_num
            try:  # If there is a newline, be sure to strip it
                comment = request.POST.get('comment').strip('\n')
            except:  # Otherwise just take the comment
                comment = request.POST.get('comment')
            block_data['comment'] = comment
            block_data['timestamp'] = datetime.now()
            block_data['x_pos'] = float(request.POST.get('x_pos')[:-2])  # Ignore the px at the end
            block_data['y_pos'] = float(request.POST.get('y_pos')[:-2])
            block_data['width'] = float(request.POST.get('width')[:-2])  # Ignore the px at the end
            block_data['height'] = float(request.POST.get('height')[:-2])
            block.update(block_data)
            return JsonResponse(block_data)


def resize_block(request):
    """
    Function to turn on or off the resizable boolean for blocks
    """
    if request.method == 'POST':
        update_valid = request.POST.get('update_valid')
        cam = CAM.objects.get(id=request.user.active_cam_num)
        #blocks_existing = cam.block_set.all().values_list('num', flat=True)
        resize_bool = request.POST.get('resize')
        print(resize_bool)
        if update_valid:
            for block in cam.block_set.all():
                if resize_bool == 'True':
                    block.resizable = True
                else:
                    block.resizable = False
                block.save()
            for block in cam.block_set.all():
                print(block.resizable)
            message = 'Blocks resized'
        else:
            message = 'Failed to change block resizeable'
        print(message)
    return JsonResponse({'resize_message': message})
def delete_block(request):
    """
    Function to delete a block from the current CAM. The id of the block to be deleted is passed through the Jquery/Ajax call
    defined in templates/Concept/delete_block.html. After deleting the block all links associated with the block are deleted
    from the database. The function returns a list of those links so that the Jquery/Ajax call can delete from them the
    drawing canvas.
    """
    links_ = []
    if request.method == 'POST':
        delete_valid = request.POST.get('delete_valid')  # block delete
        if delete_valid:
            cam = CAM.objects.get(id=request.user.active_cam_num)
            block_id = request.POST.get('block_id')
            block = cam.block_set.get(num=block_id)
            # Delete related links
            links = cam.link_set.filter(starting_block=block.id)|cam.link_set.filter(ending_block=block.id)
            links_ = [model_to_dict(link) for link in links]
            block.delete()
    return JsonResponse({'links': links_})


def drag_function(request):
    """
    Functionality to update a block's position after it is dragged on the canvas. This call is invoked via a Jquery/Ajax
    call defined in templates/Concepts/drag_function.html. The function takes the new positions of the block and updates the current blocks
    position. Then each link associated with the block is collected and their information is passed back to the drawing
    canvas in order to be updated via a Jquery call.
    """
    if request.method == 'POST':
        drag_valid = request.POST.get('drag_valid')
        if drag_valid:
            cam = CAM.objects.get(id=request.user.active_cam_num)

            # Just need this information for later
            ids = []; starting_x_ = []; ending_x_ = []; starting_y_ = []; ending_y_ = []
            style_ = []; width_ = []; starting_block_ = []; ending_block_ = []
            # Grab block ID
            block_id = request.POST.get('block_id')
            if cam.block_set.get(num=block_id):  # Make sure block exists (it really should)
                block = cam.block_set.get(num=block_id)
                try:
                    text_scale = float(request.POST.get('text_scale'))
                except:
                    text_scale = block.text_scale
                block.x_pos = float(request.POST.get('x_pos')[:-2])  # get rid of px at the end
                block.y_pos = float(request.POST.get('y_pos')[:-2])  # Ditto
                block.width = float(request.POST.get('width')[:-2])  # get rid of px at the end
                block.height = float(request.POST.get('height')[:-2])  # Ditto
                block.text_scale = text_scale
                block.save()  # Update position
                # Link will be automatically updated, but we need to get the information to pass to JQuery!
                links = cam.link_set.filter(starting_block=block.id)|cam.link_set.filter(ending_block=block.id)
                for link in links:
                    # Get all that good info
                    ids.append(link.id); starting_x_.append(link.starting_block.x_pos); starting_y_.append(link.starting_block.y_pos)
                    ending_x_.append(link.ending_block.x_pos); ending_y_.append(link.ending_block.y_pos); style_.append(link.line_style)
                    starting_block_.append(link.starting_block.num); ending_block_.append(link.ending_block.num)
            return JsonResponse({'id':ids,'start_x':starting_x_,'start_y':starting_y_,'end_x':ending_x_,
                                 'end_y':ending_y_,'style':style_,'width':width_,'starting_block':starting_block_,
                                 'ending_block':ending_block_})



def trans_slide_to_shape(slide_val):
    """
    Translate between slider value and shape
    """
    if slide_val == '0':
        shape = 'negative strong'
    elif slide_val == '1':
        shape = 'negative'
    elif slide_val == '2':
        shape = 'negative weak'
    elif slide_val == '3':
        shape = 'neutral'
    elif slide_val == '4':
        shape = 'positive weak'
    elif slide_val == '5':
        shape = 'positive'
    elif slide_val == '6':
        shape = 'positive strong'
    elif slide_val == '7':
        shape = 'ambivalent'
    else:
        shape = 'neutral'
    return shape
