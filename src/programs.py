from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from src.parser import parse_decision_response


def resolve_primitive(use_case: str) -> str:
    """Map a business use case to the best Decision 2.0 primitive."""
    normalized = (use_case or "").strip().lower().replace("-", "_").replace(" ", "_")

    mapping = {
        "route": "choice",
        "routing": "choice",
        "classification": "choice",
        "triage": "choice",
        "selection": "choice",
        "dispatch": "choice",
        "verification": "noul",
        "boolean": "noul",
        "noul": "noul",
        "audit": "noul",
        "compliance": "noul",
        "priority": "score",
        "urgency": "score",
        "severity": "score",
        "score": "score",
        "risk": "score",
        "grading": "score",
        "confidence": "choice",
        "system_confidence": "choice",
    }

    return mapping.get(normalized, "choice")


def _choice_criteria(use_case: str) -> Dict[str, str]:
    normalized = (use_case or "").strip().lower().replace("-", "_").replace(" ", "_")

    if normalized in {"route", "routing", "triage", "classification"}:
        return {
            "returns": "Refunds, replacements, and damaged deliveries",
            "billing": "Payments, invoices, and charges",
            "technical": "Product setup and faults",
        }

    if normalized in {"dispatch", "selection"}:
        return {
            "agent_a": "Primary agent",
            "agent_b": "Fallback agent",
            "human_review": "Escalate for human review",
        }

    if normalized in {"confidence", "system_confidence"}:
        return {
            "choice": "Choose a categorical decision path",
            "noul": "Use a yes/no verification",
            "score": "Use a graded urgency or risk score",
        }

    return {
        "option_a": "Option A",
        "option_b": "Option B",
        "option_c": "Option C",
    }


def _score_criteria(use_case: str) -> List[str]:
    normalized = (use_case or "").strip().lower().replace("-", "_").replace(" ", "_")

    if normalized in {"priority", "urgency", "severity"}:
        return ["Routine", "Soon", "Today"]

    if normalized in {"risk"}:
        return ["Low", "Moderate", "High", "Critical"]

    return ["Low", "Medium", "High"]


@dataclass
class DecisionProgram:
    """Represents a single use-case-specific decision program."""

    use_case: str
    instruction: str
    key: Optional[str] = None
    criteria: Optional[Union[Dict[str, str], List[str]]] = None
    primitive: str = field(init=False)
    questions: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.primitive = resolve_primitive(self.use_case)
        question_key = self.key or self._default_key()

        if self.primitive == "choice":
            choice_criteria = self.criteria if self.criteria is not None else _choice_criteria(self.use_case)
            self.questions[question_key] = {
                "type": "choice",
                "instructions": self.instruction,
                "criteria": choice_criteria,
            }
        elif self.primitive == "noul":
            self.questions[question_key] = {
                "type": "noul",
                "instructions": self.instruction,
            }
        else:
            score_criteria = self.criteria if self.criteria is not None else _score_criteria(self.use_case)
            self.questions[question_key] = {
                "type": "score",
                "instructions": self.instruction,
                "criteria": score_criteria,
            }

    def _default_key(self) -> str:
        mapping = {
            "route": "route",
            "routing": "route",
            "verification": "receipt",
            "noul": "receipt",
            "priority": "urgency",
            "urgency": "urgency",
            "severity": "urgency",
            "score": "urgency",
            "risk": "risk",
            "confidence": "primitive_selector",
            "system_confidence": "primitive_selector",
        }

        normalized = (self.use_case or "").strip().lower().replace("-", "_").replace(" ", "_")
        return mapping.get(normalized, "decision")

    def select_primitive(self, engine: Any, state_text: str) -> str:
        """Use the model engine to classify the use case into choice, noul, or score."""
        selector_questions = {
            "primitive_selector": {
                "type": "choice",
                "instructions": (
                    f"Given this use case: '{self.use_case}'. "
                    "Choose the single best Decision 2.0 primitive for this task. "
                    "Options are: choice, noul, and score. "
                    "Use choice for multi-option classification or routing, "
                    "noul for yes/no verification, and score for graded urgency, risk, or severity."
                ),
                "criteria": {
                    "choice": "Multi-option classification or routing",
                    "noul": "Yes/no verification or binary fact check",
                    "score": "Ordinal scoring, urgency, risk, or severity",
                },
            }
        }

        raw_response = engine(state_text, selector_questions)
        parsed = parse_decision_response(raw_response)
        selected = parsed.get("decisions", {}).get("primitive_selector", {}).get("selected_choice")
        print(f"Use case: {self.use_case} | Inferred primitive: {selected}")
        return selected or self.primitive

    def execute(self, engine: Any, state_text: str, *, auto_select_primitive: bool = False) -> Dict[str, Any]:
        """Run the program through the engine. If requested, classify the primitive first."""
        if auto_select_primitive:
            self.primitive = self.select_primitive(engine, state_text)
        return engine(state_text, self.questions)


def build_decision_program(
    use_case: str,
    instruction: str,
    *,
    key: Optional[str] = None,
    criteria: Optional[Union[Dict[str, str], List[str]]] = None,
) -> DecisionProgram:
    """Factory for building a decision program that matches a use case."""
    return DecisionProgram(use_case=use_case, instruction=instruction, key=key, criteria=criteria)


@dataclass
class DecisionOrchestrator:
    """Runs multiple decision programs together as a single decision workflow."""

    programs: List[DecisionProgram] = field(default_factory=list)
    auto_select_primitive: bool = False

    def add_program(self, program: DecisionProgram) -> "DecisionOrchestrator":
        self.programs.append(program)
        return self

    def run(self, engine: Any, state_text: str, *, auto_select_primitive: Optional[bool] = None) -> Dict[str, Any]:
        """Execute all programs, optionally selecting each primitive with the engine first."""
        use_auto_select = self.auto_select_primitive if auto_select_primitive is None else auto_select_primitive
        all_results: Dict[str, Any] = {}

        for program in self.programs:
            if use_auto_select:
                program.primitive = program.select_primitive(engine, state_text)

            raw_response = engine(state_text, program.questions)
            parsed = parse_decision_response(raw_response)
            all_results.update(parsed.get("decisions", {}))

        return {
            "results": all_results,
            "summary": {
                "program_count": len(self.programs),
                "primitives": [program.primitive for program in self.programs],
            },
        }


def build_decision_orchestrator(
    programs: Optional[List[DecisionProgram]] = None,
    *,
    auto_select_primitive: bool = False,
) -> DecisionOrchestrator:
    """Factory that creates a workflow of multiple decision programs."""
    return DecisionOrchestrator(programs=list(programs or []), auto_select_primitive=auto_select_primitive)


__all__ = [
    "DecisionOrchestrator",
    "DecisionProgram",
    "build_decision_orchestrator",
    "build_decision_program",
    "resolve_primitive",
]
