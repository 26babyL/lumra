# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Categories(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField()
    slug = models.CharField(unique=True, max_length=100, blank=True, null=True)
    code = models.CharField(max_length=10, blank=True, null=True)
    icon_url = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = '_categories'


class Taxes(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = '_taxes'


class Units(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=50)
    symbol = models.CharField(max_length=10)
    description = models.TextField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = '_units'


class Vendors(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=100)
    address = models.TextField()
    website = models.CharField(max_length=255)
    tax_number = models.CharField(max_length=50)
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = '_vendors'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class LumraConfigCustomers(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.CharField(unique=True, max_length=254)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    tier = models.CharField(max_length=20)
    loyalty_points = models.IntegerField()
    total_spent = models.DecimalField(max_digits=15, decimal_places=2)
    total_orders = models.IntegerField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    last_order_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lumra_config_customers'


class LumraConfigLocations(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    address = models.TextField()
    location_type = models.CharField(max_length=20)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'lumra_config_locations'


class LumraConfigOrderitems(models.Model):
    id = models.BigAutoField(primary_key=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    order = models.ForeignKey('LumraConfigOrders', models.DO_NOTHING)
    variant = models.ForeignKey('LumraConfigProductvariants', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'lumra_config_orderitems'


class LumraConfigOrders(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    customer = models.ForeignKey(LumraConfigCustomers, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lumra_config_orders'


class LumraConfigProductattributeItems(models.Model):
    id = models.BigAutoField(primary_key=True)
    attr_name = models.CharField(max_length=100)
    attr_value = models.CharField(max_length=255)
    updated_at = models.DateTimeField()
    variant = models.ForeignKey('LumraConfigProductvariants', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'lumra_config_productattribute_items'


class LumraConfigProducts(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    category = models.ForeignKey(Categories, models.DO_NOTHING, blank=True, null=True)
    tax = models.ForeignKey(Taxes, models.DO_NOTHING, blank=True, null=True)
    unit = models.ForeignKey(Units, models.DO_NOTHING, blank=True, null=True)
    vendor = models.ForeignKey(Vendors, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lumra_config_products'


class LumraConfigProductvariants(models.Model):
    id = models.BigAutoField(primary_key=True)
    sku = models.CharField(unique=True, max_length=50)
    size_weight = models.CharField(max_length=50, blank=True, null=True)
    price_buy = models.DecimalField(max_digits=12, decimal_places=2)
    price_sell = models.DecimalField(max_digits=12, decimal_places=2)
    updated_at = models.DateTimeField()
    product = models.ForeignKey(LumraConfigProducts, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'lumra_config_productvariants'


class LumraConfigRequisitionitem(models.Model):
    id = models.BigAutoField(primary_key=True)
    quantity = models.IntegerField()
    requisition = models.ForeignKey('LumraConfigRequisitions', models.DO_NOTHING)
    variant = models.ForeignKey(LumraConfigProductvariants, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'lumra_config_requisitionitem'
        unique_together = (('requisition', 'variant'),)


class LumraConfigRequisitions(models.Model):
    id = models.BigAutoField(primary_key=True)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    approved_at = models.DateTimeField(blank=True, null=True)
    approved_by = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    from_location = models.ForeignKey(LumraConfigLocations, models.DO_NOTHING)
    requested_by = models.ForeignKey(AuthUser, models.DO_NOTHING, related_name='lumraconfigrequisitions_requested_by_set')
    to_location = models.ForeignKey(LumraConfigLocations, models.DO_NOTHING, related_name='lumraconfigrequisitions_to_location_set')

    class Meta:
        managed = False
        db_table = 'lumra_config_requisitions'


class LumraConfigStock(models.Model):
    id = models.BigAutoField(primary_key=True)
    quantity = models.IntegerField()
    transaction_type = models.CharField(max_length=20)
    notes = models.TextField()
    last_updated = models.DateTimeField()
    created_at = models.DateTimeField()
    location = models.ForeignKey(LumraConfigLocations, models.DO_NOTHING)
    variant = models.ForeignKey(LumraConfigProductvariants, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'lumra_config_stock'


class LumraConfigStockopnameItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    current_stock = models.IntegerField()
    counted_qty = models.IntegerField()
    notes = models.TextField()
    created_at = models.DateTimeField()
    variant = models.ForeignKey(LumraConfigProductvariants, models.DO_NOTHING)
    session = models.ForeignKey('LumraConfigStockopnameSession', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'lumra_config_stockopname_item'
        unique_together = (('session', 'variant'),)


class LumraConfigStockopnameSession(models.Model):
    id = models.BigAutoField(primary_key=True)
    status = models.CharField(max_length=20)
    notes = models.TextField()
    created_at = models.DateTimeField()
    submitted_at = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    location = models.ForeignKey(LumraConfigLocations, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'lumra_config_stockopname_session'


class LumraConfigSupplierPrices(models.Model):
    id = models.BigAutoField(primary_key=True)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3)
    minimum_quantity = models.IntegerField()
    maximum_quantity = models.IntegerField(blank=True, null=True)
    lead_time_days = models.IntegerField()
    is_active = models.BooleanField()
    is_preferred = models.BooleanField()
    effective_date = models.DateField(blank=True, null=True)
    valid_until = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    last_updated_by = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)
    variant = models.ForeignKey(LumraConfigProductvariants, models.DO_NOTHING)
    vendor = models.ForeignKey(Vendors, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'lumra_config_supplier_prices'
        unique_together = (('vendor', 'variant'),)


class LumraConfigTransferitem(models.Model):
    id = models.BigAutoField(primary_key=True)
    quantity_sent = models.IntegerField()
    quantity_received = models.IntegerField(blank=True, null=True)
    transfer = models.ForeignKey('LumraConfigTransfers', models.DO_NOTHING)
    variant = models.ForeignKey(LumraConfigProductvariants, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'lumra_config_transferitem'


class LumraConfigTransfers(models.Model):
    id = models.BigAutoField(primary_key=True)
    status = models.CharField(max_length=20)
    notes = models.TextField()
    created_at = models.DateTimeField()
    sent_at = models.DateTimeField(blank=True, null=True)
    received_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(AuthUser, models.DO_NOTHING)
    destination_location = models.ForeignKey(LumraConfigLocations, models.DO_NOTHING)
    requisition = models.OneToOneField(LumraConfigRequisitions, models.DO_NOTHING, blank=True, null=True)
    source_location = models.ForeignKey(LumraConfigLocations, models.DO_NOTHING, related_name='lumraconfigtransfers_source_location_set')

    class Meta:
        managed = False
        db_table = 'lumra_config_transfers'


class LumraConfigUserprofile(models.Model):
    id = models.BigAutoField(primary_key=True)
    location = models.ForeignKey(LumraConfigLocations, models.DO_NOTHING, blank=True, null=True)
    user = models.OneToOneField(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'lumra_config_userprofile'


class ProductionRecipeCategories(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField()
    is_active = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'production_recipe_categories'


class ProductionRecipeIngredients(models.Model):
    id = models.BigAutoField(primary_key=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal_cost = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField()
    created_at = models.DateTimeField()
    recipe = models.ForeignKey('ProductionRecipes', models.DO_NOTHING)
    variant = models.ForeignKey(LumraConfigProductvariants, models.DO_NOTHING)
    unit = models.ForeignKey(Units, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'production_recipe_ingredients'
        unique_together = (('recipe', 'variant'),)


class ProductionRecipes(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    description = models.TextField()
    instructions = models.TextField()
    yield_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    preparation_time = models.IntegerField()
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    cost_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    is_archived = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    category = models.ForeignKey(ProductionRecipeCategories, models.DO_NOTHING, blank=True, null=True)
    yield_unit = models.ForeignKey(Units, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'production_recipes'