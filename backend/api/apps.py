from django.apps import AppConfig
from django.conf import settings


# class ApiConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "api"


class OmnixConfig(AppConfig):
    name = 'api'

    def ready(self):
        from django.contrib.auth.models import User
        for user_data in settings.PREDEFINED_USERS:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email']
                )
                user.set_password(user_data['password'])
                user.save()
