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




def build_choice_question(key_name: str, instructions: str, criteria: dict) -> dict:
    """Helper to build a single choice decision schema under a given key name."""
    return {
        key_name: {
            "type": "choice",
            "instructions": instructions,
            "criteria": criteria
        }
    }


# Scenarios across diverse domains using choice primitives
MULTI_DOMAIN_SCENARIOS = [
    {
        "id": 1,
        "domain": "Finance & Wealth Management",
        "key": "investment_vehicle",
        "state": "The client is 62 years old, risk-averse, and requires steady quarterly income payouts with principal preservation.",
        "instructions": "Select the most appropriate investment vehicle for this client profile.",
        "criteria": {
            "fixed_income_bonds": "Treasury bonds, corporate bonds, and fixed income funds focused on capital preservation and yield",
            "growth_equities": "High-beta technology stocks, small-cap growth funds, and emerging market equities",
            "crypto_assets": "Digital currencies, crypto spot ETFs, and decentralized finance liquidity pools"
        }
    },
    {
        "id": 2,
        "domain": "Healthcare Triage",
        "key": "triage_severity",
        "state": "Patient presents with severe localized swelling, mild fever, and a small cut on the forearm sustained 3 days ago.",
        "instructions": "Categorize the clinical urgency level for immediate routing.",
        "criteria": {
            "urgent_care": "Non-life-threatening conditions requiring evaluation within hours like minor cuts or low fever",
            "resuscitation_trauma": "Immediate life threats including cardiac arrest, severe respiratory distress, or heavy bleeding",
            "routine_outpatient": "Elective wellness visits, annual checkups, and prescription refill consultations"
        }
    },
    {
        "id": 3,
        "domain": "Mathematics & Data Science",
        "key": "algorithm_choice",
        "state": "We need to predict continuous house prices based on tabular features with complex non-linear feature interactions and missing values.",
        "instructions": "Which machine learning model family is best suited for this tabular dataset?",
        "criteria": {
            "gradient_boosted_trees": "XGBoost or LightGBM decision tree ensembles optimized for structured tabular data",
            "convolutional_neural_net": "Spatial grid processing networks suited for computer vision and image processing",
            "naive_bayes": "Simple probabilistic classifiers assuming strong conditional feature independence"
        }
    },
    {
        "id": 4,
        "domain": "World History & Historiography",
        "key": "historical_period",
        "state": "The text discusses the fall of Constantinople in 1453 and the subsequent flourishing of humanist scholarship in Florence.",
        "instructions": "Which major historical transition period does this text describe?",
        "criteria": {
            "renaissance_transition": "The transition from the late Middle Ages to early modern European humanism and trade",
            "industrial_revolution": "18th-19th century mechanization, steam engines, and factory urbanization",
            "bronze_age_collapse": "1200 BCE regional societal collapse in the Aegean and Eastern Mediterranean"
        }
    },
    {
        "id": 5,
        "domain": "Telecom & Connectivity",
        "key": "network_fault_type",
        "state": "Cell site #402 reports high packet loss and dropped calls exclusively during peak hour congestion, with normal RF power levels.",
        "instructions": "Classify the root cause of this network issue.",
        "criteria": {
            "backhaul_capacity": "Insufficient bandwidth capacity on the transport backhaul link under load",
            "hardware_rf_failure": "Damaged antenna cables, blown power amplifiers, or physical radio hardware failure",
            "sim_authorization": "Authentication server errors preventing SIM cards from joining the core network"
        }
    },
    {
        "id": 6,
        "domain": "Legal & Billing Audit",
        "key": "billing_discrepancy",
        "state": "Law firm billed 14 hours in a single day for 'document review' without specifying the associated case matter or line items.",
        "instructions": "Identify the primary compliance issue with this fee entry.",
        "criteria": {
            "block_billing_vague": "Unitemized or overly vague task descriptions lacking specific legal work detail",
            "out_of_pocket_expense": "Disbursements like court filing fees, expert witness costs, or travel mileage",
            "conflict_of_interest": "Representing adverse parties in active litigation without signed waivers"
        }
    },
    {
        "id": 7,
        "domain": "Software Tool Call Routing",
        "key": "function_to_call",
        "state": "User requested: 'Send an email to dev-team@company.com with subject Deployment Failed and body check log #4892'.",
        "instructions": "Which API tool function should the agent execute?",
        "criteria": {
            "send_email": "Dispatches an outbound email message with recipient, subject line, and body parameters",
            "query_database": "Executes an SQL or document database query to retrieve raw database rows",
            "restart_pod": "Issues a Kubernetes API call to restart a running container pod"
        }
    },
    {
        "id": 8,
        "domain": "Cybersecurity Incident Response",
        "key": "incident_category",
        "state": "Employee opened a fake invoice PDF attachment; endpoint ED-88 executed Powershell scripts connecting to a known malicious C2 IP address.",
        "instructions": "Classify the security incident for containment workflow.",
        "criteria": {
            "malware_c2_infection": "Active endpoint malware infection establishing command and control callback channels",
            "ddos_attack": "Volumetric network traffic flooding external web servers to disrupt availability",
            "insider_data_exfiltration": "Authorized user downloading unauthorized confidential files onto a USB drive"
        }
    }
]


def main():
    engine = DecisionModelEngine()

    print(f"\n Running Choice Primitive Benchmark Across {len(MULTI_DOMAIN_SCENARIOS)} Domains...\n" + "="*80)
    
    latencies = []

    for scenario in MULTI_DOMAIN_SCENARIOS:
        s_id = scenario["id"]
        domain = scenario["domain"]
        key_name = scenario["key"]
        state_text = scenario["state"]
        instructions = scenario["instructions"]
        criteria = scenario["criteria"]

        # Build schema using domain-specific key
        questions = build_choice_question(key_name, instructions, criteria)

        start_time = time.perf_counter()
        
        # Execute query against model
        raw_response = engine(state_text, questions)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        latencies.append(elapsed_ms)

        # Parse with parse_decision_response
        parsed_data = parse_decision_response(raw_response)
        print(parsed_data)
        
        decision_info = parsed_data["decisions"].get(key_name, {})
        
        selected_choice = decision_info.get("selected_choice", "N/A")
        confidence = decision_info.get("confidence", 0.0)
        top_prob = decision_info.get("top_probability", 0.0)
        all_probs = decision_info.get("all_probabilities", {})

        print(f"Scenario #{s_id:02d} | Domain: {domain} | Time: {elapsed_ms:.2f} ms")
        print(f"State Input : \"{state_text}\"")
        print(f"Decision Key: {key_name}")
        print(f"Selected    : {selected_choice}")
        print(f"Confidence  : {confidence:.4f} | Top Prob: {top_prob * 100:.2f}%")
        print(f"All Probs   : {json.dumps(all_probs)}")
        print("-" * 80)

    avg_latency = sum(latencies) / len(latencies)
    print("\n Multi-Domain Benchmark Summary:")
    print(f"Total Domains Evaluated   : {len(MULTI_DOMAIN_SCENARIOS)}")
    print(f"Average System One Latency: {avg_latency:.2f} ms / decision")
    print(f"Fastest Decision          : {min(latencies):.2f} ms")
    print(f"Slowest Decision          : {max(latencies):.2f} ms")


if __name__ == "__main__":
    main()