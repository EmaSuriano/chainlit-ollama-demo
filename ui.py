import chainlit as cl
from multi_agent import run_news_workflow


@cl.on_message
async def main(message: cl.Message):
    """
    Main function to handle user messages and run the news workflow.
    """
    # Get the topic from the user message
    topic = message.content

    # Send a thinking message
    await cl.Message(
        content=f"Searching for news about '{topic}'...", author="News Bot"
    ).send()

    try:
        # Run the news workflow
        news_content = run_news_workflow(topic)

        # Send the result back to the user
        await cl.Message(content=news_content, author="News Bot").send()
    except Exception as e:
        # Handle any errors
        await cl.Message(
            content=f"Error fetching news: {str(e)}", author="News Bot"
        ).send()


@cl.on_chat_start
async def start():
    """
    Function that runs when a new chat session starts.
    """
    # Send a welcome message
    await cl.Message(
        content="Welcome to the News Assistant! What topic would you like to get news about?",
        author="News Bot",
    ).send()
