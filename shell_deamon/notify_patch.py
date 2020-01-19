"""
增补发送通知
"""
import sys
import argparse
import traceback
import requests
import json
import main.import_django_settings

from freezers.models import TrainRecord

from set_config import config
def parse_arguments(argv):
    # type,jpg_path,xml_path,classnames,online_batch_id
    parser = argparse.ArgumentParser()

    parser.add_argument('--trainid', type=int, help='trainid', default=0)
    return parser.parse_args(argv)

if __name__ == "__main__":
    args = parse_arguments(sys.argv[1:])
    train_record = TrainRecord.objects.get(id=args.trainid)
    try:
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