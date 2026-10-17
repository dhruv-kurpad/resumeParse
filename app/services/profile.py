from anthropic import Anthropic

from app.schemas import ResumeProfile

PROMPT = """Extract the candidate's profile from the resume text below.
Only use information that appears in the text. Use null or an empty list for anything missing; do not guess.
The text came from OCR, so fix obvious spacing errors (e.g. "github. com" -> "github.com").

Resume:
{text}"""


class ClaudeProfileBuilder:
    def __init__(self, api_key: str, model: str):
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def build(self, text: str) -> ResumeProfile:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            tools=[
                {
                    "name": "save_profile",
                    "description": "Save the structured resume profile.",
                    "input_schema": ResumeProfile.model_json_schema(),
                }
            ],
            tool_choice={"type": "tool", "name": "save_profile"},
            messages=[{"role": "user", "content": PROMPT.format(text=text)}],
        )

        tool_call = next(block for block in response.content if block.type == "tool_use")
        return ResumeProfile.model_validate(tool_call.input)
