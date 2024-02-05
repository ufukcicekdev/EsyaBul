from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class EmailNotification(models.Model):
    subject = models.CharField(max_length=255)
    body = CKEditor5Field(config_name='extends', null=True, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject}"