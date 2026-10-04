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


def build_custom_route_question(instructions: str, criteria: dict) -> dict:
    """Factory function to build a route-focused question schema."""
    return {
        "route": {
            "type": "choice",
            "instructions": instructions,
            "criteria": criteria
        }
    }


# Queue of 10 distinct topics with custom states, instructions, and criteria options
MULTI_TOPIC_SCENARIOS = [
    {
        "id": 1,
        "topic": "Customer Support Triage",
        "state": "The order arrived damaged yesterday. I have the receipt and want a refund.",
        "instructions": "Which customer service department should process this ticket?",
        "criteria": {
            "returns": "Refunds, exchanges, damaged items, and returns",
            "billing": "Invoices, payment charges, and subscription queries",
            "technical": "Product troubleshooting, installation, and bugs"
        }
    },
    {
        "id": 2,
        "topic": "HR & Internal Employee Requests",
        "state": "I need to submit my parental leave request for next month and update my health insurance coverage.",
        "instructions": "Route this internal employee request to the correct HR division.",
        "criteria": {
            "benefits": "Health insurance, parental leave, wellness, and perks",
            "payroll": "Salary, tax documents, direct deposits, and bonuses",
            "recruiting": "Interviewing, hiring, job postings, and onboarding"
        }
    },
    {
        "id": 3,
        "topic": "Corporate Legal & Risk Management",
        "state": "A former customer sent a cease-and-desist letter alleging copyright infringement on our website images.",
        "instructions": "Which legal or compliance team should handle this notice?",
        "criteria": {
            "intellectual_property": "Copyright, trademark disputes, and patents",
            "data_privacy": "GDPR, CCPA, data breaches, and user privacy",
            "contracts": "Vendor agreements, service contracts, and NDAs"
        }
    },
    {
        "id": 4,
        "topic": "DevOps & Cloud Infrastructure",
        "state": "Production database connection pools are exhausted, causing HTTP 500 errors across all API endpoints.",
        "instructions": "Assign this incident to the primary engineering on-call unit.",
        "criteria": {
            "database_reliability": "Database clusters, query performance, and storage failure",
            "security_operations": "DDoS attacks, unauthorized access, and key rotation",
            "frontend_ui": "CSS layout bugs, client side web app rendering, and icons"
        }
    },
    {
        "id": 5,
        "topic": "Healthcare Patient Triage",
        "state": "Patient reports sudden onset shortness of breath and chest tightness starting 20 minutes ago.",
        "instructions": "Direct this patient encounter to the appropriate care level.",
        "criteria": {
            "emergency_dept": "Life-threatening symptoms, chest pain, and severe trauma",
            "primary_care": "Routine checkups, physicals, and mild cold symptoms",
            "pharmacy": "Medication refills, prescription status, and dosage info"
        }
    },
    {
        "id": 6,
        "topic": "Financial & Fraud Operations",
        "state": "Account holder flagged three unrecognized charges from an overseas vendor made within 5 minutes.",
        "instructions": "Route this financial transaction anomaly.",
        "criteria": {
            "fraud_prevention": "Unusual transactions, stolen cards, and unauthorized activity",
            "loan_servicing": "Mortgage applications, interest rates, and loan payoff",
            "wealth_management": "Stock portfolio advisory, retirement accounts, and investments"
        }
    },
    {
        "id": 7,
        "topic": "E-commerce Supply Chain",
        "state": "The container ship carrying key raw materials is delayed by 10 days due to port congestion.",
        "instructions": "Which supply chain team should adjust operations for this delay?",
        "criteria": {
            "inventory_planning": "Stock level adjustments, reorder delays, and warehouse capacity",
            "last_mile_delivery": "Local courier dispatch, door delivery, and driver routes",
            "supplier_sourcing": "Negotiating new vendor terms and purchasing materials"
        }
    },
    {
        "id": 8,
        "topic": "Content Moderation & Safety",
        "state": "User post contains explicit hate speech and targets a minority group with targeted harassment.",
        "instructions": "Classify this policy violation for moderation action.",
        "criteria": {
            "harassment_and_hate": "Hate speech, personal attacks, and targeted bullying",
            "spam_and_scams": "Phishing links, automated bot posts, and deceptive ads",
            "copyright_abuse": "Unauthorized media uploads, pirated movies, and stolen music"
        }
    },
    {
        "id": 9,
        "topic": "B2B Enterprise Sales Lead Routing",
        "state": "A company with 5,000 employees wants a custom demo for enterprise-wide deployment and security audit.",
        "instructions": "Assign this incoming sales lead to the proper representative tier.",
        "criteria": {
            "enterprise_sales": "Large accounts over 1,000 employees requiring custom SLAs",
            "smb_sales": "Small business accounts needing self-serve tier or basic setup",
            "partner_alliances": "Resellers, affiliate programs, and co-marketing agreements"
        }
    },
    {
        "id": 10,
        "topic": "IT Operations Hardware Provisioning",
        "state": "New employee starting on Monday needs an M3 MacBook Pro, dual monitors, and a docking station.",
        "instructions": "Where should this equipment request be routed?",
        "criteria": {
            "hardware_procurement": "Laptops, monitors, peripherals, and workstation setup",
            "identity_access": "SSO accounts, active directory, and email creation",
            "facilities": "Desk assignment, office badges, and physical keys"
        }
    }
]


def main():
    engine = DecisionModelEngine()

    print(f"\n Starting execution across 10 distinct routing topics...\n" + "="*75)
    
    latencies = []

    for item in MULTI_TOPIC_SCENARIOS:
        q_id = item["id"]
        topic = item["topic"]
        state_text = item["state"]
        instructions = item["instructions"]
        criteria = item["criteria"]

        questions = build_custom_route_question(instructions, criteria)

        start_time = time.perf_counter()
        
        # Execute query against model
        raw_response = engine(state_text, questions)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        latencies.append(elapsed_ms)

        # Pass raw response directly into parse_decision_response
        parsed_data = parse_decision_response(raw_response)
        
        route_info = parsed_data["decisions"].get("route", {})
        
        selected_choice = route_info.get("selected_choice", "N/A")
        confidence = route_info.get("confidence", 0.0)
        top_prob = route_info.get("top_probability", 0.0)
        all_probs = route_info.get("all_probabilities", {})

        print(f"Scenario #{q_id:02d} | Topic: {topic} | Time: {elapsed_ms:.2f} ms")
        print(f"Input State  : \"{state_text}\"")
        print(f"Instruction  : \"{instructions}\"")
        print(f"Routed Choice: {selected_choice}")
        print(f"Confidence   : {confidence:.4f}")
        print(f"Top Prob     : {top_prob * 100:.2f}%")
        print(f"All Probs    : {json.dumps(all_probs)}")
        print("-" * 75)

    avg_latency = sum(latencies) / len(latencies)
    print("\n Execution Benchmark Summary:")
    print(f"Total Scenarios Evaluated : {len(MULTI_TOPIC_SCENARIOS)}")
    print(f"Average System One Latency: {avg_latency:.2f} ms / query")
    print(f"Fastest Decision          : {min(latencies):.2f} ms")
    print(f"Slowest Decision          : {max(latencies):.2f} ms")


if __name__ == "__main__":
    main()