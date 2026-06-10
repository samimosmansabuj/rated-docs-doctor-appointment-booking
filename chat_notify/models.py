from django.db import models
from core.common_models import TimeStampedModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from core.constants import NOTIFICATION_FOR, LogStatus
from account.models import User


class Notification(TimeStampedModel):
    notification_for = models.CharField(max_length=15, choices=NOTIFICATION_FOR.choices, default=NOTIFICATION_FOR.ADMIN)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications", blank=True, null=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_notifications")
    action = models.CharField(max_length=255)
    message = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)

    entity_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, blank=True, null=True)
    entity_id = models.PositiveIntegerField(blank=True, null=True)
    service = GenericForeignKey('entity_type', 'entity_id')

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def notify_text(self):
        return f"{self.receiver.first_name} {self.receiver.last_name if self.receiver.last_name else ''} {self.action} at {self.created_at}"

    def __str__(self):
        return f"{self.receiver.first_name} {self.receiver.last_name if self.receiver.last_name else ''} {self.action} at {self.created_at}"

# Logs Model==============================================
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    message = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=LogStatus.choices, default=LogStatus.SUCCESS)
    
    entity_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, blank=True, null=True)
    entity_id = models.PositiveBigIntegerField(blank=True, null=True)
    service = GenericForeignKey('entity_type', 'entity_id')
    
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    need_notify = models.BooleanField(default=False)

    def __str__(self):
        # return f"{self.user.username} {self.action} "
        username = self.user.username if self.user else None
        return f"{self.created_at} - {username} - {self.action} | {self.status}"



