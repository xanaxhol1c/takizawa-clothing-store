from django.urls import path
from . import views, webhooks

app_name = 'payments'

urlpatterns = [
    path('process/', views.payment_process, name='process'),
    path('completed/', views.payment_completed, name='completed'),
    path('canceled/',  views.payment_canceled, name='canceled'),
    path('webhook/',  webhooks.stripe_webhook, name='webhook')
]