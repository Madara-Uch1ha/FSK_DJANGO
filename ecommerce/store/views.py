from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from .models import Product, CartItem, Order, OrderItem
from .forms import ProductForm
import json

def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

def cart(request):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    
    cart_items = CartItem.objects.filter(session_id=session_id)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'store/cart.html', {'cart_items': cart_items, 'total': total})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    
    cart_item, created = CartItem.objects.get_or_create(product=product, session_id=session_id)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

def update_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id)
        action = request.POST.get('action')
        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease':
            cart_item.quantity -= 1
        
        if cart_item.quantity > 0:
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart')

def checkout(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        
        order = Order.objects.create(name=name, email=email, address=address)
        
        session_id = request.session.session_key
        cart_items = CartItem.objects.filter(session_id=session_id)
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        
        cart_items.delete()
        return render(request, 'store/order_confirmation.html', {'order': order})
    
    return render(request, 'store/checkout.html')

# ... (keep the existing views)

@staff_member_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductForm()
    return render(request, 'store/add_product.html', {'form': form})

# ... (keep the rest of the existing views)