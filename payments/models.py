from django.db import models
from django.contrib.auth.models import User
from home.models import profile as Profile


class Payment(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("REFUNDED", "Refunded"),
    ]

    GATEWAY_CHOICES = [
        ("RAZORPAY", "Razorpay"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=10,
        default="INR"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    gateway = models.CharField(
        max_length=20,
        choices=GATEWAY_CHOICES,
        default="RAZORPAY"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    razorpay_order_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )

    razorpay_payment_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} ({self.status})"


class Subscription(models.Model):

    PLAN_CHOICES = [
        ("FREE", "Free"),
        ("PREMIUM", "Premium"),
    ]

    STATUS_CHOICES = [
        ("ACTIVE", "Active"),
        ("EXPIRED", "Expired"),
        ("CANCELLED", "Cancelled"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="subscription"
    )

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default="FREE"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="ACTIVE"
    )

    start_date = models.DateTimeField(
        null=True,
        blank=True
    )

    end_date = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.plan}"