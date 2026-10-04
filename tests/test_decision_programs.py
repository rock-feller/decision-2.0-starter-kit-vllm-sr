from src.programs import DecisionOrchestrator, DecisionProgram, build_decision_program


class FakeEngine:
    def __init__(self, selected_choice):
        self.selected_choice = selected_choice

    def __call__(self, state_text, questions):
        if "primitive_selector" in questions:
            return {
                "model": "fake-model",
                "answers": {
                    "primitive_selector": {
                        "type": "choice",
                        "choice": self.selected_choice,
                        "probabilities": {
                            "choice": 0.2,
                            "noul": 0.3,
                            "score": 0.5,
                        },
                        "confidence": 0.9,
                    }
                },
                "usage": {"input_tokens": 7, "output_tokens": 0},
            }

        answers = {}
        for key, question in questions.items():
            q_type = question["type"]
            if q_type == "noul":
                answers[key] = {"type": "noul", "noul": 0.94}
            elif q_type == "choice":
                answers[key] = {
                    "type": "choice",
                    "choice": "returns",
                    "probabilities": {"returns": 0.9, "billing": 0.05, "technical": 0.05},
                    "confidence": 0.9,
                }
            elif q_type == "score":
                answers[key] = {
                    "type": "score",
                    "score": 2.0,
                    "confidence": 0.8,
                    "probabilities": {"0": 0.2, "1": 0.3, "2": 0.5},
                    "legend": {"0": "Routine", "1": "Soon", "2": "Today"},
                }

        return {"model": "fake-model", "answers": answers, "usage": {"input_tokens": 5, "output_tokens": 0}}


def test_routing_program_uses_choice_primitive():
    program = build_decision_program("routing", "Which team should handle this request?")

    assert program.primitive == "choice"
    assert program.questions["route"]["type"] == "choice"
    assert "criteria" in program.questions["route"]


def test_verification_program_uses_noul_primitive():
    program = build_decision_program("verification", "Did the customer include a receipt?")

    assert program.primitive == "noul"
    assert program.questions["receipt"]["type"] == "noul"
    assert "instructions" in program.questions["receipt"]


def test_priority_program_uses_score_primitive():
    program = build_decision_program("priority", "How urgent is this request?")

    assert program.primitive == "score"
    assert program.questions["urgency"]["type"] == "score"
    assert "criteria" in program.questions["urgency"]


def test_default_program_handles_unknown_use_case():
    program = DecisionProgram("mixed", "Determine the best action.")

    assert program.primitive == "choice"
    assert program.questions["decision"]["type"] == "choice"


def test_program_can_use_engine_to_classify_primitive():
    program = DecisionProgram("confidence", "How confident is the system?")
    engine = FakeEngine("score")

    assert program.select_primitive(engine, "The system is uncertain but trending lower.") == "score"


def test_orchestrator_runs_multiple_decision_programs():
    engine = FakeEngine("score")
    orchestrator = DecisionOrchestrator([
        build_decision_program("routing", "Which team should handle this request?"),
        build_decision_program("verification", "Did the customer include a receipt?"),
    ])

    result = orchestrator.run(engine, "The package arrived damaged and the receipt is attached.")

    assert "results" in result
    assert "route" in result["results"]
    assert "receipt" in result["results"]
    assert result["summary"]["program_count"] == 2
