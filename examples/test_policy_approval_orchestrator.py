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
        "An employee submitted a $1,200 client dinner expense without manager pre-approval. "
        "Corporate policy requires pre-approval for expenses exceeding $500."
    )

    orchestrator = DecisionOrchestrator([
        build_decision_program(
            "routing",
            "Which team should review this approval request?",
            key="review_team",
            criteria={
                "finance": "Finance and expense review",
                "legal": "Legal or policy review",
                "management": "Manager review",
            },
        ),
        build_decision_program(
            "verification",
            "Was this expense submitted in violation of policy?",
            key="policy_violation",
        ),
        build_decision_program(
            "risk",
            "How severe is the approval risk?",
            key="approval_risk",
            criteria=["Low", "Moderate", "High", "Critical"],
        ),
    ])

    result = orchestrator.run(engine, state_text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
