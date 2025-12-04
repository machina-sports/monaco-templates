def invoke_enrich_validation_metadata(request_data):
    """
    Enriches generated questions with validation metadata.

    Takes questions and their validation results, matches them up,
    and adds validation metadata to each question.

    For regenerated content: compares new score vs original score.
    - If new_score > old_score: normal status (approved/needs_review)
    - If new_score <= old_score: status = "discarded" (no improvement)
    """

    params = request_data.get("params", {})

    questions = params.get("questions", [])
    validation_results = params.get("validation_results", [])
    original_scores = params.get("original_scores", [])  # For regeneration comparison

    # Match questions with validation results by index
    # (foreach processes them in order)
    enriched_questions = []
    for i, question in enumerate(questions):
        # Get corresponding validation result (or empty dict if not found)
        validation = validation_results[i] if i < len(validation_results) else {}

        # Get new and old scores
        new_score = validation.get("score", 0)
        old_score = original_scores[i] if i < len(original_scores) else None

        # Determine validation status
        is_valid = validation.get("valid", False)

        # If we're regenerating (have original_scores) and didn't improve, discard
        if old_score is not None and new_score <= old_score:
            validation_status = "discarded"
        else:
            # Normal validation logic
            validation_status = "approved" if is_valid else "needs_review"

        # Build enriched question with metadata
        enriched_question = {
            **question,
            "validation-status": validation_status,
            "validation-score": new_score,
            "validation-issues": validation.get("issues", []),
        }

        enriched_questions.append(enriched_question)

    return {
        "status": True,
        "message": f"Enriched {len(enriched_questions)} questions with validation metadata.",
        "data": {
            "enriched_questions": enriched_questions
        }
    }

