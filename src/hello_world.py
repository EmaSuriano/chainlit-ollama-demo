from agents import Agent, OpenAIChatCompletionsModel, Runner, AsyncOpenAI

# Set Ollama Model
model = OpenAIChatCompletionsModel(
    model="llama3.2",
    openai_client=AsyncOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="NOT_AN_API_KEY",
    ),
)

# Create an agent
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant",
    model=model,
)

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.
