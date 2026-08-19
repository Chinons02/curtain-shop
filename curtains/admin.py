from django.contrib import admin
from .models import FabricType, FabricColor, CurtainDesign, CurtainCustomization, ReadyMadeCurtain, HeroImage


@admin.register(FabricType)
class FabricTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_per_meter', 'is_light_fabric', 'available')
    list_filter = ('is_light_fabric', 'available')
    search_fields = ('name',)


@admin.register(FabricColor)
class FabricColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code', 'category', 'price_multiplier', 'available')
    list_filter = ('category', 'available')
    search_fields = ('name',)


@admin.register(CurtainDesign)
class CurtainDesignAdmin(admin.ModelAdmin):
    list_display = ('name', 'style', 'heading_type', 'base_price', 'is_featured', 'is_customizable', 'available')
    list_filter = ('style', 'heading_type', 'is_featured', 'is_customizable', 'available')
    search_fields = ('name', 'description')


@admin.register(ReadyMadeCurtain)
class ReadyMadeCurtainAdmin(admin.ModelAdmin):
    list_display = ('design', 'fabric_type', 'fabric_color', 'width', 'height', 'price', 'stock', 'available')
    list_filter = ('available', 'fabric_type', 'fabric_color', 'includes_inner_curtain')
    search_fields = ('design__name',)


@admin.register(CurtainCustomization)
class CurtainCustomizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'width', 'height', 'fabric_type', 'fabric_color', 'style', 'total_price')
    list_filter = ('style', 'heading_type')
    readonly_fields = ('unit_price', 'total_price')


@admin.register(HeroImage)
class HeroImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'is_active', 'created_at')
    list_filter = ('is_active',)
    list_editable = ('is_active',)
