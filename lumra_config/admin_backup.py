# lumra_config/admin.py
# Auto-sync dari core/admin.py oleh lumra_sync.py

from django.contrib import admin
from .models import Location, Product, Stock, Requisition, Transfer, UserProfile

admin.site.register(Location)
admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(Requisition)
admin.site.register(Transfer)
admin.site.register(UserProfile)