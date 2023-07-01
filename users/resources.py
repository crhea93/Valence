from import_export import resources
from .models import CustomUser
from block.models import Block
from link.models import Link

class CustomUserResource(resources.ModelResource):
    class Meta:
        model = CustomUser

class BlockResource(resources.ModelResource):
    class Meta:
        model = Block
        # exclude = ('id', )


class LinkResource(resources.ModelResource):
    class Meta:
        model = Link
        # exclude = ('id', )
