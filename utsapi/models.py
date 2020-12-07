from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=100, null=False)
    description = models.CharField(max_length=200, null=True)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # dir = models.CharField()

    def __str__(self):
        return self.name


class File(models.Model):
    name = models.CharField(max_length=100, null=True)
    extension = models.CharField(max_length=10, null=True)
    route = models.CharField(max_length=150, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=False)
    favorite = models.BooleanField(default=False)
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    media = models.FileField(upload_to='message/%Y/%m/%d/', null=True, blank=True)
    # dir = models.CharField()

    def __str__(self):
        return self.name
