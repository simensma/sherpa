from django.db import models

class Menu(models.Model):
    name = models.CharField(max_length=50)
    page = models.ForeignKey('page.Page', unique=True)
    order = models.IntegerField(unique=True)

class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.CharField(max_length=50, unique=True)
    published = models.BooleanField()
    pub_date = models.DateTimeField(null=True)

    def deep_delete(self):
        Menu.objects.filter(page=self).delete()
        for variant in PageVariant.objects.filter(page=self):
            variant.deep_delete()
        self.delete()

class PageVariant(models.Model):
    page = models.ForeignKey('page.Page')
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=50)
    segment = models.ForeignKey('analytics.Segment', null=True)
    priority = models.IntegerField()
    # probability
    # publisher = models.ForeignKey('users.Profile')
    # change_comment = models.TextField()
    # The active field can be set by the view in order to get a reference to
    # the active version in the template. Not sure if there exists a better
    # way to do this?
    active = None

    def deep_delete(self):
        # Note: We don't really need to cascade priorities
        for version in PageVersion.objects.filter(variant=self):
            version.deep_delete()
        self.delete()

class PageVersion(models.Model):
    variant = models.ForeignKey('page.PageVariant')
    version = models.IntegerField()
    active = models.BooleanField()

    def deep_delete(self):
        for block in Block.objects.filter(version=self):
            block.deep_delete()
        self.delete()

### CMS

class Block(models.Model):
    version = models.ForeignKey('page.PageVersion')
    template = models.CharField(max_length=50)
    order = models.IntegerField()
    columns = []

    def deep_delete(self):
        for content in HTMLContent.objects.filter(block=self):
            content.deep_delete()
        for widget in Widget.objects.filter(block=self):
            widget.deep_delete()
        self.delete()

class HTMLContent(models.Model):
    block = models.ForeignKey('page.Block')
    content = models.TextField()
    column = models.IntegerField() # 0-indexed (max 2)
    order = models.IntegerField() # 0-indexed

    def deep_delete(self):
        collapse_block_order(self.block, self.column, self.order)
        self.delete()

class Widget(models.Model):
    block = models.ForeignKey('page.Block')
    widget = models.TextField()
    column = models.IntegerField() # 0-indexed (max 2)
    order = models.IntegerField() # 0-indexed

    def deep_delete(self):
        collapse_block_order(self.block, self.column, self.order)
        self.delete()

def collapse_block_order(block, column, order):
    for widget in Widget.objects.filter(block=block, column=column, order__gt=order):
        widget.order = (widget.order-1)
        widget.save();
    for content in HTMLContent.objects.filter(block=block, column=column, order__gt=order):
        content.order = (content.order-1)
        content.save();
