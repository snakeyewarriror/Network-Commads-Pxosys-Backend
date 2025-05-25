from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _t
import re

class AtLeastOneUppercaseValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _t("The password must contain at least one uppercase letter."),
                code='password_no_upper',
            )

    def get_help_text(self):
        return _t("Your password must contain at least one uppercase letter.")


class AtLeastOneLowercaseValidator:
    def validate(self, password, user=None):
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _t("The password must contain at least one lowercase letter."),
                code='password_no_lower',
            )

    def get_help_text(self):
        return _t("Your password must contain at least one lowercase letter.")


class AtLeastOneDigitValidator:
    def validate(self, password, user=None):
        if not re.search(r'\d', password):
            raise ValidationError(
                _t("The password must contain at least one digit."),
                code='password_no_digit',
            )

    def get_help_text(self):
        return _t("Your password must contain at least one digit.")
