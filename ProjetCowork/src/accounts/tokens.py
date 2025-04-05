from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from django.utils import six  # si erreur, on corrigera avec Python 3

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)

account_activation_token = AccountActivationTokenGenerator()