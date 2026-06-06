import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Twilio import — only fails at runtime if twilio package not installed
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False


class CommunicationAgent:

    # ─────────────────────────────────────────────
    # 1. Build the alert message text
    # ─────────────────────────────────────────────
    def generate_alert(self, disaster_type, severity, location):
        return (
            f"🚨 PUBLIC SAFETY ALERT 🚨\n"
            f"Disaster Type : {disaster_type}\n"
            f"Severity Level: {severity}\n"
            f"Location      : {location}\n"
            f"Emergency services have been notified.\n"
            f"Follow official instructions and move to safe zones if required."
        )

    # ─────────────────────────────────────────────
    # 2. Send alert via Email (SMTP / Gmail)
    #
    # HOW TO SET UP:
    #   - Use a Gmail account
    #   - Enable "App Passwords" at myaccount.google.com/apppasswords
    #   - Pass those credentials here (or load from env / Streamlit secrets)
    # ─────────────────────────────────────────────
    def send_email_alert(
        self,
        alert_message: str,
        recipient_emails: list,
        sender_email: str,
        sender_password: str,
    ) -> dict:
        """
        Sends the alert to every address in recipient_emails.
        Returns {"success": True/False, "message": "..."}
        """
        if not recipient_emails:
            return {"success": False, "message": "No recipient emails provided."}

        subject = "🚨 DISASTER ALERT — Immediate Action Required"

        try:
            # Connect to Gmail's SMTP server over TLS
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.ehlo()
                server.starttls()          # Encrypt the connection
                server.login(sender_email, sender_password)

                for email in recipient_emails:
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = subject
                    msg["From"] = sender_email
                    msg["To"] = email

                    # Plain-text body
                    text_part = MIMEText(alert_message, "plain")

                    # HTML body (nicer formatting in inbox)
                    html_body = alert_message.replace("\n", "<br>")
                    html_part = MIMEText(
                        f"""
                        <html><body>
                        <div style="font-family:Arial,sans-serif;
                                    background:#fff3cd;
                                    border:2px solid #e53935;
                                    border-radius:8px;
                                    padding:20px;
                                    max-width:500px;">
                          <h2 style="color:#e53935;">🚨 Disaster Alert</h2>
                          <pre style="font-size:15px;">{html_body}</pre>
                        </div>
                        </body></html>
                        """,
                        "html",
                    )

                    msg.attach(text_part)
                    msg.attach(html_part)
                    server.sendmail(sender_email, email, msg.as_string())

            return {
                "success": True,
                "message": f"✅ Email alert sent to {len(recipient_emails)} recipient(s).",
            }

        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "message": "❌ Email authentication failed. Check your Gmail App Password.",
            }
        except Exception as e:
            return {"success": False, "message": f"❌ Email error: {str(e)}"}

    # ─────────────────────────────────────────────
    # 3. Send alert via Telegram Bot
    #
    # HOW TO SET UP:
    #   - Message @BotFather on Telegram → /newbot → copy the token
    #   - Add your bot to a group/channel and get the chat_id
    #     (send a message, then visit:
    #      https://api.telegram.org/bot<TOKEN>/getUpdates)
    # ─────────────────────────────────────────────
    def send_telegram_alert(
        self,
        alert_message: str,
        bot_token: str,
        chat_id: str,
    ) -> dict:
        """
        Posts the alert to a Telegram chat/channel.
        Returns {"success": True/False, "message": "..."}
        """
        if not bot_token or not chat_id:
            return {"success": False, "message": "Telegram bot token or chat ID missing."}

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": alert_message,
            "parse_mode": "Markdown",
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return {"success": True, "message": "✅ Telegram alert sent successfully."}
            else:
                return {
                    "success": False,
                    "message": f"❌ Telegram error {response.status_code}: {response.text}",
                }
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"❌ Telegram connection error: {str(e)}"}

    # ─────────────────────────────────────────────
    # 4. Send SMS via Twilio  (works worldwide)
    #
    # HOW TO SET UP (Free Trial):
    #   1. Sign up at twilio.com → verify your phone number
    #   2. From the Console dashboard copy:
    #        • Account SID
    #        • Auth Token
    #   3. Get a free Twilio phone number (the "from" number)
    #   NOTE: Free trial can only send to VERIFIED numbers.
    #         Upgrade to a paid plan for bulk / unverified numbers.
    # ─────────────────────────────────────────────
    def send_sms_twilio(
        self,
        alert_message: str,
        phone_numbers: list,       # list of strings like ["+919876543210"]
        account_sid: str,
        auth_token: str,
        from_number: str,          # your Twilio number e.g. "+15551234567"
    ) -> dict:
        """
        Sends SMS to every number in phone_numbers via Twilio.
        Numbers must include country code: +91 for India, +1 for US, etc.
        """
        if not TWILIO_AVAILABLE:
            return {"success": False, "message": "❌ Twilio package not installed. Run: pip install twilio"}

        if not phone_numbers:
            return {"success": False, "message": "No phone numbers provided."}

        try:
            client = TwilioClient(account_sid, auth_token)
            failed = []
            for number in phone_numbers:
                try:
                    client.messages.create(
                        body=alert_message,
                        from_=from_number,
                        to=number.strip(),
                    )
                except Exception as e:
                    failed.append(f"{number}: {str(e)}")

            if failed:
                return {
                    "success": False,
                    "message": f"⚠️ Some SMS failed:\n" + "\n".join(failed),
                }
            return {
                "success": True,
                "message": f"✅ SMS sent to {len(phone_numbers)} number(s) via Twilio.",
            }
        except Exception as e:
            return {"success": False, "message": f"❌ Twilio error: {str(e)}"}

    # ─────────────────────────────────────────────
    # 5. Send SMS via Fast2SMS  (India only, FREE)
    #
    # HOW TO SET UP:
    #   1. Sign up at fast2sms.com
    #   2. Go to Dev API → copy your API key
    #   NOTE: Free account gives ~100 SMS credits.
    #         Only works for Indian numbers (no +91 prefix needed).
    # ─────────────────────────────────────────────
    def send_sms_fast2sms(
        self,
        alert_message: str,
        phone_numbers: list,   # Indian numbers without +91, e.g. ["9876543210"]
        api_key: str,
    ) -> dict:
        """
        Sends SMS to Indian phone numbers using Fast2SMS (free tier available).
        """
        if not phone_numbers:
            return {"success": False, "message": "No phone numbers provided."}

        # Fast2SMS accepts comma-separated numbers
        numbers_str = ",".join([n.strip() for n in phone_numbers])

        url = "https://www.fast2sms.com/dev/bulkV2"
        headers = {"authorization": api_key, "Content-Type": "application/json"}
        payload = {
            "message": alert_message,
            "language": "english",
            "route": "q",          # "q" = Quick Transactional route
            "numbers": numbers_str,
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            data = response.json()
            if data.get("return") is True:
                return {
                    "success": True,
                    "message": f"✅ SMS sent to {len(phone_numbers)} number(s) via Fast2SMS.",
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ Fast2SMS error: {data.get('message', 'Unknown error')}",
                }
        except requests.exceptions.RequestException as e:
            return {"success": False, "message": f"❌ Fast2SMS connection error: {str(e)}"}
