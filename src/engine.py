import warnings
from typing import Dict, Any, Union
import torch
from transformers import AutoModel

# Suppress PyTorch C++ kernel fallback warnings on macOS/MPS
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")


class DecisionModelEngine:
    """Engine wrapper for local vllm-sr/Decision-2.0-Eos-0.8B execution."""

    def __init__(self, model_id: str = "vllm-sr/Decision-2.0-Eos-0.8B"):
        """Initializes hardware device and loads model weights onto target device."""
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")

        print(f"Loading {model_id} onto {self.device}...")
        self.model = AutoModel.from_pretrained(
            model_id, 
            trust_remote_code=True
        ).to(self.device)

    def __call__(
        self, 
        state_text: Union[str, Dict[str, Any]], 
        questions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executes system_one forward pass for input state and question payload.
        
        Args:
            state_text: Input text string or state dictionary.
            questions: Dictionary defining decision primitives (choice, noul, score).
            
        Returns:
            Raw response dictionary returned from model.system_one().
        """
        return self.model.system_one(state=state_text, questions=questions)


# Quick verification entry point if executed directly
if __name__ == "__main__":
    engine = DecisionModelEngine()
    
    test_state = "The order arrived damaged yesterday."
    test_questions = {
        "is_damaged": {
            "type": "noul",
            "instructions": "Is the order damaged?"
        }
    }
    
    response = engine(test_state, test_questions)
    print("Engine Self-Test Output:")
    print(response)