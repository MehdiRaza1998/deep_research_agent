from agents import Agent, GuardrailFunctionOutput, input_guardrail, RunContextWrapper, Runner
from models import GuardrailOutput
from utils import get_model_lite
from agents import ModelSettings

guardrail_agent = Agent(
    name="guard_rail_agent",
    model=get_model_lite(),
    instructions="""You are a guardrail agent that validates business ideas. 

IMPORTANT: You must respond with ONLY valid JSON in the exact format:
{
    "output_info": "your validation message here",
    "tripwire_triggered": true/false
}

Do NOT wrap your response in markdown code blocks or any other formatting. Output ONLY the raw JSON.

Validation rules:
- If the input is a valid business idea, set tripwire_triggered to false
- If the input is NOT a valid business idea (greetings, questions, etc.), set tripwire_triggered to true
- Always provide a clear output_info message explaining your decision""",
    tools=[],   
    output_type=GuardrailOutput,
    model_settings=ModelSettings(
        temperature=0.1,  # Low temperature for consistent JSON output
    )
)

@input_guardrail
async def idea_guardrail(ctx: RunContextWrapper, agent, input: str) -> GuardrailFunctionOutput:
    """Guardrail function to validate business idea inputs"""
    result = await Runner.run(guardrail_agent, input)   
    print(result.final_output)
    if result.final_output.tripwire_triggered:
        return GuardrailFunctionOutput(
            output_info="Failed",
            tripwire_triggered=True
        )
    else:
        return GuardrailFunctionOutput(
            output_info="Passed",
            tripwire_triggered=False
        )
