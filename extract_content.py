import os
import sys

from browser_use.browser.browser import Browser, BrowserConfig

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio

from langchain_openai import ChatOpenAI

from browser_use import Agent


llm = ChatOpenAI(model='gpt-4o-mini', api_key='')

small_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.0, api_key='')

agent = Agent(
	task="Navigate to 'https://www.wellsfargo.com/help/security-and-fraud/passkey-faqs/' "
		 "and extract all the questions and answers with ',' separation and end answer with '|' ",
	llm=llm,
	page_extraction_llm=small_llm,
	browser=Browser(config=BrowserConfig(headless=False)),
)


async def main():
	history = await agent.run()

	result = history.final_result()
	print('Content Extracted is : ')
	print(result)


if __name__ == '__main__':
	asyncio.run(main())