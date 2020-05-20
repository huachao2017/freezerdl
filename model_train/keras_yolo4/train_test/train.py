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
from model_train.keras_yolo4.util import fileutils,write_img_name,voc_anotion
from keras.optimizers import Adam
from keras.callbacks import TensorBoard, ModelCheckpoint, ReduceLROnPlateau, EarlyStopping
from model_train.keras_yolo4.yolo4.model import preprocess_true_boxes, yolo4_body, yolo4_loss
from model_train.keras_yolo4.yolo4.utils import get_random_data
from model_train.keras_yolo4.util.default_anchors import default_anchors
from set_config import config
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["CUDA_VISIBLE_DEVICES"]="0"
train_params = config.yolov4_train_params
def train(shop_id,batch_id,model, convert_path, input_shape, anchors, num_classes, model_dir='model/',type=None):
    model.compile(optimizer='adam',loss={'yolo_loss':lambda y_true,y_pred:y_pred})
    model_dir = str(model_dir).format(shop_id,batch_id)
    logging = TensorBoard(log_dir=model_dir)
    model_name = str(shop_id)+"_"+str(batch_id)+".h5"
    checkpoint = ModelCheckpoint(os.path.join(model_dir , model_name),monitor = 'val_loss',
                                 save_weights_only=True, save_best_only=True, period=2)
    batch_size = 4
    val_split = 0.3
    convert_path = str(convert_path).format(shop_id,batch_id)
    train_voc_file = os.path.join(convert_path,"2007_train.txt")
    with open(train_voc_file) as f:
        lines = f.readlines()
    if type is not None and type == 0:
        np.random.shuffle(lines)
        epochs = train_params['type_all_echos']
    else:
        np.random.shuffle(lines)
        epochs = train_params['type_add_echos']
    num_val = int(len(lines)*val_split)
    num_train = len(lines) - num_val
    # num_train = len(lines)
    print('Train on {} samples, val on {} samples, with batch size {}.'.format(num_train, num_val, batch_size))
    model.fit_generator(data_generator_wrapper(lines[:num_train], batch_size, input_shape, anchors, num_classes),
                        steps_per_epoch=max(1, num_train // batch_size),
                        validation_data=data_generator_wrapper(lines[num_train:], batch_size, input_shape, anchors,
                                                               num_classes),
                        validation_steps=max(1, num_val // batch_size),
                        epochs=epochs,
                        initial_epoch=1,
                        callbacks=[logging, checkpoint])
    model.save_weights(model_dir + model_name)


def create_model(input_shape, anchors, num_classes, load_pretrained=True, freeze_body=2,
            weights_path=None):
    '''create the training model'''
    K.clear_session() # get a new session
    image_input = Input(shape=(None, None, 3))
    h, w = input_shape
    num_anchors = len(anchors)
    y_true = [Input(shape=(h//{0:32, 1:16, 2:8}[l], w//{0:32, 1:16, 2:8}[l], \
        num_anchors//3, num_classes+5)) for l in range(3)]
    model_body = yolo4_body(image_input, num_anchors//3, num_classes)
    print('Create YOLOv4 model with {} anchors and {} classes.'.format(num_anchors, num_classes))
    if load_pretrained:
        model_body.load_weights(weights_path, by_name=True, skip_mismatch=True)
        print('Load weights {}.'.format(weights_path))
        if freeze_body in [1, 2]:
            # Freeze darknet53 body or freeze all but 3 output layers.
            num = (250, len(model_body.layers)-3)[freeze_body-1]
            for i in range(num): model_body.layers[i].trainable = False
            print('Freeze the first {} layers of total {} layers.'.format(num, len(model_body.layers)))

    label_smoothing = 0
    use_focal_obj_loss = False
    use_focal_loss = False
    use_diou_loss = True
    use_softmax_loss = False

    model_loss = Lambda(yolo4_loss, output_shape=(1,), name='yolo_loss',
        arguments={'anchors': anchors, 'num_classes': num_classes, 'ignore_thresh': 0.5,
        'label_smoothing': label_smoothing, 'use_focal_obj_loss': use_focal_obj_loss, 'use_focal_loss': use_focal_loss, 'use_diou_loss': use_diou_loss,
        'use_softmax_loss': use_softmax_loss})(
        [*model_body.output, *y_true])
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
            if i==0:
                np.random.shuffle(annotation_lines)
            image, box = get_random_data(annotation_lines[i], input_shape, random=True)
            image_data.append(image)
            box_data.append(box)
            i = (i+1) % n
        image_data = np.array(image_data)
        box_data = np.array(box_data)
        y_true = preprocess_true_boxes(box_data, input_shape, anchors, num_classes)
        yield [image_data, *y_true], np.zeros(batch_size)

def data_generator_wrapper(annotation_lines, batch_size, input_shape, anchors, num_classes):
    n = len(annotation_lines)
    if n==0 or batch_size<=0: return None
    return data_generator(annotation_lines, batch_size, input_shape, anchors, num_classes)

def _main(class_names,shop_id,batch_id,type,online_batch_id):
    anchors = np.array(default_anchors)
    input_shape = (608,608)
    flag = False
    weights_path = None
    if online_batch_id is not None and type==1: # 增量训练
        flag = True
        weights_path = os.path.join(str(train_params['model_dir']).format(shop_id,online_batch_id),(str(shop_id)+"_"+str(online_batch_id)+".h5"))
    model = create_model(input_shape, anchors, len(class_names),load_pretrained=flag,weights_path=weights_path)
    train(shop_id,batch_id,model, train_params['convert_path'], input_shape, anchors, len(class_names), model_dir=train_params['model_dir'],type=type)

if __name__ == '__main__':
    class_names=["8993175537445", "6942404230086", "6922255447833", "6928804010145", "6941704408317", "6911988014320", "6902083880781", "6922222702156", "6921168509256", "6942404210088", "6921168593576", "6941704408492", "6925303730574", "6928804011296", "6941704403824", "6925303770563", "6907992513560", "6920459905012"]
    shop_id = 1
    batch_id = 1
    write_img_name.generate_main_txt(shop_id, batch_id)
    voc_anotion.convert(shop_id, batch_id, class_names=class_names)
    _main(class_names,1,1,type=1,online_batch_id=1)