from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

NAME_MAX_LENGTH = 122
COMMAND_MAX_LENGTH = 255
DESCRIPTION_MAX_LENGTH = 500
EXAMPLE_MAX_LENGTH = 255
VERSION_MAX_LENGTH = 20

User = get_user_model()

# Validators
version_validator = RegexValidator(
    regex=r'^\d+(\.\d+)+(\([0-9]+\))?([A-Za-z])?$',
    message="Enter a valid version number (e.g., 15.2.3, 15.2(3)T)"
)


# Vendor Model
class Vendor(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        verbose_name=_t("Vendor Name")
    )
    date_created = models.DateTimeField(default=timezone.now, verbose_name=_t("Created At"))
    date_updated = models.DateTimeField(auto_now=True, verbose_name=_t("Updated At"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vendors_created",
        verbose_name="Created By"
    )

    def __str__(self) -> str:
        return self.name
#:


# OS Model
class OS(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        verbose_name=_t("OS"),
        null=False,
        blank=False
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="oses_created",
        verbose_name="Created By"
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='oses',
        verbose_name=_t("Vendor")
    )

    def __str__(self):
        return f"{self.name} ({self.vendor.name})"
#:


# Command Category Model
class Category(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        verbose_name=_t("Command Category"),
        null=False,
        blank=False
    )
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='subcategories',
        on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(default=timezone.now, verbose_name=_t("Created At"))
    date_updated = models.DateTimeField(auto_now=True, verbose_name=_t("Updated At"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="categories_created",
        verbose_name="Created By"
    )

    def __str__(self) -> str:
        def get_full_path(category):
            if category.parent:
                return f"{get_full_path(category.parent)}/{category.name}"
            return category.name
        return get_full_path(self)
    #:

    @property
    def has_subcategories(self):
        return self.subcategories.exists()
    #:

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
#:


# Command Model
class Commands(models.Model):
    command = models.CharField(
        max_length=COMMAND_MAX_LENGTH,
        unique=True,
        verbose_name=_t("Command"),
        null=False,
        blank=False
    )
    description = models.TextField(
        max_length=DESCRIPTION_MAX_LENGTH,
        verbose_name=_t("Description"),
        null=True,
        blank=True
    )
    example = models.TextField(
        max_length=EXAMPLE_MAX_LENGTH,
        verbose_name=_t("Example"),
        null=True,
        blank=True
    )
    version = models.CharField(
        max_length=VERSION_MAX_LENGTH,
        validators=[version_validator],
        verbose_name=_t("Version"),
        null=True,
        blank=True
    )
    date_created = models.DateTimeField(default=timezone.now, verbose_name=_t("Created At"))
    date_updated = models.DateTimeField(auto_now=True, verbose_name=_t("Updated At"))

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='commands',
        verbose_name=_t("Vendor"),
        null=False,
        blank=False
    )
    os = models.ForeignKey(
        OS,
        on_delete=models.SET_NULL,
        related_name="commands",
        verbose_name=_t("OS"),
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="commands",
        verbose_name=_t("Category"),
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="commands_created",
        verbose_name="Created By"
    )

    def __str__(self) -> str:
        return self.command[:50]

    def clean(self):
        # Ensure vendor consistency across category and OS
        if self.category and self.category.vendor != self.vendor:
            raise ValidationError("Category vendor must match the command vendor.")
        if self.os and self.os.vendor != self.vendor:
            raise ValidationError("OS vendor must match the command vendor.")

    class Meta:
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['command']),
        ]
#:
