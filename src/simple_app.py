import chainlit as cl
import requests
import json


@cl.on_chat_start
def start_chat():
    # Initialize the message history with a system prompt
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )


@cl.on_message
async def main(message: cl.Message):
    # Get the current message history
    message_history = cl.user_session.get("message_history")

    # Add the user's new message to history
    message_history.append({"role": "user", "content": message.content})

    # Create a message object for streaming
    msg = cl.Message(content="")

    try:
        # Set up the request to Ollama's API
        response = requests.post(
            "http://localhost:11434/api/chat",  # Using the chat endpoint instead of generate
            json={
                "model": "llama3.2",  # Change to your preferred model
                "messages": message_history,  # Pass the entire message history
                "stream": True,  # Enable streaming
            },
            stream=True,  # Important for requests to stream the response
        )

        # Prepare to collect the full response
        full_response = ""

        # Process the streaming response
        for line in response.iter_lines():
            if line:
                # Parse the JSON line
                json_line = json.loads(line)

                # Check if this is a content token
                if "message" in json_line and "content" in json_line["message"]:
                    token = json_line["message"]["content"]
                    full_response += token
                    # Stream the token to the UI
                    await msg.stream_token(token)

                # Check if this is the end of the stream
                if json_line.get("done", False):
                    break

        # Add the assistant's response to the message history
        message_history.append({"role": "assistant", "content": full_response})

        # Update the session with the new message history
        cl.user_session.set("message_history", message_history)

        # Update the message (this is required even with streaming)
        await msg.update()

    except Exception as e:
        # Handle any errors
        await cl.Message(content=f"Error: {str(e)}", author="System").send()
