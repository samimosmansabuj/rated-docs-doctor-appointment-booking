from django.db import models
from core.common_models import TimeStampedModel

# Create your models here.
class Notification(TimeStampedModel):
    user = models.ForeignKey("account.User", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)


