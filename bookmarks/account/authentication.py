from django.contrib.auth.models import User

class EmailAuthBackend:
    """
    通过email来登录
    """

    def authenticate(self, request, username=None, password=None):
        try:
            user:User = User.objects.get(email=username)
            if user.check_password(password):
                return user
            return None

        except User.DoesNotExist:
            return None


    def get_user(self, user_id:str):

        try: 
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None