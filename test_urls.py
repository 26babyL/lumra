from django.test import Client
from django.contrib.auth.models import User
import time

urls = [
    '/sales/order/', '/sales/quotation/', '/sales/invoice/', '/sales/payment/', '/sales/retur/',
    '/marketing/campaigns/', '/marketing/discounts/', '/marketing/vouchers/', '/marketing/loyalty/', '/marketing/promotions/',
    '/inventory/planning/', '/inventory/movement/', '/inventory/expiry/', '/reports/expiry/',
    '/taxes/', '/bank-accounts/', '/payment-terms/', '/tags/',
    '/settings/api-keys/', '/settings/backup/', '/settings/numbering/', '/settings/permissions/'
]

c = Client()
u = User.objects.first()

if not u:
    print('NO_USER_FOUND')
else:
    print(f'USER_OK: {u.username}')
    c.force_login(u)
    
    for url in urls:
        print(f"Menguji {url:<25} ... ", end="", flush=True)
        try:
            start_time = time.time()
            response = c.get(url)
            elapsed = time.time() - start_time
            print(f"[HTTP {response.status_code}] ({elapsed:.2f} detik)")
        except Exception as e:
            print(f"[GAGAL: {e}]")