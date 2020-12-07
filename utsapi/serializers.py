from rest_framework import serializers
from django.conf import settings

from .models import File, Project
from django.contrib.auth.models import User

class FileSerializer(serializers.HyperlinkedModelSerializer):
    media_url = serializers.SerializerMethodField('get_thumbnail_url')

    def get_thumbnail_url(self, obj):
        return '%s%s' % (settings.MEDIA_URL, obj.media)

    class Meta:
        model = File
        fields = ('id', 'name', 'extension', 'route', 'project', 'favorite', 'updated_at', 'media_url')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'updated_at')
