# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from .models import Items, Reviews, UserBalance, UserCart
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.views.generic import View
from .forms import UserForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
import re
from decimal import Decimal


# VIEWS below:

#takes user to form to add money
def addMoneyForm(request):
	if request.user.is_authenticated():
		user = UserBalance.objects.get(username__username=request.user.username)
		balance = user.balance
		context = {'balance': balance}

	return render(request, 'homepage/addmoney.html', context)

#adds money to user's balance
def addMoney(request):
	amount = request.POST['add-money']
	if request.user.is_authenticated():
		user = UserBalance.objects.get(username__username=request.user.username)		
		user.balance += Decimal(amount)
		user.save()
		balance = user.balance

	context = {'balance': balance}

	return render(request, 'homepage/addmoney.html', context)

#pass single item info to display in detail.html
def detail(request, item_id):
	item = get_object_or_404(Items, pk=item_id)

	# get the user's balance
	if request.user.is_authenticated():
		user = UserBalance.objects.get(username__username=request.user.username)
		balance = user.balance
	else: 
		balance = 0

	context = {
		'item': item,
		'balance': balance
	}

	return render(request, 'homepage/detail.html', context)

def category(request):
	#get list of items in that specific category
	selected_category = request.POST['select_category']
	item_list = Items.objects.filter(category=selected_category,sold=False)

	# get the user's balance
	if request.user.is_authenticated():
		user = UserBalance.objects.get(username__username=request.user.username)
		balance = user.balance
	else: 
		balance = 0

	# send data to template
	context = {
		'item_list': item_list,
		'balance': balance,
		'category': selected_category
	}

	return render(request, 'homepage/index.html', context)

# filter items by price
def filterPrice(request):
	maxPrice = request.POST['max-price']
	item_list = Items.objects.filter(price__lte=Decimal(maxPrice), sold=False)

	if request.user.is_authenticated():
		user = UserBalance.objects.get(username__username=request.user.username)
		balance = user.balance
	else: 
		balance = 0

	context = {'item_list': item_list, 'balance': balance}
	return render(request, 'homepage/index.html', context)

# search for items
def searchItems(request):
	#get user's query, separate the words and search for them in Items table		
	query = request.GET['q']
	wordList = re.compile('([^,\s]+)').findall(query)
	item_list = []
	for word in wordList:
		tag_result = Items.objects.filter(tags__contains=word, sold=False)
		description_result = Items.objects.filter(description__contains=word, sold=False)
		name_result = Items.objects.filter(name__contains=word, sold=False)
		item_list += tag_result 
		item_list += name_result 
		item_list += description_result

	# get rid of duplicate items
	item_list = set(item_list)

	# get the user's balance
	if request.user.is_authenticated():
		user = UserBalance.objects.get(username__username=request.user.username)
		balance = user.balance
	else: 
		balance = 0


	context = {'item_list': item_list, 'balance': balance}
	return render(request, 'homepage/index.html', context)

#pass all items to display in index.html
def ItemListView(request):

	balance = 0
	item_list = Items.objects.filter(sold=False)

	#get the user's balance
	if request.user.is_authenticated():
		user = UserBalance.objects.get(username__username=request.user.username)
		balance = user.balance

	context = {'item_list': item_list, 'balance': balance}
	return render(request,'homepage/index.html', context)

# get list of items in the user's cart, and send info to cart.html
def cart(request):
	item_list = None
	balance = 0

	# get the items in the cart and the user's balance
	if request.user.is_authenticated():
		item_list = UserCart.objects.filter(username__username=request.user.username)
		user = UserBalance.objects.get(username__username=request.user.username)
		balance = user.balance

	context = {'item_list': item_list, 'balance': balance}
	return render(request,'homepage/cart.html', context)

# add an item to user's cart if it isn't already there
def addCart(request, item_id):
	item = get_object_or_404(Items, pk=item_id)
	newCartItem = UserCart.objects.get_or_create(username=request.user, item=item)
	return redirect('homepage:cart')

# allows users to checkout items from their cart
def checkoutItems(request):
	cartItems = UserCart.objects.filter(username=request.user)
	sum = 0

	#find total sum of cart items
	for item in cartItems:
		sum = sum + item.item.price

	user = UserBalance.objects.get(username=request.user)

	#if user doesn't have enough money, don't checkout
	if user.balance < sum:
		context = {'notEnoughMoney': True, 'balance': user.balance, 'item_list': cartItems}
		return render(request, 'homepage/cart.html', context)

	# checkout
	else:
		for item in cartItems:
			
			# set item as sold and set item owner as current user
			var = Items.objects.get(id=item.item.id)
			var.sold = True
			var.owner = request.user.username
			var.save()

			#update account balance of seller
			seller = UserBalance.objects.get(username=item.item.seller)
			seller.balance = seller.balance + item.item.price
			seller.save()

		#remove the items in the cart
		cartItems.delete()

		#update the buying user's balance
		user = UserBalance.objects.get(username=request.user)
		user.balance = user.balance - sum
		user.save()

		return redirect('homepage:profile')

# this view sends the list of items owned by the current user
def profile(request):
	ownedItems = Items.objects.filter(owner=request.user.username)
	balance = UserBalance.objects.get(username=request.user).balance
	context = {'item_list': ownedItems, 'balance': balance}
	return render(request, 'homepage/profile.html', context)

# add a review to an item
class addReview(CreateView):
	model = Reviews
	fields = ['review']

	#Source: https://stackoverflow.com/questions/22238663/pass-current-user-to-initial-for-createview-in-django
	#Sets 'seller' field to the currently logged in user
	def form_valid(self, form):
		form.instance.item = Items.objects.get(id=self.kwargs['item_id'])
		form.instance.user = self.request.user
		return super(addReview, self).form_valid(form)

	#source: https://stackoverflow.com/questions/14817326/class-based-generic-views-extra-context
	# this function allows us to send additional context; in this case the user balance
	def get_context_data(self, *args, **kwargs):
		context = super(addReview, self).get_context_data(*args, **kwargs)
		context['balance'] = UserBalance.objects.get(username=self.request.user).balance
		return context

#creates form for adding an item
class addItem(CreateView):
	model = Items
	fields = ['name', 'price','description', 'image', 'category', 'tags']

	#Source: https://stackoverflow.com/questions/22238663/pass-current-user-to-initial-for-createview-in-django
	#Sets 'seller' field to the currently logged in user
	def form_valid(self, form):
		form.instance.seller = self.request.user
		form.instance.sold = False
		return super(addItem, self).form_valid(form)

	#source: https://stackoverflow.com/questions/14817326/class-based-generic-views-extra-context
	# this function allows us to send additional context; in this case the user balance
	def get_context_data(self, *args, **kwargs):
		context = super(addItem, self).get_context_data(*args, **kwargs)
		context['balance'] = UserBalance.objects.get(username=self.request.user).balance
		return context

#creates form for editing an item; fields are autofilled
class editItem(UpdateView):
	model = Items
	fields = ['name', 'price','description', 'image', 'category', 'tags']

	# pass data that user doesn't have to fill
	def form_valid(self, form):
		form.instance.seller = self.request.user
		form.instance.sold = False
		return super(editItem, self).form_valid(form)

	#source: https://stackoverflow.com/questions/14817326/class-based-generic-views-extra-context
	# this function allows us to send additional context; in this case the user balance
	def get_context_data(self, *args, **kwargs):
		context = super(editItem, self).get_context_data(*args, **kwargs)
		context['balance'] = UserBalance.objects.get(username=self.request.user).balance
		return context

#allows users to delete items they posted
class deleteItem(DeleteView):
	model = Items
	success_url = reverse_lazy('homepage:index')

 
#view that allows users to register on to the website, based on code written by thenewboston in 'Django for beginners'
#tutorial series
class UserRegistrationView(View):
	form_class = UserForm
	template_name = 'homepage/register.html'

	#User requests empty registration form
	def get(self, request):
		emptyForm = self.form_class(None)
		context = {'form': emptyForm}
		return render(request, self.template_name, context)

	#Info on registration form gets posted	
	def post(self, request):
		filledForm = self.form_class(request.POST)

		#check if form is valid
		if (filledForm.is_valid()):
			userFormData = filledForm.save(commit=False)

			#clean up input
			username = filledForm.cleaned_data['username']
			password = filledForm.cleaned_data['password']

			#set password and save to User table
			userFormData.set_password(password)
			userFormData.save()

			#add new user to UserBalance table
			newUser = User.objects.get(username=username)
			newBalance = UserBalance(username=newUser,balance=100)
			newBalance.save()


			#login the user after successful registration
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect('homepage:index')

		# if form is invalid, display empty form
		else:
			emptyForm = self.form_class(None)
			context = {'form': emptyForm}
			return render(request, self.template_name, context)

#log the user out
def logout_view(request):
	logout(request)
	# return redirect('homepage:index')
	item_list = Items.objects.filter(sold=False)
	context = {'item_list': item_list}
	return render(request,'homepage/index.html', context)

