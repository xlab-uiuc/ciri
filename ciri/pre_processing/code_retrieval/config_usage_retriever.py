import os
from pathlib import Path
from typing import Optional, List
from ciri.pre_processing.code_retrieval.code_crawler import CodeCrawler


class ConfigUsageRetriever:
	"""Retrieves and caches configuration parameter usage from code."""

	def __init__(self, system: str, read_code_loc: str, config_format: str, language: str) -> None:
		"""
		Initialize the config usage retriever.

		Args:
			system: Name of the system being analyzed
			read_code_loc: Location of code to search for config usage
			config_format: Format of config files ('xml' or 'kv')
			language: Programming language to search in
		"""
		if config_format not in ["xml", "kv"]:
			raise ValueError(f"Unsupported config format: {config_format}")

		self.system = system
		self.read_code_loc = read_code_loc
		self.config_format = config_format
		self.language = language
		self.cur_path = Path(os.path.dirname(os.path.abspath(__file__)))
		self.code_crawler = CodeCrawler(read_code_loc, language)

	def get_usage(self, param: str) -> Optional[str]:
		"""
		Get usage of a config parameter from cache or code search.

		Args:
			param: Configuration parameter to look up

		Returns:
			Usage string if found, None otherwise
		"""
		cache_file = self.cur_path / ".cache" / self.system / param
		if cache_file.exists():
			if cache_file.stat().st_size == 0:
				return None
			return cache_file.read_text().strip()
		return None

	def _extract_param_from_xml(self, line: str) -> Optional[str]:
		"""Extract parameter name from XML line."""
		if "<name>" not in line or "</name>" not in line:
			return None
		return line.split("<name>")[1].split("</name>")[0]

	def _extract_param_from_kv(self, line: str) -> Optional[str]:
		"""Extract parameter name from key-value line."""
		line = line.strip()
		if "=" in line:
			return line.split("=")[0]
		if ": " in line:
			return line.split(": ")[0]
		return None

	def generate(self, content: str) -> str:
		"""
		Generate output with usage information added.

		Args:
			content: Original configuration content

		Returns:
			Configuration content with usage information added
		"""
		lines = content.splitlines()
		output_lines: List[str] = []
		usage: Optional[str] = None

		if self.config_format == "xml":
			for line in lines:
				output_lines.append(line)
				if "<name" in line:
					param = self._extract_param_from_xml(line)
					if param:
						usage = self.get_usage(param)
				elif "<value" in line and usage and "final" not in usage:
					output_lines.append(f"  <usage>{usage}</usage>")

		elif self.config_format == "kv":
			for line in lines:
				output_lines.append(line)
				param = self._extract_param_from_kv(line)
				if param:
					usage = self.get_usage(param)
					if usage:
						output_lines.append(f"# Usage: {usage}")

		return "\n".join(output_lines)
