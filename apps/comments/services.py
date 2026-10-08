"""Comment create / list helpers."""
from django.contrib.contenttypes.models import ContentType

from .models import Comment


def get_comments_for_object(obj, *, viewer=None):
    """
    Approved comments for everyone; viewer also sees own pending.
    """
    ct = ContentType.objects.get_for_model(obj.__class__)
    qs = (
        Comment.objects.filter(content_type=ct, object_id=obj.pk)
        .select_related('user', 'user__profile')
        .order_by('created_at')
    )
    if viewer and viewer.is_authenticated:
        from django.db.models import Q

        return qs.filter(
            Q(status=Comment.Status.APPROVED)
            | Q(user=viewer, status=Comment.Status.PENDING)
        )
    return qs.filter(status=Comment.Status.APPROVED)


def submit_comment(*, user, obj, text: str) -> Comment:
    text = (text or '').strip()
    if not text:
        raise ValueError('empty')
    ct = ContentType.objects.get_for_model(obj.__class__)
    return Comment.objects.create(
        user=user,
        content_type=ct,
        object_id=obj.pk,
        text=text,
        status=Comment.Status.PENDING,
    )


def resolve_comment_target(app_label: str, model: str, object_id: int):
    """Resolve Course / Article / NewsPost by app_label.model + pk."""
    allowed = {
        ('courses', 'course'),
        ('knowledge_base', 'article'),
        ('news', 'newspost'),
    }
    key = (app_label, model)
    if key not in allowed:
        return None
    try:
        ct = ContentType.objects.get(app_label=app_label, model=model)
    except ContentType.DoesNotExist:
        return None
    return ct.get_object_for_this_type(pk=object_id)


def comments_context_for(obj, viewer) -> dict:
    """Template context for comments/_thread.html."""
    rows = []
    for c in get_comments_for_object(obj, viewer=viewer):
        profile = getattr(c.user, 'profile', None)
        rows.append({
            'text': c.text,
            'created_at': c.created_at,
            'is_pending': c.status == Comment.Status.PENDING,
            'display_name': (
                profile.get_public_username()
                if profile
                else (c.user.get_full_name() or c.user.get_username())
            ),
        })
    return {
        'comments': rows,
        'comment_app_label': obj._meta.app_label,
        'comment_model': obj._meta.model_name,
        'comment_object_id': obj.pk,
    }
