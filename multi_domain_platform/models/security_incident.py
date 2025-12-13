class SecurityIncident:
    """Represents a cybersecurity incident in the platform."""
    def __init__(self,date_reported: str, incident_type: str, severity: str, status: str, description: str):
        self.__date_reported = date_reported
        self.__incident_type = incident_type
        self.__severity = severity
        self.__status = status
        self.__description = description
    def get_incident_type(self) -> str:
        return self.__incident_type
    
    def get_date_reported(self) -> str:
        return self.__date_reported
    def get_severity(self) -> str:
        return self.__severity
    def get_status(self) -> str:
        return self.__status
    def get_description(self) -> str:
        return self.__description
    def update_status(self, new_status: str) -> None:
        self.__status = new_status
    def get_severity_level(self) -> int:
         """Return an integer severity level (simple example)."""
         mapping = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4,
        } 
         return mapping.get(self.__severity.lower(), 0)
    def __str__(self) -> str:
        return f"Incident {self.__id} [{self.__severity.upper()}] {self.__incident_type}"