from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import json
import hmac
import hashlib
import razorpay

from home.models import profile as Profile
from .models import Payment
from .services.razorpay_service import RazorpayService


# ---------------------------------------------------
# PREMIUM PAGE
# ---------------------------------------------------

def premium(request):
    return render(request, "premium.html")


# ---------------------------------------------------
# RAZORPAY WEBHOOK
# ---------------------------------------------------

@csrf_exempt
@require_POST
def razorpay_webhook(request):

    webhook_signature = request.headers.get("X-Razorpay-Signature")

    body = request.body.decode("utf-8")

    generated_signature = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
        body.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(generated_signature, webhook_signature):
        return JsonResponse(
            {
                "success": False,
                "error": "Invalid webhook signature"
            },
            status=400
        )

    payload = json.loads(body)

    event = payload.get("event")

    # Ignore unrelated events
    if event != "payment.captured":
        return JsonResponse({"status": "ignored"})

    payment_entity = payload["payload"]["payment"]["entity"]

    razorpay_payment_id = payment_entity["id"]
    razorpay_order_id = payment_entity["order_id"]

    try:

        payment = Payment.objects.get(
            razorpay_order_id=razorpay_order_id
        )

    except Payment.DoesNotExist:

        return JsonResponse(
            {"status": "payment not found"},
            status=404
        )

    # -----------------------------
    # IDEMPOTENCY
    # -----------------------------
    if payment.status == "SUCCESS":
        return JsonResponse(
            {"status": "already processed"}
        )

    payment.status = "SUCCESS"
    payment.razorpay_payment_id = razorpay_payment_id
    payment.save()

    profile, _ = Profile.objects.get_or_create(
        user=payment.user
    )

    profile.is_premium = True
    profile.save()

    return JsonResponse({"status": "ok"})


# ---------------------------------------------------
# SUCCESS PAGE
# ---------------------------------------------------

def payment_success(request):
    return render(request, "success.html")


# ---------------------------------------------------
# CREATE ORDER
# ---------------------------------------------------

@csrf_exempt
@login_required
@require_POST
def create_order(request):

    PREMIUM_PRICE = 99

    payment = Payment.objects.create(
        user=request.user,
        amount=PREMIUM_PRICE,
        status="PENDING",
        gateway="RAZORPAY"
    )

    try:

        service = RazorpayService()

        order = service.create_order(PREMIUM_PRICE)

        payment.razorpay_order_id = order["id"]
        payment.save()

        return JsonResponse({
            "success": True,
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key": settings.RAZORPAY_KEY_ID
        })

    except Exception as e:

        payment.status = "FAILED"
        payment.save()

        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)


# ---------------------------------------------------
# VERIFY PAYMENT (Frontend)
# ---------------------------------------------------

@csrf_exempt
@login_required
@require_POST
def verify_payment(request):

    try:

        data = json.loads(request.body)

        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_signature = data.get("razorpay_signature")

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        client.utility.verify_payment_signature({

            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature

        })

        payment = Payment.objects.get(
            razorpay_order_id=razorpay_order_id
        )

        # -----------------------------
        # IDEMPOTENCY
        # -----------------------------
        if payment.status == "SUCCESS":

            return JsonResponse({
                "success": True,
                "message": "Already Verified"
            })

        payment.status = "SUCCESS"
        payment.razorpay_payment_id = razorpay_payment_id
        payment.save()

        profile, _ = Profile.objects.get_or_create(
            user=payment.user
        )

        profile.is_premium = True
        profile.save()

        return JsonResponse({
            "success": True,
            "message": "Payment Verified Successfully"
        })

    except Exception as e:

        print(e)

        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)