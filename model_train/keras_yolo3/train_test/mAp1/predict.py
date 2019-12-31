import cv2
import numpy
import os
import json
import time
from freezer.keras_yolo3.yolo3 import yolo
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
YOLO = yolo.YOLO()
# 选取较低得阈值 预测测试集样本并存储
def predict (testPath,wfile,select_threshold=0.2,nms=0.15):
    startTime = time.time()
    imgs = os.listdir(testPath)
    iNum = len(imgs)
    listPre = []
    for img in imgs:
        dictPre = {}
        img1=cv2.imdecode(numpy.fromfile(os.path.join(testPath,img), dtype=numpy.uint8), cv2.IMREAD_COLOR)
        rclasses,rscores,rbboxes = YOLO.predict_img(img1)
        dictPre['fileName'] = img
        crl = []
        for i in range(len(rclasses)):
            crd = {}
            crd['rclasses'] = rclasses[i]
            crd['rscores'] = rscores[i]
            crd['rbboxes']=str(tuple(rbboxes[i]))
            crl.append(crd)
        dictPre['predictInfo'] = str(crl)
        listPre.append(dictPre)
    endTime = time.time()
    print ((endTime-startTime)/float(iNum))
    with open(wfile,"w") as f :
        jsonL = json.dumps(listPre)
        f.write(str(jsonL))

def _main():
    predict("E:\\opt\\data\\1_windows\\jpg\\", "./data/wPreFile.txt")



if __name__=='__main__':
     predict("E:\\opt\\data\\1_windows\\jpg\\","./data/wPreFile.txt")

