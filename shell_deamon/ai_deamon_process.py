"""
任务1：轮询训练表，下载图片，启动训练进程（每一个训练进程都会传参 商家Id和批次Id）
任务2：轮询训练状态，训练状态表字段表明结束后，拷贝模型，更新数据库
"""
import os
import time
import json
import shutil
import traceback
import urllib.request
import subprocess
import main.import_django_settings
from freezers.models import TrainRecord, OnlineModels

from django.conf import settings

from django.db import close_old_connections
from django.db import connections
from set_config import config


class RemoteShell:
    def __init__(self, host, user, pwd):
        self.host = host
        self.user = user
        self.pwd = pwd

    def put(self, local_path, remote_path):
        scp_put = '''  
        set timeout -1
        spawn scp %s %s@%s:%s  
        expect "(yes/no)?" {  
        send "yes\r"  
        expect "password:"  
        send "%s\r"  
        } "password:" {send "%s\r"}  
        expect eof  
        exit'''
        os.system("echo '%s' > scp_put.cmd" % (scp_put % (os.path.expanduser(local_path), self.user, self.host, remote_path, self.pwd, self.pwd)))
        os.system('expect scp_put.cmd')
        os.system('rm scp_put.cmd')

if __name__ == "__main__":
    while True:
        print('workflow deamon is alive')
        close_old_connections()

        cursor_default = connections['default'].cursor()
        try:

            # 任务1：轮询训练表，下载图片，启动训练进程（每一个训练进程都会传参 商家Id和批次Id）
            training_records = TrainRecord.objects.filter(status=10)
            if len(training_records) == 0: # 必须没有正在训练的
                waiting_records = TrainRecord.objects.filter(status=0)
                if len(waiting_records) > 0: # 发现有排队的
                    waiting_record = waiting_records[0]
                    waiting_record.status = 10
                    # 下载图片
                    upcs = json.loads(waiting_record.upcs)
                    files = json.loads(waiting_record.datas)
                    img_download_file_dir = config.ai_config["img_download_file_dir_template"].format(waiting_record.group_id, waiting_record.model_id)
                    xml_download_file_dir = config.ai_config["xml_download_file_dir_template"].format(waiting_record.group_id, waiting_record.model_id)

                    shutil.rmtree(img_download_file_dir, ignore_errors=True)
                    shutil.rmtree(xml_download_file_dir, ignore_errors=True)
                    os.makedirs(img_download_file_dir)
                    os.makedirs(xml_download_file_dir)
                    for file in files:
                        image_name = file['image'].split('/')[-1]
                        urllib.request.urlretrieve(file['image'], os.path.join(img_download_file_dir, image_name))
                        xml_name = file['xml'].split('/')[-1]
                        urllib.request.urlretrieve(file['xml'], os.path.join(xml_download_file_dir, xml_name))

                    waiting_record.pic_cnt = len(files)
                    waiting_record.save()

                    log_dir = config.yolov3_train_params['log_dir'].format(waiting_record.group_id, waiting_record.model_id)
                    shutil.rmtree(log_dir, ignore_errors=True)
                    os.makedirs(log_dir)
                    # 判断全量和增量
                    online_models = OnlineModels.objects.filter(status=10).filter(group_id=waiting_record.group_id).all()
                    if len(online_models)>0:
                        type = 1
                        command = "nohup python3 {}/model_train/keras_yolo3/service/train_service.py --groupid={} --modelid={} --type={} --jpg_path={} --xml_path={} --classnames={} --online_model_id={} > {}train.out 2>&1 &".format(
                            settings.BASE_DIR,
                            waiting_record.group_id,
                            waiting_record.model_id,
                            type,
                            img_download_file_dir,
                            xml_download_file_dir,
                            waiting_record.upcs,
                            online_models[0].model_id,
                            log_dir
                        )
                    else:
                        type = 0
                        command = "nohup python3 {}/model_train/keras_yolo3/service/train_service.py --groupid={} --modelid={} --type={} --jpg_path={} --xml_path={} --classnames={} --online_model_id={} > {}train.out 2>&1 &".format(
                            settings.BASE_DIR,
                            waiting_record.group_id,
                            waiting_record.model_id,
                            type,
                            img_download_file_dir,
                            xml_download_file_dir,
                            waiting_record.upcs,
                            0,
                            log_dir
                    )

                    # 启动训练进程
                    print(command)
                    subprocess.call(command, shell=True)

            # 任务2：轮询训练状态，训练状态表字段表明结束后，拷贝模型，更新数据库
            cursor_default.execute("select tr.id, td.status, td.model_path, td.accuracy_rate, td.params_config, td.train_los_time from freezers_traindetail as td, freezers_trainrecord as tr where tr.model_id=td.model_id and td.status=1")
            finish_train_details = cursor_default.fetchall()
            for finish_train_detail in finish_train_details:
                train_record = TrainRecord.objects.get(id=finish_train_detail[0])
                if finish_train_detail[1] == 0:
                    train_record.status = 30
                    train_record.save()
                elif finish_train_detail[1] == 1:
                    ai_model_path = finish_train_detail[2]
                    ai_model_name = ai_model_path.split('/')[-1]
                    train_record.status = 20
                    train_record.model_path = '{}/{}_{}_{}'.format(config.ai_config["app_models_path"], train_record.group_id, train_record.model_id, ai_model_name)
                    train_record.duration = finish_train_detail[5]
                    train_record.params = finish_train_detail[4]
                    train_record.finishtime = '' # fixme
                    train_record.accuracy_rate = finish_train_detail[3]


                    # 拷贝模型
                    rs = RemoteShell(config.ai_config["app_host"], config.ai_config["app_user"], config.ai_config["app_password"])
                    rs.put(ai_model_path, train_record.model_path)

                    train_record.save()

        except Exception as e:
            traceback.print_exc()
            print('守护进程出现错误：{}'.format(e))
        finally:
            cursor_default.close()

        time.sleep(10)
