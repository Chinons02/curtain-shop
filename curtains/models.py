from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from decimal import Decimal

def validate_image_dimensions(image):
    width, height = get_image_dimensions(image)
    if width is not None and height is not None:
        if width < 735 or height < 735:
            raise ValidationError(f"Image must be at least 735x735 pixels. Uploaded image is {width}x{height} pixels.")

class FabricType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_per_meter = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in Naira per meter")
    image = models.ImageField(upload_to='fabrics/', blank=True, null=True)
    is_light_fabric = models.BooleanField(default=False, help_text="Check if this is a light fabric suitable for inner curtains")
    available = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - ₦{self.price_per_meter}/m"

class FabricColor(models.Model):
    CATEGORY_BASIC = 'basic'
    CATEGORY_PREMIUM = 'premium'
    CATEGORY_EXOTIC = 'exotic'

    CATEGORY_CHOICES = [
        (CATEGORY_BASIC, 'Basic'),
        (CATEGORY_PREMIUM, 'Premium'),
        (CATEGORY_EXOTIC, 'Exotic'),
    ]

    name = models.CharField(max_length=100)
    hex_code = models.CharField(max_length=7, help_text="Hex color code e.g., #FF0000")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.0'), 
                                           help_text="Multiply base price by this value")
    available = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def get_category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class CurtainDesign(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='designs/', validators=[validate_image_dimensions])
    
    # Design specifications
    STYLE_CHOICES = [
        ('rod_pocket', 'Rod Pocket'),
        ('grommet', 'Grommet'),
        ('pinch_pleat', 'Pinch Pleat'),
        ('goblet_pleat', 'Goblet Pleat'),
        ('tab_top', 'Tab Top'),
        ('eyelet', 'Eyelet'),
        ('pencil_pleat', 'Pencil Pleat'),
    ]

    HEADING_CHOICES = [
        ('standard', 'Standard'),
        ('double_pleat', 'Double Pleat'),
        ('triple_pleat', 'Triple Pleat'),
        ('box_pleat', 'Box Pleat'),
    ]

    style = models.CharField(max_length=100, choices=STYLE_CHOICES)
    
    heading_type = models.CharField(max_length=100, choices=HEADING_CHOICES)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base price in Naira")
    customization_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))

    # Features
    is_customizable = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    has_inner_curtain = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    available = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return self.name
    
    def get_price_range(self):
        """Calculate price range based on fabric options"""
        base = self.base_price
        return f"₦{base:,.2f}"

class CurtainCustomization(models.Model):
    """Model for customized curtain orders"""
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Measurements
    width = models.DecimalField(max_digits=6, decimal_places=2, help_text="Width in inches", 
                                validators=[MinValueValidator(12), MaxValueValidator(240)])
    height = models.DecimalField(max_digits=6, decimal_places=2, help_text="Height in inches",
                                 validators=[MinValueValidator(12), MaxValueValidator(240)])
    
    # Fabric choices
    fabric_type = models.ForeignKey(FabricType, on_delete=models.CASCADE)
    fabric_color = models.ForeignKey(FabricColor, on_delete=models.CASCADE)
    
    # Inner curtain options
    include_inner_curtain = models.BooleanField(default=False)
    inner_fabric = models.ForeignKey(FabricType, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='inner_curtains', limit_choices_to={'is_light_fabric': True})
    
    # Design preferences
    design = models.ForeignKey(CurtainDesign, on_delete=models.CASCADE, null=True, blank=True)
    style = models.CharField(max_length=100, choices=CurtainDesign.STYLE_CHOICES)
    heading_type = models.CharField(max_length=100, choices=CurtainDesign.HEADING_CHOICES)
    
    # Quantity
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(20)])
    
    # Special instructions
    special_instructions = models.TextField(blank=True, null=True)
    
    # Pricing
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Status
    added_to_cart = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_price(self):
        """Calculate total price based on all factors"""
        # Base fabric cost (width * height converted to meters * fabric price)
        width_meters = float(self.width) * 0.0254  # Convert inches to meters
        height_meters = float(self.height) * 0.0254
        
        # Fabric needed (with 2x fullness for pleating)
        fabric_needed = (width_meters * 2) * height_meters
        
        # Base price from fabric
        base_price = Decimal(str(fabric_needed)) * self.fabric_type.price_per_meter
        
        # Color multiplier
        base_price *= self.fabric_color.price_multiplier
        
        # Style pricing
        style_multipliers = {
            'rod_pocket': 1.0,
            'grommet': 1.1,
            'pinch_pleat': 1.3,
            'goblet_pleat': 1.4,
            'tab_top': 1.0,
            'eyelet': 1.15,
            'pencil_pleat': 1.2,
        }
        base_price *= Decimal(str(style_multipliers.get(self.style, 1.0)))
        
        # Heading type multiplier
        heading_multipliers = {
            'standard': 1.0,
            'double_pleat': 1.2,
            'triple_pleat': 1.3,
            'box_pleat': 1.25,
        }
        base_price *= Decimal(str(heading_multipliers.get(self.heading_type, 1.0)))
        
        # Inner curtain cost
        if self.include_inner_curtain and self.inner_fabric:
            inner_fabric_needed = (width_meters * 1.5) * height_meters
            inner_cost = Decimal(str(inner_fabric_needed)) * self.inner_fabric.price_per_meter
            base_price += inner_cost
        
        # Design fee
        if self.design:
            base_price += self.design.customization_fee
        
        # Labor cost (fixed)
        labor_cost = Decimal('5000.00')
        base_price += labor_cost
        
        # Multiply by quantity
        base_price *= self.quantity
        
        return base_price.quantize(Decimal('0.01'))
    
    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.calculate_price() / self.quantity
        self.total_price = self.calculate_price()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Custom Curtain {self.width}x{self.height} - {self.fabric_type.name}"

class ReadyMadeCurtain(models.Model):
    design = models.ForeignKey(CurtainDesign, on_delete=models.CASCADE)
    fabric_type = models.ForeignKey(FabricType, on_delete=models.CASCADE)
    fabric_color = models.ForeignKey(FabricColor, on_delete=models.CASCADE)
    
    # Standard sizes
    width = models.DecimalField(max_digits=6, decimal_places=2)
    height = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Optional specific image for this ready-made curtain
    image = models.ImageField(upload_to='ready_made/', blank=True, null=True, validators=[validate_image_dimensions], help_text="Upload specific image for this curtain, or leave blank to use the design's image.")
    
    # Stock and pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    
    # Features
    includes_inner_curtain = models.BooleanField(default=False)
    inner_fabric = models.ForeignKey(FabricType, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='ready_made_inner', limit_choices_to={'is_light_fabric': True})
    
    available = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Ready-Made Curtain"
        verbose_name_plural = "Ready-Made Curtains"
    
    def __str__(self):
        return f"{self.design.name} - {self.width}x{self.height} - ₦{self.price:,.2f}"

class HeroImage(models.Model):
    image = models.ImageField(upload_to='hero_images/', validators=[validate_image_dimensions])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Hero Image"
        verbose_name_plural = "Hero Images"
        ordering = ['-created_at']

    def __str__(self):
        return f"Hero Image {self.id}"