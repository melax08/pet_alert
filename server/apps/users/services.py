from .models import User


class UserService:
    """Service to manage users."""

    @staticmethod
    def get_staff_telegram_ids() -> list[int]:
        """Get telegram ids of staff users who have them listed."""
        return User.objects.filter(is_staff=True, telegram_id__isnull=False).values_list(
            "telegram_id", flat=True
        )
