#!/user/bin/env.python
#-*-coding:utf-8-*-

"""
Retrain the YOLO model for your own dataset.
"""
import numpy as np
import os
import keras.backend as K
from keras.layers import Input, Lambda
from keras.models import Model
from keras.optimizers import Adam
from keras.callbacks import TensorBoard, ModelCheckpoint, ReduceLROnPlateau, EarlyStopping
from model_train.keras_yolo3.yolo3.model import preprocess_true_boxes, yolo_body, tiny_yolo_body, yolo_loss
from model_train.keras_yolo3.yolo3.utils import get_random_data
from model_train.keras_yolo3.util.default_anchors import default_anchors
from set_config import config
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["CUDA_VISIBLE_DEVICES"]="0"
train_params = config.yolov3_train_params
def train(shop_id,batch_id,model, annotation_path, input_shape, anchors, num_classes, model_dir='model/',type=None):
    model.compile(optimizer='adam',loss={'yolo_loss':lambda y_true,y_pred:y_pred})
    model_dir = str(model_dir).format(shop_id,batch_id)
    logging = TensorBoard(log_dir=model_dir)
    model_name = str(shop_id)+"_"+str(batch_id)+".h5"
    checkpoint = ModelCheckpoint(os.path.join(model_dir , model_name),monitor = 'val_loss',
                                 save_weights_only=True, save_best_only=True, period=1)
    batch_size = 15
    val_split = 0.3
    annotation_path = str(annotation_path).format(shop_id,batch_id)
    with open(annotation_path) as f:
        lines = f.readlines()
    if type is not None and type == 0:
        np.random.shuffle(lines)
    num_val = int(len(lines)*val_split)
    num_train = len(lines) - num_val
    print('Train on {} samples, val on {} samples, with batch size {}.'.format(num_train, num_val, batch_size))
    model.fit_generator(data_generator_wrap(lines[:num_train], batch_size, input_shape, anchors, num_classes),
                        steps_per_epoch=max(1, num_train // batch_size),
                        validation_data=data_generator_wrap(lines[num_train:], batch_size, input_shape, anchors,
                                                            num_classes),
                        validation_steps=max(1, num_val // batch_size),
                        epochs=train_params['epochs'],initial_epoch=1,callbacks=[logging, checkpoint])
    model.save_weights(model_dir + model_name)

def create_model(input_shape, anchors, num_classes, load_pretrained=True, freeze_body=False,weights_path=None):
    K.clear_session()
    image_input = Input(shape=(None, None, 3))
    h, w = input_shape
    num_anchors = len(anchors)
    y_true = [Input(shape=(h//{0:32, 1:16, 2:8}[l], w//{0:32, 1:16, 2:8}[l],
                           num_anchors // 3, num_classes + 5)) for l in range(3)]
    model_body = yolo_body(image_input, num_anchors // 3, num_classes)
    print('Create YOLOv3 model with {} anchors and {} classes.'.format(num_anchors, num_classes))

    if load_pretrained:
        model_body.load_weights(weights_path, by_name=True, skip_mismatch=True)
        print('Load weights {}.'.format(weights_path))
        if freeze_body:
            # Do not freeze 3 output layers
            num = len(model_body.layers) - 7
            for i in range(num): model_body.layers[i].trainable = False
            print('Freeze the first {} layers of total {} layers.'.format(num, len(model_body.layers)))
    model_loss = Lambda(yolo_loss, output_shape=(1,), name='yolo_loss',
                        arguments={'anchors': anchors, 'num_classes': num_classes, 'ignore_thresh': 0.5})([*model_body.output, *y_true])
    model = Model([model_body.input, *y_true], model_loss)
    return model

def data_generator(annotation_lines, batch_size, input_shape, anchors, num_classes):
    '''data generator for fit_generator'''
    n = len(annotation_lines)
    i = 0
    while True:
        image_data = []
        box_data = []
        for b in range(batch_size):
            i %= n
            image, box = get_random_data(annotation_lines[i], input_shape, random=True)
            image_data.append(image)
            box_data.append(box)
            i = i + 1
        image_data = np.array(image_data)
        box_data = np.array(box_data)
        y_true = preprocess_true_boxes(box_data, input_shape, anchors, num_classes)
        yield [image_data, *y_true], np.zeros(batch_size)

def data_generator_wrap(annotation_lines, batch_size, input_shape, anchors, num_classes):
    n = len(annotation_lines)
    if n==0 or batch_size<=0: return None
    return data_generator(annotation_lines, batch_size, input_shape, anchors, num_classes)

def _main(class_names,shop_id,batch_id,type,online_batch_id):
    anchors = np.array(default_anchors)
    input_shape = (416,416)
    flag = False
    weights_path = None
    if online_batch_id is not None and type==1: # 增量训练
        flag = True
        weights_path = os.path.join(str(train_params['model_dir']).format(shop_id,batch_id),(str(shop_id)+"_"+str(online_batch_id)+".h5"))
    model = create_model(input_shape, anchors, len(class_names),load_pretrained=flag,weights_path=weights_path)
    train(shop_id,batch_id,model, train_params['Annotations_path'], input_shape, anchors, len(class_names), model_dir=train_params['model_dir'],type=type)

if __name__ == '__main__':
    class_names=["1","2","3","4","5"]
    _main(class_names,1284,20191231,type=0,online_batch_id=None)