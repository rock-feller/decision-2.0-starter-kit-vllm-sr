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


# Progressive Scenarios for 'noul' (Level 1 to Level 4)
NOUL_PROGRESSIVE_SCENARIOS = [
    # -------------------------------------------------------------------------
    # LEVEL 1: Direct Keyword Matching (Simple Presence Check)
    # -------------------------------------------------------------------------
    {
        "level": "Level 1 - Direct Fact Verification",
        "domain": "Customer Support",
        "state": "The customer provided receipt #88412 and requested a full refund.",
        "questions": {
            "has_receipt": {
                "type": "noul",
                "instructions": "Does the customer have a valid receipt?"
            }
        }
    },
    {
        "level": "Level 1 - Direct Fact Verification",
        "domain": "E-Commerce Logistics",
        "state": "The parcel was marked as delivered at the front porch at 2:15 PM.",
        "instructions_summary": "Check package delivery status",
        "questions": {
            "is_delivered": {
                "type": "noul",
                "instructions": "Is the package delivered?"
            }
        }
    },

    # -------------------------------------------------------------------------
    # LEVEL 2: Implicit / Contextual Inference (No explicit key phrases)
    # -------------------------------------------------------------------------
    {
        "level": "Level 2 - Contextual Inference",
        "domain": "Healthcare Triage",
        "state": "Patient has BP of 180/110 mmHg, reports seeing spots, and has numbness in left arm.",
        "questions": {
            "requires_immediate_icu": {
                "type": "noul",
                "instructions": "Is the patient showing signs of a hypertensive emergency requiring critical intervention?"
            }
        }
    },
    {
        "level": "Level 2 - Contextual Inference",
        "domain": "Fintech Credit Risk",
        "state": "Applicant missed two credit card payments in the last 6 months and maxed out their overdraft limit.",
        "questions": {
            "high_default_risk": {
                "type": "noul",
                "instructions": "Is the applicant exhibiting high financial default risk?"
            }
        }
    },

    # -------------------------------------------------------------------------
    # LEVEL 3: Multi-Flag Parallel Evaluation (Simultaneous Binary Queries)
    # -------------------------------------------------------------------------
    {
        "level": "Level 3 - Multi-Flag Parallel Verification",
        "domain": "Cybersecurity & Email Security",
        "state": "Email originates from spoofed domain 'g00gle.com', contains an executable .exe attachment, but passed SPF validation.",
        "questions": {
            "is_phishing": {
                "type": "noul",
                "instructions": "Is this email a phishing attempt?"
            },
            "has_suspicious_attachment": {
                "type": "noul",
                "instructions": "Does the email contain a high-risk file attachment?"
            },
            "spf_passed": {
                "type": "noul",
                "instructions": "Did the email pass SPF domain authentication?"
            }
        }
    },

    # -------------------------------------------------------------------------
    # LEVEL 4: Complex Business Logic & Regulatory Compliance Checks
    # -------------------------------------------------------------------------
    {
        "level": "Level 4 - Complex Compliance & Policy Logic",
        "domain": "Corporate Legal & HR Compliance",
        "state": "An employee spent $1,200 on an client dinner without manager pre-approval. Corporate policy requires pre-approval for expenses exceeding $500.",
        "questions": {
            "exceeds_threshold": {
                "type": "noul",
                "instructions": "Does the expense amount exceed the $500 policy limit?"
            },
            "is_policy_compliant": {
                "type": "noul",
                "instructions": "Is this expense fully compliant with corporate approval policy?"
            },
            "requires_audit_escalation": {
                "type": "noul",
                "instructions": "Should this submission be escalated to internal audit?"
            }
        }
    }
]


def main():
    engine = DecisionModelEngine()

    print(f"\n Running 'noul' Primitive Progressive Complexity Benchmark...\n" + "="*80)
    
    for idx, scenario in enumerate(NOUL_PROGRESSIVE_SCENARIOS, 1):
        level = scenario["level"]
        domain = scenario["domain"]
        state_text = scenario["state"]
        questions = scenario["questions"]

        start_time = time.perf_counter()
        
        # Execute query against model
        raw_response = engine(state_text, questions)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Parse output using parse_decision_response
        parsed_data = parse_decision_response(raw_response)
        decisions = parsed_data["decisions"]

        print(f"Test #{idx:02d} | [{level}] | Domain: {domain}")
        print(f"State Input: \"{state_text}\"")
        print(f"Execution Time: {elapsed_ms:.2f} ms")
        print("Evaluated Flags ('noul'):")

        for key, details in decisions.items():
            val = details.get("value")
            prob = details.get("probability", 0.0)
            print(f"  └─ {key:<28}: Answer = {str(val):<5} | Probability = {prob * 100:.2f}%")
        
        print("-" * 80)


if __name__ == "__main__":
    main()



### RAW NOUL PRIMITIVE
# {'model': 'Decision-2.0-Eos-0.8B', 
#  'answers': 
#     {'receipt': 
#         {'type': 'noul', 
#          'noul': 0.9970894253250121}
#     }, 
         
# 'usage': 
#     {'input_tokens': 90,
#       'output_tokens': 0
#     }
    
# }
