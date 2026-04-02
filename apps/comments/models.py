from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Comment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    text = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_comments',
    )

    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at'], name='comments_co_status_08b9ef_idx'),
            models.Index(fields=['content_type', 'object_id', 'status'], name='comments_co_content_1832ed_idx'),
        ]

    def __str__(self):
        return f'Comment({self.status}) by {self.user_id} on {self.content_type_id}:{self.object_id}'

    def approve(self, *, by_user) -> None:
        if self.status != self.Status.PENDING:
            return
        self.status = self.Status.APPROVED
        self.moderated_at = timezone.now()
        self.moderated_by = by_user
        self.save(update_fields=['status', 'moderated_at', 'moderated_by'])

    def reject(self, *, by_user) -> None:
        if self.status != self.Status.PENDING:
            return
        self.status = self.Status.REJECTED
        self.moderated_at = timezone.now()
        self.moderated_by = by_user
        self.save(update_fields=['status', 'moderated_at', 'moderated_by'])

