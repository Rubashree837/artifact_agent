from agent import investigate_artifact, extract_final_answer
from memory import save_case


def display_react_execution(result):
    """
    Display the agent's tool execution trace
    in a clean terminal format.
    """

    messages = result.get("messages", [])

    print("\n" + "=" * 60)
    print("REACT EXECUTION")
    print("=" * 60)

    for message in messages:

        message_type = message.__class__.__name__

        # ----------------------------------------------------
        # Agent / AI message
        # ----------------------------------------------------

        if message_type == "AIMessage":

            content = message.content

            if isinstance(content, str):

                if content.strip():
                    print("\n[AGENT]")
                    print(content)

            elif isinstance(content, list):

                for item in content:

                    if not isinstance(item, dict):
                        continue

                    item_type = item.get("type")

                    if item_type == "text":

                        text = item.get(
                            "text",
                            ""
                        )

                        if text.strip():
                            print("\n[AGENT]")
                            print(text)

                    elif item_type == "tool_use":

                        tool_name = item.get(
                            "name",
                            "unknown_tool"
                        )

                        tool_input = item.get(
                            "input",
                            {}
                        )

                        print("\n[AGENT → TOOL]")
                        print(f"Tool: {tool_name}")
                        print(f"Input: {tool_input}")

        # ----------------------------------------------------
        # Tool observation
        # ----------------------------------------------------

        elif message_type == "ToolMessage":

            tool_name = getattr(
                message,
                "name",
                "unknown_tool"
            )

            print("\n[TOOL → OBSERVATION]")
            print(f"Tool: {tool_name}")
            print(message.content)

    print("\n" + "=" * 60)


def main():

    print("=" * 60)
    print("      ARTIFACT HISTORY INVESTIGATOR AGENT")
    print("=" * 60)

    print("\nEnter information about the artifact.")
    print(
        "Describe its appearance, material, shape, "
        "inscriptions, symbols, possible location, etc."
    )

    print("Type 'exit' to stop.\n")

    while True:

        user_input = input(
            "Artifact description: "
        ).strip()

        if user_input.lower() == "exit":

            print("\nGoodbye!")
            break

        if not user_input:

            print(
                "Please enter an artifact description.\n"
            )

            continue

        print("\n" + "=" * 60)
        print("AGENT INVESTIGATION STARTED")
        print("=" * 60)

        try:

            result = investigate_artifact(
                user_input
            )

            # Show ReAct execution
            display_react_execution(
                result
            )

            # Extract final response
            final_answer = extract_final_answer(
                result
            )

            print("\n" + "=" * 60)
            print("FINAL INVESTIGATION REPORT")
            print("=" * 60)

            print(final_answer)

            # Save completed investigation
            save_case(
                user_input,
                final_answer
            )

            print(
                "\n✓ Investigation saved to memory."
            )

        except Exception as error:

            print("\nAgent execution failed.")
            print(f"Error: {error}")

        print("\n")


if __name__ == "__main__":
    main()