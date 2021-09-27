from django.db import models
from users.models import CustomUser, CAM
# Create your models here.


class Block(models.Model):
    title = models.CharField(max_length=100, blank=True, default='')
    x_pos = models.FloatField(default=0.0, blank=False)
    y_pos = models.FloatField(default=0.0, blank=False)
    width = models.FloatField(default=160, blank=False)
    height = models.FloatField(default=120, blank=False)
    shape_choices = [('neutral', 'rectangle'), ('positive', 'rounded-circle'), ('negative', 'hexagon'),
                     ('positive strong', 'rounded-circle-strong'), ('negative strong', 'hexagon strong'),
                     ('ambivalent', 'hexagon rounded-circle'),
                     ('negative weak', 'hexagon weak'), ('positive weak', 'rounded-circle-weak')]
    shape = models.CharField(max_length=100, choices=shape_choices, blank=False)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    num = models.FloatField(default=0, blank=True)
    comment = models.CharField(max_length=300, blank=True, default=' ', null=True)
    timestamp = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    modifiable = models.BooleanField(null=True, blank=True, default=True)
    text_scale = models.FloatField(default=12, blank=True)
    CAM = models.ForeignKey(CAM, on_delete=models.CASCADE, default='')

    def __str__(self):
        return self.title

    def update(self, form_info):
        if self._state.adding:
            # If instance doesn't exist!
            raise self.DoesNotExist
        for field, value in form_info.items():
            # Let's get updating
            setattr(self, field, value)
        # And finally save
        self.save(update_fields=list(form_info.keys()))

