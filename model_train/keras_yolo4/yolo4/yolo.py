# -*- coding: utf-8 -*-
"""
Class definition of YOLO_v3 style detection model on image and video
"""

import colorsys
from timeit import default_timer as timer

import numpy as np
from keras import backend as K
from keras.models import load_model
from keras.layers import Input
from PIL import Image, ImageFont, ImageDraw
import cv2
from model_train.keras_yolo4.yolo4.model import yolo_eval,yolo4_body
from model_train.keras_yolo4.yolo4.utils import letterbox_image
from model_train.keras_yolo4.good_proxy import proxy
import os
from keras.utils import multi_gpu_model
from set_config import config
from model_train.keras_yolo4.util.default_anchors import default_anchors
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
gpu_num = 1

class YOLO(object):

    def __init__(self,class_names,diff_switch_iou,single_switch_iou_minscore,model_path,iou,score):
        """
        对象初始化
        :param class_names: 商品upc 列表
        :param diff_switch_iou: 不同 类品策略开关及iou配置   (True,0.2)
        :param single_switch_iou_minscore: 单独 品策略开关及iou配置  (True,0.0,0.28)
        :param model_path:  线上模型路径
        :param iou:  线上模型配置 iou
        :param score:  线上模型阈值
        """
        print ("class_names"+str(class_names))
        print ("diff_switch_iou"+str(diff_switch_iou))
        print ("single_switch_iou_minscore"+str(single_switch_iou_minscore))
        print ("model_path"+str(model_path))
        print ("iou"+str(iou))
        print ("score"+str(score))

        config = tf.ConfigProto()
        config.gpu_options.allocator_type = 'BFC'  # A "Best-fit with coalescing" algorithm, simplified from a version of dlmalloc.
        config.gpu_options.per_process_gpu_memory_fraction = 0.2
        config.gpu_options.allow_growth = True
        set_session(tf.Session(config=config))
        (self.diff_switch, self.diff_iou) = diff_switch_iou
        (self.single_switch, self.single_iou, self.single_min_score) = single_switch_iou_minscore
        self.model_path = model_path
        self.iou = iou
        self.score = score
        self.model_image_size = (608,608)
        self.class_names = class_names
        self.anchors = np.array(default_anchors)
        self.sess = K.get_session()
        self.boxes, self.scores, self.classes = self.load_yolo()
        self.gpu_num = gpu_num

    def load_yolo(self):
        model_path = os.path.expanduser(self.model_path)
        assert model_path.endswith('.h5'), 'Keras model or weights must be a .h5 file.'
        num_anchors = len(self.anchors)
        num_classes = len(self.class_names)
        # Generate colors for drawing bounding boxes.
        hsv_tuples = [(x / len(self.class_names), 1., 1.)
                      for x in range(len(self.class_names))]
        self.colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        self.colors = list(
            map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
                self.colors))
        self.sess = K.get_session()

        # Load model, or construct model and load weights.
        self.yolo4_model = yolo4_body(Input(shape=(608, 608, 3)), num_anchors // 3, num_classes)
        self.yolo4_model.load_weights(model_path)

        print('{} model, anchors, and classes loaded.'.format(model_path))

        if self.gpu_num >= 2:
            self.yolo4_model = multi_gpu_model(self.yolo4_model, gpus=self.gpu_num)

        self.input_image_shape = K.placeholder(shape=(2,))
        boxes, scores, classes = yolo_eval(self.yolo4_model.output, self.anchors,
                                                          len(self.class_names), self.input_image_shape,
                                                          score_threshold=self.score)
        return self.boxes, self.scores, self.classes
    def detect_image(self, image, model_image_size=(608, 608)):
        start = timer()
        boxed_image = letterbox_image(image, tuple(reversed(model_image_size)))
        image_data = np.array(boxed_image, dtype='float32')
        print(image_data.shape)
        image_data /= 255.
        image_data = np.expand_dims(image_data, 0)  # Add batch dimension.
        out_boxes, out_scores, out_classes = self.sess.run(
            [self.boxes, self.scores, self.classes],
            feed_dict={
                self.yolo4_model.input: image_data,
                self.input_image_shape: [image.size[1], image.size[0]],
                # K.learning_phase(): 0
            })
        out_classes, out_scores, out_boxes = list(out_classes), list(out_scores), list(out_boxes)
        if self.diff_switch:
            out_classes, out_scores, out_boxes = proxy.diff_fiter(self.diff_iou, out_classes, out_scores, out_boxes)

        if self.single_switch:
            out_classes, out_scores, out_boxes = proxy.single_filter(self.single_iou, self.single_min_score,
                                                                     out_classes, out_scores, out_boxes)
        print('Found {} boxes for {}'.format(len(out_boxes), 'img'))
        font_file = config.yolov4_predict_params['font_file']
        font = ImageFont.truetype(font=font_file,
                    size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
        thickness = (image.size[0] + image.size[1]) // 300
        for i, c in reversed(list(enumerate(out_classes))):
            predicted_class = self.class_names[c]
            box = out_boxes[i]
            score = out_scores[i]
            label = '{} {:.2f}'.format(predicted_class, score)
            draw = ImageDraw.Draw(image)
            label_size = draw.textsize(label, font)
            top, left, bottom, right = box
            top = max(0, np.floor(top + 0.5).astype('int32'))
            left = max(0, np.floor(left + 0.5).astype('int32'))
            bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
            right = min(image.size[0], np.floor(right + 0.5).astype('int32'))
            print(label, (left, top), (right, bottom))
            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])

            # My kingdom for a good redistributable image drawing library.
            for i in range(thickness):
                draw.rectangle(
                    [left + i, top + i, right - i, bottom - i],
                    outline=self.colors[c])
            draw.rectangle(
                [tuple(text_origin), tuple(text_origin + label_size)],
                fill=self.colors[c])
            draw.text(text_origin, label, fill=(0, 0, 0), font=font)
            del draw
        end = timer()
        print(end - start)
        return image,out_classes, out_scores, out_boxes

    def predict_img(self,img):
        """
        检测图片
        :param img:  cv2 read的img
        :return: 类别，得分，位置列表
        """
        image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if self.model_image_size != (None, None):
            assert self.model_image_size[0] % 32 == 0, 'Multiples of 32 required'
            assert self.model_image_size[1] % 32 == 0, 'Multiples of 32 required'
            boxed_image = letterbox_image(image, tuple(reversed(self.model_image_size)))
        else:
            new_image_size = (image.width - (image.width % 32),
                              image.height - (image.height % 32))
            boxed_image = letterbox_image(image, new_image_size)
        image_data = np.array(boxed_image, dtype='float32')
        print(image_data.shape)
        image_data /= 255.
        image_data = np.expand_dims(image_data, 0)  # Add batch dimension.
        out_boxes, out_scores, out_classes = self.sess.run(
            [self.boxes, self.scores, self.classes],
            feed_dict={
                self.yolo_model.input: image_data,
                self.input_image_shape: [image.size[1], image.size[0]],
                #K.learning_phase(): 0
            })
        print('Found {} boxes for {}'.format(len(out_boxes), 'img'))
        p_class = []
        p_prob = []
        p_box = []
        for i, c in reversed(list(enumerate(out_classes))):
            predicted_class = self.class_names[c]
            p_class.append(predicted_class)
            xmin = int(out_boxes[i][1]) if int(out_boxes[i][1]) > 0 else 0
            ymin = int(out_boxes[i][0]) if int(out_boxes[i][0]) > 0 else 0
            xmax = int(out_boxes[i][3]) if int(out_boxes[i][3]) > 0 else 0
            ymax = int(out_boxes[i][2]) if int(out_boxes[i][2]) > 0 else 0
            box = (xmin,ymin,xmax,ymax)
            p_box.append(box)
            score = out_scores[i]
            p_prob.append(score)
        if self.diff_switch:
            p_class, p_prob, p_box = proxy.diff_fiter(self.diff_iou,  p_class, p_prob, p_box)
        if self.single_switch:
            p_class, p_prob, p_box = proxy.single_filter(self.single_iou, self.single_min_score, p_class, p_prob, p_box)
        return p_class,p_prob,p_box
    def close_session(self):
        self.sess.close()

def detect_video(yolo, video_path, output_path=""):
    import cv2
    vid = cv2.VideoCapture(video_path)
    if not vid.isOpened():
        raise IOError("Couldn't open webcam or video")
    video_FourCC = int(vid.get(cv2.CAP_PROP_FOURCC))
    video_fps = vid.get(cv2.CAP_PROP_FPS)
    video_size = (int(vid.get(cv2.CAP_PROP_FRAME_WIDTH)),int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    isOutput = True if output_path != "" else False
    if isOutput:
        print("!!! TYPE:", type(output_path), type(video_FourCC), type(video_fps), type(video_size))
        out = cv2.VideoWriter(output_path, video_FourCC, video_fps, video_size)
    accum_time = 0
    curr_fps = 0
    fps = "FPS: ??"
    prev_time = timer()
    while True:
        return_value, frame = vid.read()
        image = Image.fromarray(frame)
        image = yolo.detect_image(image)
        result = np.asarray(image)
        curr_time = timer()
        exec_time = curr_time - prev_time
        prev_time = curr_time
        accum_time = accum_time + exec_time
        curr_fps = curr_fps + 1
        if accum_time > 1:
            accum_time = accum_time - 1
            fps = "FPS: " + str(curr_fps)
            curr_fps = 0
        cv2.putText(result, text=fps, org=(3, 15), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.50, color=(255, 0, 0), thickness=2)
        cv2.namedWindow("result", cv2.WINDOW_NORMAL)
        cv2.imshow("result", result)
        if isOutput:
            out.write(result)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    yolo.close_session()

