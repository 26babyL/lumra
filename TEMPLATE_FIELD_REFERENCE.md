# 📚 LUMRA TEMPLATE FIELD REFERENCE GUIDE
**For Template Developers - Use ONLY These Fields**

---

## ✅ ProductVariant Model - Correct Field Names

These fields are available directly on `ProductVariant` objects in templates.

```django
{% for variant in variants %}
  <!-- ✓ CORRECT USAGE -->
  {{ variant.sku }}              {# Product SKU/Code #}
  {{ variant.size_weight }}      {# Size or weight (e.g., "250g", "Small") #}
  {{ variant.price_buy }}        {# Purchasing/cost price #}
  {{ variant.price_sell }}       {# Selling price #}
  {{ variant.total_stock }}      {# Total stock across all locations #}
  {{ variant.updated_at }}       {# Last update timestamp #}
  
  <!-- RELATED OBJECTS -->
  {{ variant.product.name }}     {# Product name #}
  {{ variant.product.sell_price }}{# Product standard selling price #}
  {{ variant.product.barcode }}  {# Product barcode/code #}
  {{ variant.product.category }} {# Product category #}
  {{ variant.product.vendor }}   {# Supplier/vendor #}
  {{ variant.product.tax }}      {# Tax rate #}
  {{ variant.product.unit }}     {# Unit of measurement #}
{% endfor %}
```

---

## ❌ WRONG - Fields That Don't Exist

**DO NOT USE THESE:**

```django
{{ variant.unit_price }}         {# ✗ WRONG - use variant.price_buy instead #}
{{ variant.product.base_price }} {# ✗ WRONG - use variant.price_sell instead #}
{{ variant.product.unit_price }} {# ✗ WRONG - use variant.price_buy instead #}
{{ variant.code }}               {# ✗ WRONG - use variant.sku instead #}
```

---

## 📋 Complete Field Reference by Model

### Product Model (lumra_config_products)
```python
name              # CharField - Product name
description       # TextField - Product description
category          # ForeignKey - Product category
vendor            # ForeignKey - Supplier/vendor
tax               # ForeignKey - Tax rate
unit              # ForeignKey - Unit of measurement
sell_price        # DecimalField - Standard selling price
barcode           # CharField - Product barcode (same as code field)
min_stock         # DecimalField - Minimum stock level for alerts
max_stock         # DecimalField - Maximum stock for auto-ordering
is_active         # BooleanField - Active/inactive status
track_batch       # BooleanField - Requires batch tracking?
has_expiry        # BooleanField - Has expiry date?
created_at        # DateTimeField - Creation timestamp
updated_at        # DateTimeField - Last update timestamp
```

**Usage in Templates:**
```django
{{ product.name }}
{{ product.sell_price|floatformat:0 }}
{% if product.is_active %}Active{% endif %}
```

---

### ProductVariant Model (lumra_config_productvariants)
```python
product           # ForeignKey - Related product
sku               # CharField - Unique SKU/identifier
size_weight       # CharField - Size or weight descriptor
price_buy         # DecimalField - Purchase/cost price
price_sell        # DecimalField - Selling price
updated_at        # DateTimeField - Last update timestamp

# Properties (read-only unless cached)
total_stock       # Property that sums Stock.quantity for this variant
_cached_total_stock # Cache field (internal use)
```

**Usage in Templates:**
```django
<!-- Stock Purchasing Pages -->
{{ variant.sku }} - {{ variant.size_weight }}
Price: Rp {{ variant.price_buy|floatformat:0 }}
Stock: {{ variant.total_stock }}

<!-- Notes: Use price_buy for purchasing pages, NOT unit_price -->
```

---

### Stock Model (lumra_config_stock)
```python
variant           # ForeignKey - Product variant
location          # ForeignKey - Store/warehouse location
quantity          # IntegerField - Current quantity on hand
transaction_type  # CharField - in/out/adjustment/transfer/etc
notes             # TextField - Transaction notes
reserved_quantity # DecimalField - Reserved/held quantity
available_quantity # Property - quantity - reserved_quantity
last_updated      # DateTimeField - Last update
created_at        # DateTimeField - Creation timestamp
```

**Usage in Templates:**
```django
{{ stock.quantity }} units available
Reserved: {{ stock.reserved_quantity }}
Available: {{ stock.available_quantity }}
```

---

### Customer Model (lumra_config_customers)
```python
name              # CharField - Customer name
email             # EmailField - Customer email
phone             # CharField - Customer phone
address           # TextField - Customer address
city              # CharField - City name
tier              # CharField - Customer tier (bronze/silver/gold/platinum)
is_active         # BooleanField - Active status
created_at        # DateTimeField - Registration date
updated_at        # DateTimeField - Last update
```

**Usage in Templates:**
```django
{{ customer.name }}
Email: {{ customer.email }}
Tier: {{ customer.get_tier_display }}
```

---

### Location Model (lumra_config_locations)
```python
name              # CharField - Location name (e.g., "Lumra Coffee - CBD Jakarta")
address           # TextField - Physical address
location_type     # CharField - store/warehouse/roastery
created_at        # DateTimeField - Creation date
```

**Usage in Templates:**
```django
<h3>{{ location.name }}</h3>
<p>{{ location.address }}</p>
<span>{{ location.location_type }}</span>
```

---

### Category Model (_categories)
```python
name              # CharField - Category name (unique)
description       # TextField - Category description
parent            # ForeignKey - Parent category (for hierarchy)
slug              # CharField - URL-friendly slug
code              # CharField - Category code
icon_url          # CharField - Icon URL
is_active         # BooleanField - Active status
created_at        # DateTimeField - Creation date
updated_at        # DateTimeField - Last update
```

**Usage in Templates:**
```django
{% for category in categories %}
  <div class="category">
    {{ category.name }}
    {% if category.icon_url %}
      <img src="{{ category.icon_url }}" />
    {% endif %}
  </div>
{% endfor %}
```

---

### Vendor Model (_vendors)
```python
name              # CharField - Vendor/supplier name
code              # CharField - Vendor code
contact_person    # CharField - Primary contact name
phone             # CharField - Contact phone
email             # EmailField - Contact email
address           # TextField - Vendor address
website           # URLField - Website URL
tax_number        # CharField - Tax ID
is_active         # BooleanField - Active status
created_at        # DateTimeField - Creation date
updated_at        # DateTimeField - Last update
```

---

### Unit Model (_units)
```python
name              # CharField - Unit name (e.g., "Gram", "Liter")
symbol            # CharField - Unit symbol (e.g., "g", "L")
description       # TextField - Description
is_active         # BooleanField - Active status
created_at        # DateTimeField - Creation date
```

**Usage in Templates:**
```django
Quantity: {{ quantity }} {{ unit.symbol }}
```

---

### Tax Model (_taxes)
```python
name              # CharField - Tax name (e.g., "PPN 11%")
rate              # DecimalField - Tax rate as decimal (11.00 = 11%)
description       # TextField - Tax description
is_active         # BooleanField - Active status
created_at        # DateTimeField - Creation date
```

**Usage in Templates:**
```django
Tax: {{ tax.name }} ({{ tax.rate }}%)
```

---

## 🎯 Common Template Patterns

### Pattern 1: Displaying Product with Variant Price
```django
{% for variant in variants %}
  <div class="product-card">
    <h4>{{ variant.product.name }}</h4>
    <span class="sku">SKU: {{ variant.sku }}</span>
    <span class="size">{{ variant.size_weight }}</span>
    
    {# ✓ CORRECT - Use price_buy for purchasing #}
    <span class="price">Rp {{ variant.price_buy|floatformat:0 }}</span>
    
    {# ✓ CORRECT - Use total_stock #}
    <span class="stock">{{ variant.total_stock }} in stock</span>
  </div>
{% endfor %}
```

### Pattern 2: Stock Status Badge
```django
{% if variant.total_stock > 50 %}
  <span class="badge-available">Tersedia ({{ variant.total_stock }})</span>
{% elif variant.total_stock > 10 %}
  <span class="badge-limited">Terbatas ({{ variant.total_stock }})</span>
{% else %}
  <span class="badge-out">Habis</span>
{% endif %}
```

### Pattern 3: Location and Stock by Location
```django
{% for location in locations %}
  <h4>{{ location.name }}</h4>
  <p>{{ location.address }}</p>
  
  {% for stock in location.stock_set.all %}
    {{ stock.variant.sku }}: {{ stock.quantity }} {{ stock.variant.product.unit.symbol }}
  {% endfor %}
{% endfor %}
```

---

## 🔴 ERROR PREVENTION CHECKLIST

Before deploying templates, check:

- [ ] No `base_price` references (use `price_buy` or `price_sell`)
- [ ] No `unit_price` references (use `price_buy` or `price_sell`)
- [ ] No `code` on ProductVariant (use `sku`)
- [ ] No `total_qty` or non-existent fields
- [ ] All ForeignKey relationships using correct names
- [ ] All URLs use actual route names or correct paths
- [ ] All model fields exist in the database

---

**Last Updated:** 2026-04-16  
**Template Compatibility:** Django 6.0.3, LUMRA Coffee Shop ERP
