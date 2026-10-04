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
        "Patient reports chest pain radiating to the jaw, severe sweating, and oxygen saturation at 88%. "
        "The symptoms began 45 minutes ago."
    )

    orchestrator = DecisionOrchestrator([
        build_decision_program(
            "verification",
            "Is this a likely emergency requiring immediate intervention?",
            key="emergency",
        ),
        build_decision_program(
            "severity",
            "How urgent is the clinical acuity?",
            key="acuity",
            criteria=["Non-Urgent", "Less Urgent", "Urgent", "Emergent", "Resuscitation Required"],
        ),
        build_decision_program(
            "classification",
            "Which clinical response is most appropriate?",
            key="response_path",
            criteria={
                "emergency_room": "Immediate emergency department response",
                "urgent_care": "Prompt evaluation and monitoring",
                "routine": "Routine follow-up and observation",
            },
        ),
    ])

    result = orchestrator.run(engine, state_text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
