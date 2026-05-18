# =============================================================
# lumra_system/middleware/logging_middleware.py
#
# Middleware ini otomatis mencatat:
# - Setiap request masuk (method, path, user, IP)
# - Response time (deteksi endpoint lambat)
# - Error 4xx dan 5xx
# =============================================================

import time
import logging

logger = logging.getLogger('lumra')
perf_logger = logging.getLogger('lumra.performance')

SLOW_REQUEST_THRESHOLD_MS = 1000  # Log warning jika response > 1 detik


class LumraRequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()

        # Info request masuk
        user = getattr(request, 'user', None)
        username = user.username if user and user.is_authenticated else 'anonymous'
        ip = self._get_client_ip(request)

        logger.debug(
            f"→ {request.method} {request.path} | "
            f"user={username} | ip={ip}"
        )

        # Proses request
        response = self.get_response(request)

        # Hitung durasi
        duration_ms = (time.monotonic() - start_time) * 1000

        # Log response
        log_msg = (
            f"← {request.method} {request.path} | "
            f"status={response.status_code} | "
            f"user={username} | "
            f"{duration_ms:.1f}ms"
        )

        if response.status_code >= 500:
            logger.error(log_msg)
        elif response.status_code >= 400:
            logger.warning(log_msg)
        else:
            logger.debug(log_msg)

        # Deteksi slow request
        if duration_ms > SLOW_REQUEST_THRESHOLD_MS:
            perf_logger.warning(
                f"SLOW REQUEST {duration_ms:.1f}ms | "
                f"{request.method} {request.path} | "
                f"user={username}"
            )

        return response

    def process_exception(self, request, exception):
        """Tangkap semua uncaught exception dengan full traceback."""
        user = getattr(request, 'user', None)
        username = user.username if user and user.is_authenticated else 'anonymous'
        ip = self._get_client_ip(request)

        logger.error(
            f"UNCAUGHT EXCEPTION | "
            f"{request.method} {request.path} | "
            f"user={username} | ip={ip} | "
            f"error={type(exception).__name__}: {exception}",
            exc_info=True  # ← Full traceback otomatis masuk ke log
        )
        return None  # Biarkan Django handle response error-nya

    def _get_client_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


# =============================================================
# CARA PASANG DI settings.py:
#
# MIDDLEWARE = [
#     'lumra_system.middleware.logging_middleware.LumraRequestLoggingMiddleware',
#     'django.middleware.security.SecurityMiddleware',
#     ... (middleware lainnya)
# ]
#
# PENTING: Taruh di posisi PERTAMA agar semua request tercatat,
# termasuk yang error di middleware lain.
# =============================================================