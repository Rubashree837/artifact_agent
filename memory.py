import json
import os
from datetime import datetime


MEMORY_FILE = "artifact_memory.json"


def load_memory():
    """
    Load previous artifact investigations from disk.
    """

    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if not isinstance(data, list):
                return []

            return data

    except (
        json.JSONDecodeError,
        OSError
    ):
        return []


def save_case(
    user_input,
    investigation_report
):
    """
    Save one completed investigation.
    """

    memory = load_memory()

    case = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_input,
        "investigation_report": investigation_report
    }

    memory.append(case)

    try:
        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                memory,
                file,
                indent=4,
                ensure_ascii=False
            )

    except OSError as error:
        print(f"Warning: Could not save memory: {error}")


def get_recent_cases(limit=3):
    """
    Get the most recent valid investigation cases.
    """

    memory = load_memory()

    valid_cases = []

    for case in memory:

        if not isinstance(case, dict):
            continue

        if (
            "user_input" not in case
            or "investigation_report" not in case
        ):
            continue

        valid_cases.append(case)

    return valid_cases[-limit:]


def build_memory_context(limit=3):
    """
    Convert recent investigations into context
    that can be given to the agent.
    """

    recent_cases = get_recent_cases(limit)

    if not recent_cases:
        return (
            "No previous artifact investigations "
            "are available."
        )

    context = [
        "PREVIOUS ARTIFACT INVESTIGATIONS:"
    ]

    for index, case in enumerate(
        recent_cases,
        start=1
    ):

        context.append(
            f"\nCASE {index}"
        )

        context.append(
            f"Previous input: "
            f"{case.get('user_input', 'Unknown')}"
        )

        context.append(
            "Previous report:\n"
            f"{case.get('investigation_report', 'Unknown')}"
        )

    return "\n".join(context)