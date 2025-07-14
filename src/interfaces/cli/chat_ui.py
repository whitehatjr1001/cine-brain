import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.markdown import Markdown
from rich.text import Text

from src.graph.graph import graph
from langchain_core.messages import HumanMessage, AIMessage

console = Console()

async def chat_ui():
    console.print(Panel("[bold green]Welcome to CineBrain AI Companion![/bold green]", expand=False))
    console.print("[italic]Type 'quit' or 'exit' to end the chat.[/italic]")

    while True:
        user_input = console.input("[bold blue]You:[/bold blue] ").strip()

        if user_input.lower() in ["quit", "exit"]:
            console.print("[bold red]Ending chat. Goodbye![/bold red]")
            break

        if not user_input:
            continue

        try:
            # Prepare the initial state with the user's message
            # The graph expects a list of messages
            initial_state = {"messages": [HumanMessage(content=user_input)]}

            # Use Live to show thinking process
            with Live(
                Text("CineBrain is thinking...", style="italic yellow"),
                console=console,
                vert_align="top",
                refresh_per_second=8
            ) as live:
                # Invoke the graph
                # Assuming the graph returns a state object with a 'messages' key
                # And the last message in 'messages' is the AI's response
                response_state = await graph.ainvoke(initial_state)
                
                # Extract the last AI message
                ai_response_message = None
                if response_state and "messages" in response_state:
                    for msg in reversed(response_state["messages"]):
                        if isinstance(msg, AIMessage):
                            ai_response_message = msg.content
                            break
                
                if ai_response_message:
                    live.update(Panel(Markdown(ai_response_message), title="[bold green]CineBrain[/bold green]", title_align="left", border_style="green"), refresh=True)
                else:
                    live.update(Panel("[italic red]CineBrain did not provide a response.[/italic red]", title="[bold red]Error[/bold red]", title_align="left", border_style="red"), refresh=True)
                live.stop() # Stop the live display immediately after updating
                
        except Exception as e:
            console.print(Panel(f"[bold red]An error occurred: {e}[/bold red]", title="[bold red]Error[/bold red]", title_align="left", border_style="red"))

if __name__ == "__main__":
    asyncio.run(chat_ui()) 