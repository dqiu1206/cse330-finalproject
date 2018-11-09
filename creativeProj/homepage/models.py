# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.

# table for items
class Items(models.Model):

	CATEGORY_CHOICES = (
		('Fashion', 'Fashion'),
		('Furniture', 'Furniture'),
		('Books', 'Books'),
		('Electronics', 'Electronics'),
		('Beauty', 'Beauty'),
		('Hygiene', 'Hygiene'),
		('Sports', 'Sports'),
		('Food', 'Food'),
		('Health', 'Health'),
		('Other', 'Other'))

	name = models.CharField(max_length=50, blank=False)
	seller = models.ForeignKey(User, on_delete=models.CASCADE)
	price = models.DecimalField(max_digits=7, decimal_places=2, blank=False)
	description = models.CharField(max_length=300, blank=False)
	image = models.FileField(blank=False)
	sold = models.BooleanField(default=False)
	owner = models.CharField(max_length=50, default="")
	category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default='Other')
	tags = models.CharField(max_length=100, blank=True)

	def get_absolute_url(self):
		return reverse('homepage:detail', kwargs={'item_id':self.pk})

# table for reviews
class Reviews(models.Model):
	item = models.ForeignKey(Items, on_delete=models.CASCADE)
	user = models.ForeignKey(User)
	review = models.CharField(max_length=200,null=False)

	def get_absolute_url(self):
		return reverse('homepage:detail', kwargs={'item_id':self.item.pk})

# table for user balances
class UserBalance(models.Model):
	username = models.ForeignKey(User, on_delete=models.CASCADE)
	balance = models.DecimalField(max_digits=7, decimal_places=2, default=100.00)
	
	class Meta:
		unique_together = ["username", "balance"]

# table for items in user's cart
class UserCart(models.Model):
	username = models.ForeignKey(User, on_delete=models.CASCADE)
	item = models.ForeignKey(Items, on_delete=models.CASCADE)

	class Meta:
		unique_together = ["username", "item"]

