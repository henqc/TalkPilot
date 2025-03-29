# In testing.py
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig, Controller, ActionResult
from browser_use.browser.context import BrowserContext
from browser_use.browser.context import BrowserContextConfig
import asyncio
from dotenv import load_dotenv

# Global variables
browser = None
browser_context = None
loop = None

# Initialize everything
def init_browser():
    global browser, browser_context, loop
    
    # Create event loop if it doesn't exist
    if loop is None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Initialize browser if it doesn't exist
    if browser is None:
        config = BrowserConfig(headless=False)
        browser = Browser(config=config)
        
    # Create context config
    context_config = BrowserContextConfig(
        wait_for_network_idle_page_load_time=3.0,
        browser_window_size={"width": 1920, "height": 1080},
        locale="en-US",
        highlight_elements=True,
    )
    
    # Create browser context if it doesn't exist
    if browser_context is None:
        browser_context = BrowserContext(browser=browser, config=context_config)
    
    return browser_context

async def run_agent(transcript):
    print('\n \n \n \n agent received transcript: ', transcript)
    
    global browser_context
    
    # Ensure browser context is initialized
    if browser_context is None:
        browser_context = init_browser()
    
    agent = Agent(
        browser_context=browser_context,
        task=transcript,
        llm=ChatOpenAI(model="gpt-4o"),
        use_vision=True,
    )
    
    try:
        history = await agent.run()
        result = history.final_result()
        return result
    except Exception as e:
        print(f"Error during agent run: {e}")
        return f"I encountered an error: {str(e)}"

def cleanup_resources():
    global browser, browser_context, loop
    
    # Clean up in the correct event loop
    if loop and browser_context:
        try:
            loop.run_until_complete(browser_context.close())
        except Exception as e:
            print(f"Error closing browser context: {e}")
    
    if loop and browser:
        try:
            loop.run_until_complete(browser.close())
        except Exception as e:
            print(f"Error closing browser: {e}")
    
    # Close the event loop
    if loop:
        try:
            loop.close()
        except Exception as e:
            print(f"Error closing event loop: {e}")
        
    browser = None
    browser_context = None
    loop = None