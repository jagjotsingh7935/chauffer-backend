from django.core.mail import send_mail

def send_enquiry_email(enquiry, status):
    subject = f"Your Booking Request is {status}"

    if status == "ACCEPTED":
        message = f"""
Hello {enquiry.name},

Your booking request has been ACCEPTED.

Route: {enquiry.pickup_location} → {enquiry.drop_location}
Date: {enquiry.travel_date}

Thank you for choosing us!
"""
    else:
        message = f"""
Hello {enquiry.name},

We regret to inform you that your booking request has been REJECTED.

Please try again with different options.
"""

    send_mail(
        subject,
        message,
        None,
        [enquiry.email],
    )