from django.conf.urls import url
from . import views
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required, permission_required

app_name = 'homepage'

urlpatterns = [
	#  /homepage/
	url(r'^$', views.ItemListView, name='index'),

	# /homepage/123/
	url(r'^(?P<item_id>[0-9]+)/$', views.detail, name='detail'),

	# /homepage/add
	url(r'^add/$', login_required(views.addItem.as_view()), name='add_item'),

	# /homepage/123/edit
	url(r'^(?P<pk>[0-9]+)/edit/$', login_required(views.editItem.as_view()), name='edit_item'),

	# /homepage/123/delete
	url(r'^(?P<pk>[0-9]+)/delete/$', login_required(views.deleteItem.as_view()), name='delete_item'),

	# /homepage/register
	url(r'^register/$', views.UserRegistrationView.as_view(), name='register'),

	# /homepage/logout
	url(r'^logout/$', login_required(views.logout_view), name='logout'),

	# /homepage/login
	url(r'^login/$', auth_views.login, name='login'),	

	# /homepage/123/addReview
	url(r'^(?P<item_id>[0-9]+)/addReview/$', login_required(views.addReview.as_view()), name='add_review'),

	# /homepage/cart
	url(r'^cart/$', login_required(views.cart), name='cart'),	

	# /homepage/123/addcart
	url(r'^(?P<item_id>[0-9]+)/addcart/$', login_required(views.addCart), name='add_to_cart'),

	# /homepage/checkout
	url(r'^checkout/$', login_required(views.checkoutItems), name='checkout'),

	# /homepage/profile
	url(r'^profile/$', login_required(views.profile), name='profile'),

	# /homepage/sort
	url(r'^sort/$', views.category, name='category'),

	# /homepage/?q=
	url(r'^search$', views.searchItems, name='search'),

	# /homepage/filterprice
	url(r'^filterprice$', views.filterPrice, name='filterprice'),

	# /homepage/addmoneyform
	url(r'^addmoneyform$', views.addMoneyForm, name='addmoneyform'),

	# /homepage/addmoney
	url(r'^addmoney$', views.addMoney, name='addmoney'),

]