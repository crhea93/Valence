# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import (
    CustomUser,
    Contact,
    Participant,
    Researcher,
    CAM,
    Project,
    logCamActions,
)


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = {
            "contacter",
            "email",
            "message",
        }


class CustomUserCreationForm(UserCreationForm):
    # captcha = ReCaptchaField()

    class Meta(UserCreationForm):
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "language_preference",
        )

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.language_preference = self.cleaned_data["language_preference"]
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ()  # ('username', 'email')


class ParticipantSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "language_preference",
        )

    def save(self):
        user = super().save(commit=False)
        user.is_participant = True
        user.save()
        participant = Participant.objects.create(user=user)
        return user


class ResearcherSignupForm(UserCreationForm):
    # captcha = ReCaptchaField()
    affiliation = forms.CharField(max_length=200, required=False, label="Affiliation")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            "language_preference",
        )

    def save(self):
        user = super().save(commit=False)
        user.is_researcher = True
        user.save()
        researcher = Researcher.objects.create(user=user)
        researcher.affiliation = self.cleaned_data.get("affiliation", "")
        researcher.save()
        return user


class IndividualCAMCreationForm(forms.ModelForm):
    class Meta:
        model = CAM
        fields = {
            "name",
            "user",
        }

    def save(self, commit=True):
        cam = super(forms.ModelForm, self).save(commit=False)
        cam.name = self.cleaned_data["name"]
        cam.user = self.cleaned_data["user"]
        if commit:
            cam.save()
        return cam


class ProjectCreationForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = {
            "name",
            "researcher",
            "num_part",
            "description",
            "name_participants",
            "password",
        }
        error_messages = {
            "name": {
                "unique": "That Project Title has been taken.",
                "required": "A Project Title must be entered",
            },
            "name_participants": {
                "unique": "The Participant Prefix you have chosen has been taken.",
                "required": "A Participant Prefix must be entered",
            },
            "num_part": {"required": "A Number of Participants must be entered"},
            "description": {"required": "A Project Description must be entered"},
        }

    def save(self, commit=True):
        project = super(forms.ModelForm, self).save(commit=False)
        project.name = self.cleaned_data["name"]
        project.researcher = self.cleaned_data["researcher"]
        project.num_part = self.cleaned_data["num_part"]
        project.description = self.cleaned_data["description"]
        project.name_participants = self.cleaned_data["name_participants"]
        project.password = self.cleaned_data["password"]
        if commit:
            project.save()
        return project


class ProjectCAMCreationForm(forms.ModelForm):
    class Meta:
        model = CAM
        fields = {"name", "user", "project", "description"}

    def save(self, commit=True):
        cam = super(forms.ModelForm, self).save(commit=False)
        cam.name = self.cleaned_data["name"]
        cam.user = self.cleaned_data["user"]
        cam.project = self.cleaned_data["project"]
        cam.description = self.cleaned_data["description"]
        if commit:
            cam.save()
        return cam


class LogCamActionForm(forms.ModelForm):
    class Meta:
        model = logCamActions
        fields = {"camId", "actionId", "actionType", "objType", "objDetails"}
