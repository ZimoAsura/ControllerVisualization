from django.db import models
import uuid

class controller_data(models.Model):
    ego_speed = models.FloatField()
    leader_speed = models.FloatField()
    space_gap = models.FloatField()
    accel = models.FloatField()
    file_id = models.UUIDField()

class controller_file(models.Model):
    file_id = models.UUIDField()
    file_name = models.CharField(max_length=100)
    upload_time = models.DateTimeField()