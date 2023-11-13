from ads.models import Message


def new_messages(request):
    """Show count of unread messages."""
    if request.user.is_authenticated:
        return {
            "new_messages": Message.objects.filter(
                recipient=request.user, checked=False
            ).count()
        }
    return {"new_messages": 0}
