import logging
import os
import shutil
import time
import json
import numpy as np
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from .serializers import *
from django.conf import settings
import urllib.request
import urllib.parse

import cv2
from PIL import Image
import requests
import traceback
from freezers.third_tools import visualization_utils as vis_util
from model_train.keras_yolo3.yolo3 import yolo
logger = logging.getLogger("django")
def start_yolov3_map_models():
    yolov3_ins_map = {}
    online_model_list = OnlineModels.objects.filter(status=10)
    for online_model in online_model_list:
        class_names = json.loads(online_model.upcs)
        diff_switch_iou = dict(json.loads(online_model.params))['diff_switch_iou']
        single_switch_iou_minscore =  dict(json.loads(online_model.params))['single_switch_iou_minscore']
        model_path = online_model.model_path
        iou =  dict(json.loads(online_model.params))['iou']
        score = dict(json.loads(online_model.params))['score']
        yolo_ins = yolo.YOLO(class_names,diff_switch_iou,single_switch_iou_minscore,model_path,iou,score)
        key = str(online_model.group_id)+"_"+str(online_model.model_id)
        yolov3_ins_map[key] = yolo_ins
    return yolov3_ins_map
yolov3_inss_map = start_yolov3_map_models()

class Test(APIView):
    def get(self, request):
        url = "https://autodisplay:xianlife2018@taizhang.aicvs.cn/api/autoDisplay"
        print(url)
        headers = {
            "Accept":"application/json",
            "Content-Type":"application/json"
        }

        a = '{"taizhang_id": 1199, "shelfs": [{"shelf_id": 1100, "levels": [{"level_id": 0, "height": 50, "goods": [{"mch_good_code": "2004638", "upc": "6954767413877", "width": 108, "height": 338, "depth": 108, "displays": [{"top": 338, "left": 0, "row": 0, "col": 0}]}, {"mch_good_code": "2004092", "upc": "6921168520015", "width": 85, "height": 325, "depth": 85, "displays": [{"top": 325, "left": 108, "row": 0, "col": 0}, {"top": 325, "left": 193, "row": 0, "col": 1}, {"top": 325, "left": 278, "row": 0, "col": 2}, {"top": 325, "left": 363, "row": 0, "col": 3}]}, {"mch_good_code": "2019540", "upc": "6921581540270", "width": 63, "height": 220, "depth": 63, "displays": [{"top": 220, "left": 448, "row": 0, "col": 0}]}, {"mch_good_code": "2042696", "upc": "6917878054780", "width": 56, "height": 164, "depth": 56, "displays": [{"top": 164, "left": 511, "row": 0, "col": 0}]}, {"mch_good_code": "2021662", "upc": "6917878030623", "width": 58, "height": 166, "depth": 58, "displays": [{"top": 166, "left": 567, "row": 0, "col": 0}]}, {"mch_good_code": "2035957", "upc": "6921168593811", "width": 53, "height": 85, "depth": 53, "displays": [{"top": 85, "left": 625, "row": 0, "col": 0}]}, {"mch_good_code": "2035958", "upc": "6921168593804", "width": 53, "height": 85, "depth": 53, "displays": [{"top": 85, "left": 678, "row": 0, "col": 0}]}, {"mch_good_code": "2037750", "upc": "6921168593880", "width": 53, "height": 85, "depth": 53, "displays": [{"top": 85, "left": 731, "row": 0, "col": 0}]}, {"mch_good_code": "2034860", "upc": "898999000022", "width": 55, "height": 145, "depth": 55, "displays": [{"top": 145, "left": 784, "row": 0, "col": 0}]}]}, {"level_id": 1, "height": 438, "goods": [{"mch_good_code": "2026210", "upc": "6921168558049", "width": 60, "height": 204, "depth": 60, "displays": [{"top": 204, "left": 0, "row": 0, "col": 0}, {"top": 204, "left": 60, "row": 0, "col": 1}, {"top": 204, "left": 120, "row": 0, "col": 2}]}, {"mch_good_code": "2044244", "upc": "6972215667535", "width": 60, "height": 225, "depth": 60, "displays": [{"top": 225, "left": 180, "row": 0, "col": 0}]}, {"mch_good_code": "2044180", "upc": "6956416205956", "width": 55, "height": 210, "depth": 55, "displays": [{"top": 210, "left": 240, "row": 0, "col": 0}]}, {"mch_good_code": "2043144", "upc": "8806002016917", "width": 72, "height": 209, "depth": 72, "displays": [{"top": 209, "left": 295, "row": 0, "col": 0}]}, {"mch_good_code": "2029398", "upc": "6905069200030", "width": 70, "height": 209, "depth": 70, "displays": [{"top": 209, "left": 367, "row": 0, "col": 0}]}, {"mch_good_code": "2034858", "upc": "6927216920011", "width": 75, "height": 210, "depth": 75, "displays": [{"top": 210, "left": 437, "row": 0, "col": 0}]}, {"mch_good_code": "2034859", "upc": "6927216920059", "width": 75, "height": 210, "depth": 75, "displays": [{"top": 210, "left": 512, "row": 0, "col": 0}]}, {"mch_good_code": "2042505", "upc": "6938888889803", "width": 88, "height": 155, "depth": 88, "displays": [{"top": 155, "left": 587, "row": 0, "col": 0}]}, {"mch_good_code": "2045483", "upc": "6907305713328", "width": 70, "height": 145, "depth": 70, "displays": [{"top": 145, "left": 675, "row": 0, "col": 0}]}]}, {"level_id": 2, "height": 713, "goods": [{"mch_good_code": "2004998", "upc": "6921581596048", "width": 65, "height": 209, "depth": 65, "displays": [{"top": 209, "left": 0, "row": 0, "col": 0}, {"top": 209, "left": 65, "row": 0, "col": 1}, {"top": 209, "left": 130, "row": 0, "col": 2}]}, {"mch_good_code": "2005413", "upc": "6925303721367", "width": 66, "height": 220, "depth": 66, "displays": [{"top": 220, "left": 195, "row": 0, "col": 0}]}, {"mch_good_code": "2003963", "upc": "4891599338393", "width": 65, "height": 115, "depth": 65, "displays": [{"top": 115, "left": 261, "row": 0, "col": 0}]}, {"mch_good_code": "2040855", "upc": "6917878056197", "width": 52, "height": 119, "depth": 52, "displays": [{"top": 119, "left": 326, "row": 0, "col": 0}]}, {"mch_good_code": "2044181", "upc": "4897036691175", "width": 52, "height": 120, "depth": 52, "displays": [{"top": 120, "left": 378, "row": 0, "col": 0}]}, {"mch_good_code": "2004353", "upc": "6920202888883", "width": 64, "height": 91, "depth": 64, "displays": [{"top": 91, "left": 430, "row": 0, "col": 0}]}, {"mch_good_code": "2012607", "upc": "6920180209601", "width": 65, "height": 115, "depth": 65, "displays": [{"top": 115, "left": 494, "row": 0, "col": 0}]}, {"mch_good_code": "2044177", "upc": "6954767417684", "width": 56, "height": 145, "depth": 56, "displays": [{"top": 145, "left": 559, "row": 0, "col": 0}, {"top": 145, "left": 615, "row": 0, "col": 1}]}, {"mch_good_code": "2043574", "upc": "6970399920415", "width": 66, "height": 205, "depth": 66, "displays": [{"top": 205, "left": 671, "row": 0, "col": 0}, {"top": 205, "left": 737, "row": 0, "col": 1}]}]}, {"level_id": 3, "height": 983, "goods": [{"mch_good_code": "2018241", "upc": "6902538005141", "width": 75, "height": 210, "depth": 75, "displays": [{"top": 210, "left": 0, "row": 0, "col": 0}]}, {"mch_good_code": "2004326", "upc": "6902538004045", "width": 73, "height": 209, "depth": 73, "displays": [{"top": 209, "left": 75, "row": 0, "col": 0}]}, {"mch_good_code": "2025479", "upc": "6921168550098", "width": 66, "height": 190, "depth": 66, "displays": [{"top": 190, "left": 148, "row": 0, "col": 0}]}, {"mch_good_code": "2025480", "upc": "6921168550128", "width": 66, "height": 190, "depth": 66, "displays": [{"top": 190, "left": 214, "row": 0, "col": 0}]}, {"mch_good_code": "2026253", "upc": "6922255451427", "width": 60, "height": 230, "depth": 60, "displays": [{"top": 230, "left": 280, "row": 0, "col": 0}, {"top": 230, "left": 340, "row": 0, "col": 1}]}, {"mch_good_code": "2004083", "upc": "6921168509256", "width": 62, "height": 229, "depth": 62, "displays": [{"top": 229, "left": 400, "row": 0, "col": 0}, {"top": 229, "left": 462, "row": 0, "col": 1}, {"top": 229, "left": 524, "row": 0, "col": 2}, {"top": 229, "left": 586, "row": 0, "col": 3}]}, {"mch_good_code": "2021612", "upc": "6906907907012", "width": 58, "height": 240, "depth": 58, "displays": [{"top": 240, "left": 648, "row": 0, "col": 0}, {"top": 240, "left": 706, "row": 0, "col": 1}]}, {"mch_good_code": "2019634", "upc": "6954767423579", "width": 64, "height": 232, "depth": 64, "displays": [{"top": 232, "left": 764, "row": 0, "col": 0}, {"top": 232, "left": 828, "row": 0, "col": 1}]}]}, {"level_id": 4, "height": 1273, "goods": [{"mch_good_code": "2043903", "upc": "6902538007664", "width": 70, "height": 210, "depth": 70, "displays": [{"top": 210, "left": 0, "row": 0, "col": 0}]}, {"mch_good_code": "2009198", "upc": "6932529211107", "width": 65, "height": 212, "depth": 65, "displays": [{"top": 212, "left": 70, "row": 0, "col": 0}]}, {"mch_good_code": "2013136", "upc": "6902083886455", "width": 67, "height": 197, "depth": 67, "displays": [{"top": 197, "left": 135, "row": 0, "col": 0}]}, {"mch_good_code": "2023591", "upc": "6925303730574", "width": 55, "height": 219, "depth": 55, "displays": [{"top": 219, "left": 202, "row": 0, "col": 0}]}, {"mch_good_code": "2044894", "upc": "4710094106118", "width": 67, "height": 225, "depth": 67, "displays": [{"top": 225, "left": 257, "row": 0, "col": 0}]}, {"mch_good_code": "2036473", "upc": "6921581597076", "width": 82, "height": 285, "depth": 82, "displays": [{"top": 285, "left": 324, "row": 0, "col": 0}]}, {"mch_good_code": "2041439", "upc": "6921317998825", "width": 100, "height": 310, "depth": 90, "displays": [{"top": 310, "left": 406, "row": 0, "col": 0}]}, {"mch_good_code": "2020054", "upc": "6921168500956", "width": 64, "height": 200, "depth": 64, "displays": [{"top": 200, "left": 506, "row": 0, "col": 0}]}, {"mch_good_code": "2031718", "upc": "6921168559244", "width": 64, "height": 200, "depth": 64, "displays": [{"top": 200, "left": 570, "row": 0, "col": 0}]}, {"mch_good_code": "2030338", "upc": "6922279400265", "width": 65, "height": 203, "depth": 65, "displays": [{"top": 203, "left": 634, "row": 0, "col": 0}]}, {"mch_good_code": "2032659", "upc": "6921581540089", "width": 61, "height": 223, "depth": 61, "displays": [{"top": 223, "left": 699, "row": 0, "col": 0}]}]}]}]}'
        json_info = json.dumps(a)
        data = bytes(json_info, 'utf8')
        resp = requests.post(url=url,data=data,headers=headers)
        print(resp)
        # request = urllib.request.Request(url=url, data=data, headers=headers)

        # response = urllib.request.urlopen(request)
        # print(response.read().decode())
        return Response()


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyEncoder, self).default(obj)

class FreezerImageViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = FreezerImage.objects.order_by('-id')
    serializer_class = FreezerImageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        logger.info('begin detect:{}, {},{}'.format(serializer.instance.group_id, serializer.instance.device_id, serializer.instance.source.path))

        try:
            online_model = OnlineModels.objects.filter(group_id=serializer.instance.group_id).filter(status=10).order_by('-id')[0]
        except:
            serializer.instance.ret = 'model is not ready'
            serializer.instance.save()
            return Response(serializer.instance.ret, status=status.HTTP_400_BAD_REQUEST, headers=headers)

        key = str(online_model.group_id) + "_" + str(online_model.model_id)

        image_np = cv2.imread(serializer.instance.source.path)
        p_class, p_prob, p_box = yolov3_inss_map[key].predict_img(image_np)
        detect_ret = []
        for i in range(len(p_box)):
            detect_ret.append(
                {'class':p_class[i],
                 'score':p_prob[i],
                 'xmin':p_box[i][0],'ymin':p_box[i][1],'xmax':p_box[i][2],'ymax':p_box[i][3]
                 })

        ret = json.dumps(detect_ret, cls=NumpyEncoder)
        serializer.instance.ret = ret
        if len(p_box) > 0:
            image_path = serializer.instance.source.path
            image_dir = os.path.dirname(image_path)
            visual_image_path = os.path.join(image_dir, 'visual_' + os.path.split(image_path)[-1])
            vis_util.visualize_boxes_and_labels_on_image_array(
                image_np,
                np.array(p_box),
                np.array(p_class),
                np.array(p_prob),
                yolov3_inss_map[key].class_names,
                use_normalized_coordinates=False,
                max_boxes_to_draw=None,
                min_score_thresh=yolov3_inss_map[key].score,
                line_thickness=4)
            output_image = Image.fromarray(image_np)
            # output_image.thumbnail((int(im_width), int(im_height)), Image.ANTIALIAS)
            output_image.save(visual_image_path)
            serializer.instance.visual = visual_image_path.replace(settings.MEDIA_ROOT,'')
        serializer.instance.save()

        logger.info('end detect:{}'.format(serializer.instance.device_id))
        return Response(serializer.instance.ret, status=status.HTTP_201_CREATED, headers=headers)

class OnlineModelsViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = OnlineModels.objects.order_by('-id')
    serializer_class = OnlineModelsSerializer

class TrainRecordViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = TrainRecord.objects.order_by('-id')
    serializer_class = TrainRecordSerializer


class MulitImage(APIView):
    def post(self, request):
        try:
            group_id = int(request.query_params['groupid'])
            model_id = int(request.query_params['modelid'])

            filenames = request.data['filenames']

            logger.info(request.data)

            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            logger.error('AddTrain error:{}'.format(e))
            traceback.print_exc()
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)

class AddTrain(APIView):
    def post(self, request):
        try:
            group_id = int(request.query_params['groupid'])
            model_id = int(request.query_params['modelid'])

            data = request.data
            TrainRecord.objects.create(
                group_id=group_id,
                model_id=model_id,
                upcs=json.dumps(data["upcs"]),
                datas=json.dumps(data["files"]),
                status=0
            )


            return Response(status=status.HTTP_200_OK)

        except Exception as e:
            logger.error('AddTrain error:{}'.format(e))
            traceback.print_exc()
            return Response(-1, status=status.HTTP_400_BAD_REQUEST)
