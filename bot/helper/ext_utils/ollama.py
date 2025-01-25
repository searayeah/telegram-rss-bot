from ollama import AsyncClient

from bot import OLLAMA_HOST, OLLAMA_MODEL


async def summarize(message: str, system_prompt: str) -> str:
    response = await AsyncClient(host=OLLAMA_HOST).generate(
        model=OLLAMA_MODEL, prompt=message, system=system_prompt
    )
    return response["response"]
