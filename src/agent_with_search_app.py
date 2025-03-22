from datetime import datetime
from agents import Agent, OpenAIChatCompletionsModel, AsyncOpenAI, Runner, function_tool
import chainlit as cl
from duckduckgo_search import DDGS
from openai.types.responses import ResponseTextDeltaEvent

from multi_agent import get_news_articles

model = OpenAIChatCompletionsModel(
    model="qwen2.5",
    openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="mock"),
)


@function_tool
def search_the_web(topic: str):
    """Search the web for news articles on a given topic"""
    print(f"Running DuckDuckGo news search for {topic}...")

    ddg_api = DDGS()

    current_date = datetime.now().strftime("%Y-%m")
    results = ddg_api.text(f"{topic} {current_date}", max_results=5)

    if results:
        print(results)
        news_results = "\n\n".join(
            [
                f"Title: {result['title']}\nURL: {result['href']}\nDescription: {result['body']}"
                for result in results
            ]
        )

        return news_results
    else:
        return f"Could not find news results for {topic}."


agent = Agent(
    name="News Assistant",
    instructions="You are a helpful assistant.",
    model=model,
    tools=[search_the_web],
)


@cl.on_chat_start
def start_chat():
    cl.user_session.set("message_history", [])


@cl.on_message
async def main(message: cl.Message):
    # Get the current message history
    message_history = cl.user_session.get("message_history")

    # Add the user's new message to history
    message_history.append({"role": "user", "content": message.content})

    # Create a message object for streaming
    msg = cl.Message(content="")

    # Prepare to collect the full response
    full_response = ""

    response = Runner.run_streamed(agent, input=message_history)

    try:
        async for event in response.stream_events():
            if event.type == "raw_response_event" and isinstance(
                event.data, ResponseTextDeltaEvent
            ):
                full_response += event.data.delta
                await msg.stream_token(event.data.delta)

        message_history.append({"role": "assistant", "content": full_response})

        # Update the session with the new message history
        cl.user_session.set("message_history", message_history)

        # Update the message (this is required even with streaming)
        await msg.update()

    except Exception as e:
        # Handle any errors
        await cl.Message(content=f"Error: {str(e)}", author="System").send()
