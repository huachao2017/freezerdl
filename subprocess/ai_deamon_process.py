"""
任务1：轮询训练表，下载图片，启动训练进程（每一个训练进程都会传参 商家Id和批次Id）
任务2：轮询训练状态，训练状态表字段表明结束后，拷贝模型，更新数据库
"""
import os
import time
import json
import traceback
import urllib.request
import subprocess
import main.import_django_settings
from freezers.models import TrainRecord

from django.conf import settings

from django.db import close_old_connections
from django.db import connections
from set_config import config

img_download_file_dir_template = "/data/downloads/{}_{}/imgs/"
xml_download_file_dir_template = "/data/downloads/{}_{}/xmls/"
app_models_path = ""
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
                    img_download_file_dir = img_download_file_dir_template.format(waiting_record.group_id, waiting_record.model_id)
                    xml_download_file_dir = xml_download_file_dir_template.format(waiting_record.group_id, waiting_record.model_id)

                    os.makedirs(img_download_file_dir)
                    os.makedirs(xml_download_file_dir)
                    for file in files:
                        image_name = file['image'].split('/')[-1]
                        urllib.request.urlretrieve(file['image'], os.path.join(img_download_file_dir, image_name))
                        xml_name = file['xml'].split('/')[-1]
                        urllib.request.urlretrieve(file['xml'], os.path.join(xml_download_file_dir, xml_name))

                    waiting_record.save()

                    # TODO 需要判断全量和增量
                    log_dir = config.yolov3_train_params['log_dir'].format(waiting_record.group_id, waiting_record.model_id)

                    # FIXME 启动训练进程
                    command = 'nohup python3 {}/raw/train.py -- > {}/train.out 2>&1 &'.format(
                        os.path.join(settings.BASE_DIR, 'dl'),
                        log_dir
                    )
                    print(command)
                    subprocess.call(command, shell=True)

            # 任务2：轮询训练状态，训练状态表字段表明结束后，拷贝模型，更新数据库
            cursor_default.execute("select tr.id, td.status, td.model_path, td.accuracy_rate from freezers_traindetail as td left join freezers_trainrecord as tr on tr.model_id=om.model_id where tr.model_id is null")
            finish_train_details = cursor_default.fetchall()
            for finish_train_detail in finish_train_details:
                train_record = TrainRecord.objects.get(id=finish_train_detail[0])
                if finish_train_detail[1] == 0:
                    train_record.status = 30
                    train_record.save()
                elif finish_train_detail[1] == 1:
                    ai_model_path = finish_train_detail[2]
                    train_record.status = 20
                    train_record.model_path = 0 # fixme
                    train_record.duration = 0 # fixme
                    train_record.finishtime = 0 # fixme
                    train_record.accuracy_rate = finish_train_detail[3]


                    # TODO 拷贝模型
                    train_record.save()

        except Exception as e:
            print('守护进程出现错误：{}'.format(e))
        finally:
            cursor_default.close()

        time.sleep(10)
