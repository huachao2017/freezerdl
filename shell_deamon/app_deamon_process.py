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

if __name__ == "__main__":
    while True:
        print('workflow deamon is alive')
        close_old_connections()

        cursor_default = connections['default'].cursor()
        try:

            # 比较线上版本和训练表
            cursor_default.execute("select tr.id from freezers_trainrecord as tr left join freezers_onlinemodels as om on tr.model_id=om.model_id where tr.status=20 and om.model_id is null")
            train_records = cursor_default.fetchall()

            for raw_train_record in train_records:
                train_record = TrainRecord.objects.get(id=raw_train_record[0])
                try:
                    begin_time = time.time()

                    # 更新数据库表
                    all_online_models = OnlineModels.objects.filter(group_id=train_record.group_id).filter(status=10).all()
                    for online_model in all_online_models:
                        online_model.status = 0
                        online_model.save()

                    # 添加数据库表
                    online_model_dir = "{}/{}".format(config.app_config["online_model_dir"], train_record.group_id)
                    shutil.rmtree(online_model_dir, ignore_errors=True)
                    os.makedirs(online_model_dir)
                    type = 0
                    online_model_path = "{}/{}.{}".format(online_model_dir, type, 'h5')

                    # 拷贝模型
                    shutil.copy(train_record.model_path, online_model_path)

                    # 更新数据库表
                    OnlineModels.objects.create(
                        group_id = train_record.group_id,
                        model_id = train_record.model_id,
                        type = type,
                        model_path = online_model_path,
                        upcs = train_record.upcs,
                        params = "", # fixme
                        status = 10
                    )

                    # 发布上线
                    os.system('touch /home/src/freezerdl/main/settings.py')
                    os.system('touch /home/src/freezerdl/main/test_settings.py')

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
            print('守护进程出现错误：{}'.format(e))
        finally:
            cursor_default.close()

        time.sleep(10)
