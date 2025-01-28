import subprocess
from typing import Optional, Dict


class CodeCrawler:
	"""A class to retrieve code snippets containing configuration parameters from a code repository."""

	# Map of supported languages to their file extensions
	LANGUAGE_TO_EXTENSION: Dict[str, str] = {
		"java": "java",
		"go": "go", 
		"c": "c"
	}

	def __init__(self, repo_loc: str, language: str) -> None:
		"""
		Initialize the code retriever.

		Args:
			repo_loc: Path to the code repository
			language: Programming language to search for ('java', 'go', or 'c')
		"""
		if language not in self.LANGUAGE_TO_EXTENSION:
			raise ValueError(f"Unsupported language: {language}")
		self.repo_loc = repo_loc
		self.language = language

	def retrieve_code(self, param: str) -> Optional[str]:
		"""
		Search repository for code containing the given parameter.

		Args:
			param: Configuration parameter to search for

		Returns:
			The longest line containing the parameter, or None if not found
		"""
		extension = self.LANGUAGE_TO_EXTENSION[self.language]
		command = [
			"grep",
			"-rh",
			f"--include=*.{extension}",
			f'"{param}"',
			self.repo_loc
		]

		try:
			output = subprocess.run(
				command,
				capture_output=True,
				text=True,
				check=True
			).stdout
		except subprocess.CalledProcessError:
			return None

		lines = [line.strip() for line in output.splitlines() if line.strip()]
		return max(lines, key=len) if lines else None
