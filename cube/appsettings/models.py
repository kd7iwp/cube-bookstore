from django.db import models

class AppSetting(models.Model):
    name = models.CharField(max_length=200)
    value = models.TextField()
    description = models.TextField()

    def __unicode__(self):
        return self.name
