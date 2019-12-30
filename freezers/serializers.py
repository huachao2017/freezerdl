from rest_framework import serializers
from freezers.models import FreezerImage
from django.conf import settings

class FreezerImageSerializer(serializers.ModelSerializer):
    visual_url = serializers.SerializerMethodField()
    class Meta:
        model = FreezerImage
        fields = ('pk', 'deviceid', 'ret', 'source','visual_url',
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
