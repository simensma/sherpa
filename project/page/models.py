from django.db import models

class Menu(models.Model):
    name = models.CharField(max_length=50)
    page = models.ForeignKey('page.Page', unique=True)
    # Even though this should be unique, it's not enforced because
    # when swapping, two orders will temporarily clash.
    order = models.IntegerField()

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
    # publisher = models.ForeignKey('user.Profile')
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
        for row in Row.objects.filter(version=self):
            row.deep_delete()
        self.delete()

### CMS

class Row(models.Model):
    version = models.ForeignKey('page.PageVersion')
    order = models.IntegerField()
    columns = None

    def deep_delete(self):
        for column in Column.objects.filter(version=self):
            column.deep_delete()
        self.delete()

class Column(models.Model):
    row = models.ForeignKey('page.Row')
    span = models.IntegerField()
    order = models.IntegerField()
    contents = None

    def deep_delete(self):
        for content in Content.objects.filter(version=self):
            content.deep_delete()
        self.delete()

class Content(models.Model):
    column = models.ForeignKey('page.Column')
    content = models.TextField()
    type = models.CharField(max_length=1, choices=(('w', 'Widget'), ('h', 'HTML')))
    order = models.IntegerField()
    widget = None

    def deep_delete(self):
        for content in Content.objects.filter(column=self.column, order__get=order):
            content.order = (content.order-1)
            content.save();
        self.delete()
