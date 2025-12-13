class Dataset:
    """Represents a data science dataset in the platform."""

    def __init__(self, name: str, last_updated: str, description: str, source: str):   
        self.__name = name
        self.__last_updated = last_updated
        self.__description = description
        self.__source = source
    def get_source(self) -> str:
        return self.__source
    
    def get_name(self) -> str:
        return self.__name
    
    def get_description(self) -> str:
        return self.__description
    
    def get_last_updated(self) -> str:
        return self.__last_updated
    
    def __str__(self) -> str:
        return f"Dataset: {self.__name} (Updated: {self.__last_updated}) from {self.__source}"