import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.engine import DecisionModelEngine
from src.programs import build_decision_program


if __name__ == "__main__":
    engine = DecisionModelEngine()

    use_cases = [
        ("routing", "Which team should handle this request?", "The package arrived damaged and the customer wants a replacement."),
        ("verification", "Did the customer include a receipt?", "The customer attached a receipt and needs a refund."),
        ("priority", "How urgent is this request?", "A product outage is blocking orders and the customer needs help today."),
        ("confidence", "How confident should the system be in deciding the best action?", "The model is seeing a damaged order claim with a receipt and a time-sensitive request."),
    ]

    for use_case, instruction, state_text in use_cases:
        program = build_decision_program(use_case, instruction)
        inferred_primitive = program.select_primitive(engine, state_text)
        print(f"Use case: {program.use_case} | Inferred primitive: {inferred_primitive}")
        print(f"Question schema: {program.questions}")
        print("-" * 60)
