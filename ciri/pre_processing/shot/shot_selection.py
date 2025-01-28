import os
import random
from pathlib import Path
from typing import Dict, List, Optional, Callable
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from ciri.ciri_logger import logger


class ShotSelection:
    """
    Handles shot selection for configuration validation using various methods.
    
    Supports multiple selection strategies including random, category-based,
    and similarity-based.
    
    Attributes:
        system: The system to select shots from
        selection_method: Method to use for shot selection ('random', 'category', or 'similarity')
        validconfig_shot_num: Number of valid configuration shots to select
        misconfig_shot_num: Number of misconfiguration shots to select
        input_file_content: Content of the input configuration file
    """

    def __init__(
        self,
        args: Dict,
        input_file_content: str,
    ) -> None:
        """
        Initialize the shot selection system.
        
        Args:
            args: Dictionary containing configuration arguments
            input_file_content: Content of the input configuration file
        """
        self.system = args.shot_system if args.shot_system else args.system
        self.selection_method = args.shot_selection
        self.validconfig_shot_num = args.validconfig_shot_num
        self.misconfig_shot_num = args.misconfig_shot_num
        self.input_file_content = input_file_content

        self._init_paths()
        self._init_selection_methods()
        self.shot_category = self._init_shot_categories()

    def _init_paths(self) -> None:
        """Initialize paths for shot pool and validate they exist."""
        self.cur_file_path = os.path.dirname(os.path.abspath(__file__))
        self.shot_pool_path = Path(self.cur_file_path, "shot_pool", self.system)
        self.validconfig_path = Path(self.shot_pool_path, "ValidConfig")
        self.misconfig_path = Path(self.shot_pool_path, "Misconfig")

        if not self.validconfig_path.exists() or not self.misconfig_path.exists():
            raise FileNotFoundError(f"Shot pool directories not found at {self.shot_pool_path}")

        self.total_validconfig_shot_num = len(list(self.validconfig_path.glob("*")))
        self.total_misconfig_shot_num = len(list(self.misconfig_path.glob("*")))

    def _init_selection_methods(self) -> None:
        """Initialize mapping of selection method names to their implementation functions."""
        self.selection_methods: Dict[str, Callable[[], List[int]]] = {
            "random": self._random_shot_selection,
            "category": self._diff_category_selection,
            "similarity": self._similarity_selection
        }

    def _init_shot_categories(self) -> Dict[str, List[int]]:
        """
        Initialize the mapping of systems to their shot categories.
        
        Returns:
            Dictionary mapping category names to lists of shot numbers
        """
        categories: Dict[str, List[int]] = {}
        for file_path in self.misconfig_path.glob("*"):
            try:
                number_str, category = file_path.name.split('_', 1)
                number = int(number_str)
                categories.setdefault(category, []).append(number)
            except ValueError:
                logger.warning(f"Skipping malformed filename: {file_path.name}")
                continue
        
        return {category: sorted(shots) for category, shots in categories.items()}

    def select(self) -> str:
        """
        Select shots based on the configured selection method.
        
        Returns:
            String containing the concatenated content of all selected shots
        """
        shot_content = []

        if self.misconfig_shot_num:
            selection_func = self.selection_methods.get(self.selection_method)
            if not selection_func:
                raise ValueError(f"Invalid shot selection method: {self.selection_method}")
            shot_list = selection_func()
            shot_content.append(self._get_shot_content("Misconfig", shot_list))
            logger.info(f"Selected misconfiguration shots: {shot_list}")

        if self.validconfig_shot_num:
            shot_list = self._correct_shot_selection()
            shot_content.append(self._get_shot_content("ValidConfig", shot_list))
            logger.info(f"Selected valid configuration shots: {shot_list}")
            
        shot_content_str = "\n".join(shot_content) + "\n"
        logger.debug(f"[Ciri] Complete shot content:\n{shot_content_str}")
        return shot_content_str

    def _get_shot_content(self, shot_type: str, shot_list: List[int]) -> str:
        """
        Retrieve shot content based on the shot type and shot numbers.
        
        Args:
            shot_type: Type of shots to retrieve ('Misconfig' or 'ValidConfig')
            shot_list: List of shot numbers to retrieve
            
        Returns:
            String containing concatenated content of all found shots
        """
        def _get_shot_filename(shot_num: int) -> Optional[str]:
            base_path = self.misconfig_path if shot_type == "Misconfig" else self.validconfig_path
            
            for file_path in base_path.glob("*"):
                try:
                    if shot_type == "Misconfig":
                        number = int(file_path.stem.split('_')[0])
                    else:
                        number = int(file_path.name)
                    if number == shot_num:
                        return file_path.name
                except ValueError:
                    logger.warning(f"Skipping malformed filename: {file_path.name}")
                    continue
            return None

        shot_contents = []
        for shot in shot_list:
            filename = _get_shot_filename(shot)
            if not filename:
                logger.warning(f"Could not find file for {shot_type} shot number {shot}")
                continue
                
            file_path = (self.misconfig_path if shot_type == "Misconfig" else self.validconfig_path) / filename
            try:
                content = file_path.read_text()
                shot_contents.append(content)
            except Exception as e:
                logger.error(f"Error reading shot file {filename}: {str(e)}")
                continue

        return "\n".join(shot_contents)

    def _random_shot_selection(self) -> List[int]:
        """
        Select random shot numbers.
        
        Returns:
            List of randomly selected shot numbers
        """
        return random.sample(range(1, self.total_misconfig_shot_num + 1), self.misconfig_shot_num)

    def _diff_category_selection(self) -> List[int]:
        """
        Select shots from different categories.
        
        Returns:
            List of selected shot numbers, one from each category
            
        Raises:
            ValueError: If requested number of shots exceeds available categories
        """
        if self.misconfig_shot_num > len(self.shot_category):
            raise ValueError("Number of requested shots exceeds number of available categories")

        selected_categories = random.sample(list(self.shot_category.keys()), self.misconfig_shot_num)
        return [random.choice(self.shot_category[category]) for category in selected_categories]

    def _similarity_selection(self) -> List[int]:
        """
        Select shots based on their similarity to the input content.
        
        Returns:
            List of shot numbers ordered by similarity to input
        """
        shot_file_content = [
            Path(file_path).read_text()
            for file_path in self.misconfig_path.glob("*")
        ]
        count_vectorizer = CountVectorizer(stop_words="english")
        count_matrix = count_vectorizer.fit_transform(
            [self.input_file_content] + shot_file_content
        )
        similarity = cosine_similarity(count_matrix[0:1], count_matrix[1:])
        similar_shots = list(similarity.argsort()[0][::-1][:self.misconfig_shot_num] + 1)
        similar_shots.reverse()
        random.shuffle(similar_shots)
        return similar_shots

    def _correct_shot_selection(self) -> List[int]:
        """
        Select valid configuration shots randomly.
        
        Returns:
            List of randomly selected valid configuration shot numbers
        """
        return random.sample(range(1, self.total_validconfig_shot_num + 1), self.validconfig_shot_num)
