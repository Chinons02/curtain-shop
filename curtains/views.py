from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from decimal import Decimal
import random
from .models import (
    FabricType, FabricColor, CurtainDesign, 
    CurtainCustomization, ReadyMadeCurtain, HeroImage
)
from .forms import CustomizationForm

def home(request):
    featured_designs = CurtainDesign.objects.filter(is_featured=True)
    fabric_types = FabricType.objects.filter(available=True)
    ready_made = ReadyMadeCurtain.objects.filter(available=True)[:4]
    
    # Get custom hero images and featured design images
    custom_hero_images = HeroImage.objects.filter(is_active=True)
    hero_image_urls = [img.image.url for img in custom_hero_images if img.image]
    hero_image_urls.extend([design.image.url for design in featured_designs if design.image])
    
    # Randomize the merged list
    random.shuffle(hero_image_urls)
    
    context = {
        'featured_designs': featured_designs,
        'fabric_types': fabric_types,
        'ready_made_curtains': ready_made,
        'hero_images': hero_image_urls,
    }
    return render(request, 'curtains/home.html', context)

def design_detail(request, design_id):
    """View details of a specific curtain design"""
    design = get_object_or_404(CurtainDesign, id=design_id, available=True)
    ready_made = ReadyMadeCurtain.objects.filter(design=design, available=True)
    
    context = {
        'design': design,
        'ready_made_curtains': ready_made,
        'fabric_types': FabricType.objects.filter(available=True),
        'fabric_colors': FabricColor.objects.filter(available=True),
    }
    return render(request, 'curtains/design_detail.html', context)

def customize_curtain(request, design_id=None):
    """Custom curtain builder"""
    design = None
    if design_id:
        design = get_object_or_404(CurtainDesign, id=design_id, is_customizable=True)
    
    if request.method == 'POST':
        form = CustomizationForm(request.POST)
        if form.is_valid():
            customization = form.save(commit=False)
            if request.user.is_authenticated:
                customization.user = request.user
            customization.session_id = request.session.session_key
            if not request.session.session_key:
                request.session.create()
                customization.session_id = request.session.session_key
            
            # Calculate price
            customization.save()
            
            # Add to cart
            customization.added_to_cart = True
            customization.save()
            
            messages.success(request, 'Custom curtain added to cart!')
            return redirect('cart')
    else:
        initial = {}
        if design:
            initial = {
                'design': design,
                'style': design.style,
                'heading_type': design.heading_type,
            }
        form = CustomizationForm(initial=initial)
    
    context = {
        'form': form,
        'design': design,
        'fabric_types': FabricType.objects.filter(available=True, is_light_fabric=False),
        'inner_fabrics': FabricType.objects.filter(available=True, is_light_fabric=True),
        'fabric_colors': FabricColor.objects.filter(available=True),
    }
    return render(request, 'curtains/customize.html', context)

def calculate_price_ajax(request):
    """AJAX endpoint to calculate price in real-time"""
    if request.method == 'POST':
        width = Decimal(request.POST.get('width', 0))
        height = Decimal(request.POST.get('height', 0))
        fabric_id = request.POST.get('fabric_type')
        color_id = request.POST.get('fabric_color')
        style = request.POST.get('style')
        heading_type = request.POST.get('heading_type')
        include_inner = request.POST.get('include_inner_curtain') == 'true'
        inner_fabric_id = request.POST.get('inner_fabric')
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            fabric = FabricType.objects.get(id=fabric_id)
            color = FabricColor.objects.get(id=color_id)
            
            # Calculate dimensions in meters
            width_meters = width * Decimal('0.0254')
            height_meters = height * Decimal('0.0254')
            
            # Fabric needed
            fabric_needed = (width_meters * 2) * height_meters
            
            # Base price
            price = fabric_needed * fabric.price_per_meter
            
            # Color multiplier
            price *= color.price_multiplier
            
            # Style multiplier
            style_multipliers = {
                'rod_pocket': Decimal('1.0'),
                'grommet': Decimal('1.1'),
                'pinch_pleat': Decimal('1.3'),
                'goblet_pleat': Decimal('1.4'),
                'tab_top': Decimal('1.0'),
                'eyelet': Decimal('1.15'),
                'pencil_pleat': Decimal('1.2'),
            }
            price *= style_multipliers.get(style, Decimal('1.0'))
            
            # Heading multiplier
            heading_multipliers = {
                'standard': Decimal('1.0'),
                'double_pleat': Decimal('1.2'),
                'triple_pleat': Decimal('1.3'),
                'box_pleat': Decimal('1.25'),
            }
            price *= heading_multipliers.get(heading_type, Decimal('1.0'))
            
            # Inner curtain
            if include_inner and inner_fabric_id:
                inner_fabric = FabricType.objects.get(id=inner_fabric_id)
                inner_needed = (width_meters * Decimal('1.5')) * height_meters
                inner_cost = inner_needed * inner_fabric.price_per_meter
                price += inner_cost
            
            # Labor
            price += Decimal('5000.00')
            
            # Quantity
            price *= quantity
            
            return JsonResponse({
                'price': float(price),
                'price_display': f'₦{price:,.2f}'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def cart(request):
    """View cart contents"""
    if request.user.is_authenticated:
        custom_items = CurtainCustomization.objects.filter(user=request.user, added_to_cart=True)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        custom_items = CurtainCustomization.objects.filter(session_id=session_id, added_to_cart=True)
    
    # Calculate totals
    subtotal = sum(item.total_price for item in custom_items)
    shipping = Decimal('2000.00') if subtotal > 0 else Decimal('0.00')
    tax = subtotal * Decimal('0.075')  # 7.5% VAT
    total = subtotal + shipping + tax
    
    context = {
        'custom_items': custom_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'total': total,
    }
    return render(request, 'curtains/cart.html', context)

def remove_from_cart(request, item_id):
    """Remove item from cart"""
    item = get_object_or_404(CurtainCustomization, id=item_id)
    if request.user.is_authenticated and item.user == request.user:
        item.delete()
    elif item.session_id == request.session.session_key:
        item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('cart')

def product_list(request):
    """List all available ready-made curtains"""
    curtains = ReadyMadeCurtain.objects.filter(available=True).select_related(
        'design', 'fabric_type', 'fabric_color'
    )
    
    # Filters
    fabric_type = request.GET.get('fabric_type')
    color = request.GET.get('color')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if fabric_type:
        curtains = curtains.filter(fabric_type_id=fabric_type)
    if color:
        curtains = curtains.filter(fabric_color_id=color)
    if min_price:
        curtains = curtains.filter(price__gte=min_price)
    if max_price:
        curtains = curtains.filter(price__lte=max_price)
    
    context = {
        'curtains': curtains,
        'fabric_types': FabricType.objects.filter(available=True),
        'fabric_colors': FabricColor.objects.filter(available=True),
    }
    return render(request, 'curtains/product_list.html', context)