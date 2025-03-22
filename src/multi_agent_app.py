import chainlit as cl
from multi_agent import run_news_workflow


async def get_news_by_topic(topic):
    # Create a message that we'll stream to
    stream_msg = cl.Message(content="")

    async for chunk in run_news_workflow(topic):
        if chunk["type"] == "raw_news":
            await cl.Message(content=chunk["content"]).send()

        if chunk["type"] == "stream":
            token = chunk["content"]
            await stream_msg.stream_token(token)

    # Make sure to call update after streaming is complete
    await stream_msg.update()


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Morning routine ideation",
            message="Can you help me create a personalized morning routine that would help increase my productivity throughout the day? Start by asking me about my current habits and what activities energize me in the morning.",
        ),
        cl.Starter(
            label="Explain superconductors",
            message="Explain superconductors like I'm five years old.",
        ),
    ]


@cl.on_message
async def main(message: cl.Message):
    """
    Main function to handle user messages and run the news workflow.
    """
    # Get the topic from the user message

    topic = message.content
    await get_news_by_topic(topic)
