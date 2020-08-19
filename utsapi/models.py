from django.db import models

# Create your models here.
class File(models.Model):
    name = models.CharField(max_length=100, null=True)
    extension = models.CharField(max_length=10, null=True)
    route = models.CharField(max_length=150, null=True)
    # dir = models.CharField()

    def __str__(self):
        return self.name