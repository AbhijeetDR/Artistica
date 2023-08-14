from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cartData, cookieCart, guestOrder
from .forms import CreateUserForm
from django.contrib.auth.forms import AuthenticationForm
from .decorators import anonymous_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from .filters import ProductFilter
from django.contrib.auth.models import User

# Create your views here.

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']


    products = Product.objects.all()
    productfilter = ProductFilter(request.GET, queryset=products)

    productfilter.form.fields['name'].widget.attrs['placeholder'] = 'Search product...'
    products = productfilter.qs
    context ={'products' : products, 'cartItems' : cartItems,'productfilter' : productfilter}
    return render(request, 'base/store.html', context)

def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context = {'items' : items, 'order':order, 'cartItems': cartItems,}
    return render(request, 'base/cart.html', context)

def checkout(request):

    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context= {'items' : items, 'order':order, 'cartItems' : cartItems,}
    return render(request, 'base/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('ProductId:', productId)
    print('Action:', action)

    customer = request.user.customer
    product = Product.objects.get(id = productId)
    order, created = Order.objects.get_or_create(customer = customer, complete = False)

    orderItem, created = OrderItem.objects.get_or_create(order = order, product = product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity -1)

    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)


    else:
        print("user is not logged in")
        print("Cookies:", request.COOKIES)
        customer , order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id
    print("total:",total)
    print("ordergetcartotal:", order.get_cart_total)
    if total == order.get_cart_total:
        order.complete = True

    order.save()
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment Complete', safe=False)

@anonymous_required
def login_user(request):
    context = {}
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            uname = form.cleaned_data['username']
            pwd = form.cleaned_data['password']

            user = authenticate(request, username = uname, password = pwd)
            if user is not None:
                login(request, user)
                return redirect('store')

            else:
                return render(request, 'store/login.html', {'error': 'Invalid username or password'})
    context = {'form' : form}
    return render(request, 'base/login.html', context)

@anonymous_required
def register_user(request):
    form = CreateUserForm()
    context = {'form' : form}
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            #redirect to login
            #new user created so create corresponding customer
            customer = Customer(user = user, name = user.username, email = user.email)
            customer.save()
            return redirect('login')
    return render(request, 'base/register.html', context)

def logout_user(request):
    print("came here")
    logout(request)
    return redirect('login')


def product(request, pk):
    item = Product.objects.get(id = pk)
    data = cartData(request)
    cartItems = data['cartItems']
    # print(item)
    productfilter = ProductFilter()
    context = {'item': item, 'cartItems' : cartItems,'productfilter' : productfilter}
    return render(request, 'base/product.html', context)

@login_required
def profile(request):
    orders = Order.objects.filter(customer = request.user.customer).order_by('-date_ordered')
    context = {'orders' : orders}
    return render(request, 'base/profile.html', context)

@login_required
def order_summary(request, order_id):

    order = Order.objects.get(id = order_id)
    orderitem = OrderItem.objects.filter(order = order)
    carttotal = 0
    cartitems = 0
    for i in orderitem:
        cartitems += i.quantity
        carttotal += i.product.price * i.quantity
    context = {'orderitem' : orderitem, 'carttotal': carttotal, 'cartitems' : cartitems}
    return render(request, 'base/ordersummary.html', context)