from typing import Dict, List, Optional
from pathlib import Path

from ciri.post_processing import selection
from ciri.query.llm_gen import GPTGen, ClaudeGen, LlamaGen, DeepseekGen
from ciri.ciri_logger import logger
from ciri.post_processing.reason_cluster import get_dominant_reason


def ciri_runner(args: Dict, file_content: str, output_path: str, model, tokenizer) -> None:
    """
    Run the Ciri analysis pipeline on the input file.
    
    Args:
        args: Dictionary of command line arguments
        file_content: Content of the file to analyze
        output_path: Path to write output logs
        model: The language model to use
        tokenizer: The tokenizer for the model
    """
    # Initialize appropriate LLM generator based on model type
    llm_gen = _get_llm_generator(args, file_content, model, tokenizer)

    # Run analysis until agreement is reached
    result, reasons = _run_analysis(llm_gen)
    
    # Log and print results
    _output_results(result, reasons, output_path)


def _get_llm_generator(args: Dict, file_content: str, model, tokenizer):
    """Create appropriate LLM generator based on model type."""
    if args.model in ["gpt-3.5-turbo-0125", "gpt-4-0125-preview"]:
        return GPTGen(args, file_content)
    elif args.model.startswith("claude"):
        return ClaudeGen(args, file_content)
    elif args.model.startswith("CodeLLaMa"):
        return LlamaGen(args, file_content, model, tokenizer)
    elif args.model.startswith("deepseek"):
        return DeepseekGen(args, file_content, model, tokenizer)
    else:
        raise ValueError(f"Model {args.model} is not supported")


def _run_analysis(llm_gen) -> tuple[str, Optional[dict[str, str]]]:
    """Run the analysis until agreement is reached."""
    while True:
        answer_parser = llm_gen.generate()
        selection_gen = selection.Selection()
        pure_result = selection_gen.select(answer_parser.candidate_pool.pool)

        if len(pure_result) > 1:
            return "NO CONSISTENT RESULT", None
            
        if pure_result[0] == ["None"]:
            return "The CONFIGURATION FILE IS CORRECT", None
            
        # Get reasons for each misconfiguration
        reasons = {}
        raw_answers = answer_parser.answer_pool.pool
        for param in pure_result[0]:
            reason_list = [
                answer["reason"][answer["errParameter"].index(param)]
                for answer in raw_answers
                if set(answer["errParameter"]) == set(pure_result[0])
            ]
            reasons[param] = get_dominant_reason(reason_list)
            
        result = (
            f"There are {len(pure_result[0])} misconfiguration parameters in the input: "
            + "\t".join(pure_result[0])
        )
        return result, reasons


def _output_results(result: str, reasons: Optional[dict[str, str]], output_path: str, verbose: bool = False) -> None:
    """Log and print the analysis results."""
    if verbose:
        logger.info("Final result:\n")
        logger.info(result)
        
    print(f"[Ciri] Start")
    print(f"[Ciri] Running for file {output_path}")
    print(f"[Ciri] Result: {result}")
    
    if reasons:
        for param, reason in reasons.items():
            message = f"[Ciri] Reason for {param}: {reason}"
            print(message)
            if verbose:
                logger.info(message)
            
    print(f"[Ciri] Writing log file to {output_path}")
    print("[Ciri] End")
