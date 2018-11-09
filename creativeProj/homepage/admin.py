# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Items, Reviews, UserBalance, UserCart


#import models
admin.site.register(Items)
admin.site.register(Reviews)
admin.site.register(UserBalance)
admin.site.register(UserCart)