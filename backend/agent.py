from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv(Path(__file__).parents[1] / ".env")
if os.getenv("PORTKEY_API_KEY") and not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.environ["PORTKEY_API_KEY"]
    os.environ.setdefault("OPENAI_BASE_URL", "https://api.portkey.ai/v1")
from pydantic_ai import Agent, RunContext
from models import ChatReply, ProductCard, ChatDeps
from tools import search_catalogue
PROMPT = (Path(__file__).parent / 'prompts' / 'prompt.md').read_text()
agent = Agent('openai:gpt-4o-mini', system_prompt=PROMPT, output_type=ChatReply, deps_type=ChatDeps)
@agent.tool
async def find_products(ctx: RunContext[ChatDeps], query: str) -> list[ProductCard]: return search_catalogue(query)
@agent.tool
async def product_details(ctx: RunContext[ChatDeps], product_id: str) -> ProductCard | None:
    from tools import get_product_details
    return get_product_details(product_id)
@agent.tool
async def product_stock(ctx: RunContext[ChatDeps], product_id: str) -> dict:
    from tools import check_stock
    return check_stock(product_id)
