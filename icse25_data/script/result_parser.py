import argparse
import os
from typing import List, Optional, Tuple, Dict, Any

# Global constants
PRINT_TO_CONSOLE = False
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
GROUND_TRUTH_PATH = os.path.join(SCRIPT_PATH, "..", "datasets", "synthesize_config", "ground_truth")
RESULTS_PATH = os.path.join(SCRIPT_PATH, "..", "results", "synthesize_config")

def print_func(message: str) -> None:
    """Print message to console if PRINT_TO_CONSOLE is True"""
    if PRINT_TO_CONSOLE:
        print(message)

def format_number(value: Optional[float]) -> str:
    """
    Format a float number with 2 decimal places or return 'N.A.' if None
    
    Args:
        value: Number to format
        
    Returns:
        Formatted string representation
    """
    if value is None:
        return "N.A."
    return f"{value:.2f}"

def compute_metrics(tp: int, fp: int, tn: int, fn: int) -> Tuple[Optional[float], Optional[float], float, Optional[float]]:
    """
    Compute classification metrics from confusion matrix values
    
    Args:
        tp: True positives
        fp: False positives 
        tn: True negatives
        fn: False negatives
        
    Returns:
        Tuple of (precision, recall, accuracy, f1)
    """
    total = tp + tn + fp + fn
    if total == 0:
        return None, None, 0.0, None
        
    precision = tp / (tp + fp) if tp + fp > 0 else None
    recall = tp / (tp + fn) if tp + fn > 0 else None
    accuracy = (tp + tn) / total
    
    if tp == 0 or precision is None or recall is None:
        f1 = None
    else:
        f1 = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else None
        
    return precision, recall, accuracy, f1

def get_result(file_path: str) -> List[str]:
    """
    Extract result parameters from a result file
    
    Args:
        file_path: Path to result file
        
    Returns:
        List of parameter names from result, or empty list if correct
    """
    try:
        with open(file_path, "r") as file:
            file_content = file.readlines()
            
        for i, line in enumerate(file_content):
            if "Final result:" in line and i + 2 < len(file_content):
                result_line = file_content[i + 2].strip()
                if result_line == "The CONFIGURATION FILE IS CORRECT":
                    return []
                return result_line.split("in the input: ")[1].split("\t")
                
        return []
        
    except Exception as e:
        print(f"Error parsing result in {file_path}: {str(e)}")
        return []

def parse_error_folder(path: str, project: str, mis_type: Optional[str] = None) -> Tuple[int, int, int, int, int, int]:
    """
    Parse error folder to compute confusion matrix values
    
    Args:
        path: Path to error folder
        project: Project name
        mis_type: Optional misconfiguration type filter
        
    Returns:
        Tuple of (file_tp, file_fn, param_tp, param_fp, param_tn, param_fn)
    """
    metrics = {"f_tp": 0, "f_fn": 0, "p_tp": 0, "p_fp": 0, "p_tn": 0, "p_fn": 0}
    ground_truth_file = os.path.join(GROUND_TRUTH_PATH, f"{project}.tsv")
    
    try:
        with open(ground_truth_file, "r") as file:
            lines = file.readlines()
            
        for i, line in enumerate(lines, 1):
            result = get_result(os.path.join(path, f"{i}"))
            parts = line.strip().split("\t")
            sub_category = parts[1]
            
            if mis_type is not None and sub_category != mis_type:
                continue
                
            # File level metrics
            if not result:
                metrics["f_fn"] += 1
            else:
                metrics["f_tp"] += 1
                
            # Parameter level metrics
            if sub_category == "Value Relationship":
                param1, param2 = parts[2], parts[4]
                params_found = sum(p in result for p in (param1, param2))
                
                metrics["p_tp"] += params_found
                metrics["p_fp"] += len(result) - params_found
                metrics["p_tn"] += 8 - len(result)
                metrics["p_fn"] += (2 - params_found)
            else:
                param = parts[2]
                if param in result:
                    metrics["p_tp"] += 1
                    metrics["p_fp"] += len(result) - 1
                    metrics["p_tn"] += 8 - len(result)
                else:
                    metrics["p_fp"] += len(result)
                    metrics["p_tn"] += 7 - len(result)
                    metrics["p_fn"] += 1
                    
        return (metrics["f_tp"], metrics["f_fn"], metrics["p_tp"], 
                metrics["p_fp"], metrics["p_tn"], metrics["p_fn"])
                
    except Exception as e:
        print(f"Error parsing error folder: {str(e)}")
        return (0, 0, 0, 0, 0, 0)

def parse_correct_folder(path: str, project: str) -> Tuple[int, int, int, int]:
    """
    Parse correct folder to compute confusion matrix values
    
    Args:
        path: Path to correct folder
        project: Project name
        
    Returns:
        Tuple of (file_fp, file_tn, param_fp, param_tn)
    """
    metrics = {"f_tn": 0, "f_fp": 0, "p_fp": 0, "p_tn": 0}
    ground_truth_file = os.path.join(GROUND_TRUTH_PATH, f"{project}.tsv")
    
    try:
        with open(ground_truth_file, "r") as file:
            lines = file.readlines()
            
        for i, line in enumerate(lines, 1):
            file_path = os.path.join(path, f"{i}")
            if not os.path.exists(file_path):
                print(f"Warning: File {file_path} does not exist.")
                continue
                
            result = get_result(file_path)
            if not result:
                metrics["f_tn"] += 1
            else:
                metrics["f_fp"] += 1
                
            metrics["p_fp"] += len(result)
            metrics["p_tn"] += 8 - len(result)
            
        return (metrics["f_fp"], metrics["f_tn"], metrics["p_fp"], metrics["p_tn"])
        
    except Exception as e:
        print(f"Error parsing correct folder: {str(e)}")
        return (0, 0, 0, 0)

def parser_func(project: str, model: str, mode: str) -> Optional[Tuple[Optional[float], Optional[float], float, Optional[float], Optional[float], Optional[float], float, Optional[float]]]:
    """
    Parse results for a given experiment configuration
    
    Args:
        project: Project name
        model: Model name
        mode: Evaluation mode
        
    Returns:
        Tuple of metrics (file_precision, file_recall, file_accuracy, file_f1,
                         param_precision, param_recall, param_accuracy, param_f1)
        or None if directory does not exist
    """
    experiment_path = os.path.join(RESULTS_PATH, project, model, mode)
    if not os.path.exists(experiment_path):
        print(f"[Ciri Result] {project} {model} {mode}")
        print("The directory does not exist.")
        return None
        
    metrics = {"f_tp": 0, "f_fp": 0, "f_tn": 0, "f_fn": 0,
              "p_tp": 0, "p_fp": 0, "p_tn": 0, "p_fn": 0}
              
    # Process correct folder
    correct_path = os.path.join(experiment_path, "correct")
    if os.path.exists(correct_path):
        c_result = parse_correct_folder(correct_path, project)
        metrics["f_fp"] += c_result[0]
        metrics["f_tn"] += c_result[1]
        metrics["p_fp"] += c_result[2]
        metrics["p_tn"] += c_result[3]
    else:
        print(f"[Ciri Result] No correct folder found for {project}/{model}/{mode}")
        
    # Process error folder
    error_path = os.path.join(experiment_path, "erroneous")
    if os.path.exists(error_path):
        e_result = parse_error_folder(error_path, project)
        metrics["f_tp"] += e_result[0]
        metrics["f_fn"] += e_result[1]
        metrics["p_tp"] += e_result[2]
        metrics["p_fp"] += e_result[3]
        metrics["p_tn"] += e_result[4]
        metrics["p_fn"] += e_result[5]
    else:
        print(f"[Ciri Result] No erroneous folder found for {project}/{model}/{mode}")
        
    # Compute final metrics
    f_metrics = compute_metrics(metrics["f_tp"], metrics["f_fp"], 
                              metrics["f_tn"], metrics["f_fn"])
    p_metrics = compute_metrics(metrics["p_tp"], metrics["p_fp"],
                              metrics["p_tn"], metrics["p_fn"])
                              
    print_func(f"[Ciri Result] on {project} with {model} and {mode} mode")
    print_func(
        f"File-Level: Precision: {format_number(f_metrics[0])}, "
        f"Recall: {format_number(f_metrics[1])}, "
        f"Accuracy: {format_number(f_metrics[2])}, "
        f"F1: {format_number(f_metrics[3])}"
    )
    print_func(
        f"Param-Level: Precision: {format_number(p_metrics[0])}, "
        f"Recall: {format_number(p_metrics[1])}, "
        f"Accuracy: {format_number(p_metrics[2])}, "
        f"F1: {format_number(p_metrics[3])}"
    )
    
    return f_metrics + p_metrics

def main() -> None:
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="Parse and analyze configuration validation results"
    )
    parser.add_argument(
        "--project", 
        required=True,
        type=str,
        help="Project name"
    )
    parser.add_argument(
        "--model",
        required=True, 
        type=str,
        help="Model name"
    )
    parser.add_argument(
        "--mode",
        required=True,
        type=str, 
        help="Evaluation mode"
    )
    
    args = parser.parse_args()
    parser_func(args.project, args.model, args.mode)

if __name__ == "__main__":
    PRINT_TO_CONSOLE = True
    main()
