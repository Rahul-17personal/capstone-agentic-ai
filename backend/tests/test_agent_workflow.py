from app.services import agent_workflow as workflow


def test_langgraph_workflow_uses_all_agents(monkeypatch):
    def fake_generate_structured(provider, schema, system_prompt, user_prompt):
        if schema is workflow.StrategyFinding:
            return schema(
                value_proposition="Reduce manual sales preparation",
                target_audience="Sales leaders",
                positioning="Sales productivity platform",
                differentiators=["Pitch analysis"],
                proof_points_present=[],
                overall_score=80,
            )
        if schema is workflow.CriticFinding:
            return schema(
                executive_summary="Clear idea, but evidence is limited.",
                strengths=["Clear product purpose"],
                weaknesses=["No quantified outcomes"],
                missing_information=["Customer proof"],
                risk_flags=["Claims need validation"],
                messaging_quality=75,
                value_proposition=70,
                target_audience_clarity=80,
                call_to_action=60,
            )
        return schema(
            recommendations=["Add a verified customer outcome"],
            improved_pitch="Help sales teams prepare stronger pitches. [Add verified proof point.]",
            suggested_call_to_action="Schedule a product walkthrough.",
        )

    monkeypatch.setattr(workflow, "generate_structured", fake_generate_structured)
    result = workflow.run_pitch_workflow("Example pitch text", "openai", ["Example competitor"])

    assert result["workflow"]["engine"] == "LangGraph"
    assert result["workflow"]["status"] == "completed"
    assert result["workflow"]["completed_agents"] == [
        "strategist", "critic", "sales_coach", "report_synthesizer"
    ]
    assert result["analysis"]["overall_score"] == 73
    assert "Example competitor" in result["analysis"]["competitor_context"]
