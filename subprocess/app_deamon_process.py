"""
比较线上版本和训练表，如有新的模型，更新数据库表并发布上线
"""
import time
import traceback
import main.import_django_settings

from freezers.models import OnlineModels, TrainRecord

from django.db import close_old_connections
from django.db import connections

if __name__ == "__main__":
    while True:
        print('workflow deamon is alive')
        close_old_connections()

        cursor_default = connections['default'].cursor()
        try:

            # 比较线上版本和训练表
            cursor_default.execute("select tr.id from freezers_trainrecord as tr left join freezers_onlinemodels as om on tr.model_id=om.model_id where tr.status=20 and om.model_id is null")
            train_records = cursor_default.fetchall()

            for train_record in train_records:
                try:
                    begin_time = time.time()
                    # TODO 更新数据库表并发布上线

                except Exception as e:
                    traceback.print_exc()
                    print('更新数据库表并发布上线错误：{}'.format(e))

        except Exception as e:
            print('守护进程出现错误：{}'.format(e))
        finally:
            cursor_default.close()

        time.sleep(10)
