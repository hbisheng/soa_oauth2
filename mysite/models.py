from django.db import models

class User(models.Model):
    uid           = models.CharField(max_length=100)
    #screen_name   = models.CharField(max_length=100)
    access_token  = models.CharField(max_length=100)
    #description   = models.TextField()

# Create your models here.
