# -*- coding: utf-8 -*-
from django import forms


class TestForm(forms.Form):
    message = forms.CharField()
