from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class KnowledgeBaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.knowledge_base'
    verbose_name = _('Knowledge Base')
