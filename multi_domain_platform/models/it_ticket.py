class ITTicket:
    """Represents an IT support ticket."""
    def __init__(self, ticket_id: int, date_created: str, priority: str, status:str,assigned_to:str):
        self.__id = ticket_id
        self.__date_created = date_created
        self.__priority = priority
        self.__status = status
        self.__assigned_to = assigned_to
       
    def get_id(self) -> int:
        return self.__id
    
    def get_date_created(self) -> str:
        return self.__date_created
    
    def get_priority(self) -> str: 
        return self.__priority
    def get_assigned_to(self) -> str:
        return self.__assigned_to

    def get_status(self) -> str:
        return self.__status
    
    def __str__(self) -> str:
        return (
            f"Ticket {self.__id}: {self.__date_created} "
            f"[{self.__priority}] - {self.__status}"
            f"{self.__assigned_to}")

