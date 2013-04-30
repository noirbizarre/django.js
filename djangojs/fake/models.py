# -*- coding: utf-8 -*-
from django.db import models


class FakeModel(models.Model):
    something = models.CharField(max_length=256)

    class Meta:
        permissions = (
            ("do_something", "Can do something"),
            ("do_something_else", "Can do something else"),
        )
