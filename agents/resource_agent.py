class ResourceAgent:

    def allocate_resources(self, severity):

        if severity in ["Extreme", "Severe"]:
            return """
- Deploy NDRF Teams
- Send Rescue Boats
- Medical Emergency Units
- Food & Relief Trucks
- Evacuation Support
"""

        elif severity == "High":
            return """
- Local Disaster Response Teams
- Ambulances
- Police Control Units
"""

        elif severity == "Moderate":
            return """
- Local Monitoring Teams
- Preparedness Units
"""

        else:
            return "Keep emergency teams on standby"
