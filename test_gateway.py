"""Verify CMU AI Gateway key + model ID, using the same call the app makes."""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=os.environ["OPENAI_BASE_URL"])
r = client.responses.create(
    model=os.environ["OPENAI_MODEL"],
    instructions="You are a concise assistant.",
    input="Reply with one short sentence confirming you're working.",
)
print(r.output_text)
