from random import uniform

from django.db import models
from django.contrib.postgres.indexes import BrinIndex
from apps.users.models import User


class Snippet(models.Model):
    LANGUAGE_CHOICES = (
        ('python', 'Python'),
        ('c#', 'C#'),
        ('java', 'Java'),
    )

    title = models.CharField(max_length=100, blank=True, default='', unique=True)
    code = models.TextField()
    linenos = models.BooleanField(default=False)
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)
    status = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='snippets')

    class Meta:
        ordering = ['created']
        indexes = [
            BrinIndex(fields=['id']),
        ]
        db_table = 'snippets'
        app_label = 'snippets'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.title = self.title + str(int(uniform(1, 10000)))
        super().save(*args, **kwargs)
