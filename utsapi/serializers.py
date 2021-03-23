from rest_framework import serializers
from django.conf import settings

from .models import File, Project, Profile
from django.contrib.auth.models import User

class FileSerializer(serializers.HyperlinkedModelSerializer):
    # media_url = serializers.SerializerMethodField('get_thumbnail_url')

    def get_thumbnail_url(self, obj):
        return '%s%s' % (settings.MEDIA_URL, obj.media)

    class Meta:
        model = File
        fields = ('id', 'name', 'extension', 'route', 'project', 'favorite', 'updated_at', 'download_date')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'updated_at')
        

class ProfileEditSerializer(serializers.HyperlinkedModelSerializer):
    # photo_url = serializers.SerializerMethodField('get_thumbnail_url')

    # def get_thumbnail_url(self, obj):
    #     return '%s%s' % (settings.MEDIA_URL, obj.photo)
    
    class Meta:
        model = Profile
        fields = "__all__"
        
        
class UserEditSerializer(serializers.HyperlinkedModelSerializer):
    profile = serializers.SerializerMethodField('get_profile')
    
    def get_profile(self, obj):
        profile = Profile.objects.get(user_id=obj.id).values()
        return profile
    
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {'read_only': True},
            'password': {'read_only': True},
        }

