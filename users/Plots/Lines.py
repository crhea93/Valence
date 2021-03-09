import cv2 as cv
import numpy as np
import operator


def lines(image, starting_block, ending_block, line_style, arrow_type, scale):
    x_start = float(starting_block['x_pos'])
    x_end = float(ending_block['x_pos'])
    y_start = float(starting_block['y_pos'])
    y_end = float(ending_block['y_pos'])
    starting_point = (int(scale*(starting_block['x_pos']+starting_block['width']/2)), int(scale*(starting_block['y_pos']+starting_block['height']/2)))
    ending_point = (int(scale*(ending_block['x_pos']+ending_block['width']/2)), int(scale*(ending_block['y_pos']+ending_block['height']/2)))
    if 'Strong' in line_style:
        thickness = scale*4
    elif 'Weak' in line_style:
        thickness = scale*2
    else:
        thickness = scale*3
    color = (119, 119, 119)
    if 'Solid' in line_style:
        if arrow_type == 'none':
            image = cv.line(image, starting_point, ending_point, color, thickness)
        else:
            if x_end > x_start:
                temp = x_start
                x_start = x_end
                x_end = temp
                temp = y_start
                y_start = y_end
                y_end = temp
                x_end = x_end + 0.5*float(ending_block['width'])
                y_start = y_start + 0.5*float(ending_block['height'])
                x_start = x_start + 0.5*float(ending_block['width'])
                y_end = y_end + 0.5*float(ending_block['height'])
                angle = np.arctan((y_end-y_start)/(x_end-x_start))
                length = np.sqrt((x_start - x_end) * (x_start - x_end) + (y_start - y_end ) * (y_start - y_end ))
                x_end_new = scale*(x_start-0.5*np.sqrt(ending_block['width']**2+ending_block['height']**2)*np.cos(angle)) - 0.5*length*(1-np.cos(angle))
                y_end_new = scale*(y_start-0.5*np.sqrt(ending_block['width']**2+ending_block['height']**2)*np.sin(angle)) + 0.5*length*np.sin(angle)
                new_end = (int(x_end_new), int(y_end_new))  # tuple(np.subtract(ending_point,(scale*100,scale*100)))
                image = cv.arrowedLine(image, starting_point, new_end, color, thickness,line_type=8)
            else:
                temp = x_start
                x_start = x_end
                x_end = temp
                temp = y_start
                y_start = y_end
                y_end = temp
                x_end = x_end + 0.5*float(ending_block['width'])
                y_start = y_start + 0.5*float(ending_block['height'])
                x_start = x_start + 0.5*float(ending_block['width'])
                y_end = y_end + 0.5*float(ending_block['height'])
                angle = np.arctan((y_end-y_start)/(x_end-x_start))
                length = np.sqrt((x_start - x_end) * (x_start - x_end) + (y_start - y_end ) * (y_start - y_end ))
                x_end_new = scale*(x_start+0.42*np.sqrt(ending_block['width']**2+ending_block['height']**2)*np.cos(angle)) - 0.5*length*(1-np.cos(angle))
                y_end_new = scale*(y_start+0.42*np.sqrt(ending_block['width']**2+ending_block['height']**2)*np.sin(angle)) + 0.5*length*np.sin(angle)
                new_end = (int(x_end_new), int(y_end_new))  # tuple(np.subtract(ending_point,(scale*100,scale*100)))
                image = cv.arrowedLine(image, starting_point, new_end, color, thickness, line_type=8)
    else:  # Dashed
        if arrow_type == 'none':
            length = np.sqrt((x_start - x_end)**2 + (y_start - y_end )**2)
            angle = np.arctan((y_end-y_start)/(x_end-x_start))
            k = 1*scale
            for it in range(int(length)):
                if it%8 == 0:
                    if x_end > x_start:
                        starting_point_new = tuple(map(operator.add,starting_point,(it*k*np.cos(angle), it*k*np.sin(angle))))
                        ending_point_new = tuple(map(operator.add,starting_point,((it+1)*k*np.cos(angle), (it+1)*k*np.sin(angle))))
                        starting_point_new = tuple(int(i) for i in starting_point_new)
                        ending_point_new = tuple(int(i) for i in ending_point_new)
                        image = cv.line(image, starting_point_new, ending_point_new, color, thickness)
                    else:
                        starting_point_new = tuple(map(operator.add,ending_point,(it*k*np.cos(angle), it*k*np.sin(angle))))
                        ending_point_new = tuple(map(operator.add,ending_point,((it+1)*k*np.cos(angle), (it+1)*k*np.sin(angle))))
                        starting_point_new = tuple(int(i) for i in starting_point_new)
                        ending_point_new = tuple(int(i) for i in ending_point_new)
                        image = cv.line(image, starting_point_new, ending_point_new, color, thickness)
        else:  # Arrow
            temp = x_start
            x_start = x_end
            x_end = temp
            temp = y_start
            y_start = y_end
            y_end = temp
            x_end = x_end - 0.5*scale*float(ending_block['width'])
            y_start = y_start - 0.5*scale*float(ending_block['height'])
            x_start = x_start - 0.5*scale*float(ending_block['width'])
            y_end = y_end - 0.5*scale*float(ending_block['height'])
            length = np.sqrt((x_start - x_end)**2 + (y_start - y_end )**2)
            angle = np.arctan((y_end-y_start)/(x_end-x_start))
            k = 1*scale
            starting_point_new = None   # init
            ending_point_new = None   # init
            for it in range(int(length/2)):
                if it%8 == 0:
                    if x_end > x_start and y_start > y_end:
                        starting_point_new = tuple(map(operator.add,starting_point,(it*k*np.cos(angle)-scale*np.cos(angle)*float(ending_block['width']), it*k*np.sin(angle)-np.sin(angle)*1.5*scale*float(ending_block['height']))))
                        ending_point_new = tuple(map(operator.add,starting_point,((it+1)*k*np.cos(angle)-scale*np.cos(angle)*float(ending_block['width']), (it+1)*k*np.sin(angle)-np.sin(angle)*1.5*scale*float(ending_block['height']))))
                        starting_point_new = tuple(int(i) for i in starting_point_new)
                        ending_point_new = tuple(int(i) for i in ending_point_new)
                        image = cv.line(image, starting_point_new, ending_point_new, color, thickness)
                    elif x_end > x_start and y_start < y_end:
                        ending_point_new = tuple(map(operator.add,starting_point,(it*k*np.cos(angle)-scale*np.cos(angle)*float(ending_block['width']), it*k*np.sin(angle)-np.sin(angle)*scale*0.5*float(ending_block['height']))))
                        starting_point_new = tuple(map(operator.add,starting_point,((it+1)*k*np.cos(angle)-scale*np.cos(angle)*float(ending_block['width']), (it+1)*k*np.sin(angle)-np.sin(angle)*scale*0.5*float(ending_block['height']))))
                        starting_point_new = tuple(int(i) for i in starting_point_new)
                        ending_point_new = tuple(int(i) for i in ending_point_new)
                        image = cv.line(image, starting_point_new, ending_point_new, color, thickness)
                    elif x_end < x_start and y_start > y_end:
                        starting_point_new = tuple(map(operator.add,starting_point,(it*k*np.cos(angle)+scale*np.cos(angle)*0.5*float(ending_block['width']), it*k*np.sin(angle)+np.sin(angle)*scale*0.5*float(ending_block['height']))))
                        ending_point_new = tuple(map(operator.add,starting_point,((it+1)*k*np.cos(angle)+scale*np.cos(angle)*0.5*float(ending_block['width']), (it+1)*k*np.sin(angle)+np.sin(angle)*scale*0.5*float(ending_block['height']))))
                        starting_point_new = tuple(int(i) for i in starting_point_new)
                        ending_point_new = tuple(int(i) for i in ending_point_new)
                        image = cv.line(image, starting_point_new, ending_point_new, color, thickness)
                    elif x_end < x_start and y_start < y_end:
                        starting_point_new = tuple(map(operator.add,starting_point,(it*k*np.cos(angle)+0.5*np.cos(angle)*scale*float(ending_block['width']), it*k*np.sin(angle)+np.sin(angle)*0.5*scale*float(ending_block['height']))))
                        ending_point_new = tuple(map(operator.add,starting_point,((it+1)*k*np.cos(angle)+0.5*np.cos(angle)*scale*float(ending_block['width']), (it+1)*k*np.sin(angle)+np.sin(angle)*0.5*scale*float(ending_block['height']))))
                        starting_point_new = tuple(int(i) for i in starting_point_new)
                        ending_point_new = tuple(int(i) for i in ending_point_new)
                        image = cv.line(image, starting_point_new, ending_point_new, color, thickness)
            # Add final arrow
            if x_end > x_start and y_start > y_end:
                # Need for dash!
                it = 0
                starting_point_new = tuple(map(operator.add,starting_point,(it*k*np.cos(angle)-scale*np.cos(angle)*float(ending_block['width']), it*k*np.sin(angle)-np.sin(angle)*1.5*scale*float(ending_block['height']))))
                ending_point_new = tuple(map(operator.add,starting_point,((it+1)*k*np.cos(angle)-scale*np.cos(angle)*float(ending_block['width']), (it+1)*k*np.sin(angle)-np.sin(angle)*1.5*scale*float(ending_block['height']))))
                starting_point_new = tuple(int(i) for i in starting_point_new)
                ending_point_new = tuple(int(i) for i in ending_point_new)
                image = cv.arrowedLine(image, ending_point_new, starting_point_new, color, thickness, tipLength=thickness)
            elif x_end > x_start and y_start < y_end:
                # Need for dash!
                it = 0
                ending_point_new = tuple(map(operator.add,starting_point,(it*k*np.cos(angle)-scale*np.cos(angle)*float(ending_block['width']), it*k*np.sin(angle)-np.sin(angle)*0.5*scale*float(ending_block['height']))))
                starting_point_new = tuple(map(operator.add,starting_point,((it+1)*k*np.cos(angle)-scale*np.cos(angle)*float(ending_block['width']), (it+1)*k*np.sin(angle)-np.sin(angle)*0.5*scale*float(ending_block['height']))))
                starting_point_new = tuple(int(i) for i in starting_point_new)
                ending_point_new = tuple(int(i) for i in ending_point_new)
                image = cv.arrowedLine(image, starting_point_new, ending_point_new, color, thickness, tipLength=thickness)
            elif x_end < x_start and y_start > y_end:
                it = length/2
                starting_point_new = tuple(map(operator.add,starting_point,(it*k*np.cos(angle)+scale*np.cos(angle)*0.5*float(ending_block['width']), it*k*np.sin(angle)+np.sin(angle)*scale*0.5*float(ending_block['height']))))
                ending_point_new = tuple(map(operator.add,starting_point,((it+1)*k*np.cos(angle)+scale*np.cos(angle)*0.5*float(ending_block['width']), (it+1)*k*np.sin(angle)+np.sin(angle)*scale*0.5*float(ending_block['height']))))
                starting_point_new = tuple(int(i) for i in starting_point_new)
                ending_point_new = tuple(int(i) for i in ending_point_new)
                image = cv.arrowedLine(image, starting_point_new, ending_point_new, color, thickness, tipLength=thickness)
            elif x_end < x_start and y_start < y_end:
                it = length/2
                starting_point_new = tuple(map(operator.add,starting_point,(it*k*np.cos(angle)+0.5*np.cos(angle)*scale*float(ending_block['width']), it*k*np.sin(angle)+np.sin(angle)*0.5*scale*float(ending_block['height']))))
                ending_point_new = tuple(map(operator.add,starting_point,((it+1)*k*np.cos(angle)+0.5*np.cos(angle)*scale*float(ending_block['width']), (it+1)*k*np.sin(angle)+np.sin(angle)*0.5*scale*float(ending_block['height']))))
                starting_point_new = tuple(int(i) for i in starting_point_new)
                ending_point_new = tuple(int(i) for i in ending_point_new)
                image = cv.arrowedLine(image, starting_point_new, ending_point_new, color, thickness, tipLength=thickness)
    return image
