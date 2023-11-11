import datetime as dt


def year(request):
    """Add template context variable with current year."""
    return {
        'year': dt.datetime.now().year
    }
