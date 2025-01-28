class ConfigUnit:
    """A class representing a configuration unit with name, value and description."""

    def __init__(self, name: str = "", value: str = "", description: str = "") -> None:
        """Initialize a ConfigUnit with optional name, value and description.
        
        Args:
            name: The name of the configuration parameter
            value: The value of the configuration parameter  
            description: Optional description of the parameter
        """
        self._name = name
        self._value = value 
        self._description = description

    def __str__(self) -> str:
        """Return string representation of the ConfigUnit."""
        return (
            f"name: {self._name}\n"
            f"value: {self._value}\n"
            f"description: {self._description}"
        )

    def __repr__(self) -> str:
        """Return detailed string representation of the ConfigUnit."""
        return (
            f"ConfigUnit(name='{self._name}', "
            f"value='{self._value}', "
            f"description='{self._description}')"
        )

    @property
    def name(self) -> str:
        """Get the configuration parameter name."""
        return self._name

    @name.setter 
    def name(self, name: str) -> None:
        """Set the configuration parameter name."""
        self._name = name

    @property
    def value(self) -> str:
        """Get the configuration parameter value."""
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """Set the configuration parameter value."""
        self._value = value

    @property
    def description(self) -> str:
        """Get the configuration parameter description."""
        return self._description

    @description.setter
    def description(self, description: str) -> None:
        """Set the configuration parameter description."""
        self._description = description

    # Keep old interface for backwards compatibility
    def set_name(self, name: str) -> None:
        """Legacy method to set name. Use name property instead."""
        self.name = name

    def set_value(self, value: str) -> None:
        """Legacy method to set value. Use value property instead."""
        self.value = value

    def set_description(self, description: str) -> None:
        """Legacy method to set description. Use description property instead."""
        self.description = description

    def get_name(self) -> str:
        """Legacy method to get name. Use name property instead."""
        return self.name

    def get_value(self) -> str:
        """Legacy method to get value. Use value property instead."""
        return self.value

    def get_description(self) -> str:
        """Legacy method to get description. Use description property instead."""
        return self.description
