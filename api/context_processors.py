# api/context_processors.py
from .models import ConnectionRequest

def pending_requests_count(request):
    if request.user.is_authenticated:
        count = ConnectionRequest.objects.filter(receiver=request.user, status="pending").count()
        return {"pending_count": count}
    return {"pending_count": 0}
