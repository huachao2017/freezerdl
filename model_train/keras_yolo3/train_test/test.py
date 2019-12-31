from model_train.keras_yolo3.yolo3 import yolo
import os
from PIL import Image
import cv2
YOLO = yolo.YOLO()

def test(test_jpg_path,test_jpg_write_path):
    files = os.listdir(test_jpg_path)
    for file in files:
        img = Image.open(os.path.join(test_jpg_path,file))
        img = YOLO.detect_image(img)
        img.save(os.path.join(test_jpg_write_path,file))

if __name__=='__main__':
    test_jpg_path = "D:\\opt\\data\\freezer\\20191205\\train\\jpg\\"
    test_jpg_write_path = "D:\\opt\\data\\freezer\\20191205\\train\\test_write_jpg6\\"
    test(test_jpg_path,test_jpg_write_path)
