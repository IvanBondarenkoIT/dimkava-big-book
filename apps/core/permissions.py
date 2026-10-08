"""Portal permission helpers."""


def user_can_edit_content(user) -> bool:
    """HR managers and superusers may create/edit content in the portal."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name='hr_manager').exists()
