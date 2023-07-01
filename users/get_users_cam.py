from users.models import CustomUser
from .resources import BlockResource, LinkResource
from zipfile import ZipFile
from block.models import Block
from link.models import Link
from io import BytesIO


## IMPORTS ##
num_part = 20  # Number of participants
call_id = 'B'
outfile = call_id + '_CAMS.zip'

with ZipFile(outfile, 'w') as zf:
    for user_num in range(num_part):
        user = CustomUser.objects.get(username=call_id + str(user_num))
        block_resource = BlockResource().export(Block.objects.filter(creator=user.username)).csv
        link_resource = LinkResource().export(Link.objects.filter(creator=user.username)).csv
        outfile = BytesIO()  # io.BytesIO() for python 3
        names = ['blocks', 'links']
        with ZipFile('CAMS/'+call_id+str(user_num)+'.zip', 'w') as zf2:
            ct = 0
            for resource in [block_resource,link_resource]:
                zf.writestr("{}.csv".format(call_id+str(user_num)+'_'+names[ct]), resource)
                zf2.writestr("{}.csv".format(names[ct]), resource)
                ct += 1
