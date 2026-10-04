import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.engine import DecisionModelEngine
from src.programs import DecisionOrchestrator, build_decision_program


def main():
    engine = DecisionModelEngine()
    state_text = (
        "The package arrived damaged yesterday. The customer attached a receipt "
        "and wants a replacement sent today."
    )

    orchestrator = DecisionOrchestrator([
        build_decision_program(
            "routing",
            "Which team should handle this request?",
            key="route",
            criteria={
                "returns": "Refunds, replacements, and damaged deliveries",
                "billing": "Payments, invoices, and charges",
                "technical": "Product setup and faults",
            },
        ),
        build_decision_program(
            "verification",
            "Did the customer attach a valid receipt?",
            key="receipt",
        ),
        build_decision_program(
            "priority",
            "How urgent is this request?",
            key="urgency",
            criteria=["Routine", "Soon", "Today"],
        ),
    ])

    result = orchestrator.run(engine, state_text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
