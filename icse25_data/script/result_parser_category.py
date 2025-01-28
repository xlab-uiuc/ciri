import argparse
import os
from typing import List, Optional, Tuple, Dict, Any

from result_parser import compute_metrics, format_number, get_result

# Global constants
PRINT_TO_CONSOLE = False
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
GROUND_TRUTH_PATH = os.path.join(SCRIPT_PATH, "..", "datasets", "synthesize_config", "ground_truth")
RESULTS_PATH = os.path.join(SCRIPT_PATH, "..", "results", "synthesize_config")

subcategories = [
    "Syntax:Data Type", "Syntax:Path", "Syntax:URL", "Syntax:IP Address",
    "Syntax:Port", "Syntax:Permission", "Range:Basic Numeric", "Range:Bool", 
    "Range:Enum", "Range:IP Address", "Range:Port", "Range:Permission",
    "Dependency:Control", "Dependency:Value Relationship", "Version:Parameter Change"
]

def get_metrics_by_subcat(project: str, model: str, subcat_full: str) -> None:
    """
    Get metrics by subcat
    """
    ground_truth_file = os.path.join(GROUND_TRUTH_PATH, f"{project}.tsv")
    metrics = {"p_tp": 0, "p_fp": 0, "p_tn": 0, "p_fn": 0}
    # print(f"Processing {subcat_full} for {project} with {model}")
    if subcat_full == "Syntax:IP Address":
        import pdb; pdb.set_trace()
    try:
        with open(ground_truth_file, "r") as file:
            lines = file.readlines()
            
        for i, line in enumerate(lines, 1):
            result = get_result(os.path.join(RESULTS_PATH, project, model, "default", "erroneous", f"{i}"))
            parts = line.strip().split("\t")
            cat, sub_cat = parts[0], parts[1]

            if f"{cat}:{sub_cat}" != subcat_full:
                continue
            # print(f"Line: {line}")
            if sub_cat == "Value Relationship":
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

        precision, recall, accuracy, f1 = compute_metrics(
            metrics["p_tp"], metrics["p_fp"], metrics["p_tn"], metrics["p_fn"]
        )
        print(f"{subcat_full}: {format_number(f1)}")
    except Exception as e:
        print(f"Error processing {subcat_full}: {e}")


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

    args = parser.parse_args()
    
    for subcat_full in subcategories:
        get_metrics_by_subcat(args.project, args.model, subcat_full)

if __name__ == "__main__":
    main()
