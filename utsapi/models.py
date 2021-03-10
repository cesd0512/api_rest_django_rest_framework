import os
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth.models import User


fs = FileSystemStorage(location=settings.PRIVATE_DIR)


class Project(models.Model):
    name = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=200, null=True)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    consulted_date = models.DateTimeField(null=True)
    favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# def my_awesome_upload_function(instance, filename):
#     """ this function has to return the location to upload the file """
#     print('hello')

#     return os.path.join('/media/%s/' % instance.id, filename)


class File(models.Model):
    name = models.CharField(max_length=100, null=True)
    extension = models.CharField(max_length=10, null=True)
    route = models.CharField(max_length=150, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=False)
    favorite = models.BooleanField(default=False)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    download_date = models.DateTimeField(null=True)
    media = models.FileField(upload_to='files/%Y/%m/%d/', null=True, blank=True)
    # media = models.FileField(upload_to=my_awesome_upload_function, null=True, blank=True)


    def __str__(self):
        return self.name


class FileDownload(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    download_date = models.DateTimeField(null=True)



def get_upload_path(instance, filename):
    return os.path.join(
      "%s_" % instance.user.id, "user_%s" % instance.user.username, filename)
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profession = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    country = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    alternative_email = models.TextField(null=True, blank=True)
    photo = models.FileField(upload_to=get_upload_path, null=True, blank=True)