# lumra_config/signals.py
# Auto-sync dari core/signals.py oleh lumra_sync.py
# Menangani: pengurangan stock otomatis saat order, tracking customer, dll.
# WAJIB: apps.py harus memanggil signals di ready()

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import Order, OrderItem, Stock, Product, Location
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=OrderItem)
# TODO[C3-LONG]: 'deduct_stock_on_order' = 45 baris (max 30). Pecah: deduct_stock_on_order_validate(), deduct_stock_on_order_query(), deduct_stock_on_order_render()
# TODO[C3-LONG]: 'deduct_stock_on_order' terlalu panjang (45 baris). Pecah: deduct_stock_on_order_validate(), deduct_stock_on_order_build_context(), deduct_stock_on_order_render()
def deduct_stock_on_order(sender, instance, created, **kwargs):
    """
    Kurangi stock secara otomatis ketika OrderItem dibuat (order completed).
    """
    if not created:
        return  # Hanya proses saat item baru dibuat
    
    try:
        order = instance.order
        
        # Hanya kurangi stock untuk order yang completed atau pending (akan diisi nanti)
        if order.status not in ['pending', 'completed']:
            return
        
        variant = instance.variant
        qty = instance.quantity
        
        # Cari lokasi default (biasanya warehouse/gudang utama)
        default_location = Location.objects.filter(
            name__icontains='warehouse'
        ).first() or Location.objects.first()
        
        if not default_location:
            logger.warning(f"No location found to deduct stock for OrderItem {instance.id}")
            return
        
        # Get or create stock entry
        stock_entry, created_stock = Stock.objects.get_or_create(
            variant=variant,
            location=default_location,
            defaults={'quantity': 0, 'transaction_type': 'out', 'notes': f'Order #{order.id}'}
        )
        
        # Kurangi quantity
        stock_entry.quantity -= qty
        if stock_entry.quantity < 0:
            stock_entry.quantity = 0  # Jangan negatif
        stock_entry.transaction_type = 'out'
        stock_entry.notes = f'Order #{order.id} - {variant.sku} ({qty} units)'
        stock_entry.save(update_fields=['quantity', 'transaction_type', 'notes', 'last_updated'])
        
        logger.info(f"Stock deducted: {variant.sku} x{qty} from {default_location.name}")
    
    except Exception as e:
        logger.error(f"Error deducting stock for OrderItem {instance.id}: {e}")


# TODO[C3-LONG]: 'restore_stock_on_order_cancel' = 33 baris (max 30). Pecah: restore_stock_on_order_cancel_validate(), restore_stock_on_order_cancel_query(), restore_stock_on_order_cancel_render()
@receiver(post_delete, sender=OrderItem)
# TODO[C3-LONG]: 'restore_stock_on_order_cancel' terlalu panjang (34 baris). Pecah: restore_stock_on_order_cancel_validate(), restore_stock_on_order_cancel_build_context(), restore_stock_on_order_cancel_render()
def restore_stock_on_order_cancel(sender, instance, **kwargs):
    """
    Kembalikan stock jika OrderItem dihapus (order dibatalkan).
    """
    try:
        variant = instance.variant
        qty = instance.quantity
        
        # Cari lokasi default
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        # TODO[C2-DRY]: Blok duplikat — extract ke function terpisah
        default_location = Location.objects.filter(
            name__icontains='warehouse'
        ).first() or Location.objects.first()
        
        if not default_location:
            return
        
        # Get atau create stock entry
        stock_entry, created = Stock.objects.get_or_create(
            variant=variant,
            location=default_location,
            defaults={'quantity': 0, 'transaction_type': 'in', 'notes': f'Order Cancelled'}
        )
        
        # Tambah kembali quantity
        stock_entry.quantity += qty
        stock_entry.transaction_type = 'in'
        stock_entry.notes = f'Order Cancelled - {variant.sku} returned ({qty} units)'
        stock_entry.save(update_fields=['quantity', 'transaction_type', 'notes', 'last_updated'])
        
        logger.info(f"Stock restored: {variant.sku} x{qty} to {default_location.name}")
    
    except Exception as e:
        logger.error(f"Error restoring stock for OrderItem {instance.id}: {e}")
