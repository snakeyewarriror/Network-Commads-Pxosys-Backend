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


# Platform Model
class Platform(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        verbose_name=_t("Platform"),
        null=False,
        blank=False
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="platforms_created",
        verbose_name="Created By"
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name='platforms',
        verbose_name=_t("Vendor")
    )

    def __str__(self):
        return f"{self.name}"
#:


# Command Tag Model
class Tag(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name=_t("Command Tag"),
        null=False,
        blank=False
    )
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='subtags',
        on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(default=timezone.now, verbose_name=_t("Created At"))
    date_updated = models.DateTimeField(auto_now=True, verbose_name=_t("Updated At"))
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tags_created",
        verbose_name="Created By"
    )

    def __str__(self) -> str:
        def get_full_path(tag):
            if tag.parent:
                return f"{get_full_path(tag.parent)}/{tag.name}"
            return tag.name
        return get_full_path(self)
    #:

    @property
    def subtags(self):
        return self.subtags.exists()
    #:

    class Meta:
        verbose_name_plural = "Tags"
        ordering = ['name']
        unique_together = ('name', 'vendor', 'parent')
#:

    
# Command Model
class Commands(models.Model):
    

    # --- METHOD FIELD OPTIONS ---
    METHOD_CHOICES = [
        ('BULK', 'Bulk'),
        ('SINGULAR', 'Singular'),
    ]
    
    
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
    platform = models.ForeignKey(
        Platform,
        on_delete=models.SET_NULL,
        related_name="commands",
        verbose_name=_t("Platform"),
        null=True,
        blank=True
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="commands",
        verbose_name=_t("Tag"),
        null=True,
        blank=True
    )
    
    sub_command = models.CharField(
        max_length=COMMAND_MAX_LENGTH,
        verbose_name=_t("Sub Command"),
        null=True,
        blank=True
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="commands_created",
        verbose_name="Created By"
    )
    
    method = models.CharField(
        max_length=12,
        choices=METHOD_CHOICES,
        default='SINGULAR', # Set a default
        verbose_name=_t("Creation Method"),
        null=False,
        blank=False
    )

    def __str__(self) -> str:
        return self.command[:50]

    def clean(self):
        # Ensure vendor consistency across tag and platform
        if self.tag and self.tag.vendor != self.vendor:
            raise ValidationError("Tag vendor must match the command vendor.")
        if self.platform and self.platform.vendor != self.vendor:
            raise ValidationError("Platform vendor must match the command vendor.")

    class Meta:
        ordering = ['-date_created']
        indexes = [
            models.Index(fields=['command']),
        ]
#:


# Parameter Model
class CommandParameter(models.Model):
    command = models.ForeignKey(Commands, on_delete=models.CASCADE, related_name="parameters")
    value = models.CharField(max_length=COMMAND_MAX_LENGTH)
#:
