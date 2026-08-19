from .models import CurtainCustomization

def cart_count(request):
    """Add cart count to template context"""
    count = 0
    if request.user.is_authenticated:
        count = CurtainCustomization.objects.filter(
            user=request.user, added_to_cart=True
        ).count()
    elif request.session.session_key:
        count = CurtainCustomization.objects.filter(
            session_id=request.session.session_key, added_to_cart=True
        ).count()
    
    return {'cart_count': count}