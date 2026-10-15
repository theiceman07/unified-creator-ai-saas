import asyncio

from app.orchestration.registry import registry
from app.platform.judge import judge


async def run_checks():
    print("--- 1. Checking Agents ---")
    try:
        registry.load('../../capability_registry.yaml')
        count = len(registry.capabilities)
        print(f"Total agents registered: {count}")
        for name in registry.capabilities:
            print(f" - {name}")
    except Exception as e:
        print(f"Agent Registry Error: {e}")

    print("\n--- 2. Checking LLM Judge ---")
    try:
        res = await judge.judge_asset(
            asset_id="test",
            capability="script",
            content="Testing the judge output"
        )
        print("Judge successfully returned grading:")
        print(f"Overall Score: {res.get('overall')}")
        print(f"Passed: {res.get('passed')}")
        print(f"Critique: {res.get('critique')}")
    except Exception as e:
        print(f"Judge Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_checks())
