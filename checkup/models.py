import datetime

from django.db import models
from django.utils import timezone

from .validators import validate_url


class Rule(models.Model):
    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(
        choices=(
            ('common', 'Common'),
            ('server', 'Server'),
            ('advanced_seo', 'Advanced SEO'),
        ),
        max_length=200,
    )
    description = models.TextField(max_length=5000, null=True, blank=True)
    priority = models.CharField(
        choices=(
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low'),
        ),
        max_length=200,
        default='medium',
    )

    def __str__(self):
        return self.name

class Message(models.Model):
    name = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='rule_name')
    message = models.TextField(max_length=5000)
    status = models.NullBooleanField()
    def __str__(self):
        return self.message#[:75] + '...' if len(self.message) > 75 else self.message

