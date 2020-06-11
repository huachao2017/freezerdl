from model_train.keras_yolo4.yolo4 import yolo
import os
from PIL import Image
import cv2

class_names = ["8993175537445", "6942404230086", "6922255447833", "6941704408317", "6911988014320", "6902083880781", "6922222702156", "6921168509256", "6942404210088", "6921168593576", "6941704408492", "6925303730574", "6928804011296", "6941704403824", "6925303770563", "6907992513560", "6920459905012", "6928804014648", "6928804014570", "6942404210064", "6920907800913", "6970399920415", "6920202888883", "6921482336064", "6924743912878", "6920459954997", "6917878030623", "6920459950180", "6920459907429", "4891028164456", "6944488539239", "6909995103472"]

diff_switch_iou = [False,0.6]
single_switch_iou_minscore = [False,0.0,0.28]
model_path = "/data/ai/yolov4/model/1_38/1_38.h5"
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
    test_jpg_path = "/data/ai/ai_data/test/"
    test_jpg_write_path = "/data/ai/ai_data/test_predict/"
    test(test_jpg_path, test_jpg_write_path)
if __name__=='__main__':
    test_jpg_path = "/data/ai/ai_data/test/"
    test_jpg_write_path = "/data/ai/ai_data/test_predict/"
    test(test_jpg_path,test_jpg_write_path)
