import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

from tools import (
    artifact_search,
    historical_search,
    timeline_tool
)

from memory import build_memory_context


load_dotenv()


# ============================================================
# GEMINI LLM
# ============================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)


# ============================================================
# TOOLS AVAILABLE TO THE AGENT
# ============================================================

tools = [
    artifact_search,
    historical_search,
    timeline_tool
]


# ============================================================
# AGENT INSTRUCTIONS
# ============================================================

SYSTEM_PROMPT = """
You are the Artifact History Investigator Agent.

Your task is to investigate an unknown artifact and reconstruct
its historical context using evidence from real external sources.

You are NOT an authentication or provenance verification system.

You must reason using the available tools.

INVESTIGATION GOALS:

1. Identify the most likely artifact type.
2. Estimate a plausible historical period.
3. Identify possible geographical or cultural associations.
4. Explain likely historical use.
5. Identify relevant historical developments.
6. Find similar objects in museum or heritage collections.
7. Clearly separate evidence from inference.
8. Report uncertainty and confidence.

EVIDENCE RULES:

- Museum and heritage records are evidence about the records
  themselves and about comparable objects.
- A similar museum object does NOT prove that the user's object
  is the same object.
- Do not claim that the user's artifact is authentic.
- Do not claim an exact date unless the retrieved evidence
  supports that date.
- Do not claim a specific geographic origin unless evidence
  supports it.
- Do not treat general model knowledge as retrieved evidence.
- Never invent museum records, IDs, dates, URLs, or historical
  facts.
- If evidence is insufficient, explicitly say so.
- Physical wear alone must NOT be treated as proof of age.
- Multiple possible origins should be presented when the evidence
  cannot distinguish between them.

TOOL USAGE:

- Start with artifact_search when the object description can
  be compared with museum collections.
- Use historical_search for relevant historical entities,
  terminology, cultures, materials, or object types.
- Use timeline_tool only after proposing a historically plausible
  date range.
- Avoid repeated searches with almost identical queries.
- Use different evidence sources when useful.

REASONING:

Before making a conclusion, consider:

OBSERVED INFORMATION:
What did the user actually tell you?

SOURCE EVIDENCE:
What do the external tools actually show?

INFERENCE:
What can reasonably be inferred by comparing the observations
with the retrieved evidence?

UNCERTAINTY:
What cannot be determined from the available information?

FINAL REPORT:

ARTIFACT HISTORY INVESTIGATION

Observed Description:
...

Likely Identification:
...

Historical Period:
...

Possible Origin:
...

Likely Use:
...

Historical Context:
...

Source Evidence:
...

Reasoning / Inference:
...

Confidence:
High / Medium / Low

Uncertainty:
...

Sources:
...

Remember:
A historical investigation can produce a plausible hypothesis,
not necessarily a verified identification.
"""


# ============================================================
# CREATE REACT AGENT
# ============================================================

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT
)


# ============================================================
# RUN INVESTIGATION
# ============================================================

def investigate_artifact(user_input):
    """
    Run the Artifact History Investigator agent.
    """

    memory_context = build_memory_context()

    complete_prompt = f"""
Previous investigation memory:

{memory_context}

----------------------------------------

Current artifact investigation request:

{user_input}

Investigate this artifact using the available tools.
"""

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": complete_prompt
                }
            ]
        }
    )

    return result


# ============================================================
# EXTRACT FINAL TEXT
# ============================================================

def extract_final_answer(result):
    """
    Extract only the final textual response from Gemini.

    Gemini may return structured content containing internal
    metadata/signatures. We only display the actual text.
    """

    messages = result.get(
        "messages",
        []
    )

    if not messages:
        return "No response was produced by the agent."

    final_message = messages[-1]

    content = final_message.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, dict):

                if item.get("type") == "text":

                    text = item.get(
                        "text",
                        ""
                    )

                    if text:
                        text_parts.append(text)

        if text_parts:
            return "\n".join(text_parts)

    return str(content)