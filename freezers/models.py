from django.db import models
import datetime
from django.conf import settings

def image_upload_source(instance, filename):
    now = datetime.datetime.now()
    return '{}/{}/{}/{}/{}_{}_{}'.format(settings.DETECT_DIR_NAME, 'freezer', now.strftime('%Y%m'),
                                         now.strftime('%d%H'), now.strftime('%M%S'), str(now.time()), filename)


class FreezerImage(models.Model):
    deviceid = models.CharField(max_length=20, default='0', db_index=True)
    ret = models.TextField(default='')
    source = models.ImageField(max_length=200, upload_to=image_upload_source)
    visual = models.URLField(max_length=200, default='')
    create_time = models.DateTimeField('date created', auto_now_add=True, db_index=True)
