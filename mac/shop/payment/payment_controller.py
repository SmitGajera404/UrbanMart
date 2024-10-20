
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def verifyPaymentById(req,payment_id):

    razor_client=razorpay.Client(auth=(settings.RAZORPAY_API_KEY,settings.RAZORPAY_API_SECRET))
    try:
        params_dict = {
            'razorpay_payment_id': payment_id,
        }
        payment_details = razor_client.payment.fetch(payment_id)
        
        if payment_details['status'] == 'authorized':
            return True
        else:
            return False
    except razorpay.errors.BadRequestError:
        return False


    # Check if the payment_id is valid
    pass