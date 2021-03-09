"""
Code to take black and line csv information and create an image
"""

import cv2 as cv
import numpy as np
import pandas as pd
from users.Plots.Shapes import shapes
from users.Plots.Lines import lines
from users.models import CustomUser

def data_to_plot(username,file_name):
    scale = 5
    # Read in data to pandas
    #blocks = pd.read_csv('/home/carterrhea/Documents/CAM-proj/'+id+'_blocks.csv')
    #links = pd.read_csv('/home/carterrhea/Documents/CAM-proj/'+id+'_links.csv')
    blocks = pd.DataFrame.from_records(
        CustomUser.objects.get(username=username).block_set.all().values_list('id', 'x_pos', 'y_pos', 'height', 'width', 'shape', 'title'),
        columns=['id', 'x_pos', 'y_pos', 'height', 'width', 'shape', 'title']
    )
    links = pd.DataFrame.from_records(
        CustomUser.objects.get(username=username).link_set.all().values_list('starting_block', 'ending_block', 'line_style', 'arrow_type'),
        columns=['starting_block', 'ending_block', 'line_style', 'arrow_type']
    )
    # Create Background
    x_size = int(blocks['y_pos'].max())
    y_size = int(blocks['x_pos'].max())
    image = np.zeros((int(1.3*scale*x_size), int(1.3*scale*y_size), 3), np.uint8)
    image.fill(255)  # Make white background
    # Step through each line
    for index, row in links.iterrows():
        starting_block = blocks[blocks['id'] == row['ending_block']]
        ending_block = blocks[blocks['id'] == row['starting_block']]
        image = lines(image, starting_block, ending_block, row['line_style'], row['arrow_type'], scale)
    # Step through each block
    for index, row in blocks.iterrows():
        image = shapes(image, row['shape'], row['x_pos'], row['y_pos'], row['width'], row['height'], row['title'], scale)


    # resize image
    #percent by which the image is resized
    scale_percent = int((1/(scale))*100)
    #calculate the 50 percent of original dimensions
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)

    # dsize
    dsize = (width, height)

    image = cv.resize(image, dsize)

    cv.imwrite(file_name, image)