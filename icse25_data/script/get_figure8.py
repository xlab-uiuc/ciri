import math
import os
from pathlib import Path
from typing import List, Tuple, Dict, Optional

SCRIPT_PATH = Path(__file__).parent.absolute()
GHIT_PATH = SCRIPT_PATH.parent / "g_hits" 
DATASET_PATH = SCRIPT_PATH.parent / "datasets" / "synthesize_config"
RESULTS_PATH = SCRIPT_PATH.parent / "results" / "synthesize_config"
GROUND_TRUTH_PATH = SCRIPT_PATH.parent / "datasets" / "synthesize_config" / "ground_truth"

def get_result(file_path: str) -> List[str]:
    """Get the validation result from a file.
    
    Args:
        file_path: Path to the result file
        
    Returns:
        List of parameter names identified as problematic, or empty list if valid
    """
    try:
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
    except FileNotFoundError:
        print(f"Could not find file: {file_path}")
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
    return []

def get_ser(param: str, project: str) -> int:
    """Get the search engine ranking for a parameter.
    
    Args:
        param: Parameter name
        project: Project name
        
    Returns:
        Search engine ranking score (0 if None)
        
    Raises:
        FileNotFoundError: If SER file not found
        ValueError: If parameter not found in file
    """
    ghit_file = GHIT_PATH / f"{project}.tsv"
    try:
        with open(ghit_file) as f:
            for line in f:
                cur_param, cur_ser = line.strip().split("\t")
                if cur_param == param:
                    return int(cur_ser) if cur_ser != "None" else 0
    except FileNotFoundError:
        print(f"Could not find SER file for project {project}")
        raise
    return 0

def parse_folder(path: str, refer: str, project: str) -> Tuple[List[int], List[int]]:
    """Parse results folder and calculate SER scores.
    
    Args:
        path: Path to results folder
        refer: Path to reference file
        project: Project name
        
    Returns:
        Tuple of (correct_ser_list, wrong_ser_list) containing SER scores
    """
    try:
        with open(refer) as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Reference file not found: {refer}")
        return [], []
        
    correct_ser_list = []
    wrong_ser_list = []
    
    for i, line in enumerate(lines, 1):
        row = line.strip().split("\t")
        cat, sub_cat = row[0:2]
        success = False
        
        result = get_result(os.path.join(path, str(i)))
        
        if result:
            if sub_cat == "Value Relationship":
                param1, param2 = row[2], row[4]
                ser = (get_ser(param1, project) + get_ser(param2, project)) / 2
                success = (len(result) == 2 and param1 in result and param2 in result) or \
                         (len(result) == 1 and (param1 in result or param2 in result))
            else:
                param = row[2]
                ser = get_ser(param, project)
                success = len(result) == 1 and result[0] == param
        else:
            param = row[2]
            ser = get_ser(param, project)
            
        (correct_ser_list if success else wrong_ser_list).append(ser)
    correct_ser_list = [math.log10(x) / math.log10(100) for x in correct_ser_list if x != 0]
    wrong_ser_list = [math.log10(x) / math.log10(100) for x in wrong_ser_list if x != 0]
    return correct_ser_list, wrong_ser_list

def calculate_average(values: List[float]) -> Optional[float]:
    """Calculate average of a list of values.
    
    Args:
        values: List of numeric values
        
    Returns:
        Average value or None if list is empty
    """
    return sum(values) / len(values) if values else None

def main() -> None:
    """Process and analyze search engine ranking results for all projects and models."""
    projects = [
        "hcommon", "hbase", "alluxio", "hdfs", "yarn",
        "zookeeper", "redis", "etcd", "postgresql", "django"
    ]
    
    models = [
        "claude-3-opus-20240229", "claude-3-sonnet-20240229", 
        "CodeLLaMa-7b-Instruct-hf", "CodeLLaMa-13b-Instruct-hf", "CodeLLaMa-34b-Instruct-hf",
        "deepseek-coder-6.7b-instruct", "gpt-3.5-turbo-0125", "gpt-4-0125-preview"
    ]

    for model in models:
        correct_ser_total = []
        wrong_ser_total = []
        
        for project in projects:
            refer = GROUND_TRUTH_PATH / f"{project}.tsv"
            output_path = RESULTS_PATH / project / model / "default" / "erroneous"
            
            correct_ser_list, wrong_ser_list = parse_folder(str(output_path), str(refer), project)
            correct_ser_total.extend(correct_ser_list)
            wrong_ser_total.extend(wrong_ser_list)
            
            avg_correct = calculate_average(correct_ser_list)
            avg_wrong = calculate_average(wrong_ser_list)
            
            # if avg_correct is not None and avg_wrong is not None:
            #     print(f"{model} {project} correct: {avg_correct:.2f}")
            #     print(f"{model} {project} wrong: {avg_wrong:.2f}")
            # else:
            #     print(f"No results found for {model} {project}")
        
        avg_correct_total = calculate_average(correct_ser_total)
        avg_wrong_total = calculate_average(wrong_ser_total)
        
        print(f"\n{model} overall:")
        if avg_correct_total is not None and avg_wrong_total is not None:
            print(f"Correct: {avg_correct_total:.2f}")
            print(f"Wrong: {avg_wrong_total:.2f}\n")
        else:
            print(f"No overall results found for {project}\n")

if __name__ == "__main__":
    main()
