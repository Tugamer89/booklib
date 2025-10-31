import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from core.config import settings
from utils.logger import logger
from core.templates import templates

def _send_email_brevo(to_email: str, subject: str, html_content: str) -> bool:
    if not settings.BREVO_API_KEY or not settings.BREVO_EMAIL_FROM_ADDRESS:
        logger.error("BREVO_API_KEY o BREVO_EMAIL_FROM_ADDRESS non configurati. Impossibile inviare email.")
        return False

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    sender = {"name": settings.BREVO_EMAIL_FROM_NAME, "email": settings.BREVO_EMAIL_FROM_ADDRESS}
    to = [{"email": to_email}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        sender=sender,
        subject=subject,
        html_content=html_content
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"Email inviata a {to_email} via Brevo. Oggetto: {subject}. Response: {api_response.message_id if hasattr(api_response, 'message_id') else 'N/A'}")
        return True
    except ApiException as e:
        error_body = e.body if hasattr(e, 'body') else str(e)
        logger.error(f"Errore API Brevo inviando a {to_email}. Status: {e.status if hasattr(e, 'status') else 'N/A'}. Body: {error_body}")
        return False
    except Exception as e:
        logger.error(f"Errore generico durante l'invio dell'email a {to_email} via Brevo: {e}")
        return False


def send_password_reset_email(email: str, username: str, token: str, request_url: str):
    reset_link = f"{request_url}/reset-password?token={token}"
    subject = "Reset della password per BookLib"

    try:
        template = templates.get_template('emails/password_reset.html')
        html_content = template.render(
            username=username,
            reset_link=reset_link,
            expire_minutes=settings.password_reset_token_expire_minutes
        )
    except Exception as e:
        logger.error(f"Errore caricamento/render template email password_reset.html: {e}")
        html_content = f"Clicca qui per resettare: {reset_link}"

    if not settings.BREVO_API_KEY or not settings.BREVO_EMAIL_FROM_ADDRESS:
        logger.info("="*50)
        logger.info("CONFIGURAZIONE EMAIL MANCANTE - Stampa fallback")
        logger.info(f"Invio a: {email}")
        logger.info(f"Oggetto: {subject}")
        logger.info(f"Link reset: {reset_link}")
        logger.info("="*50)
        return False

    return _send_email_brevo(email, subject, html_content)


def send_verification_email(email: str, username: str, token: str, request_url: str):
    verification_link = f"{request_url}/verify-email?token={token}"
    subject = "Verifica il tuo account BookLib"

    try:
        template = templates.get_template('emails/account_verification.html')
        html_content = template.render(
            username=username,
            verification_link=verification_link
        )
    except Exception as e:
        logger.error(f"Errore caricamento/render template email account_verification.html: {e}")
        html_content = f"Clicca qui per verificare: {verification_link}"

    if not settings.BREVO_API_KEY or not settings.BREVO_EMAIL_FROM_ADDRESS:
        logger.info("="*50)
        logger.info("CONFIGURAZIONE EMAIL MANCANTE - Stampa fallback")
        logger.info(f"Invio a: {email}")
        logger.info(f"Oggetto: {subject}")
        logger.info(f"Link verifica: {verification_link}")
        logger.info("="*50)
        return False

    return _send_email_brevo(email, subject, html_content)
