# Decision 2.0 Starter Kit

## Chapter 1: Why this repo exists

This project is a compact starter kit for building decision systems around the `vllm-sr/Decision-2.0-Eos-0.8B` model. Instead of generating free-form text, the model evaluates structured decision questions in a single forward pass and returns probability-based outputs for a small number of reusable primitives.

The three core primitives are:
- `choice`: choose the best category or route
- `noul`: answer a yes/no verification question
- `score`: rate urgency, risk, or severity on a scale

This repo turns those outputs into minimal Python workflows that are easy to compose into decision programs.

## Chapter 2: Repository layout

```text
decision-2.0-starter-kit-vllm-sr/
├── AGENTS.md
├── README.md
├── __init__.py
├── examples/
│   ├── test_all_primitives.py
│   ├── test_choice_primitive.py
│   ├── test_decision_programs.py
│   ├── test_noul_primitive.py
│   ├── test_score_primitive.py
│   └── ...
├── src/
│   ├── __init__.py
│   ├── engine.py
│   ├── parser.py
│   └── programs.py
└── tests/
    └── test_decision_programs.py
```

## Chapter 3: Core architecture

The system is intentionally simple:

1. `src/engine.py` loads the model and calls `model.system_one(...)`.
2. `src/parser.py` converts the raw answer dict into structured outputs.
3. `src/programs.py` builds use-case-specific decision programs that choose the right primitive automatically.

A typical flow looks like this:

```python
from src.engine import DecisionModelEngine
from src.parser import parse_decision_response
from src.programs import build_decision_program

engine = DecisionModelEngine()
program = build_decision_program("routing", "Which team should handle this request?")
selected_primitive = program.select_primitive(engine, state_text)
raw_response = engine(state_text, program.questions)
parsed = parse_decision_response(raw_response)
```

The `select_primitive(...)` method is the meta-step that asks the model to choose between `choice`, `noul`, and `score` for a given use case. This is especially useful for higher-level flows such as a confidence or system-evaluation use case, where the goal is to decide which primitive best matches the task before executing the final decision.

## Chapter 4: Decision primitives

### 4.1 Choice
Use `choice` when you need to route, classify, or select from a finite set of outcomes.

Example use cases:
- routing support tickets
- categorizing issues by department
- selecting the most relevant workflow

### 4.2 Noul
Use `noul` when you need a yes/no answer grounded in the supplied state.

Example use cases:
- checking if the customer provided a receipt
- verifying an exception condition
- answering policy or compliance yes/no questions

### 4.3 Score
Use `score` when you need a ranked or graded output.

Example use cases:
- urgency scoring
- compliance severity
- risk or priority estimation

## Chapter 5: Decision programs by use case

The project now exposes a small decision-program abstraction that maps a business use case to the appropriate primitive.

```python
from src.programs import build_decision_program

routing = build_decision_program("routing", "Which team should handle this request?")
verification = build_decision_program("verification", "Did the customer include a receipt?")
priority = build_decision_program("priority", "How urgent is this request?")
```

This pattern makes the repository feel more like a system of reusable programs rather than isolated examples.

Examples of the mapping:
- `routing` -> `choice`
- `verification` -> `noul`
- `priority` -> `score`
- unknown use case -> defaults to `choice`

## Chapter 6: Getting started

### Conda environment

```bash
conda activate decision_env
```

### Run the example programs

```bash
python examples/test_decision_programs.py
python examples/test_choice_primitive.py
python examples/test_noul_primitive.py
python examples/test_score_primitive.py
```

### Validate the code

```bash
python -m pytest tests/test_decision_programs.py
```

## Chapter 7: Recommended project direction

The next step is to keep expanding the repo as a decision-program library rather than a loose collection of model demos. A good pattern is:

1. Define a use case
2. Map it to a primitive
3. Build a small question schema
4. Run the program with a state description
5. Parse and act on the returned structured result

This keeps the repository aligned with real decision workflows while staying lightweight and easy to reason about.

## License

Distributed under the MIT License.
