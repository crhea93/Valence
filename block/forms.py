from django import forms
from .models import Block


class BlockForm(forms.ModelForm):
    class Meta:
        model = Block
        fields = {
            'title',
            'shape',
            'num',
            'shape',
            'creator',
            'x_pos',
            'y_pos',
            'width',
            'height',
            'comment',
            'timestamp',
            'CAM'
        }

    def save(self, commit=True):
        block = super(forms.ModelForm, self).save(commit=False)
        block.title = self.cleaned_data["title"]
        block.shape = self.cleaned_data["shape"]
        block.x_pos = self.cleaned_data["x_pos"]
        block.y_pos = self.cleaned_data["y_pos"]
        block.width = self.cleaned_data["width"]
        block.height = self.cleaned_data["height"]
        block.comment = self.cleaned_data["comment"]
        block.timestamp = self.cleaned_data['timestamp']
        block.CAM = self.cleaned_data['CAM']
        if commit:
            block.save()
        return block
