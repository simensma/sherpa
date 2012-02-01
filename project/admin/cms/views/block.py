from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db.models import Max
from project.page.models import PageVersion, Block, HTMLContent, Widget

def add(request, version, template):
    version = PageVersion.objects.get(id=version)
    blocks = Block.objects.filter(version=version)
    if(len(blocks) == 0):
        max = 0
    else:
        max = blocks.aggregate(Max('order'))['order__max']
    block = Block(version=version, template=template, order=(max+1))
    block.save()
    return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[version.id]))

def move_up(request, block):
    block = Block.objects.get(id=block)
    if(block.order == 1):
        # error handling
        raise Exception
    else:
        swap_blocks(block, -1)
        return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[block.version.id]))

def move_down(request, block):
    block = Block.objects.get(id=block)
    max = Block.objects.filter(version=block.version).aggregate(Max('order'))['order__max']
    if(block.order == max):
        # error handling
        raise Exception
    else:
        swap_blocks(block, 1)
        return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[block.version.id]))

def delete(request, block):
    block = Block.objects.get(id=block)
    block.deep_delete()
    return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[block.version.id]))


def swap_blocks(block, increment):
    other_block = Block.objects.get(version=block.version, order=(block.order + increment))
    other_block.order = block.order
    block.order = other_block.order + increment
    other_block.save()
    block.save()
