from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings


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
