import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from core.config import settings
from core.templates import templates
from utils.logger import logger


def _send_email_brevo(to_email: str, subject: str, html_content: str) -> bool:
    if not settings.BREVO_API_KEY or not settings.BREVO_EMAIL_FROM_ADDRESS:
        logger.error(
            "BREVO_API_KEY or BREVO_EMAIL_FROM_ADDRESS not configured. Cannot send email."
        )
        return False

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.BREVO_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    sender = {"name": settings.BREVO_EMAIL_FROM_NAME, "email": settings.BREVO_EMAIL_FROM_ADDRESS}
    to = [{"email": to_email}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to, sender=sender, subject=subject, html_content=html_content
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        logger.info(
            f"Email sent to {to_email} via Brevo. Subject: {subject}. Response: {api_response.message_id if hasattr(api_response, 'message_id') else 'N/A'}"
        )
        return True
    except ApiException as e:
        error_body = e.body if hasattr(e, "body") else str(e)
        logger.error(
            f"Brevo API error sending to {to_email}. Status: {e.status if hasattr(e, 'status') else 'N/A'}. Body: {error_body}"
        )
        return False
    except Exception as e:
        logger.error(f"Generic error sending email to {to_email} via Brevo: {e}")
        return False


def send_password_reset_email(email: str, username: str, token: str, request_url: str):
    reset_link = f"{request_url}/reset-password?token={token}"
    subject = "BookLib password reset"

    try:
        template = templates.get_template("emails/password_reset.html")
        html_content = template.render(
            username=username,
            reset_link=reset_link,
            expire_minutes=settings.password_reset_token_expire_minutes,
        )
    except Exception as e:
        logger.error(f"Error loading/rendering password_reset.html email template: {e}")
        html_content = f"Click here to reset your password: {reset_link}"

    if not settings.BREVO_API_KEY or not settings.BREVO_EMAIL_FROM_ADDRESS:
        logger.info("=" * 50)
        logger.info("EMAIL CONFIG MISSING - Fallback print")
        logger.info(f"Sending to: {email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Reset link: {reset_link}")
        logger.info("=" * 50)
        return False

    return _send_email_brevo(email, subject, html_content)


def send_verification_email(email: str, username: str, token: str, request_url: str):
    verification_link = f"{request_url}/verify-email?token={token}"
    subject = "Verify your BookLib account"

    try:
        template = templates.get_template("emails/account_verification.html")
        html_content = template.render(username=username, verification_link=verification_link)
    except Exception as e:
        logger.error(f"Error loading/rendering account_verification.html email template: {e}")
        html_content = f"Click here to verify: {verification_link}"

    if not settings.BREVO_API_KEY or not settings.BREVO_EMAIL_FROM_ADDRESS:
        logger.info("=" * 50)
        logger.info("EMAIL CONFIG MISSING - Fallback print")
        logger.info(f"Sending to: {email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Verification link: {verification_link}")
        logger.info("=" * 50)
        return False

    return _send_email_brevo(email, subject, html_content)
