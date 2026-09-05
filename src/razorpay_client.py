import os
import razorpay
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

def create_order(amount, currency="INR"):
    """
    Create a Razorpay order.

    amount is provided in rupees.
    Razorpay expects amount in paise.
    """

    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        raise RuntimeError(
            "RAZORPAY_KEY_ID or RAZORPAY_KEY_SECRET not found in environment variables."
        )

    client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    amount_paise = int(amount * 100)

    order_data = {
        "amount": amount_paise,
        "currency": currency,
        "receipt": "risk_manager_receipt",
    }

    order = client.order.create(
        data=order_data
    )

    return order


if __name__ == "__main__":

    print("\n==========================================")
    print("       RAZORPAY CONNECTION TEST")
    print("==========================================")

    order = create_order(300)

    print("\nRazorpay order created successfully!")

    print("\nOrder ID:")
    print(order["id"])

    print("\nAmount:")
    print(f"₹{order['amount'] / 100:.2f}")

    print("\nCurrency:")
    print(order["currency"])
