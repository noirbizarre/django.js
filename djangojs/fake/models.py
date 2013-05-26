# -*- coding: utf-8 -*-
from django import VERSION as DJANGO_VERSION
from django.db import models


class FakeModel(models.Model):
    something = models.CharField(max_length=256)

    class Meta:
        permissions = (
            ("do_something", "Can do something"),
            ("do_something_else", "Can do something else"),
        )


if DJANGO_VERSION >= (1, 5):
    from django.contrib.auth.models import AbstractBaseUser, UserManager

    class CustomUser(AbstractBaseUser):
        identifier = models.CharField(max_length=40, unique=True, db_index=True)
        USERNAME_FIELD = 'identifier'

        objects = UserManager()
