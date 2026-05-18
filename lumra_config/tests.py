from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from .models import (
    Category, Vendor, Tax, Unit, Location, Product, ProductVariant, 
    Stock, Customer, Order, OrderItem, UserProfile
)


class CategoryModelTest(TestCase):
    """Test cases for Category model"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name="Test Category",
            description="Test description",
            code="TCAT",
            slug="test-category"
        )
    
    def test_category_creation(self):
        """Test category creation"""
        self.assertEqual(self.category.name, "Test Category")
        self.assertEqual(self.category.code, "TCAT")
        self.assertEqual(self.category.slug, "test-category")
        self.assertTrue(self.category.is_active)
    
    def test_category_str_representation(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), "Test Category")
    
    def test_category_verbose_name_plural(self):
        """Test category verbose name plural"""
        self.assertEqual(self.category._meta.verbose_name_plural, "Categories")


class VendorModelTest(TestCase):
    """Test cases for Vendor model"""
    
    def setUp(self):
        self.vendor = Vendor.objects.create(
            name="Test Vendor",
            contact_person="John Doe",
            phone="123456789",
            email="test@vendor.com",
            address="Test Address"
        )
    
    def test_vendor_creation(self):
        """Test vendor creation"""
        self.assertEqual(self.vendor.name, "Test Vendor")
        self.assertEqual(self.vendor.contact_person, "John Doe")
        self.assertEqual(self.vendor.email, "test@vendor.com")
        self.assertTrue(self.vendor.is_active)
    
    def test_vendor_str_representation(self):
        """Test vendor string representation"""
        self.assertEqual(str(self.vendor), "Test Vendor")


class TaxModelTest(TestCase):
    """Test cases for Tax model"""
    
    def setUp(self):
        self.tax = Tax.objects.create(
            name="VAT",
            rate=Decimal('10.00'),
            description="Value Added Tax"
        )
    
    def test_tax_creation(self):
        """Test tax creation"""
        self.assertEqual(self.tax.name, "VAT")
        self.assertEqual(self.tax.rate, Decimal('10.00'))
        self.assertEqual(self.tax.description, "Value Added Tax")
        self.assertTrue(self.tax.is_active)
    
    def test_tax_str_representation(self):
        """Test tax string representation"""
        self.assertEqual(str(self.tax), "VAT (10.00%)")


class UnitModelTest(TestCase):
    """Test cases for Unit model"""
    
    def setUp(self):
        self.unit = Unit.objects.create(
            name="Kilogram",
            symbol="kg",
            description="Weight measurement"
        )
    
    def test_unit_creation(self):
        """Test unit creation"""
        self.assertEqual(self.unit.name, "Kilogram")
        self.assertEqual(self.unit.symbol, "kg")
        self.assertEqual(self.unit.description, "Weight measurement")
        self.assertTrue(self.unit.is_active)
    
    def test_unit_str_representation(self):
        """Test unit string representation"""
        self.assertEqual(str(self.unit), "Kilogram")


class LocationModelTest(TestCase):
    """Test cases for Location model"""
    
    def setUp(self):
        self.location = Location.objects.create(
            name="Main Store",
            address="123 Main St",
            location_type="warehouse"
        )
    
    def test_location_creation(self):
        """Test location creation"""
        self.assertEqual(self.location.name, "Main Store")
        self.assertEqual(self.location.address, "123 Main St")
        self.assertEqual(self.location.location_type, "warehouse")
        self.assertTrue(self.location.is_active)
    
    def test_location_str_representation(self):
        """Test location string representation"""
        self.assertEqual(str(self.location), "Main Store")


class ProductModelTest(TestCase):
    """Test cases for Product model"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name="Electronics",
            code="ELEC"
        )
        self.vendor = Vendor.objects.create(
            name="Tech Supplier",
            email="tech@supplier.com"
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="Test product description",
            category=self.category,
            vendor=self.vendor
        )
    
    def test_product_creation(self):
        """Test product creation"""
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.product.vendor, self.vendor)
        self.assertTrue(self.product.is_active)
    
    def test_product_str_representation(self):
        """Test product string representation"""
        self.assertEqual(str(self.product), "Test Product")


class ProductVariantModelTest(TestCase):
    """Test cases for ProductVariant model"""
    
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Product",
            description="Test product description"
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="TEST-001",
            size_weight="M",
            barcode="1234567890123",
            cost_price=Decimal('50.00'),
            selling_price=Decimal('75.00')
        )
    
    def test_variant_creation(self):
        """Test variant creation"""
        self.assertEqual(self.variant.sku, "TEST-001")
        self.assertEqual(self.variant.product, self.product)
        self.assertEqual(self.variant.cost_price, Decimal('50.00'))
        self.assertEqual(self.variant.selling_price, Decimal('75.00'))
        self.assertTrue(self.variant.is_active)
    
    def test_variant_str_representation(self):
        """Test variant string representation"""
        self.assertEqual(str(self.variant), "TEST-001")


class StockModelTest(TestCase):
    """Test cases for Stock model"""
    
    def setUp(self):
        self.location = Location.objects.create(
            name="Main Store",
            location_type="warehouse"
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="Test product description"
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="TEST-001",
            cost_price=Decimal('50.00')
        )
        self.stock = Stock.objects.create(
            variant=self.variant,
            location=self.location,
            quantity=100,
            transaction_type='in',
            reference='INIT'
        )
    
    def test_stock_creation(self):
        """Test stock creation"""
        self.assertEqual(self.stock.quantity, 100)
        self.assertEqual(self.stock.transaction_type, 'in')
        self.assertEqual(self.stock.reference, 'INIT')
        self.assertEqual(self.stock.variant, self.variant)
        self.assertEqual(self.stock.location, self.location)
    
    def test_stock_str_representation(self):
        """Test stock string representation"""
        expected = f"{self.variant.sku} - {self.location.name}"
        self.assertEqual(str(self.stock), expected)


class CustomerModelTest(TestCase):
    """Test cases for Customer model"""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Test Customer",
            email="test@customer.com",
            phone="123456789",
            address="123 Customer St",
            tier='silver'
        )
    
    def test_customer_creation(self):
        """Test customer creation"""
        self.assertEqual(self.customer.name, "Test Customer")
        self.assertEqual(self.customer.email, "test@customer.com")
        self.assertEqual(self.customer.tier, 'silver')
        self.assertTrue(self.customer.is_active)
    
    def test_customer_str_representation(self):
        """Test customer string representation"""
        self.assertEqual(str(self.customer), "Test Customer")
    
    def test_customer_tier_display(self):
        """Test customer tier display"""
        self.assertEqual(self.customer.get_tier_display(), "Silver")


class OrderModelTest(TestCase):
    """Test cases for Order model"""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Test Customer",
            email="test@customer.com"
        )
        self.order = Order.objects.create(
            customer=self.customer,
            customer_name="Test Customer",
            status='pending',
            order_type='sales_order',
            payment_status='pending',
            payment_method='cash',
            total_amount=Decimal('100.00')
        )
    
    def test_order_creation(self):
        """Test order creation"""
        self.assertEqual(self.order.customer, self.customer)
        self.assertEqual(self.order.status, 'pending')
        self.assertEqual(self.order.order_type, 'sales_order')
        self.assertEqual(self.order.payment_status, 'pending')
        self.assertEqual(self.order.total_amount, Decimal('100.00'))
    
    def test_order_str_representation(self):
        """Test order string representation"""
        expected = f"Order #{self.order.id} - {self.order.customer_name}"
        self.assertEqual(str(self.order), expected)
    
    def test_order_status_display(self):
        """Test order status display"""
        self.assertEqual(self.order.get_status_display(), "Pending")
    
    def test_order_type_display(self):
        """Test order type display"""
        self.assertEqual(self.order.get_order_type_display(), "Sales Order")


class OrderItemModelTest(TestCase):
    """Test cases for OrderItem model"""
    
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Test Customer",
            email="test@customer.com"
        )
        self.order = Order.objects.create(
            customer=self.customer,
            customer_name="Test Customer",
            status='pending',
            total_amount=Decimal('100.00')
        )
        self.product = Product.objects.create(
            name="Test Product",
            description="Test product description"
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="TEST-001",
            cost_price=Decimal('50.00'),
            selling_price=Decimal('75.00')
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            variant=self.variant,
            quantity=2,
            price=Decimal('75.00'),
            cost_price=Decimal('50.00')
        )
    
    def test_order_item_creation(self):
        """Test order item creation"""
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order_item.variant, self.variant)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.price, Decimal('75.00'))
        self.assertEqual(self.order_item.cost_price, Decimal('50.00'))
    
    def test_order_item_str_representation(self):
        """Test order item string representation"""
        expected = f"{self.order_item.quantity}x {self.variant.sku}"
        self.assertEqual(str(self.order_item), expected)


class UserProfileModelTest(TestCase):
    """Test cases for UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.location = Location.objects.create(
            name="Main Store",
            location_type="warehouse"
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            location=self.location
        )
    
    def test_user_profile_creation(self):
        """Test user profile creation"""
        self.assertEqual(self.user_profile.user, self.user)
        self.assertEqual(self.user_profile.location, self.location)
    
    def test_user_profile_str_representation(self):
        """Test user profile string representation"""
        expected = f"{self.user.username} - {self.user.location.name}"
        self.assertEqual(str(self.user_profile), expected)


class ModelIntegrationTest(TestCase):
    """Test cases for model relationships and integrations"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name="Electronics",
            code="ELEC"
        )
        self.vendor = Vendor.objects.create(
            name="Tech Supplier",
            email="tech@supplier.com"
        )
        self.product = Product.objects.create(
            name="Test Product",
            category=self.category,
            vendor=self.vendor
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="TEST-001",
            cost_price=Decimal('50.00'),
            selling_price=Decimal('75.00')
        )
        self.location = Location.objects.create(
            name="Main Store",
            location_type="warehouse"
        )
        self.customer = Customer.objects.create(
            name="Test Customer",
            email="test@customer.com"
        )
        self.order = Order.objects.create(
            customer=self.customer,
            customer_name="Test Customer",
            status='pending',
            total_amount=Decimal('150.00')
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            variant=self.variant,
            quantity=2,
            price=Decimal('75.00')
        )
        self.stock = Stock.objects.create(
            variant=self.variant,
            location=self.location,
            quantity=100,
            transaction_type='in'
        )
    
    def test_product_category_relationship(self):
        """Test product-category relationship"""
        self.assertEqual(self.product.category, self.category)
        self.assertEqual(self.category.products.count(), 1)
        self.assertEqual(self.category.products.first(), self.product)
    
    def test_product_vendor_relationship(self):
        """Test product-vendor relationship"""
        self.assertEqual(self.product.vendor, self.vendor)
        self.assertEqual(self.vendor.products.count(), 1)
        self.assertEqual(self.vendor.products.first(), self.product)
    
    def test_variant_product_relationship(self):
        """Test variant-product relationship"""
        self.assertEqual(self.variant.product, self.product)
        self.assertEqual(self.product.variants.count(), 1)
        self.assertEqual(self.product.variants.first(), self.variant)
    
    def test_order_customer_relationship(self):
        """Test order-customer relationship"""
        self.assertEqual(self.order.customer, self.customer)
        self.assertEqual(self.customer.orders.count(), 1)
        self.assertEqual(self.customer.orders.first(), self.order)
    
    def test_order_item_order_relationship(self):
        """Test order item-order relationship"""
        self.assertEqual(self.order_item.order, self.order)
        self.assertEqual(self.order.items.count(), 1)
        self.assertEqual(self.order.items.first(), self.order_item)
    
    def test_order_item_variant_relationship(self):
        """Test order item-variant relationship"""
        self.assertEqual(self.order_item.variant, self.variant)
        self.assertEqual(self.variant.order_items.count(), 1)
        self.assertEqual(self.variant.order_items.first(), self.order_item)
    
    def test_stock_variant_relationship(self):
        """Test stock-variant relationship"""
        self.assertEqual(self.stock.variant, self.variant)
        self.assertEqual(self.variant.stocks.count(), 1)
        self.assertEqual(self.variant.stocks.first(), self.stock)
    
    def test_stock_location_relationship(self):
        """Test stock-location relationship"""
        self.assertEqual(self.stock.location, self.location)
        self.assertEqual(self.location.stocks.count(), 1)
        self.assertEqual(self.location.stocks.first(), self.stock)
    
    def test_order_total_calculation(self):
        """Test order total calculation"""
        expected_total = self.order_item.quantity * self.order_item.price
        self.assertEqual(expected_total, Decimal('150.00'))
        self.assertEqual(self.order.total_amount, expected_total)
    
    def test_stock_transaction_types(self):
        """Test stock transaction types"""
        self.assertEqual(self.stock.transaction_type, 'in')
        self.assertEqual(self.stock.get_transaction_type_display(), 'Stock In')
        
        # Test stock out
        stock_out = Stock.objects.create(
            variant=self.variant,
            location=self.location,
            quantity=50,
            transaction_type='out',
            reference='SALE'
        )
        self.assertEqual(stock_out.get_transaction_type_display(), 'Stock Out')