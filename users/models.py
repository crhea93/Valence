# users/models.py
from django_mysql.models import ListCharField
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
from django.utils import timezone


class CustomUser(AbstractUser):
    email = models.EmailField(
        _("email address"), blank=True, null=True
    )  # , unique=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True, null=True)
    language_preference = models.CharField(
        _("lang_pref"),
        max_length=10,
        choices=[("en", "en"), ("de", "de")],
        blank=False,
        null=False,
        default="en",
    )
    is_researcher = models.BooleanField(default=False)
    is_participant = models.BooleanField(default=False)
    active_cam_num = models.IntegerField(blank=True, null=True, default=1)
    active_project_num = models.IntegerField(blank=True, null=True, default=1)
    avatar = models.ImageField(upload_to="avatar/", blank=True, null=True, default="")
    random_user = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Researcher(models.Model):
    """
    Researcher Profile which points towards our custom user
    """

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    affiliation = models.CharField(
        _("affiliation"), max_length=100, blank=True, null=True, default=""
    )

    def __str__(self):
        return self.user.username


class Project(models.Model):
    name = models.CharField(max_length=50, default="", unique=True)
    researcher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default="")
    description = models.CharField(max_length=1000, default="")
    num_part = models.IntegerField(default=1, blank=True, null=True)
    name_participants = models.CharField(
        max_length=10, blank=True, null=True, default="", unique=True
    )
    Initial_CAM = models.FileField(
        upload_to="InitialCAMs/", default=""
    )  # models.CharField(max_length=50, default='', unique=False)
    password = models.CharField(
        max_length=20, default="", unique=False, blank=True, null=True
    )

    def __str__(self):
        return f"Name: {self.name}"

    def update(self, form_info):
        if self._state.adding:
            raise self.DoesNotExist
        for field, value in form_info.items():
            # Let's get updating
            setattr(self, field, value)
        # And finally save
        self.save(update_fields=list(form_info.keys()))


class CAM(models.Model):
    name = models.CharField(max_length=50, default="")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default="")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, blank=True, null=True, default=""
    )
    cam_image = models.FileField(default="")
    creation_date = models.CharField(
        _("Date"), max_length=100, default=datetime.datetime.now
    )  # Create time log for creation of CAM
    description = models.CharField(max_length=500, blank=True, default=" ", null=True)

    def __str__(self):
        return f"Name: {self.name}"

    def update(self, form_info):
        """Update the model.

        Parameters
        ----------
        form_info : dict
            The dictionary of updated values.
        """

        if self._state.adding:
            raise self.DoesNotExist
        for field, value in form_info.items():
            # Let's get updating
            setattr(self, field, value)
        # And finally save
        self.save(update_fields=list(form_info.keys()))


class Participant(models.Model):
    """
    Admin Profile which points towards our custom user
    """

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    researcher = models.ForeignKey(
        Researcher, on_delete=models.CASCADE, blank=True, null=True, default=""
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, blank=True, null=True, default=""
    )

    def __str__(self):
        return self.user.username


"""
# To safe profile on every create/updates
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
"""


class Contact(models.Model):
    contacter = models.CharField(max_length=256)
    email = models.CharField(max_length=256)
    message = models.CharField(max_length=1000)

    def __str__(self):
        return f"Contacter: {self.contacter}"


class logCamActions(models.Model):
    camId = models.ForeignKey(
        CAM, on_delete=models.CASCADE, default="", blank=False
    )  # Which CAM the action took place
    actionId = models.IntegerField(
        blank=False
    )  # Counter to organize the order of actions
    actionType = models.IntegerField(blank=False)  # is the action a deletion? ( = 0 )
    objType = models.IntegerField(
        blank=False
    )  # Is the object a link ( = 0 ) and a block ( = 1 )
    objDetails = models.CharField(
        max_length=500, blank=False
    )  # Details of the object in a python dictionary
