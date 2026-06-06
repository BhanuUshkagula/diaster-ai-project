class CommunicationAgent:
    def _init_(self, api_key):
        """
        api_key : Your Fast2SMS API key from fast2sms.com dashboard
        """
        self.api_key = api_key
        self.api_url = "https://www.fast2sms.com/dev/bulkV2"

    # ------------------------------------------------------------------
    # Build the warning message text
    # (Keep it short - SMS has 160 char limit per message)
    # ------------------------------------------------------------------
    def generate_alert(self, disaster_type, severity, location):
        return (
            f"DISASTER ALERT! "
            f"Type: {disaster_type} | "
            f"Severity: {severity} | "
            f"Location: {location}. "
            f"Emergency services notified. Move to safe zones immediately."
        )

    # ------------------------------------------------------------------
    # Send SMS to MULTIPLE phone numbers via Fast2SMS
    # phone_numbers : list of 10-digit Indian mobile numbers
    # Returns       : dict {number: "Sent" / "Failed: reason"}
    # ------------------------------------------------------------------
    def send_alerts(self, alert_message, phone_numbers, disaster_type, severity):
        results = {}

        for number in phone_numbers:
            number = number.strip()
            if not number:
                continue
            try:
                response = requests.post(
                    self.api_url,
                    headers={
                        "authorization": self.api_key,
                        "Content-Type" : "application/json"
                    },
                    json={
                        "route"  : "q",       # Transactional route (free tier)
                        "message": alert_message,
                        "numbers": number,
                        "flash"  : 0
                    },
                    timeout=10
                )
                data = response.json()
                if data.get("return") is True:
                    results[number] = "✅ Sent"
                else:
                    results[number] = f"❌ Failed: {data.get('message', 'Unknown error')}"
            except Exception as e:
                results[number] = f"❌ Failed: {str(e)}"

        return results