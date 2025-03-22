from agents import Agent, OpenAIChatCompletionsModel, AsyncOpenAI, Runner
import chainlit as cl
from openai.types.responses import ResponseTextDeltaEvent

model = OpenAIChatCompletionsModel(
    model="llama3.2",
    openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="mock"),
)

agent = Agent(
    name="News Assistant",
    instructions="You are a helpful assistant.",
    model=model,
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
