def inside(box1,box2):
    [xmin1,ymin1,xmax1,ymax1] = box1
    [xmin2,ymin2,xmax2,ymax2] = box2

    if  (xmin1 > xmin2 and xmin1 < xmax2) or (xmin2 > xmin1 and xmin2 < xmax1):
        return True
    if  (xmax1 > xmin2 and xmax1 < xmax2) or (xmax2 > xmin1 and xmax2 < xmax1):
        return True
    if  (ymin1 > ymin2 and ymin1 < ymax2) or ( ymin2 > ymin1 and ymin2 < ymax1):
        return True
    if ( ymax1 > ymin2 and ymax1 < ymax2) or ( ymax2 > ymin1 and ymax2 < ymax1):
        return True

    return False