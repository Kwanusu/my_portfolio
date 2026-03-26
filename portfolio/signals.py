import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Message, SystemLog

# Get an instance of a logger for standard console output
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Message)
def handle_new_inquiry(sender, instance, created, **kwargs):
    if created:
        try:
            # 1. Generate System Log for React Dashboard
            SystemLog.objects.create(
                level="INFO",
                message=f"New Inquiry received from {instance.sender_email}",
                endpoint="/api/v1/communication/inquiry/"
            )

            # 2. Send Real-time Email Notification
            subject = f"Portfolio Alert: {instance.subject}"
            email_body = (
                f"You have a new message from {instance.sender_name} ({instance.sender_email}):\n\n"
                f"{instance.body}\n\n"
                f"View this in your Admin Dashboard: {settings.FRONTEND_URL}/admin-panel"
            )
            
            send_mail(
                subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            
            logger.info(f"Notification sent for message ID: {instance.id}")

        except Exception as e:
            # Log the failure to the monitoring table
            SystemLog.objects.create(
                level="ERROR",
                message=f"Failed to process inquiry signals: {str(e)}",
                endpoint="signals.py"
            )
            logger.error(f"Signal Error: {e}")