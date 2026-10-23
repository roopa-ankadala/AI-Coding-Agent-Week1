from groq import Groq
from dotenv import load_dotenv
import os
import re

# Load API key
load_dotenv("apikey.env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("Error: GROQ_API_KEY not found!")
    exit()

client = Groq(api_key=api_key)

SYSTEM_PROMPT = """
You are a Python code generator.

Rules:
1. Return ONLY valid Python code.
2. Do not give explanations.
3. Do not use markdown.
4. Do not use triple backticks.
5. Output executable Python code only.
"""

task = input("Enter task description: ")

try:
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task}
        ],
        temperature=0.2
    )

    code = response.choices[0].message.content.strip()

    # Remove markdown code fences if model adds them
    code = re.sub(r"```python", "", code, flags=re.IGNORECASE)
    code = re.sub(r"```", "", code).strip()

    print("\nGenerated Code:\n")
    print(code)

    with open("generated_code.py", "w", encoding="utf-8") as file:
        file.write(code)

    print("\n✅ Code saved to generated_code.py")

except Exception as e:
    print(f"\n❌ Error: {e}")