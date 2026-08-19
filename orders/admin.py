from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price', 'total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'shipping_name', 'shipping_email')
    readonly_fields = ('order_number', 'subtotal', 'shipping_cost', 'tax', 'total')
    inlines = [OrderItemInline]
