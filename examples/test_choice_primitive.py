import json
import torch
import warnings
import sys
import time
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Now use an absolute import
from src.parser import parse_decision_response
from src.engine import DecisionModelEngine
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")


# Function to generate TEST_QUESTIONS focused strictly on the route primitive
def build_route_question(instruction_text: str) -> dict:
    return {
        "route": {
            "type": "choice",
            "instructions": instruction_text,
            "criteria": {
                "returns": "Refunds, replacements and damaged deliveries",
                "billing": "Payments, invoices and charges",
                "technical": "Product setup and faults"
            }
        }
    }


# List of 10 instruction prompt variations to test routing sensitivity
ROUTE_INSTRUCTIONS = [
    "Which team should handle this request?",
    "Identify the appropriate department for this customer issue.",
    "Categorize this support ticket based on customer intent.",
    "Route this message to returns, billing, or technical support.",
    "Select the best handling team for this situation.",
    "Determine which customer service group needs to act.",
    "Classify the core issue into one of the designated support queues.",
    "Assign this ticket to the team responsible for resolving it.",
    "Which operational division should address this customer complaint?",
    "Where should this ticket be escalated?"
]


def main():
    engine = DecisionModelEngine()

    # Fixed test customer state
    sample_state = (
        "The package arrived with a smashed screen yesterday. "
        "I attached the receipt and need a replacement sent today."
    )
    print(sample_state)

    print(f"\nEvaluating state: \"{sample_state}\"\n")
    print("Running 10 instruction variations through system_one...\n" + "="*70)

    for idx, instruction in enumerate(ROUTE_INSTRUCTIONS, start=1):
        # Build updated questions dict focusing on route
        test_questions_route_focus = build_route_question(instruction)
        print(test_questions_route_focus)
        start_time = time.perf_counter()
        
        # Pass state and updated route questions into the System One model
        raw_response = engine(sample_state, test_questions_route_focus)
        print(raw_response)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # answers = raw_response.get("answers", {})
        # route_result = answers.get("route", {})

        # selected_answer = route_result.get("answer", "N/A")
        # probability = route_result.get("probability", 0.0)

        # print(f"Run #{idx:02d} | Time: {elapsed_ms:.2f} ms")
        # print(f"Instruction : \"{instruction}\"")
        # print(f"Prediction  : {selected_answer} (Confidence: {probability:.4f})")
        print("======" * 70)


if __name__ == "__main__":
    main()

## RAW OUTPUTS
# {'model': 'Decision-2.0-Eos-0.8B',
# 'answers':

#      {'route': 
#         {'type': 'choice',
#         'choice': 'returns', 
#         'probabilities': 
#             {'returns': 0.9864752897123424, 
#              'billing': 3.917361383555577e-05,
#             'technical': 0.013485536673822015}, 
#         'confidence': 0.9345529564406664}}, 
# 'usage': 
#         {'input_tokens': 124,
#             'output_tokens': 0}
# }