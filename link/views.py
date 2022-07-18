from django.http import JsonResponse
from link.models import Link
from link.forms import LinkForm
from datetime import datetime
from users.models import CAM


def add_link(request):
    link_data = {}
    if request.method == 'POST':
        link_valid = request.POST.get('link_valid')
        if link_valid:
            # Get the starting and ending block information
            cam = CAM.objects.get(id=request.user.active_cam_num)
            start_block = cam.block_set.get(num=request.POST.get('starting_block'))
            end_block = cam.block_set.get(num=request.POST.get('ending_block'))
            # Set up link form data
            link_data['starting_block'] = start_block.id
            link_data['ending_block'] = end_block.id
            link_data['line_style'] = request.POST.get('line_style')
            link_data['arrow_type'] = request.POST.get('arrow_type')
            link_data['CAM'] = request.user.active_cam_num
            if request.user.is_authenticated:
                link_data['creator'] = request.user.id
            else:
                link_data['creator'] = 1
            # Check that link doesn't already exist
            if cam.link_set.filter(starting_block=start_block.num).filter(ending_block=end_block.num):
                pass
            else:
                form_link = LinkForm(link_data)  # Create from for link
                print(form_link.errors)
                link = form_link.save()  # Save form for link
                link_data['num_link'] = link.id  # Getting additional information to pass to JQuery
                link_data['id'] = link.id
                link.timestamp = datetime.now()
                link.save()
                # Must change the starting and end block information to be passed to JQUERY
                link_data['starting_block'] = start_block.num
                link_data['ending_block'] = end_block.num
            return JsonResponse(link_data)


def update_link(request):
    link_data = {}
    if request.method == 'POST':
        link = Link.objects.get(id=request.POST.get("link_id"))  # Get link
        link_data['line_style'] = request.POST.get("line_style")  # Get updated link information
        link_data['arrow_type'] = request.POST.get('arrow_type')
        link.update(link_data)
        link.timestamp = datetime.now()
        link.save()
        # Get all info to pass
        link_data['start_x'] = link.starting_block.x_pos; link_data['start_y'] = link.starting_block.y_pos
        link_data['end_x'] = link.ending_block.x_pos; link_data['end_y'] = link.ending_block.y_pos
        link_data['id'] = link.id
        link_data['starting_block'] = link.starting_block.num
        link_data['ending_block'] = link.ending_block.num
        return JsonResponse(link_data)


def update_link_pos(request):
    """
    IGNORE FOR NOW!!!!!!!!!!!!!!!!!!!!!!
    NOT UPDATED
    """
    link_data = {}
    if request.method == 'POST':
        link = Link.objects.get(id=request.POST.get("link_id"))
        link.timestamp = datetime.now()
        link.save()
        # Get all info to pass
        link_data['start_x'] = request.POST.get("start_x"); link_data['start_y'] = request.POST.get("start_y")
        link_data['end_x'] = request.POST.get("end_x"); link_data['end_y'] = request.POST.get("end_y")
        link.update(link_data)
        link_data['line_style'] = link.line_style
        link_data['id'] = link.id
        link_data['starting_block'] = link.starting_block
        link_data['ending_block'] = link.ending_block
        return JsonResponse(link_data)


def swap_link_direction(request):
    """
    Change direction of link
    """
    link_data = {}
    if request.method == 'POST':
        link = Link.objects.get(id=request.POST.get("link_id"))  # Get link
        # Swap the start end end
        new_start_x = link.ending_block.x_pos; new_start_y = link.ending_block.y_pos; new_start_block = link.ending_block
        link.end_x = link.starting_block.x_pos; link.end_y = link.starting_block.y_pos; link.ending_block = link.starting_block
        link.start_x = new_start_x; link.start_y = new_start_y; link.starting_block = new_start_block
        link.timestamp = datetime.now()  # Add some time information
        link.save()
        # Get all info to pass
        link_data['start_x'] = link.starting_block.x_pos; link_data['start_y'] = link.starting_block.y_pos
        link_data['end_x'] = link.ending_block.x_pos; link_data['end_y'] = link.ending_block.y_pos; link_data['id'] = link.id
        link_data['starting_block'] = link.starting_block.num; link_data['ending_block'] = link.ending_block.num
        return JsonResponse(link_data)


def delete_link(request):
    if request.method == 'POST':
        link_delete_valid = request.POST.get('link_delete_valid')
        if link_delete_valid:
            link = Link.objects.get(id=request.POST.get('link_id'))
            link.delete()
    return JsonResponse({})