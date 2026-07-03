import razorpay
from django.conf import settings


class RazorpayService:

    def __init__(self):
        self.client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

    def create_order(self, amount):

        data = {
            "amount": int(amount * 100),      # Razorpay expects paise
            "currency": "INR",
        }

        order = self.client.order.create(data)

        return order