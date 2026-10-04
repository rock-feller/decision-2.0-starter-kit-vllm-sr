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




# Questions schema using the required "instructions" field name
TEST_QUESTIONS = {
    "route": {
        "type": "choice",
        "instructions": "Which team should handle this request?",
        "criteria": {
            "returns": "Refunds, replacements and damaged deliveries",
            "billing": "Payments, invoices and charges",
            "technical": "Product setup and faults"
        }
    },
    "receipt": {
        "type": "noul",
        "instructions": "Does the customer have a receipt?"
    },
    "urgency": {
        "type": "score",
        "instructions": "How urgent is this request?",
        "criteria": ["Routine", "Soon", "Today"]
    }
}


# Queue of test queries
TEST_QUEUE = [
    {
        "id": 1,
        "input_text": "The package arrived with a smashed screen yesterday. I attached the receipt and need a replacement sent today."
    },
    {
        "id": 2,
        "input_text": "I noticed a double charge on my credit card statement for invoice #1042. Can you review this when you get a chance?"
    },
    {
        "id": 3,
        "input_text": "The software app keeps crashing whenever I click on the export button. I cannot finish my work."
    },
    {
        "id": 4,
        "input_text": "I would like to change the delivery address for my order #8812 before it ships next week."
    },
    {
        "id": 5,
        "input_text": "Received the wrong color shoes in my order. Here is my receipt copy. Please send a return label."
    },
    {
        "id": 6,
        "input_text": "CRITICAL: The server setup script is throwing 500 errors and our system is completely down today!"
    },
    {
        "id": 7,
        "input_text": "Where can I find the user manual for model X-200? No hurry, just checking."
    },
    {
        "id": 8,
        "input_text": "I was overcharged by $15 on my monthly subscription renewal. Receipt attached."
    },
    {
        "id": 9,
        "input_text": "Can you provide a formal VAT invoice for my purchase last month? Needed for tax filing."
    },
    {
        "id": 10,
        "input_text": "The item was delivered damaged. I do not have the receipt, but can I exchange it anyway today?"
    }
]


def main():
    engine = DecisionModelEngine()

    print(f"\n Starting batch execution of {len(TEST_QUEUE)} queued test queries...\n" + "="*60)
    
    latencies = []

    for item in TEST_QUEUE:
        q_id = item["id"]
        state_text = item["input_text"]

        start_time = time.perf_counter()
        
        # Execute query against model
        raw_response = engine(state_text, TEST_QUESTIONS)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        latencies.append(elapsed_ms)

        answers = raw_response.get("answers", {})

        route_info = answers.get("route", {})
        receipt_info = answers.get("receipt", {})
        urgency_info = answers.get("urgency", {})

        print(f"Query #{q_id:02d} | Time: {elapsed_ms:.2f} ms")
        print(f"Input  : \"{state_text}\"")
        print(f"Route  : {route_info.get('answer')}")
        print(f"Receipt: {receipt_info.get('answer')} (Prob: {receipt_info.get('probability', 0.0):.2f})")
        print(f"Urgency: {urgency_info.get('answer')}")
        print("-" * 60)

    # Performance stats
    avg_latency = sum(latencies) / len(latencies)
    print("\n Execution Benchmark Summary:")
    print(f"Total Processed : {len(TEST_QUEUE)} queries")
    print(f"Average Latency : {avg_latency:.2f} ms / query")
    print(f"Fastest Query   : {min(latencies):.2f} ms")
    print(f"Slowest Query   : {max(latencies):.2f} ms")


if __name__ == "__main__":
    main()