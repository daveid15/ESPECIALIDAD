from .models import Profile

def user_profile(request):
    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            return {'user_profile': profile}
        except Profile.DoesNotExist:
            return {}
    return {}

