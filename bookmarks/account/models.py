from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
# Create your models here.


class Profile(models.Model):
    user: models.OneToOneField = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # 通过one-to-one将用户的Profile根用户联系起来。通过AUTH_USER_MODEL不直接访问user model，可以使app更加通用
    date_of_birth: models.DateField = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d', blank=True)

    def __str__(self):
        return f'Profile for user {self.user.username}'
