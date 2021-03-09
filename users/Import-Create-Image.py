"""
Routine to import a set of CAMS and create an image for each
"""
from .resources import BlockResource, LinkResource
from zipfile import ZipFile
from tablib import Dataset
from users.models import CAM
from django.shortcuts import render, redirect
from django.http import HttpResponse
import pandas as pd
import base64
import re
from users.Plots.DataToPlot import data_to_plot

def Image_CAM(request):
    '''
    For more pdf options look at wkhtmltopdf documentation
    :param request:
    :return:
    '''
    #config = pdfkit.configuration(wkhtmltopdf='./bin/wkhtmltopdf')
    file_name = 'media/CAMS/'+request.user.username+'_'+str(request.user.active_cam_num)+'.png'
    data_to_plot(request.user.username,file_name)
    current_cam = CAM.objects.get(id=request.user.active_cam_num)
    current_cam.cam_image = file_name
    current_cam.save()
    return HttpResponse('Saved Image')


def import_CAM(request):
    if request.method == 'POST':
        block_resource = BlockResource()
        link_resource = LinkResource()
        dataset = Dataset()
        uploaded_CAM = request.FILES['myfile']
        deletable = request.POST.get('Deletable')
        # Clear all current blocks and links
        current_cam = CAM.objects.get(id=request.user.active_cam_num)
        user = request.user
        blocks = current_cam.block_set.all()
        for block in blocks:
            block.delete()
        links = current_cam.link_set.all()
        for link in links:
            link.delete()
        ct = 0
        print(current_cam)
        try:
            with ZipFile(uploaded_CAM) as z:
                for filename in z.namelist():
                    data = z.extract(filename)
                    test = pd.read_csv(data)
                    print(test)
                    #test['id'] = test['id'].apply(lambda x: ' ')  # Must be empty to auto id
                    test['creator'] = test['creator'].apply(lambda x: request.user.id)
                    test['CAM'] = test['CAM'].apply(lambda x: current_cam.id)
                    test.to_csv(data)
                    imported_data = dataset.load(open(data).read())
                    if ct == 0:
                        result = block_resource.import_data(imported_data, dry_run=True)  # Test the data import
                        if not result.has_errors():
                            block_resource.import_data(imported_data, dry_run=False)  # Actually import now
                        else:
                            print('sad')
                    else:
                        result = link_resource.import_data(imported_data, dry_run=True)  # Test the data import
                        if not result.has_errors():
                            link_resource.import_data(imported_data, dry_run=False)  # Actually import now
                    ct += 1
        except:
            print('didnt work')
        # We now have to clean up the blocks' links...
        blocks_imported = current_cam.block_set.all()
        print(blocks_imported)
        for block in blocks_imported:
            # Clean up Comments ('none' -> '')
            if block.comment == 'None' or block.comment == 'none':
                block.comment = ''
            if deletable is not None:
                block.modifiable = False
            # Change block creator to current user
            block.creator = request.user
            block.save()
        links_imported = current_cam.link_set.all()

        for link in links_imported:
            link.creator = request.user
            link.save()
        return redirect('/')