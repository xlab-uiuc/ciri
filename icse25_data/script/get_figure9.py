import os
from pathlib import Path
from typing import Dict, List, Optional

from util.format_transfer import FormatTransfer

SCRIPT_PATH = Path(__file__).parent.absolute()
GHIT_PATH = SCRIPT_PATH.parent / "g_hits"
DATASET_PATH = SCRIPT_PATH.parent / "datasets" / "synthesize_config"
RESULTS_PATH = SCRIPT_PATH.parent / "results" / "synthesize_config"

def get_result(file_path: str) -> List[str]:
    """Get the validation result from a file.
    
    Args:
        file_path: Path to the result file
        
    Returns:
        List of parameter names identified as problematic, or empty list if valid
    """
    with open(file_path) as file:
        file_content = file.readlines()
        
    for i, line in enumerate(file_content):
        if "Final result:" in line:
            result_line = file_content[i + 2].strip()
            if result_line == "The CONFIGURATION FILE IS CORRECT":
                return []
            try:
                return result_line.split("in the input: ")[1].split("\t")
            except IndexError:
                print(f"Error parsing result in {file_path}")
                return []
    return []

def get_ser(param: str, project: str) -> int:
    """Get the search engine ranking for a parameter.
    
    Args:
        param: Parameter name
        project: Project name
        
    Returns:
        Search engine ranking score
        
    Raises:
        ValueError: If parameter not found
    """
    ghit_file = GHIT_PATH / f"{project}.tsv"
    with open(ghit_file) as f:
        for line in f:
            cur_param, cur_ser = line.strip().split("\t")
            if cur_param == param:
                return int(cur_ser) if cur_ser != "None" else 0
    raise ValueError(f"Cannot find SER of {param}")

def parse_dataset_file(dataset_path: str, project: str) -> List[str]:
    """Parse configuration parameters from a dataset file.
    
    Args:
        dataset_path: Path to dataset file
        project: Project name
        
    Returns:
        List of parameter names
    """
    file_content = Path(dataset_path).read_text()
    ft = FormatTransfer()
    
    if project in ["hcommon", "hbase", "hdfs", "yarn"]:
        file_content = file_content.replace("&", "&amp;")
        ft.xml_parser(file_content)
    elif project in ["alluxio", "zookeeper", "redis", "etcd", "postgresql", "django"]:
        ft.kv_parser(file_content)
        
    return [cu.get_name() for cu in ft.config_bank]

def parse_folder(output_path: str, dataset_path: str, project: str) -> Dict[int, float]:
    """Parse a folder of output files and calculate rank-based metrics.
    
    Args:
        output_path: Path to folder containing model output files
        dataset_path: Path to folder containing original dataset files
        project: Name of the project being analyzed
        
    Returns:
        Dictionary mapping ranks to weighted scores
        
    Raises:
        ValueError: If output_path is not a valid directory
    """
    if not Path(output_path).is_dir():
        raise ValueError(f"{output_path} is not a valid folder")
        
    rank_mapping: Dict[int, float] = {}
    
    for file in os.listdir(output_path):
        output_file = Path(output_path) / file
        dataset_file = Path(dataset_path) / file
        
        results = get_result(str(output_file))
        if not results:
            continue
            
        param_list = parse_dataset_file(str(dataset_file), project)
        param_list.sort(key=lambda x: get_ser(x, project), reverse=True)
        
        ranks = []
        for result in results:
            if result in param_list:
                rank = param_list.index(result) + 1
                ranks.append(rank)
                
        if not ranks:
            continue
            
        weight = 1 / len(ranks)
        for rank in ranks:
            rank_mapping[rank] = rank_mapping.get(rank, 0) + weight
            
    return rank_mapping

def main() -> None:
    """Main function to process results for all models and projects."""
    models = [
        "claude-3-opus-20240229", "claude-3-sonnet-20240229", 
        "CodeLLaMa-7b-Instruct-hf", "CodeLLaMa-13b-Instruct-hf", "CodeLLaMa-34b-Instruct-hf",
        "deepseek-coder-6.7b-instruct", "gpt-3.5-turbo-0125", "gpt-4-0125-preview"
    ]
    
    projects = [
        "hcommon", "hbase", "alluxio", "hdfs", "yarn",
        "zookeeper", "redis", "etcd", "postgresql", "django"
    ]

    for model in models:
        model_mapping: Dict[int, float] = {}
        
        for project in projects:
            dataset_path = DATASET_PATH / project / "correct"
            output_path = RESULTS_PATH / project / model / "default" / "correct"
            
            try:
                mapping = parse_folder(str(output_path), str(dataset_path), project)
                for rank, weight in mapping.items():
                    model_mapping[rank] = model_mapping.get(rank, 0) + weight
            except Exception as e:
                print(f"Error processing {project} with {model}: {str(e)}")
                continue

        print("#########################")
        print(f"Results for {model}:")
        for rank, weight in sorted(model_mapping.items()):
            print(f"Rank {rank}: {weight:.2f}")

if __name__ == "__main__":
    main()
