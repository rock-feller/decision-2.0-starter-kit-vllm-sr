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
        "Authentication requests are failing across production, customers cannot log in, "
        "the error rate is rising, and the issue is affecting the checkout experience."
    )

    orchestrator = DecisionOrchestrator([
        build_decision_program(
            "classification",
            "Which incident area is the primary cause?",
            key="incident_area",
            criteria={
                "auth": "Authentication and identity",
                "network": "Networking and connectivity",
                "storage": "Database or storage layer",
                "application": "Application and service logic",
            },
        ),
        build_decision_program(
            "verification",
            "Is this incident customer-facing?",
            key="customer_facing",
        ),
        build_decision_program(
            "severity",
            "How severe is the incident?",
            key="severity",
            criteria=["Low", "Moderate", "High", "Critical"],
        ),
    ])

    result = orchestrator.run(engine, state_text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
