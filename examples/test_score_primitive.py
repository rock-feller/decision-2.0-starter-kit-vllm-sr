import json
import torch
import warnings
import sys
import time
from pathlib import Path

# Add project root directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Now use an absolute import
from src.parser import parse_decision_response
from src.engine import DecisionModelEngine
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")




# Progressive Scenarios for 'score' (Level 1 to Level 4)
SCORE_PROGRESSIVE_SCENARIOS = [
    # -------------------------------------------------------------------------
    # LEVEL 1: Simple 3-Tier Urgency Scale
    # -------------------------------------------------------------------------
    {
        "level": "Level 1 - Basic 3-Point Urgency Rating",
        "domain": "Customer Support Triage",
        "state": "The order arrived damaged yesterday. The customer asks for a replacement today.",
        "questions": {
            "urgency": {
                "type": "score",
                "instructions": "How urgent is this customer request?",
                "criteria": ["Routine", "Soon", "Today"]
            }
        }
    },
    
    # -------------------------------------------------------------------------
    # LEVEL 2: 5-Point Ordinal Severity Rating
    # -------------------------------------------------------------------------
    {
        "level": "Level 2 - 5-Point Severity Gradient",
        "domain": "DevOps & Infrastructure Monitoring",
        "state": "Database CPU utilization is fluctuating around 82%, causing minor API latency spikes of +200ms on non-critical endpoints.",
        "questions": {
            "severity_level": {
                "type": "score",
                "instructions": "Rate the severity of this infrastructure metric anomaly on a 1-5 scale.",
                "criteria": ["Informational", "Minor", "Moderate", "Major", "Critical Breach"]
            }
        }
    },

    # -------------------------------------------------------------------------
    # LEVEL 3: Multi-Dimensional Simultaneous Scoring
    # -------------------------------------------------------------------------
    {
        "level": "Level 3 - Dual-Metric Simultaneous Scoring",
        "domain": "Fintech Risk Assessment",
        "state": "A new customer requested a $50,000 credit line extension. Their business has 2 years of history, positive cash flow, but zero collateral assets.",
        "questions": {
            "creditworthiness": {
                "type": "score",
                "instructions": "Score overall borrower creditworthiness.",
                "criteria": ["Poor", "Fair", "Good", "Excellent"]
            },
            "collateral_coverage": {
                "type": "score",
                "instructions": "Rate the collateral backing provided for this loan.",
                "criteria": ["Unsecured", "Partially Secured", "Fully Collateralized"]
            }
        }
    },

    # -------------------------------------------------------------------------
    # LEVEL 4: Complex Multi-Factor Regulatory Compliance Audit
    # -------------------------------------------------------------------------
    {
        "level": "Level 4 - Complex Multi-Tier Scoring",
        "domain": "Healthcare Emergency Triage & Risk",
        "state": "Patient presents with chest tightness radiating to the left jaw, severe diaphoresis, and oxygen saturation at 88%. Symptoms started 45 minutes ago.",
        "questions": {
            "acuity_score": {
                "type": "score",
                "instructions": "Rate the clinical urgency according to the Emergency Severity Index (ESI).",
                "criteria": ["Non-Urgent", "Less Urgent", "Urgent", "Emergent", "Resuscitation Required"]
            },
            "resource_intensity": {
                "type": "score",
                "instructions": "Estimate required medical resources.",
                "criteria": ["None", "Single Diagnostic Test", "Multiple Diagnostics & IV Drugs"]
            }
        }
    }
]


def main():
    engine = DecisionModelEngine()

    print(f"\n Running 'score' Primitive Progressive Benchmark Across Domains...\n" + "="*85)
    
    latencies = []

    for idx, scenario in enumerate(SCORE_PROGRESSIVE_SCENARIOS, 1):
        level = scenario["level"]
        domain = scenario["domain"]
        state_text = scenario["state"]
        questions = scenario["questions"]

        start_time = time.perf_counter()
        
        # Query model
        raw_response = engine(state_text, questions)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        latencies.append(elapsed_ms)

        # Parse response using parser
        parsed_data = parse_decision_response(raw_response)
        decisions = parsed_data["decisions"]

        print(f"Test #{idx:02d} | [{level}] | Domain: {domain}")
        print(f"State Input: \"{state_text}\"")
        print(f"Execution Time: {elapsed_ms:.2f} ms")
        print("Scoring Results ('score'):")

        for key, details in decisions.items():
            exp_score = details.get("expected_score", 0.0)
            top_class = details.get("top_class", "N/A")
            confidence = details.get("confidence", 0.0)
            probs = details.get("probabilities", {})
            
            print(f"  └─ Key: '{key}'")
            print(f"     ├─ Expected Continuous Score : {exp_score:.4f}")
            print(f"     ├─ Top Discrete Class        : {top_class}")
            print(f"     ├─ Confidence                : {confidence:.4f}")
            print(f"     └─ Probabilities Distribution: {json.dumps({k: round(v, 4) for k, v in probs.items()})}")
        
        print("-" * 85)

    avg_latency = sum(latencies) / len(latencies)
    print("\n Execution Benchmark Summary:")
    print(f"Total Scenarios Evaluated : {len(SCORE_PROGRESSIVE_SCENARIOS)}")
    print(f"Average System One Latency: {avg_latency:.2f} ms")


if __name__ == "__main__":
    main()