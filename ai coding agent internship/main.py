from groq import Groq
from dotenv import load_dotenv
import os
import re
import subprocess

# --------------------------
# Helper Functions
# --------------------------

def save_code(code):
    with open("generated_code.py", "w", encoding="utf-8") as file:
        file.write(code)


def clean_code(code):
    code = re.sub(r"```python", "", code, flags=re.IGNORECASE)
    code = re.sub(r"```", "", code)
    return code.strip()


def execute_code():
    try:
        result = subprocess.run(
            ["python", "generated_code.py"],
            capture_output=True,
            text=True,
            timeout=5
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Execution timed out after 5 seconds"
        }


def log_attempt(attempt, code, result):
    with open("logs.txt", "a", encoding="utf-8") as log:

        log.write("\n" + "=" * 60 + "\n")
        log.write(f"ATTEMPT {attempt}\n")
        log.write("=" * 60 + "\n")

        log.write("\nCODE:\n")
        log.write(code)

        log.write("\n\nSTDOUT:\n")
        log.write(result["stdout"])

        log.write("\n\nSTDERR:\n")
        log.write(result["stderr"])

        status = "PASSED" if result["success"] else "FAILED"

        log.write(f"\n\nSTATUS: {status}\n")


# --------------------------
# Load API Key
# --------------------------

load_dotenv("apikey.env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ GROQ_API_KEY not found!")
    exit()

client = Groq(api_key=api_key)

# --------------------------
# System Prompt
# --------------------------

SYSTEM_PROMPT = """
You are a Python code generator.

Rules:
1. Return ONLY valid Python code.
2. Do not give explanations.
3. Do not use markdown.
4. Do not use triple backticks.
5. Return a COMPLETE executable Python program.
6. Include any assertions provided by the user.
7. Include all tests requested by the user.
"""

# --------------------------
# User Task
# --------------------------

task = input("Enter task description: ")

MAX_ATTEMPTS = 3
prompt = task

passed = False

# --------------------------
# Agent Loop
# --------------------------

for attempt in range(1, MAX_ATTEMPTS + 1):

    print("\n" + "=" * 60)
    print(f"ATTEMPT {attempt}")
    print("=" * 60)

    try:

        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        code = response.choices[0].message.content.strip()

        code = clean_code(code)
        # For demo: force first attempt to fail
        # if attempt == 1:
        #     code += "\nassert False"
        save_code(code)

        print("\nGenerated Code:\n")
        print(code)

        result = execute_code()

        print("\nSTDOUT:")
        print(result["stdout"])

        print("\nSTDERR:")
        print(result["stderr"])

        log_attempt(attempt, code, result)

        if result["success"]:
            print("\n✅ PASSED")
            passed = True
            break

        print("\n❌ FAILED")

        prompt = f"""
The following Python code failed when executed.

CODE:
{code}

ERROR:
{result['stderr']}

Please fix the code.

Return ONLY valid Python code.
"""

    except Exception as e:
        print(f"\n❌ Error: {e}")

# --------------------------
# Final Result
# --------------------------

if not passed:
    print("\n❌ Agent failed after 3 attempts.")