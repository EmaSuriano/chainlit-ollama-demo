from duckduckgo_search import DDGS
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool
from datetime import datetime
from openai.types.responses import ResponseTextDeltaEvent
import asyncio
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional


model = OpenAIChatCompletionsModel(
    model="llama3.2",
    openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="mock"),
)


class NewsArticle(BaseModel):
    """Model for a single news article from search results"""

    title: str = Field(..., description="The title of the news article")
    href: str = Field(..., description="The URL of the news article")
    body: str = Field(
        ..., description="The description or snippet of the news article content"
    )

    def format(self) -> str:
        """Format the article for display"""
        return f"Title: {self.title}\nURL: {self.href}\nDescription: {self.body}"


# 1. Create Internet Search Tool


@function_tool
def get_news_articles(topic: str):
    """Search for news articles on a given topic"""
    print(f"Running DuckDuckGo news search for {topic}...")

    ddg_api = DDGS()

    current_date = datetime.now().strftime("%Y-%m")
    results = ddg_api.text(f"{topic} {current_date}", max_results=5)

    if results:
        news_results = "\n\n".join(
            [NewsArticle.model_validate(result).format() for result in results]
        )

        return news_results
    else:
        return f"Could not find news results for {topic}."


# 2. Create AI Agents

# News Agent to fetch news
news_agent = Agent(
    name="News Assistant",
    instructions="You provide the latest news articles for a given topic using DuckDuckGo search.",
    tools=[get_news_articles],
    model=model,
)

# Editor Agent to edit news
editor_agent = Agent(
    name="Editor Assistant",
    instructions="Rewrite and give me as news article ready for publishing. Each News story in separate section.",
    model=model,
)


# 3. Create workflow
async def run_news_workflow(topic):
    print("Running news Agent workflow...")

    yield {"type": "get_news", "content": f"Getting news about {topic}..."}

    # Step 1: Fetch news
    news_response = await Runner.run(news_agent, f"Get me the news about {topic}")

    # Access the content from RunResult object
    raw_news = news_response.final_output

    yield {"type": "raw_news", "content": raw_news}

    # Step 2: Pass news to editor for final review
    edited_news_response = Runner.run_streamed(editor_agent, input=raw_news)

    async for event in edited_news_response.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data, ResponseTextDeltaEvent
        ):
            yield {"type": "stream", "content": event.data.delta}


if __name__ == "__main__":
    asyncio.run(run_news_workflow("AI"))
