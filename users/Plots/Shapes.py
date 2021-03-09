import cv2 as cv
import math
import numpy as np

def shapes(image, shape_name, x_pos, y_pos, width, height, title, scale):
    """
    Convert shape name from pandas file to shape to be used in cv2
    """
    height = 0.6*height
    start_point = (int(scale*x_pos), int(scale*(y_pos+height)))  # Top left
    end_point = (int(scale*(x_pos+width)), int(scale*y_pos))  # Bottom right
    if 'negative' in shape_name:
        color = (182, 186, 224)
        boundary_color = (66, 66, 184)
        if 'strong' in shape_name:
            thickness = scale*8
        elif 'weak' in shape_name:
            thickness = scale*1
        else:
            thickness = scale*4
        # Hexagon points
        p1 = [int(scale*(x_pos)), int(scale*(y_pos+height/2))]
        p2 = [int(scale*(x_pos+width*0.8/3)), int(scale*(y_pos+height))]
        p3 = [int(scale*(x_pos+width*2.2/3)), int(scale*(y_pos+height))]
        p4 = [int(scale*(x_pos+width)), int(scale*(y_pos+height/2))]
        p5 = [int(scale*(x_pos+width*2.2/3)), int(scale*(y_pos))]
        p6 = [int(scale*(x_pos+width*0.8/3)), int(scale*(y_pos))]
        Hex = np.array([[p1, p2, p3, p4, p5, p6]], np.int32)
        Hex = Hex.reshape((-1, 1, 2))
        image = cv.polylines(image, [Hex], True, boundary_color, thickness)  # Boundary
        image = cv.fillPoly(image, [Hex], color)  # Main
    elif 'positive' in shape_name:
        color = (214, 228, 216)
        boundary_color = (149, 188, 149)
        if 'strong' in shape_name:
            thickness = scale*8
        elif 'weak' in shape_name:
            thickness = scale*1
        else:
            thickness = scale*4
        center_coordinates = (int(scale*(x_pos+1/2*width)), int(scale*(y_pos+1/2*height)))
        axesLength = (int(scale*(width/2)), int(scale*(height/2)))
        image = cv.ellipse(image, center_coordinates, axesLength, 0, 0, 360, boundary_color, thickness)
        image = cv.ellipse(image, center_coordinates, axesLength, 0, 0, 360, color, -1)
    elif 'neutral' in shape_name:
        color = (192, 230, 242)
        boundary_color = (49, 180, 223)
        thickness = scale*4
        image = cv.rectangle(image, start_point, end_point, boundary_color, thickness)
        image = cv.rectangle(image, start_point, end_point, color, -1)
    else:  # Ambivalent

        color = (210, 199, 207)
        boundary_color = (127, 90, 126)
        thickness = scale*4
        # Hexagon points
        p1 = [int(scale*(x_pos)), int(scale*(y_pos+height/2))]
        p2 = [int(scale*(x_pos+width*0.8/3)), int(scale*(y_pos+height))]
        p3 = [int(scale*(x_pos+width*2.2/3)), int(scale*(y_pos+height))]
        p4 = [int(scale*(x_pos+width)), int(scale*(y_pos+height/2))]
        p5 = [int(scale*(x_pos+width*2.2/3)), int(scale*(y_pos))]
        p6 = [int(scale*(x_pos+width*0.8/3)), int(scale*(y_pos))]
        Hex = np.array([[p1, p2, p3, p4, p5, p6]], np.int32)
        Hex = Hex.reshape((-1, 1, 2))
        image = cv.polylines(image, [Hex], True, boundary_color, thickness)  # Boundary
        image = cv.fillPoly(image, [Hex], color)  # Main
        # Ellipse
        center_coordinates = (int(scale*(x_pos+1/2*width)), int(scale*(y_pos+1/2*height)))
        axesLength = (int(scale*(width/2.25)), int(scale*(height/2.25)))
        image = cv.ellipse(image, center_coordinates, axesLength, 0, 0, 360, boundary_color, thickness)
        image = cv.ellipse(image, center_coordinates, axesLength, 0, 0, 360, color, -1)
    #print(image)
    # Add text
    font = cv.FONT_HERSHEY_SIMPLEX
    fontScale = 2.
    text_color = (0, 0, 0)
    thickness = scale*1
    if math.ceil(fontScale*scale*len(title)/width) == 2:  # The text is too large! --> twice as long
        text_length_half = int(len(title)/2)
        # First half
        org = (int(scale*((x_pos+1/2*width)-2.2*text_length_half-fontScale*scale)), int(scale*(y_pos+1/2*height)-4*fontScale*scale))
        image = cv.putText(image, title[:text_length_half], org, font, fontScale, text_color, thickness, cv.LINE_AA)
        # Second half
        org = (int(scale*((x_pos+1/2*width)-2.2*text_length_half-fontScale*scale)), int(scale*(y_pos+1/2*height)+4*fontScale*scale))
        image = cv.putText(image, title[text_length_half:], org, font, fontScale, text_color, thickness, cv.LINE_AA)
    elif math.ceil(fontScale*scale*len(title)/width) == 3:  # The text is too large! --> twice as long
        text_length_half = int(len(title)/3)
        # First half
        org = (int(scale*((x_pos+1/2*width)-4*text_length_half-fontScale*scale)), int(scale*(y_pos+1/2*height)-5*fontScale*scale))
        image = cv.putText(image, title[:text_length_half], org, font, fontScale, text_color, thickness, cv.LINE_AA)
        # Second half
        org = (int(scale*((x_pos+1/2*width)-4*text_length_half-fontScale*scale)), int(scale*(y_pos+1/2*height)+0*fontScale*scale))
        image = cv.putText(image, title[text_length_half:2*text_length_half], org, font, fontScale, text_color, thickness, cv.LINE_AA)
        # Third half
        org = (int(scale*((x_pos+1/2*width)-4*text_length_half-fontScale*scale)), int(scale*(y_pos+1/2*height)+5*fontScale*scale))
        image = cv.putText(image, title[2*text_length_half:], org, font, fontScale, text_color, thickness, cv.LINE_AA)
    else:
        org = (int(scale*((x_pos+1/2*width)-scale/2*len(title)-fontScale*scale)), int(scale*(y_pos+1/2*height)))
        image = cv.putText(image, title, org, font, fontScale, text_color, thickness, cv.LINE_AA)
    return image

