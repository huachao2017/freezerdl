import argparse
import sys
import os
import django
import main.import_django_settings
from django.db import connections
from django.db import close_old_connections
import time
from set_config import config
from model_train.keras_yolo3.util import fileutils,write_img_name,voc_anotion
import shutil
from model_train.keras_yolo3.train_test import train


def train_service(shop_id,batch_id,type,jpg_path,xml_path,classnames,online_batch_id=None):
    """
    训练service
    :param shop_id: 商家id
    :param batch_id: 批次id
    :param type: 全量 0  增量 1
    :param jpg_path: 训练服务器，图片绝对路径
    :param xml_path: 训练服务器，
    :param classnames 类别列表
    :param last_batch_id: 上一版 批次id   如果 增量type  , 这个值必传
    :return: None
    """
    check_path(shop_id, batch_id, online_batch_id, type)
    process_train_data(jpg_path, xml_path, shop_id, batch_id, classnames)
    start_time = time.time()
    train._main(classnames,shop_id,batch_id,type,online_batch_id)
    end_time = time.time()
    save_train_table()

def check_path(shop_id,batch_id,online_batch_id,type):
    if online_batch_id is not None and type == 1:
        online_model = os.path.join(str(config.yolov3_train_params['model_dir']).format(shop_id,online_batch_id),str(shop_id)+"_"+str(online_batch_id)+".h5")
        if os.path.exists(online_model) == False:
            print ("增量预加载模型不存在，model_path="+str(online_model))
            type = 0
    JPEGImages_path = str(config.yolov3_train_params['JPEGImages_path']).format(shop_id,batch_id)
    Annotations_path = str(config.yolov3_train_params['Annotations_path']).format(shop_id,batch_id)
    Main_path = str(config.yolov3_train_params['Main_path']).format(shop_id,batch_id)
    model_dir = str(config.yolov3_train_params['model_dir']).format(shop_id,batch_id)
    log_dir = str(config.yolov3_train_params['log_dir']).format(shop_id, batch_id)
    convert_path = str(config.yolov3_train_params['convert_path']).format(shop_id, batch_id)

    if not os.path.exists(JPEGImages_path):
        os.makedirs(JPEGImages_path)
    else:
        fileutils.remove_path_file(JPEGImages_path)
        os.makedirs(JPEGImages_path)
    if not os.path.exists(Annotations_path):
        os.makedirs(Annotations_path)
    else:
        fileutils.remove_path_file(Annotations_path)
        os.makedirs(Annotations_path)
    if not os.path.exists(Main_path):
        os.makedirs(Main_path)
    else:
        fileutils.remove_path_file(Main_path)
        os.makedirs(Main_path)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    else:
        fileutils.remove_path_file(model_dir)
        os.makedirs(model_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    else:
        fileutils.remove_path_file(log_dir)
        os.makedirs(log_dir)
    if not os.path.exists(convert_path):
        os.makedirs(convert_path)
    else:
        fileutils.remove_path_file(convert_path)
        os.makedirs(convert_path)

def process_train_data(jpg_path,xml_path,shop_id, batch_id,classnames):
    JPEGImages_path = str(config.yolov3_train_params['JPEGImages_path']).format(shop_id, batch_id)
    Annotations_path = str(config.yolov3_train_params['Annotations_path']).format(shop_id, batch_id)
    jpgfiles = os.listdir(jpg_path)
    xmlfiles = os.listdir(xml_path)
    for xmlfile in xmlfiles:
        xmlfile_path = os.listdir(xmlfiles,xmlfile)
        file_name,ext_name = os.path.splitext(xmlfile)
        jpgfile =  file_name + ".jpg"
        if os.path.getsize(xmlfile_path)>0 and jpgfile in jpgfiles and os.path.getsize(os.path.join(jpg_path,jpgfile)) > 0:
            shutil.copyfile(os.path.join(xml_path,xmlfile), os.path.join(Annotations_path,xmlfile))
            shutil.copyfile(os.path.join(jpg_path, jpgfile), os.path.join(JPEGImages_path, jpgfile))
    write_img_name.generate_main_txt(shop_id,batch_id)
    voc_anotion.convert(shop_id,batch_id,class_names=classnames)

def save_train_table():
    close_old_connections()
    conn = connections['default']
    cursor_ai = conn.cursor()

def parse_arguments(argv):
    # type,jpg_path,xml_path,classnames,online_batch_id
    parser = argparse.ArgumentParser()

    parser.add_argument('--groupid', type=int, help='groupid', default=0)
    parser.add_argument('--modelid', type=int,
                        help='modelid', default=0)
    parser.add_argument('--type', type=int,
                        help='type', default=0)
    parser.add_argument('--jpg_path', type=str,
                        help='jpg_path', default='')
    parser.add_argument('--xml_path', type=str,
                        help='xml_path', default='')
    parser.add_argument('--classnames', type=str,
                        help='classnames', default='')
    parser.add_argument('--online_model_id', type=int,
                        help='online_model_id', default=0)
    return parser.parse_args(argv)

if __name__ == "__main__":
    import json
    args = parse_arguments(sys.argv[1:])

    train_service(
        args.groupid,
        args.modelid,
        args.type,
        args.jpg_path,
        args.xml_path,
        json.loads(args.classnames),
        args.online_model_id
    )

