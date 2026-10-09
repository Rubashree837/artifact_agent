import sys
import time
import threading

from agent import investigate_artifact, extract_final_answer
from memory import save_case


def show_loading(stop_event):
    """Display a live spinner while the agent investigates."""

    messages = [
        "Analyzing artifact description...",
        "Searching historical and museum records...",
        "Evaluating possible matches...",
        "Preparing investigation report..."
    ]

    spinner = ["|", "/", "-", "\\"]
    start_time = time.time()
    index = 0

    while not stop_event.is_set():
        elapsed = int(time.time() - start_time)
        message = messages[(index // 8) % len(messages)]
        symbol = spinner[index % len(spinner)]

        status = (
            f"\r{symbol} {message} "
            f"Elapsed: {elapsed}s"
        )

        sys.stdout.write(status)
        sys.stdout.flush()

        index += 1
        stop_event.wait(0.15)

    elapsed = int(time.time() - start_time)

    sys.stdout.write(
        f"\r✓ Investigation processing finished "
        f"in {elapsed}s.{' ' * 20}\n"
    )
    sys.stdout.flush()


def display_react_execution(result):
    """Display the agent's tool execution trace."""

    messages = result.get("messages", [])

    print("\n" + "=" * 60)
    print("REACT EXECUTION")
    print("=" * 60)

    for message in messages:

        message_type = message.__class__.__name__

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

                        text = item.get("text", "")

                        if text.strip():
                            print("\n[AGENT]")
                            print(text)

                    elif item_type in ("tool_use", "tool_call"):

                        tool_name = item.get(
                            "name",
                            item.get("tool_name", "unknown_tool")
                        )

                        tool_input = item.get(
                            "input",
                            item.get("args", {})
                        )

                        print("\n[AGENT → TOOL]")
                        print(f"Tool: {tool_name}")
                        print(f"Input: {tool_input}")

            # Handle standard LangChain tool calls
            tool_calls = getattr(message, "tool_calls", [])

            for tool_call in tool_calls:
                print("\n[AGENT → TOOL]")
                print(
                    f"Tool: {tool_call.get('name', 'unknown_tool')}"
                )
                print(
                    f"Input: {tool_call.get('args', {})}"
                )

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

        user_input = input("Artifact description: ").strip()

        if user_input.lower() == "exit":
            print("\nGoodbye!")
            break

        if not user_input:
            print("Please enter an artifact description.\n")
            continue

        print("\n" + "=" * 60)
        print("AGENT INVESTIGATION STARTED")
        print("=" * 60)

        stop_event = threading.Event()
        loading_thread = None
        investigation_start = time.time()

        try:

            loading_thread = threading.Thread(
                target=show_loading,
                args=(stop_event,),
                daemon=True
            )

            loading_thread.start()

            result = investigate_artifact(user_input)

            stop_event.set()
            loading_thread.join()

            print(
                f"\nTotal investigation time: "
                f"{time.time() - investigation_start:.2f} seconds"
            )

            display_react_execution(result)

            final_answer = extract_final_answer(result)

            print("\n" + "=" * 60)
            print("FINAL INVESTIGATION REPORT")
            print("=" * 60)

            print(final_answer)

            save_case(user_input, final_answer)

            print("\n✓ Investigation saved to memory.")

        except Exception as error:

            stop_event.set()

            if loading_thread and loading_thread.is_alive():
                loading_thread.join()

            print("\nAgent execution failed.")
            print(f"Error: {error}")

        print("\n")


if __name__ == "__main__":
    main()