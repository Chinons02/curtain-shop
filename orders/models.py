from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from curtains.models import CurtainCustomization, ReadyMadeCurtain
from decimal import Decimal

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Order details
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2)

    # Shipping information
    shipping_name = models.CharField(max_length=200)
    shipping_email = models.EmailField()
    shipping_phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_zip = models.CharField(max_length=20)
    shipping_country = CountryField(default='NG')
    
    # Delivery information
    estimated_delivery_days = models.IntegerField(default=14)
    delivery_notes = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            from datetime import datetime
            self.order_number = f"CTN-{datetime.now().strftime('%Y%m%d')}-{Order.objects.count() + 1:04d}"
        super().save(*args, **kwargs)
    
    def get_estimated_delivery(self):
        from datetime import datetime, timedelta
        return datetime.now() + timedelta(days=self.estimated_delivery_days)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    
    # Can be either custom or ready-made
    custom_curtain = models.ForeignKey(CurtainCustomization, on_delete=models.SET_NULL, null=True, blank=True)
    ready_made_curtain = models.ForeignKey(ReadyMadeCurtain, on_delete=models.SET_NULL, null=True, blank=True)
    
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    def __str__(self):
        if self.custom_curtain:
            return f"Custom Curtain - {self.custom_curtain.fabric_type.name}"
        return f"Ready-Made Curtain - {self.ready_made_curtain.design.name}"