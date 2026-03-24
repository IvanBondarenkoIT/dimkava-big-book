"""Analytics permissions — HR and Admin only."""


def user_can_view_analytics(user):
    """True if user is HR or admin."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name='hr_manager').exists()
