"""
This view handles the undo button actions. At the moment (October 23, 2021), the only permitted undo action is the
"delete" action
"""
from users.models import CAM
from link.models import Link
from block.forms import BlockForm
from link.forms import LinkForm
from django.http import JsonResponse
import ast
import yaml
#import logging
#import cognitiveAffectiveMaps.log_config
import json
from django.contrib.auth import get_user_model
User = get_user_model()
#logger = logging.getLogger(__name__)


def undo_action(request):
    """
    This function will be triggered when a user hits the undo button. At that time, we will look at the users log
    which is stored in a database. We then read the last action from that database. In the case of delete, the last
    action will contain the node deleted and the links associated with that node. We will then read in the node
    and link information as dictionaries. We can then pass those directly to BlockForm and LinkForm to recreate the
    objects. The page will then be refreshed via the jquery/ajax call.
    """
    if request.method == 'POST':  # Trigger action for undo
        message = 'Undoing previous action'
        message_type = 'Warning'
        user_ = User.objects.get(username=request.user.username)
        current_cam = CAM.objects.get(id=user_.active_cam_num)
        # Get the latest action ID associated with the user's log. We need this since several rows could correspond to the same actionID
        latest_action_id = current_cam.logcamactions_set.latest('actionId').actionId
        action_set = current_cam.logcamactions_set.filter(actionId=latest_action_id)  # Set of all actions associated with the most recent actionID
        for action_ in action_set:  # Step through each action
            if action_.actionType == 0:  # Delete action
                if action_.objType == 1:  # Concept Object
                    concept_info = yaml.load(action_.objDetails)
                    form_block = BlockForm(concept_info)  # Getting our block form
                    try:
                        block = form_block.save()  # Saving the form and getting the block
                    except:
                        message = 'Block form failed.\n %s'%form_block.errors
                        message_type = 'Error'
                elif action_.objType == 0:  # Link object
                    link_info = yaml.load(action_.objDetails)
                    # Check if newly added block is starting or ending
                    start_block_bool = True  # Assume it is
                    try:
                        Link.objects.filter(ending_block=link_info['ending_block'])
                        link_info['starting_block'] = block.id
                    except:
                        # ending block doesn't exist which means it was deleted. Therefore the newly added block is the ending block
                        start_block_bool = False
                        link_info['ending_block'] = block.id
                    form_link = LinkForm(link_info)  # Getting our block form
                    # Update link info block
                    try:
                        form_link.save()  # Saving the form and getting the block
                    except:
                        message = 'Link form failed.\n %s' % form_link.errors
                        message_type = 'Error'
                else:
                    message = 'Only concepts and links can be deleted!'
                    message_type = 'Warning'
            else:  # Any other action than deletion
                message = 'We only allow the undo of deleted nodes and its associated links'
                message_type = 'Warning'
            # Delete action from logger
            #action_.delete()
    else:
        message = 'Failed to undo previous action'
        message_type = 'Warning'
    # Add message to log
    '''if message_type == 'Error':
        logger.error(message)
    else:
        logger.warning(message)'''
    return JsonResponse({"message": message})
