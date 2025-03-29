from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig, Controller, ActionResult
from browser_use.browser.context import BrowserContext
from browser_use.browser.context import BrowserContextConfig
import asyncio
from dotenv import load_dotenv
# from backend.picovoice import audio_tts, play_audio

# @controller.action('Ask user for information')
# def ask_human(question: str) -> str:
#     answer = input(f'\n{question}\nInput: ')
#     return ActionResult(extracted_content=answer)

# @controller.action('run this method after each action to let the user know what is happening')
# def speak_about_action(action: str) -> None:
#     audio_tts(action)
#     play_audio("backend/output.wav")


async def run_agent(transcript):
    load_dotenv()
    
    try:
        await browser.close();
    except:
        print('Error or something closing previous browser.')

    config = BrowserConfig(headless=False)
    browser = Browser(config=config)

    context_config = BrowserContextConfig(
        wait_for_network_idle_page_load_time=3.0,
        browser_window_size={"width": 1920, "height": 1080},
        locale="en-US",
        # user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        highlight_elements=True,
    )

    context = BrowserContext(browser=browser, config=context_config)

    initial_actions = [
        {"go_to_url": {"url": "https://www.google.com"}},
    ]

    controller = Controller()
    
    agent = Agent(
        browser_context=context,
        # initial_actions=initial_actions,
        task=transcript,
        llm=ChatOpenAI(model="gpt-4o"),
        # planner_llm=ChatOpenAI(model="o3-mini"),
        # use_vision_for_planner=False,
        # planner_interval=4,
        use_vision=True,
        # controller=controller,
    )
    
    history = await agent.run()
    result = history.final_result()
    return result