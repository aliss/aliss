import uuid

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    @property
    def is_root(self):
        return not self.parent

    @property
    def siblings(self):
        return Category.objects.filter(parent=self.parent)

    @property
    def subcategories(self):
        return Category.objects.filter(parent=self)

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        for s in self.services.all():
            s.add_to_index()

    def delete(self, *args, **kwargs):
        services = list(self.services.all())
        super(Category, self).delete(*args, **kwargs)
        for s in services:
            s.add_to_index()