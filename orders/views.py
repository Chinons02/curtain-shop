from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from decimal import Decimal
from .models import Order, OrderItem
from .forms import ShippingForm
from curtains.models import CurtainCustomization

def get_cart_items(request):
    """Helper to get cart items based on user/session"""
    if request.user.is_authenticated:
        return CurtainCustomization.objects.filter(user=request.user, added_to_cart=True)
    else:
        session_id = request.session.session_key
        if not session_id:
            return CurtainCustomization.objects.none()
        return CurtainCustomization.objects.filter(session_id=session_id, added_to_cart=True)

@login_required
def checkout(request):
    """Checkout page with order summary and shipping form"""
    cart_items = get_cart_items(request)
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty')
        return redirect('cart')
    
    # Calculate totals
    subtotal = sum(item.total_price for item in cart_items)
    shipping = Decimal('2000.00') if subtotal < 50000 else Decimal('0.00')
    tax = subtotal * Decimal('0.075')
    total = subtotal + shipping + tax
    
    if request.method == 'POST':
        form = ShippingForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create order
                    order = Order.objects.create(
                        user=request.user,
                        session_id=request.session.session_key,
                        subtotal=subtotal,
                        shipping_cost=shipping,
                        tax=tax,
                        total=total,
                        shipping_name=form.cleaned_data['name'],
                        shipping_email=form.cleaned_data['email'],
                        shipping_phone=form.cleaned_data['phone'],
                        shipping_address=form.cleaned_data['address'],
                        shipping_city=form.cleaned_data['city'],
                        shipping_state=form.cleaned_data['state'],
                        shipping_zip=form.cleaned_data.get('zip_code', ''),
                        shipping_country='NG',
                        estimated_delivery_days=14,
                        delivery_notes=form.cleaned_data.get('delivery_notes', ''),
                    )
                    
                    # Create order items
                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            custom_curtain=item,
                            quantity=item.quantity,
                            unit_price=item.unit_price,
                            total_price=item.total_price,
                        )
                    
                    # Clear cart
                    cart_items.update(added_to_cart=False)
                    
                    messages.success(request, f'Order #{order.order_number} placed successfully!')
                    return redirect('order_confirmation', order_id=order.pk)
            except Exception as e:
                messages.error(request, f'Error placing order: {str(e)}')
    else:
        # Pre-fill form with user profile data if available
        initial = {}
        if request.user.is_authenticated:
            profile = request.user.profile
            initial = {
                'name': request.user.get_full_name(),
                'email': request.user.email,
                'phone': profile.phone,
                'address': profile.address,
                'city': profile.city,
                'state': profile.state,
                'zip_code': profile.zip_code,
            }
        form = ShippingForm(initial=initial)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
        'estimated_delivery': '14-21 business days',
    }
    return render(request, 'orders/checkout.html', context)

@login_required
def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = Order.objects.get(id=order_id, user=request.user)
    
    context = {
        'order': order,
        'items': order.items.all(),
    }
    return render(request, 'orders/confirmation.html', context)

@login_required
def order_history(request):
    """View order history"""
    orders = Order.objects.filter(user=request.user)
    
    context = {
        'orders': orders,
    }
    return render(request, 'orders/history.html', context)

@login_required
def order_detail(request, order_id):
    """View specific order details"""
    order = Order.objects.get(id=order_id, user=request.user)
    
    context = {
        'order': order,
        'items': order.items.all(),
    }
    return render(request, 'orders/detail.html', context)