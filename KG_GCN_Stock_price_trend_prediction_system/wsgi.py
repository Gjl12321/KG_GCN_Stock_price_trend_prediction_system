"""
WSGI config for KG_GCN_Stock_price_trend_prediction_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KG_GCN_Stock_price_trend_prediction_system.settings')

application = get_wsgi_application()
