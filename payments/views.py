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


def premium(request):
    return render(request, "premium.html")


# ---------------------------------------------------
# WEBHOOK
# ---------------------------------------------------

@csrf_exempt
@require_POST
def razorpay_webhook(request):

    print("=" * 70)
    print("WEBHOOK HIT")

    webhook_signature = request.headers.get("X-Razorpay-Signature")

    print("Signature:", webhook_signature)
    print("Secret:", repr(settings.RAZORPAY_WEBHOOK_SECRET))
    print("Secret Length:", len(settings.RAZORPAY_WEBHOOK_SECRET))
    print("Body Type:", type(request.body))
    print("Body Length:", len(request.body))
    print("Body Preview:", repr(request.body[:100]))

    client = razorpay.Client(
        auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET
        )
    )

    try:
        client.utility.verify_webhook_signature(
            request.body,
            webhook_signature,
            settings.RAZORPAY_WEBHOOK_SECRET,
        )

        print("Webhook VERIFIED")

    except Exception as e:

        print("Verification FAILED")
        print(type(e))
        print(e)

        return JsonResponse(
            {"error": str(e)},
            status=400
        )

    payload = json.loads(request.body)

    print("Event:", payload.get("event"))

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
# VERIFY PAYMENT (Frontend Verification)
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

        # Idempotency
        if payment.status == "SUCCESS":

            return JsonResponse({
                "success": True,
                "message": "Already Verified"
            })

        payment.status = "SUCCESS"
        payment.razorpay_payment_id = razorpay_payment_id
        payment.save()

        user_profile, created = Profile.objects.get_or_create(
            user=payment.user
        )

        user_profile.is_premium = True
        user_profile.save()

        return JsonResponse({
            "success": True,
            "message": "Payment Verified Successfully"
        })

    except Exception as e:

        print("Verification Error:", e)

        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=400)