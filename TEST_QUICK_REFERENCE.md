# 🎯 QUICK START — LUMRA Test Commands

## ✅ Run Working Test NOW

```powershell
cd d:\APPS\Project\lumra
python manage.py test_basic
```

**Expected Output:**
```
[OK] Starting LUMRA ERP Full Flow Test

[FASE 0] SETUP AWAL
[0.1] Creating Locations...
  [NEW] TKO-001: Main Store
  [NEW] GUD-001: Warehouse
  [NEW] DPR-001: Production

[FASE 1] MASTER DATA
[1.1] Creating Units...
  [NEW] Cup (cup)
  [NEW] Kg (kg)

[FASE 2] CUSTOMER
[2.1] Creating Customer...
  [NEW] John Doe

[SUMMARY] Data Created
  Locations: 3
  Categories: 4
  Units: 4
  Vendors: 2
  Products: 6
  Customers: 1

[OK] Test completed successfully!
```

---

## 📋 Model Field Names (For Reference)

```python
# Location
Location.objects.create(
    name="Store Name",
    location_type="store",  # NOT 'type'
    address="Optional"
)

# Unit
Unit.objects.create(
    name="Cup",
    symbol="cup"  # NOT 'abbreviation'
)

# Product
Product.objects.create(
    name="Espresso",
    category=cat,
    unit=unit,
    sell_price=Decimal('25000')  # NOT 'price' or 'price_sell'
)

# Stock (requires ProductVariant!)
Stock.objects.create(
    variant=product_variant,  # NOT 'product'
    location=location,
    quantity=100,
    transaction_type='in'  # Required
)
```

---

## 🧪 All Available Tests

| Command | Purpose | Status |
|---------|---------|--------|
| `python manage.py test_basic` | Quick test (6 products) | ✅ WORKING |
| `python manage.py test_with_gemini` | Full 7-phase test | ⚠️ PARTIAL |
| `python manage.py test_setup` | Original test | ⚠️ LEGACY |

---

## 🔨 Common Issues & Fixes

**Error:** `FieldError: Cannot resolve keyword 'code'`  
**Fix:** Use `name` for Location lookup, not `code`

**Error:** `FieldError: Invalid field name abbreviation`  
**Fix:** Use `symbol` for Unit, not `abbreviation`

**Error:** `FieldError: Cannot resolve keyword 'product' into field`  
**Fix:** Stock uses `variant` (ProductVariant), not `product`

---

## 📊 What Was Fixed

1. ✅ Added missing `print_result()` function
2. ✅ Fixed Location field name (`code` → lookup by `name`)
3. ✅ Fixed Unit field name (`abbreviation` → `symbol`)
4. ✅ Fixed Product field names (`price` → `sell_price`)
5. ✅ Fixed Stock model understanding (uses ProductVariant)
6. ✅ Fixed Gemini model (`gemini-1.5-flash` → `gemini-pro`)

---

## 🎓 Next Level: Create ProductVariants

For full Stock testing:

```python
from lumra_config.models import ProductVariant, Stock
from decimal import Decimal

# 1. Create ProductVariant
variant = ProductVariant.objects.create(
    product=product,
    sku=f"{product.name.upper()}-V1",
    price_buy=Decimal('30000'),
    price_sell=Decimal('50000')
)

# 2. Create Stock entry
stock = Stock.objects.create(
    variant=variant,
    location=warehouse_location,
    quantity=100,
    transaction_type='in'
)
```

---

**Need help?** Check `TEST_FIXES_COMPLETE.md` for detailed explanations.

**Ready to run?** Execute: `python manage.py test_basic`
