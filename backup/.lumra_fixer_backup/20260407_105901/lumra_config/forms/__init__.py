# core/forms/__init__.py
# Central forms module - exports semua form classes

from django import forms
from lumra_config.models import Category, Unit, Vendor, Stock, ProductVariant, Location, StockOpnameSession, StockOpnameItem, Recipe, RecipeIngredient, SupplierPrice, Customer
from django.forms import inlineformset_factory


# ---------- customer form (mirrors templates) ----------
class CustomerForm(forms.ModelForm):
    whatsapp = forms.CharField(required=False, label='WhatsApp')
    birth_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'placeholder':'YYYY-MM-DD'}))
    initial_points = forms.IntegerField(required=False, min_value=0)
    points_expiry = forms.DateField(required=False, widget=forms.TextInput(attrs={'placeholder':'YYYY-MM-DD'}))
    iseller_id = forms.CharField(required=False, label='iSeller ID')
    notes = forms.CharField(required=False, widget=forms.Textarea)

    class Meta:
        model = Customer
        fields = ['name', 'email', 'address', 'city', 'tier']
        widgets = {'tier': forms.RadioSelect()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # several fields are optional in the UI
        self.fields['address'].required = False
        self.fields['city'].required = False
        self.fields['tier'].required = False
        # default tier when not provided
        self.fields['tier'].initial = 'regular'



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent', 'slug', 'code', 'is_active']


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name', 'symbol', 'description', 'is_active']


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['name', 'contact_person', 'phone', 'email', 'address', 'website', 'tax_number', 'is_active']


class StockOpnameForm(forms.Form):
    """Legacy form - deprecated in favor of workflow below"""
    variant = forms.ModelChoiceField(queryset=ProductVariant.objects.all())
    location = forms.ModelChoiceField(queryset=Location.objects.all())
    counted_quantity = forms.IntegerField(min_value=0)
    notes = forms.CharField(widget=forms.Textarea, required=False)


# ========== STOCK OPNAME WORKFLOW FORMS ==========

class StockOpnameSessionForm(forms.ModelForm):
    """Create/update a stock opname session"""
    class Meta:
        model = StockOpnameSession
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'placeholder': 'General notes for this opname session...',
                'rows': 3,
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg'
            })
        }


class StockOpnameItemForm(forms.ModelForm):
    """Form for a single product in opname"""
    class Meta:
        model = StockOpnameItem
        fields = ['counted_qty', 'notes']
        labels = {
            'counted_qty': 'Counted Quantity',
            'notes': 'Notes (optional)',
        }
        widgets = {
            'counted_qty': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg',
                'placeholder': '0',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg',
                'rows': 2,
                'placeholder': 'Optional notes...'
            })
        }


# Inline formset for batch creating opname items
StockOpnameItemFormSet = inlineformset_factory(
    StockOpnameSession,
    StockOpnameItem,
    form=StockOpnameItemForm,
    extra=5,
    can_delete=True
)


class StockOpnameCSVImportForm(forms.Form):
    """Form for importing opname data from CSV"""
    csv_file = forms.FileField(
        label='CSV File',
        help_text='CSV format: sku, counted_qty, notes',
        widget=forms.FileInput(attrs={
            'accept': '.csv',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg'
        })
    )


class StockOpnameApprovalForm(forms.Form):
    """Form for approving/rejecting opname session"""
    DECISION_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]
    decision = forms.ChoiceField(
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Reason for rejection (if applicable)...',
            # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg'
        })
    )


# ========== PRODUCTION FORMS ==========

class RecipeForm(forms.ModelForm):
    """Form untuk create/edit recipe"""
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'category', 'yield_quantity', 'yield_unit', 'preparation_time']


RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    fields=['variant', 'quantity', 'unit'],
    extra=5,
    can_delete=True
)


# ========== SUPPLIER PRICING FORMS ==========

class SupplierPriceForm(forms.ModelForm):
    """Form untuk supplier pricing"""
    class Meta:
        model = SupplierPrice
        fields = ['vendor', 'variant', 'unit_price', 'minimum_quantity', 'is_preferred', 'effective_date', 'valid_until']


__all__ = [
    'CategoryForm',
    'UnitForm',
    'VendorForm',
    'StockOpnameForm',
    'StockOpnameSessionForm',
    'StockOpnameItemForm',
    'StockOpnameItemFormSet',
    'StockOpnameCSVImportForm',
    'StockOpnameApprovalForm',
    'RecipeForm',
    'RecipeIngredientFormSet',
    'SupplierPriceForm',
    'CustomerForm',
]
