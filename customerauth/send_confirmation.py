from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from notification.smtp2gomailsender import send_email_via_smtp2go





def send_confirmation_email(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    confirmation_link = f"{request.scheme}://{request.get_host()}/accounts/confirm-email/{uid}/{token}/"
    
    subject = 'E-posta Doğrulama'
    message = render_to_string('email_templates/confirmation_email.html', {
        'user': user,
        'confirmation_link': confirmation_link,
    })

    send_email_via_smtp2go([user.email], subject, message)


def send_email_change_notification(email, user, old_email):
    subject = 'E-posta Değişikliği'
    message = render_to_string('email_templates/change_email.html', {
        'user': user,
        'new_email': email,
        'old_email':old_email,
        "subject":subject
    })

    send_email_via_smtp2go([user.email], subject, message)



def send_welcome_email(user):
    subject = 'Hoş Geldiniz'
    message = render_to_string('email_templates/welcome_email.html', {
        'user': user,
        "subject":subject,
        "site_url":"https://esyala.com/"
    })

    send_email_via_smtp2go([user.email], subject, message)