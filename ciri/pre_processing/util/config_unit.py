class ConfigUnit:
    """A class representing a configuration unit with a name, value, and description."""
    
    def __init__(self, name: str = "", value: str = "", description: str = ""):
        self._name = name
        self._value = value 
        self._description = description

    def __str__(self) -> str:
        return f"name: {self.name}\nvalue: {self.value}\ndescription: {self.description}"

    def __repr__(self) -> str:
        return f"ConfigUnit(name='{self.name}', value='{self.value}', description='{self.description}')"

    @property
    def name(self) -> str:
        """Get the name of the configuration unit."""
        return self._name

    @name.setter 
    def name(self, name: str) -> None:
        """Set the name of the configuration unit."""
        self._name = name
    
    @property
    def value(self) -> str:
        """Get the value of the configuration unit."""
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """Set the value of the configuration unit."""
        self._value = value

    @property
    def description(self) -> str:
        """Get the description of the configuration unit."""
        return self._description

    @description.setter
    def description(self, description: str) -> None:
        """Set the description of the configuration unit."""
        self._description = description
