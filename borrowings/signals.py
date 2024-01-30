import os

from django.db.models.signals import post_save
from django.dispatch import receiver
from dotenv import load_dotenv

from .telegram_helper import send_telegram_message
from .models import Borrowing

load_dotenv()


@receiver(post_save, sender=Borrowing)
async def send_telegram_notification(sender, instance, created, **kwargs):
    if created:
        try:
            await send_telegram_message(
                os.environ.get("TELEGRAM_BOT_TOKEN"),
                os.environ.get("TG_ADMIN_CHAT_ID"),
                f"New borrowing created! \n{instance.message()}",
            )
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
