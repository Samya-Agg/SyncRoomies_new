from django.urls import path
from .views import create_order
from . import views

urlpatterns = [
    path("premium/", views.premium, name="premium"),
    path("create-order/", create_order, name="create-order"),
    path(
    "verify/",
    views.verify_payment,
    name="verify-payment"
),
    path(
    "success/",
    views.payment_success,
    name="payment-success"
),
    path(
    "webhook/",
    views.razorpay_webhook,
    name="razorpay-webhook"
),
]