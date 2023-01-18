from django.utils.timezone import datetime


def year(request):
    return {
        "year": datetime.today().year,
    }
