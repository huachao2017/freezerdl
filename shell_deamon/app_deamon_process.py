"""
比较线上版本和训练表，如有新的模型，更新数据库表并发布上线
"""
import shutil
import os
import time
import traceback
import requests
import json
import main.import_django_settings

from freezers.models import OnlineModels, TrainRecord

from django.db import close_old_connections
from django.db import connections
from set_config import config
from freezers.third_tools import dingtalk
from django.conf import settings

if __name__ == "__main__":
    while True:
        print('workflow deamon is alive')
        close_old_connections()

        cursor_default = connections['default'].cursor()
        try:

            # 比较线上版本和训练表
            cursor_default.execute("select tr.id,om.id from freezers_trainrecord as tr left join freezers_onlinemodels as om on tr.group_id = om.group_id where tr.status=20")
            train_records = cursor_default.fetchall()

            for raw_train_record in train_records:
                train_record = TrainRecord.objects.get(id=raw_train_record[0])

                try:
                    begin_time = time.time()
                    # 添加数据库表
                    online_model_dir = "{}/{}".format(config.app_config["online_model_dir"], train_record.group_id)
                    online_model_file = os.path.join(online_model_dir,"0.h5")
                    if os.path.exists(online_model_file):# 如果旧模型存在 把该模型拷贝到历史目录 方便回滚
                        history_file = os.path.join(config.app_config["app_models_history"],str(train_record.group_id)+"_"+str(int(time.time()))+".h5")
                        shutil.copyfile(online_model_file,history_file)

                    shutil.rmtree(online_model_dir, ignore_errors=True)
                    os.makedirs(online_model_dir)
                    type = 0
                    online_model_path = "{}/{}.{}".format(online_model_dir, type, 'h5')

                    # 拷贝模型
                    shutil.copy(train_record.model_path, online_model_path)

                    # 更新数据库表
                    if raw_train_record[1] is not None and raw_train_record[1] > 0:
                        online_models = OnlineModels.objects.get(id=raw_train_record[1])
                        online_models.status = 0
                        online_models.save()

                    OnlineModels.objects.create(
                        group_id = train_record.group_id,
                        model_id = train_record.model_id,
                        type = type,
                        model_path = online_model_path,
                        upcs = train_record.upcs,
                        params = train_record.params,
                        status = 10
                    )

                    train_record.status = 40
                    train_record.save()
                    # 发布上线
                    if settings.IS_TEST_SERVER:
                        # os.system('touch {}/main/test_settings.py'.format(settings.BASE_DIR))
                        os.popen("sh /home/src/freezerdl/shell_deamon/server.sh")
                    else:
                        # os.system('touch {}/main/settings.py'.format(settings.BASE_DIR))
                        os.popen("sh /home/src/freezerdl/shell_deamon/server.sh")

                    # 通知后台
                    url = "{}/v2/admin/training_model/add".format(config.app_config["backend_dns"])
                    headers = {
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    }
                    json_data = {
                        "model_id":train_record.model_id,
                        "complete_time":str(train_record.update_time),
                        "duration":train_record.duration,
                        "sku_count": len(train_record.upcs),
                        "image_count": train_record.pic_cnt,
                        "accuracy_rate": train_record.accuracy_rate,
                        "version": "1.0.0"
                    }
                    json_info = json.dumps(json_data)
                    data = bytes(json_info, 'utf8')
                    resp = requests.post(url=url, data=data, headers=headers)
                    print('通知后台系统：'.format(resp))

                except Exception as e:
                    traceback.print_exc()
                    print('更新数据库表并发布上线错误：{}'.format(e))

        except Exception as e:
            dingtalk.send_message(str(e), 3)
            print('守护进程出现错误：{}'.format(e))
        finally:
            cursor_default.close()

        time.sleep(10)
