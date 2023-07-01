def dowload_cam():
    outfile = BytesIO()  # io.BytesIO() for python 3
    with ZipFile(outfile, 'w') as zf:
        for current_cam in current_project.cam_set.all():
            block_resource = BlockResource().export(current_cam.block_set.all()).csv
            link_resource = LinkResource().export(current_cam.link_set.all()).csv
            names = ['blocks', 'links']
            ct = 0
            for resource in [block_resource, link_resource]:
                zf.writestr("{}.csv".format(current_cam.user.username + '_' + names[ct]), resource)
                ct += 1
    response = HttpResponse(outfile.getvalue(), content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="' + request.user.username + '_CAM.zip"'