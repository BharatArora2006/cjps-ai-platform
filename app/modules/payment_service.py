import stripe
import os

from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv(
    "STRIPE_SECRET_KEY"
)


def create_payment_link(

    job

):

    payment_link = stripe.PaymentLink.create(

        line_items=[

            {

                "price_data": {

                    "currency": "usd",

                    "product_data": {

                        "name":
                        f"Process Service - Job #{job.id}"

                    },

                    "unit_amount":
                    int(job.invoice_amount * 100),

                },

                "quantity": 1,

            }

        ]

    )

    return payment_link.url