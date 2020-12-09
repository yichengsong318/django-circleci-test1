from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class StoreAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        email = kwargs.get("email")
        store = kwargs.get("store")

        try:
            if email is None:
                user = user_model.objects.get(username=username, customer_of=None)
            else:
                user = user_model.objects.get(email=email, customer_of=store)

            if user.check_password(password):
                return user

        except user_model.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            user_model().set_password(password)

        return None
