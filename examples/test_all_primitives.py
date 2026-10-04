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





#  Main Serving Function
def main():
    engine = DecisionModelEngine("vllm-sr/Decision-2.0-Eos-0.8B")

    # Construct the question dictionary for system_one mapping
    questions = {
        "route": {
            "type": "choice",
            "instructions": "Which agricultural intervention should be recommended for this farm?",
            "criteria": {
                "irrigation": "Water and irrigation support",
                "soil_health": "Soil fertility and nutrient management",
                "pest_control": "Crop protection and pest management"
            }
        },
        "receipt": {
            "type": "noul",
            "instructions": "Is there evidence of crop stress caused by water shortage?"
        },
        "urgency": {
            "type": "score",
            "instructions": "How urgent is the intervention needed for this farm?",
            "criteria": ["Routine", "Soon", "Immediate"]
        }
    }

    # Input state text
    input_text = "A maize farm in Kenya has yellowing leaves, dry soil, and wilting plants after two weeks without rain. The farmer needs guidance on the fastest practical field response."

    # Direct System One evaluation using the loaded model
    print("\n--- Running System One Model via Local Engine ---")
    raw_response = engine(input_text, questions)
    print(raw_response)
    print("\n--- Clean Output Answers ---")

    clean_output = parse_decision_response(raw_response)
    print(json.dumps(clean_output, indent=2))
    # print(json.dumps(raw_response["answers"], indent=2))


if __name__ == "__main__":
    main()