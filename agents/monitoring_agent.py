class MonitoringAgent:

    def monitor(self, disaster_type, severity):

        if severity in ["High", "Extreme", "Severe"]:
            status = "CRITICAL - Continuous Monitoring Activated"
        elif severity == "Moderate":
            status = "Active Monitoring"
        else:
            status = "Routine Monitoring"

        return f"{disaster_type} Status: {status}"
