from rest_framework import serializers

from .models import File, Project
from django.contrib.auth.models import User

class FileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = File
        fields = ('id', 'name', 'extension', 'route', 'project', 'favorite')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name')
