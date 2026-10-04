def parse_decision_response(response: dict, noul_threshold: float = 0.5) -> dict:
    """Parses raw Decision-2.0 system_one response dictionary into clean, structured outputs."""
    answers = response.get("answers", {})
    usage = response.get("usage", {})
    
    parsed_results = {
        "model_name": response.get("model", "Unknown"),
        "input_tokens": usage.get("input_tokens", 0),
        "decisions": {}
    }

    for decision_key, decision_data in answers.items():
        decision_type = decision_data.get("type")
        
        if decision_type == "choice":
            selected_choice = decision_data.get("choice")
            probabilities = decision_data.get("probabilities", {})
            confidence = decision_data.get("confidence", 0.0)
            
            parsed_results["decisions"][decision_key] = {
                "type": "choice",
                "selected_choice": selected_choice,
                "confidence": confidence,
                "top_probability": probabilities.get(selected_choice, 0.0),
                "all_probabilities": probabilities
            }

        elif decision_type == "noul":
            probability = decision_data.get("noul", 0.0)
            is_true = probability >= noul_threshold
            
            parsed_results["decisions"][decision_key] = {
                "type": "noul",
                "value": is_true,
                "probability": probability
            }

        elif decision_type == "score":
            expected_score = decision_data.get("score", 0.0)
            confidence = decision_data.get("confidence", 0.0)
            probabilities = decision_data.get("probabilities", {})
            legend = decision_data.get("legend", {})
            
            # Find index with highest probability for discrete class prediction
            top_index = max(probabilities, key=probabilities.get) if probabilities else "0"
            top_label = legend.get(top_index, top_index)
            
            # Map probabilities to readable category names
            named_probabilities = {
                legend.get(idx, idx): prob for idx, prob in probabilities.items()
            }
            
            parsed_results["decisions"][decision_key] = {
                "type": "score",
                "expected_score": expected_score,
                "top_class": top_label,
                "confidence": confidence,
                "probabilities": named_probabilities,
                "raw_legend": legend
            }

    return parsed_results