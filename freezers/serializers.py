from rest_framework import serializers
from freezers.models import FreezerImage, OnlineModels, TrainRecord
from django.conf import settings

class FreezerImageSerializer(serializers.ModelSerializer):
    visual_url = serializers.SerializerMethodField()
    class Meta:
        model = FreezerImage
        fields = ('pk', 'group_id','device_id', 'ret', 'source','visual_url',
                  'create_time')
        read_only_fields = ('ret', 'visual','create_time')

    def get_visual_url(self, freezerImage):
        request = self.context.get('request')
        if freezerImage.visual:
            current_uri = '{scheme}://{host}{path}{visual}'.format(scheme=request.scheme,
                                                           host=request.get_host(),
                                                           path=settings.MEDIA_URL,
                                                           visual=freezerImage.visual)
            return current_uri

        else:
            return None

class OnlineModelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineModels
        fields = ('pk', 'group_id','device_id', 'upcs', 'type', 'model_path', 'params', 'status',
                  'create_time', 'update_time')
        read_only_fields = ('create_time', 'update_time')

class TrainRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainRecord
        fields = ('pk', 'group_id','device_id', 'upcs', 'datas','pic_cnt',
                  'type', 'model_path', 'params', 'status', 'duration', 'finish_time', 'accuracy_rate'
                  'create_time', 'update_time')
        read_only_fields = ('create_time', 'update_time')
