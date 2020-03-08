from django.contrib.postgres.indexes import BrinIndex, GinIndex
from django.utils.encoding import smart_text as smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import models
from django.db.models.query import QuerySet
from random import uniform

from apps.users.models import User


class SnippetQuerySet(QuerySet):

    def live(self):
        return self.filter(status=True)

    def get_target_hulk(self):
        return self.filter(title="Hulk287")


class SnippetManager(models.Manager):

    def get_query_set(self):
        return SnippetQuerySet(self.model)

    def __getattr__(self, attr, *args):
        if attr.startswith("_"):
            raise AttributeError
        return getattr(self.get_query_set(), attr, *args)

    def create_snippet(self, *args, **kwargs):
        snippet = Snippet()
        snippet.title = kwargs.get("title")
        snippet.owner_id = kwargs.get("owner_id")
        Snippet.objects.create(snippet)

    def update_snippet(self, *args, **kwargs):
        print(kwargs)
        pass
        # snippet = Snippet.objects.get(id=kwargs.get("id"))
        # snippet.title = kwargs.get("title")
        # snippet.save()


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

    objects = SnippetManager()

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
            self.title = self.title + str(int(uniform(1, 10000)))
            self.created = timezone.now()
        self.modified = timezone.now()
        super(Snippet, self).save(*args, **kwargs)
