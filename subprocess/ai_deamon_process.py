"""
任务1：轮询训练表，下载图片，启动训练进程（每一个训练进程都会传参 商家Id和批次Id）
任务2：轮询训练状态，训练状态表字段表明结束后，拷贝模型，更新数据库
"""
import os
import time
import traceback
import subprocess
import main.import_django_settings
from freezers.models import TrainRecord

from django.conf import settings

from django.db import close_old_connections
from django.db import connections
from set_config import config
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
                    log_dir = config.yolov3_train_params['log_dir'].format(waiting_record.group_id, waiting_record.model_id)
                    # TODO 启动训练进程
                    command = 'nohup python3 {}/raw/train.py -- > {}/train.out 2>&1 &'.format(
                        os.path.join(settings.BASE_DIR, 'dl'),
                        log_dir
                    )
                    print(command)
                    subprocess.call(command, shell=True)

            # 任务2：轮询训练状态，训练状态表字段表明结束后，拷贝模型，更新数据库
            # TODO

        except Exception as e:
            print('守护进程出现错误：{}'.format(e))
        finally:
            cursor_default.close()

        time.sleep(10)
