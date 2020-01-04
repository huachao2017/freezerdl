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
from model_train.keras_yolo3.train_test.mAp1 import predict,mAp
import demjson
import traceback
def train_service(group_id, model_id, type, jpg_path, xml_path, classnames, online_model_id=None):
    """
    训练service
    :param group_id: 商家id
    :param model_id: 批次id
    :param type: 全量 0  增量 1
    :param jpg_path: 训练服务器，图片绝对路径
    :param xml_path: 训练服务器，
    :param classnames 类别列表
    :param last_batch_id: 上一版 批次id   如果 增量type  , 这个值必传
    :return: None
    """
    try:
        # 数据处理
        check_path(group_id, model_id, online_model_id, type)
        process_train_data(jpg_path, xml_path, group_id, model_id, classnames)
        # 训练
        start_time = int(time.time())
        train._main(classnames, group_id, model_id, type, online_model_id)
        end_time = int(time.time())

        # 求mAP
        good_config_params,all_config_params = cal_mAp(group_id,model_id,classnames)
        end_time1 = int(time.time())
        # 选择最优的mAp 的参数配置保存数据库
        save_train_table(group_id, model_id, type,train_los_time = int(end_time-start_time),val_los_time = int(end_time1-end_time),good_config_params= good_config_params,all_config_params = all_config_params,status = 0,des_msg='')
    except Exception as e:
        traceback.print_exc()
        des_msg = "error:e={}".format(e)
        save_train_table(group_id, model_id, type,
                         train_los_time=0, val_los_time=0,
                         good_config_params='', all_config_params='', status=0,
                         des_msg=des_msg)
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
    wfile_path = str(config.yolov3_train_params['predict_wfile_path']).format(shop_id, batch_id)
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

    if not os.path.exists(wfile_path):
        os.makedirs(wfile_path)
    else:
        fileutils.remove_path_file(wfile_path)
        os.makedirs(wfile_path)

def process_train_data(jpg_path,xml_path,shop_id, batch_id,classnames):
    JPEGImages_path = str(config.yolov3_train_params['JPEGImages_path']).format(shop_id, batch_id)
    Annotations_path = str(config.yolov3_train_params['Annotations_path']).format(shop_id, batch_id)
    jpgfiles = os.listdir(jpg_path)
    xmlfiles = os.listdir(xml_path)
    for xmlfile in xmlfiles:
        xmlfile_path = os.path.join(xml_path,xmlfile)
        file_name,ext_name = os.path.splitext(xmlfile)
        jpgfile =  file_name + ".jpg"
        if os.path.getsize(xmlfile_path)>0 and jpgfile in jpgfiles and os.path.getsize(os.path.join(jpg_path,jpgfile)) > 0:
            shutil.copyfile(os.path.join(xml_path,xmlfile), os.path.join(Annotations_path,xmlfile))
            shutil.copyfile(os.path.join(jpg_path, jpgfile), os.path.join(JPEGImages_path, jpgfile))
    write_img_name.generate_main_txt(shop_id,batch_id)
    voc_anotion.convert(shop_id,batch_id,class_names=classnames)

def cal_mAp(shop_id,batch_id,classnames):
    default_config_params = config.yolov3_train_params['default_config_params']
    good_select_config_params_mAP = 0
    good_select_config_params = ''
    for config_params in default_config_params:
        wfile = (config.yolov3_train_params['predict_wfile']).format(shop_id,batch_id,config_params)
        testJpgPath = str(config.yolov3_train_params['JPEGImages_path']).format(shop_id,batch_id)
        testXmlPath = str(config.yolov3_train_params['Annotations_path']).format(shop_id,batch_id)
        diff_switch_iou = dict(default_config_params[config_params])["diff_switch_iou"]
        single_switch_iou_minscore = dict(default_config_params[config_params])["single_switch_iou_minscore"]
        iou = dict(default_config_params[config_params])["iou"]
        score = dict(default_config_params[config_params])["score"]
        model_path = os.path.join(str(config.yolov3_train_params['model_dir']).format(shop_id,batch_id),str("{}_{}.h5").format(shop_id,batch_id))
        predict.predict(testJpgPath, wfile, classnames, diff_switch_iou, single_switch_iou_minscore, model_path, iou =iou, score =score)
        mAp_ins = mAp.MAp(classnames,testXmlPath,testJpgPath,wfile)
        ap_dict = mAp_ins.averagePrecision()
        mAp_value = mAp_ins.meanAveragePrecesion(ap_dict)
        default_config_params[config_params]["Ap"] = ap_dict
        default_config_params[config_params]["mAp"] = float(mAp_value)
        if mAp_value >= good_select_config_params_mAP:
            good_select_config_params = default_config_params[config_params]
            good_select_config_params_mAP = mAp_value
    return good_select_config_params,default_config_params




def save_train_table(group_id, model_id, type,train_los_time=0,val_los_time=0,good_config_params='',all_config_params='',status=1,des_msg=''):
    close_old_connections()
    conn = connections['default']
    cursor_ai = conn.cursor()
    delete_sql = "delete from freezers_traindetail where group_id = {} and model_id ={} and type={} "
    cursor_ai.execute(
        delete_sql.format(group_id,model_id,type))
    cursor_ai.connection.commit()

    insert_sql = "insert into freezers_traindetail (group_id,model_id,model_path,accuracy_rate,create_time,params_config,status,train_los_time,val_result,type,val_los_time,des_msg) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    model_path = os.path.join(str(config.yolov3_train_params['model_dir']).format(group_id,model_id),str("{}_{}.h5").format(group_id,model_id))
    if good_config_params != '':
        accuracy_rate = float(good_config_params['mAp'])
        (switch,score_st) = good_config_params['diff_switch_iou']
        (sswitch,s_iou,score_sst) = good_config_params['single_switch_iou_minscore']
        good_config_params['diff_switch_iou'] = (True,score_st)
        good_config_params['single_switch_iou_minscore'] = (True,s_iou,score_sst)
        config_param = {}
        config_param['diff_switch_iou'] = (True,score_st)
        config_param['single_switch_iou_minscore'] = (True,s_iou,score_sst)
        config_param['score'] = good_config_params['score']
        config_param['iou'] = good_config_params['iou']
        config_param = demjson.encode(config_param)
    else:
        accuracy_rate = 0.0
        config_param = ''
    val_result = ''
    if all_config_params != '':
        val_result = str(all_config_params)
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    data = [(
        group_id,
        model_id,
        model_path,
        accuracy_rate,
        create_time,
        config_param,
        status,
        train_los_time,
        val_result,
        type,
        val_los_time,
        des_msg
    )]
    cursor_ai.executemany(insert_sql, data)
    cursor_ai.connection.commit()
    conn.close()
    cursor_ai.close()

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

    if args.online_model_id == 0:
        args.online_model_id = None
    train_service(
        args.groupid,
        args.modelid,
        args.type,
        args.jpg_path,
        args.xml_path,
        json.loads(args.classnames),
        args.online_model_id
    )

