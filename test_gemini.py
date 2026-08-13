from llm.gemini_provider import GeminiProvider

provider = GeminiProvider()

response = provider.generate(
    prompt="Say hello in one sentence."
)

print(response)