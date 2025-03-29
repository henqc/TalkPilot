from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig
from browser_use.browser.context import BrowserContext
from browser_use.browser.context import BrowserContextConfig
import asyncio
from dotenv import load_dotenv

load_dotenv()

# async def main():
#     agent = Agent(
#         task="watch a mr beast video on youtube",
#         llm=ChatOpenAI(model="gpt-4o"),
#         browser_context=context,
#     )
#     await agent.run()

config = BrowserConfig(
    headless=False
)
browser = Browser(config=config)

context_config = BrowserContextConfig(
    wait_for_network_idle_page_load_time=3.0,
    browser_window_size={'width': 1920, 'height': 1080},
    locale='en-US',
    # user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    highlight_elements=True,
)

context = BrowserContext(browser=browser, config=context_config)

# Create the agent with your configured browser
agent = Agent(
    task="watch a mr beast video on youtube",
    llm=ChatOpenAI(model="gpt-4o"),
    browser_context=context,
)

async def main():
    await agent.run()

    input("Press Enter to close the browser...")
    await browser.close()


asyncio.run(main())
