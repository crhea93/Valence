from users.models import CustomUser, Project
from .resources import BlockResource, LinkResource
from zipfile import ZipFile
from block.models import Block
from link.models import Link
from io import BytesIO


user = CustomUser.objects.get(username='Liz')
print(user.project_set.all())


## IMPORTS ##
project_name = 'Empirische Ethik'
outfile = 'Lisa_CAMS.zip'
with ZipFile(outfile, 'w') as zf:
    current_project = Project.objects.filter(name=project_name)
    outfile = BytesIO()  # io.BytesIO() for python 3
    for current_cam in current_project.cam_set.all():
        block_resource = BlockResource().export(current_cam.block_set.all()).csv
        link_resource = LinkResource().export(current_cam.link_set.all()).csv
        names = ['blocks', 'links']
        ct = 0
        for resource in [block_resource, link_resource]:
            zf.writestr("{}.csv".format(current_cam.user.username + '_' + str(current_cam.id) + '_' + names[ct]),
                        resource)
            ct += 1
        if current_cam.cam_image:
            try:
                zf.write(str(current_cam.cam_image))
            except:
                pass
