from random import uniform

from django.db import models
from django.contrib.postgres.indexes import BrinIndex, GinIndex
from apps.users.models import User
from django.utils.encoding import smart_text as smart_unicode
from django.utils.translation import ugettext_lazy as _

from django.utils import timezone


class Snippet(models.Model):
    LANGUAGE_CHOICES = (
        ('python', 'Python'),
        ('c#', 'C#'),
        ('java', 'Java'),
    )

    title = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='snippet_owner')
    code = models.TextField(blank=True, null=True)
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    created = models.DateTimeField(editable=False)
    modified = models.DateTimeField()
    status = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            BrinIndex(fields=['id']),
            GinIndex(fields=['title']),
        ]
        db_table = 'snippets'
        app_label = 'snippets'
        verbose_name = _("Snippet")
        verbose_name_plural = _("Snippets")

    def __str__(self):
        return self.title

    def __unicode__(self):
        return smart_unicode(self.title)

    def save(self, *args, **kwargs):
        if self.pk is None:
            # self.title = self.title + str(int(uniform(1, 10000)))
            self.created = timezone.now()
        self.modified = timezone.now()
        super().save(*args, **kwargs)

    def get_snippet_detail(self):
        return self.title + ' belongs to ' + self.language + '.'
