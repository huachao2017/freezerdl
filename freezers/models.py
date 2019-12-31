from django.db import models
import datetime
from django.conf import settings

def image_upload_source(instance, filename):
    now = datetime.datetime.now()
    return '{}/{}/{}/{}/{}_{}_{}'.format(settings.DETECT_DIR_NAME, instance.group_id, now.strftime('%Y%m'),
                                         now.strftime('%d%H'), now.strftime('%M%S'), str(now.time()), filename)


class FreezerImage(models.Model):
    group_id = models.IntegerField()
    device_id = models.CharField(max_length=20, default='0', db_index=True)
    ret = models.TextField(default='')
    source = models.ImageField(max_length=200, upload_to=image_upload_source)
    visual = models.URLField(max_length=200, default='')
    create_time = models.DateTimeField('date created', auto_now_add=True)

class OnlineModels(models.Model):
    # 分组Id，模型Id，线上的模型路径，upc列表，模型参数，状态（上线/下线），开始时间，结束时间
    group_id = models.IntegerField()
    model_id = models.IntegerField()
    type = models.IntegerField(default=0)   # 0:yolov3,
    model_path = models.CharField(max_length=200)
    upcs = models.TextField()
    params = models.TextField()
    status = models.IntegerField(default=0) # 0下线，10上线
    create_time = models.DateTimeField('date created', auto_now_add=True)
    update_time = models.DateTimeField('date updated', auto_now=True)

class TrainRecord(models.Model):
    # 分组id，模型id，upc列表，照片和xml的大字段，照片总数，模型类型，训练的模型路径，模型参数，训练状态，训练耗时，训练完成时间，准确度
    group_id = models.IntegerField()
    model_id = models.IntegerField()
    upcs = models.TextField()
    datas = models.TextField()
    pic_cnt = models.IntegerField()
    type = models.IntegerField(default=0)   # 0:yolov3,
    model_path = models.CharField(max_length=200)
    params = models.TextField()
    status = models.IntegerField()          # 0:排队中，10：正在训练，20：训练结束, 30：训练失败
    duration = models.IntegerField()        # 训练耗时，小时
    finish_time = models.DateTimeField()
    accuracy_rate = models.FloatField()
    create_time = models.DateTimeField('date created', auto_now_add=True)
    update_time = models.DateTimeField('date updated', auto_now=True)

