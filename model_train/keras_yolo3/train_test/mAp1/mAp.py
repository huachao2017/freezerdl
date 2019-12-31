import demjson
import os
import numpy as np
import cv2
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

exe_params = {
    'labels':['1','2','3','4','5','6','7','8','9','10','11','12'],
    'xmlTestPath':"E:\\opt\\data\\1_windows\\xml\\",
    'jpgTestPath':"E:\\opt\\data\\1_windows\\jpg\\",
    'predictFile':"./data/wPreFile1.txt"
}

labels = exe_params['labels']
xmlTestPath =exe_params['xmlTestPath']
jpgTestPath = exe_params['jpgTestPath']
wpredict_file = exe_params['predictFile']
def sumXMlObjects(xmlTestPath):
    labels_dict = {}
    for label in labels:
        labels_dict[label] = 0
    files = os.listdir(xmlTestPath)
    for file in files:
        f = xmlTestPath + file
        tree = ET.parse(f)  # 打开xml文档
        root = tree.getroot()  # 获得root节点
        filename = root.find('filename').text
        filename = filename[:-4]
        for object in root.findall('object'):  # 找到root节点下的所有object节点
            name = object.find('name').text  # 子节点下节点name的值
            labels_dict[name] += 1
    return labels_dict

def xmlFilesDict(xmlTestPath):
    file_dict = {}
    files = os.listdir(xmlTestPath)
    for file in files:
        file_labels = []
        f = xmlTestPath + file
        tree = ET.parse(f)  # 打开xml文档
        root = tree.getroot()  # 获得root节点
        filename = root.find('filename').text
        filename = filename[:-4]
        for object in root.findall('object'):  # 找到root节点下的所有object节点
            name = object.find('name').text  # 子节点下节点name的值
            file_labels.append(name)
        file_dict[file] = file_labels
    return file_dict


def xmlObjects(file,object_dict):
    f = file
    tree = ET.parse(f)  # 打开xml文档
    root = tree.getroot()  # 获得root节点
    filename = root.find('filename').text
    filename = filename[:-4]
    for object in root.findall('object'):  # 找到root节点下的所有object节点
        name = object.find('name').text  # 子节点下节点name的值
        object_dict[name] += 1


def xmlObjectsLocations(f):

    tree = ET.parse(f)  # 打开xml文档
    root = tree.getroot()  # 获得root节点
    filename = root.find('filename').text
    filename = filename[:-4]
    object_list = []
    for object in root.findall('object'):# 找到root节点下的所有object节点
        object_dict = {}
        name = object.find('name').text  # 子节点下节点name的值
        bndbox = object.find('bndbox')  # 子节点下属性bndbox的值
        xmin = bndbox.find('xmin').text
        ymin = bndbox.find('ymin').text
        xmax = bndbox.find('xmax').text
        ymax = bndbox.find('ymax').text
        location=[]
        location.append(int(xmin))
        location.append(int(ymin))
        location.append(int(xmax))
        location.append(int(ymax))
        object_dict[name] = location
        object_list.append(object_dict)


    xmlObjectLocation = {}
    for ob_dict in object_list:
        for ob in ob_dict:
            xmlObjectLocation[ob]=[]
    for ob_dict in object_list:
        for ob in ob_dict:
            location = ob_dict[ob]
            xmlObjectLocation[ob].append(location)
    return xmlObjectLocation



def IOU (predictBox,Box,overthroud=0.2):
    cx1 = predictBox[0]
    cy1 = predictBox[1]
    cx2 = predictBox[2]
    cy2 = predictBox[3]
    gx1 = Box[0]
    gy1 = Box[1]
    gx2 = Box[2]
    gy2 = Box[3]

    carea = (cx2 - cx1) * (cy2 - cy1)  # C的面积
    garea = (gx2 - gx1) * (gy2 - gy1)  # G的面积

    x1 = max(cx1, gx1)
    y1 = max(cy1, gy1)
    x2 = min(cx2, gx2)
    y2 = min(cy2, gy2)
    w = max(0, x2 - x1)
    h = max(0, y2 - y1)
    area = w * h  # C∩G的面积

    iou = float(area) / (carea + garea - area)
    if iou > overthroud :
        return True
    else :
        return False

#predictDict 预测字典 [{'fire':[165,165,165,165]},{'fire':[165,165,165,165]}]
#xmlDict xml文件的字典 [{'fire':[165,165,165,165]},{'fire':[165,165,165,165]}]
def classPrecesion(predictDict,xmlDict,object_Dict):
    classPrecesion_dict = {}
    for predict in object_Dict:
        xmlBoxs = []
        preBoxs = []
        if predict in xmlDict.keys():
            xmlBoxs = xmlDict[predict]
        if predict in predictDict.keys():
            preBoxs = predictDict[predict]
        if len(xmlBoxs) < 1 or len(preBoxs)<1:
            continue
        for xmlBox in xmlBoxs:
            for preBox in preBoxs:
                bFalg = IOU(list(preBox), list(xmlBox))
                if bFalg:
                    object_Dict[predict] += 1  # TP
                    break
        TP = object_Dict[predict]
        classPrecesion = TP / float(len(xmlBoxs))
        classPrecesion_dict[predict] = classPrecesion
    return classPrecesion_dict


def averagePrecision(xmlTestPath,wfile):
    listPre=[]
    with open(wfile, 'rb') as f:
        line = f.readline()
        line = demjson.decode(line)
        listPre = list(line)

    classPrecesions_dict = {}
    for infoP in listPre:
        fileName = str(infoP['fileName'])
        predictInfo = list(demjson.decode(str(infoP['predictInfo'])))
        rclasses = []
        rscores = []
        rbboxes = []
        for i in range(len(predictInfo)):
            info = dict(predictInfo[i])
            rclasses.append(str(info['rclasses']))
            rscores.append(float(info['rscores']))
            locat= str(info['rbboxes']).strip().strip('()')
            locat_list = locat.split(",")
            locat_list1 = [int(locat_list[0]),int(locat_list[1]),int(locat_list[2]),int(locat_list[3])]
            rbboxes.append(list(locat_list1))
        predictDict = {}
        for i in range(len(rclasses)):
            predictDict[rclasses[i]] = rbboxes

        xmlFileName = xmlTestPath+str(fileName.split(".")[0])+".xml"
        xmlFileDict = xmlObjectsLocations(xmlFileName)
        classP_dict = {}
        for label in labels:
            classP_dict[label] = 0
        classPrecesion_dict = classPrecesion(predictDict,xmlFileDict,classP_dict)
        print (str(fileName))
        print (classPrecesion_dict)
        classPrecesions_dict[fileName] = classPrecesion_dict

    print ("cp"+str(classPrecesions_dict))
    fileC_dict = {}
    for label in labels:
        fileC_dict[label] = 0

    file_dict = xmlFilesDict(xmlTestPath)
    for l in fileC_dict:
        for file_l in file_dict:
            if l in file_dict[file_l]:
                fileC_dict[l] += 1

    classAveragePrecesion_dict = {}
    for key in fileC_dict:
        fileC = fileC_dict[key]
        cp = 0.
        for keyCp in classPrecesions_dict:
            keyCpP = dict(classPrecesions_dict[keyCp])
            if key in keyCpP:
                cp+=keyCpP[key]
        classAveragePrecesion = cp / fileC
        classAveragePrecesion_dict[key] = classAveragePrecesion
    return classAveragePrecesion_dict


def meanAveragePrecesion(classAveragePrecesion_dict):
    print ("cAp"+str(classAveragePrecesion_dict))
    classNums = 0
    classAP = 0.
    for key in classAveragePrecesion_dict:
        classNums+=1
        classAP += classAveragePrecesion_dict[key]
    mAP = (classAP / classNums)
    print ("mAP"+str(mAP))
    return mAP





if __name__=='__main__':
    classAveragePrecesion_dict = averagePrecision(xmlTestPath,wpredict_file)

    meanAveragePrecesion(classAveragePrecesion_dict)
    



