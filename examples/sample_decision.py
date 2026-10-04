
from src.parser import parse_decision_response

from src.engine import DecisionModelEngine
engine = DecisionModelEngine("vllm-sr/Decision-2.0-Eos-0.8B")
questions = {
    "route": {
        "type": "choice",
        "instructions": "Which agricultural intervention \
            should be recommended for this farm?",

        "criteria": {
            "irrigation": "Water and irrigation support",
            "soil_health": "Soil fertility and nutrient management",
            "pest_control": "Crop protection and pest management"
        }
    },
    "receipt": {
        "type": "noul",
        "instructions": "Is there evidence of crop stress \
              caused by water shortage?"
    },
    "urgency": {
        "type": "score",
        "instructions": "How urgent is the intervention needed \
            for this farm?",
        "criteria": ["Routine", "Soon", "Immediate"]
    }
}

input_text = """A maize farm in Kenya has yellowing leaves, \
    dry soil, and wilting plants after two weeks without rain.   
      The farmer needs guidance on the fastest practical \
        field response."""