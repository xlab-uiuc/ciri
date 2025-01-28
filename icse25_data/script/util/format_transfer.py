from typing import Dict, List, Optional
from xml.dom import minidom

from .config_unit import ConfigUnit


class FormatTransfer:
    """A class for parsing and converting between different configuration file formats."""

    def __init__(
        self, 
        input_format: Optional[str] = None, 
        target_format: Optional[str] = None, 
        content: str = ""
    ) -> None:
        """Initialize FormatTransfer.
        
        Args:
            input_format: The input configuration format ('xml' or 'kv')
            target_format: The target configuration format ('xml' or 'kv') 
            content: The configuration content to parse/convert
        """
        self.input_format = input_format
        self.target_format = target_format
        self.content = content
        self.config_bank: List[ConfigUnit] = []

    def xml_parser(self, input_str: str) -> None:
        """Parse XML format configuration into ConfigUnit objects.
        
        Args:
            input_str: XML string to parse
            
        Raises:
            Exception: If required elements are missing or duplicated
        """
        dom = minidom.parseString(input_str)
        root = dom.documentElement
        property_list = root.getElementsByTagName("property")

        for prop in property_list:
            cur_config_unit = ConfigUnit()
            self._process_elements("name", cur_config_unit.set_name, prop)
            self._process_elements("value", cur_config_unit.set_value, prop)
            self._process_elements("description", cur_config_unit.set_description, prop)
            self.config_bank.append(cur_config_unit)

    def _process_elements(self, tag_name: str, setter, parent_element) -> None:
        """Process XML elements and set ConfigUnit values.
        
        Args:
            tag_name: Name of XML tag to process
            setter: ConfigUnit setter method to call
            parent_element: Parent XML element
            
        Raises:
            Exception: If required elements are missing or duplicated
        """
        elements = parent_element.getElementsByTagName(tag_name)
        if tag_name in ["name", "value"] and not elements:
            raise Exception(f"No {tag_name} element in property")
        if len(elements) > 1:
            raise Exception(f"More than one {tag_name} element in property")
        elif len(elements) == 1 and elements[0].firstChild is not None:
            setter(elements[0].firstChild.data)

    def kv_parser(self, input_str: str) -> None:
        """Parse key-value format configuration into ConfigUnit objects.
        
        Args:
            input_str: Key-value string to parse
            
        Raises:
            Exception: If line cannot be parsed as key-value pair
        """
        lines = input_str.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
                
            if "=" in line or ": " in line:
                cur_config_unit = ConfigUnit()
                try:
                    if "=" in line:
                        name, value = line.split("=", 1)
                    else:
                        name, value = line.split(": ", 1)
                except ValueError:
                    raise Exception("Invalid format: unable to parse key-value pair")
                    
                cur_config_unit.set_name(name.strip())
                cur_config_unit.set_value(value.strip())
                
                # Parse description from following lines
                description = []
                i += 1
                while i < len(lines) and lines[i].strip():
                    desc_line = lines[i].strip()
                    if desc_line.startswith("Description: "):
                        desc_line = desc_line[len("Description: "):]
                    description.append(desc_line)
                    i += 1
                    
                if description:
                    cur_config_unit.set_description("\n".join(description))
                self.config_bank.append(cur_config_unit)
            i += 1

    def xml_generator(self, config_bank: Optional[List[ConfigUnit]] = None) -> str:
        """Generate XML format configuration string.
        
        Args:
            config_bank: Optional list of ConfigUnit objects to use instead of self.config_bank
            
        Returns:
            XML format configuration string
        """
        if config_bank is None:
            config_bank = self.config_bank
            
        lines = [
            '<?xml version="1.0"?>',
            '<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>',
            "",
            "<configuration>",
            ""
        ]
        
        for config_unit in config_bank:
            lines.extend([
                "\t<property>",
                f"\t\t<name>{config_unit.get_name()}</name>",
                f"\t\t<value>{config_unit.get_value()}</value>"
            ])
            if config_unit.get_description():
                lines.append(f"\t\t<description>{config_unit.get_description()}</description>")
            lines.extend(["\t</property>", ""])
            
        lines.append("</configuration>")
        return "\n".join(lines)

    def kv_generator(self, config_bank: Optional[List[ConfigUnit]] = None) -> str:
        """Generate key-value format configuration string.
        
        Args:
            config_bank: Optional list of ConfigUnit objects to use instead of self.config_bank
            
        Returns:
            Key-value format configuration string
        """
        if config_bank is None:
            config_bank = self.config_bank
            
        lines = []
        for config_unit in config_bank:
            lines.append(f"{config_unit.get_name()}={config_unit.get_value()}")
            if config_unit.get_description():
                lines.extend([f"Description: {config_unit.get_description()}", ""])
            else:
                lines.append("")
        return "\n".join(lines)

    def transfer(self) -> str:
        """Convert between configuration formats.
        
        Returns:
            Converted configuration string
            
        Raises:
            Exception: If input/target format combination is not supported
        """
        if self.input_format == "xml" and self.target_format == "kv":
            return self.xml2kv()
        elif self.input_format == "kv" and self.target_format == "xml":
            return self.kv2xml()
        raise Exception("Unsupported input format or target format.")

    def xml2kv(self) -> str:
        """Convert XML format to key-value format.
        
        Returns:
            Key-value format configuration string
        """
        self.xml_parser(self.content)
        return self.kv_generator()

    def kv2xml(self) -> str:
        """Convert key-value format to XML format.
        
        Returns:
            XML format configuration string
        """
        self.kv_parser(self.content)
        return self.xml_generator()
