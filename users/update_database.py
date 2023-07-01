'''
This file is for manually run database updates
'''

from block.models import Block
from link.models import Link


def Clear_users_cam(Block, Link):
    """
    This function will clear all blocks and links
    :return:
    """
    # Get all Blocks and Delete them
    all_blocks = Block.objects.all()
    for block in all_blocks:
        try:
            block.delete()
        except Exception:
            print(Exception)
    # Get all Links and Delete them
    all_links = Link.objects.all()
    for link in all_links:
        try:
            link.delete()
        except Exception:
            print(Exception)
    return None


Clear_users_cam(Block, Link)
