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
        "A customer made a $12,000 purchase from a new device, used a mismatched billing address, "
        "and submitted a chargeback dispute after 2 days."
    )

    orchestrator = DecisionOrchestrator([
        build_decision_program(
            "classification",
            "Classify this transaction risk category.",
            key="risk_category",
            criteria={
                "fraud": "Likely fraud or account abuse",
                "chargeback": "Potential chargeback dispute",
                "manual_review": "Needs human review",
            },
        ),
        build_decision_program(
            "verification",
            "Is the customer making a policy exception request?",
            key="exception_request",
        ),
        build_decision_program(
            "risk",
            "How severe is this financial risk?",
            key="risk_level",
            criteria=["Low", "Moderate", "High", "Critical"],
        ),
    ])

    result = orchestrator.run(engine, state_text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
