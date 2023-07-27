from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailConfirmationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.userprofile.email_verified)
