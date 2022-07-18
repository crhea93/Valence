from django import forms
from .models import Link


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = {
            'starting_block',
            'ending_block',
            'line_style',
            'arrow_type',
            'creator',
            #'timestamp',
            'CAM'
        }

    def save(self, commit=True):
        link = super(forms.ModelForm, self).save(commit=False)
        link.starting_block = self.cleaned_data["starting_block"]
        print(self.cleaned_data)
        link.ending_block = self.cleaned_data["ending_block"]
        link.lin_color = self.cleaned_data["line_style"]
        link.creator = self.cleaned_data["creator"]
        link.arrow_type = self.cleaned_data['arrow_type']
        #link.timestamp = self.cleaned_data['timestamp']
        link.CAM = self.cleaned_data['CAM']
        if commit:
            link.save()
        return link
