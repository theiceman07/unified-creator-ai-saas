import os


def set_langsmith_tags(mode: str, capability: str, origin: str):
    # Setup tags for LangSmith trace
    tags = [f"mode:{mode}", f"cap:{capability}"]
    if origin:
        tags.append(f"origin:{origin}")
    os.environ["LANGCHAIN_TAGS"] = ",".join(tags)

def get_trace_url(run_id: str) -> str:
    # Helper to build a LangSmith trace URL
    return f"https://smith.langchain.com/o/default/projects/p/creatoros-demo?run_id={run_id}"
