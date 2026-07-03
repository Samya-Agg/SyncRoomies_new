from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import json
import razorpay

from home.models import profile as Profile
from .models import Payment
from .services.razorpay_service import RazorpayService


def premium(request):
    return render(request, "premium.html")

@csrf_exempt
@require_POST
def razorpay_webhook(request):

    print(request.body)

    return JsonResponse({
        "status": "received"
    })

def payment_success(request):
    return render(request, "success.html")

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

        # Create Razorpay Order ONLY ONCE
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
            "razorpay_signature": razorpay_signature,

        })

        payment = Payment.objects.get(
            razorpay_order_id=razorpay_order_id
        )

        payment.status = "SUCCESS"
        payment.razorpay_payment_id = razorpay_payment_id
        payment.save()

        user_profile = Profile.objects.get(
            user=payment.user
        )

        user_profile.is_premium = True
        user_profile.save()

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