from model_train.keras_yolo3.yolo3 import yolo
import os
from PIL import Image
import cv2


class_names = ["6926483420125", "6926483400011", "6926483420088"]
diff_switch_iou = [False,0.6]
single_switch_iou_minscore = [False,0.0,0.28]
model_path = "/data/ai/yolov3/model/8_43/8_43.h5"
iou = 0.45
score = 0.2
YOLO = yolo.YOLO(class_names,diff_switch_iou,single_switch_iou_minscore,model_path,iou,score)

def test(test_jpg_path,test_jpg_write_path):
    files = os.listdir(test_jpg_path)
    for file in files:
        img = Image.open(os.path.join(test_jpg_path,file))
        img, out_classes, out_scores, out_boxes = YOLO.detect_image(img)
        img.save(os.path.join(test_jpg_write_path,file))
def __main():
    test_jpg_path = "/data/ai/ai_data/test_8/"
    test_jpg_write_path = "/data/ai/ai_data/test_predict_8/"
    test(test_jpg_path, test_jpg_write_path)
if __name__=='__main__':
    test_jpg_path = "/data/ai/ai_data/test_8/"
    test_jpg_write_path = "/data/ai/ai_data/test_predict_8/"
    test(test_jpg_path, test_jpg_write_path)