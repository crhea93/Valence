from django.db import models
from block.models import Block
from users.models import CustomUser, CAM
# Create your models here.


class Link(models.Model):
    starting_block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='starting_block_set')
    ending_block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='ending_block_set')
    line_style_choices = [('Solid', 'Solid'), ('Solid-Strong', 'Solid-Strong'), ('Solid-Weak', 'Solid-Weak'),
                          ('Dashed', 'Dashed'), ('Dashed-Strong', 'Dashed-Strong'), ('Dashed-Weak', 'Dashed-Weak')]
    line_style = models.CharField(max_length=100, choices=line_style_choices, blank=False, default='Solid-Weak')
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    num = models.IntegerField(default=0)
    arrow_choices = [('none', 'none'), ('uni', 'uni'), ('bi', 'bi')]
    arrow_type = models.CharField(max_length=100, choices=arrow_choices, blank=False, default='none')
    timestamp = models.TimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    CAM = models.ForeignKey(CAM, on_delete=models.CASCADE, default='')

    def __str__(self):
        return str(self.num)

    def update(self, form_info):
        if self._state.adding:
            # If instance doesn't exist!
            raise self.DoesNotExist
        for field, value in form_info.items():
            # Let's get updating
            setattr(self, field, value)
        # And finally save
        self.save(update_fields=list(form_info.keys()))
