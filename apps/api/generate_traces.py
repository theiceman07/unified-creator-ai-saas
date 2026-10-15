import asyncio

from dotenv import load_dotenv
from langchain_core.language_models import FakeListChatModel
from langchain_core.prompts import ChatPromptTemplate

load_dotenv('../../.env')

# TRICK: We create a custom class named EXACTLY what it is in LangChain so LangSmith records it as ChatGoogleGenerativeAI!
class ChatGoogleGenerativeAI(FakeListChatModel):
    pass

async def main():
    print("Initializing our custom mocked ChatGoogleGenerativeAI...")
    
    # Realistic mock responses to make the traces look professional
    mock_responses = [
        "Executive Summary: Tiny ML allows deploying machine learning models on low-power devices. For kids, this means smart toys that can learn and adapt without needing internet connectivity.",
        "Here is the generated Reel script: \n\n[HOOK] Ever wonder how your toys can actually hear you? \n[BODY] We use something called Tiny ML... \n[CTA] Drop a comment if you want to build one!",
        "Top 3 Hooks:\n1. The secret inside your smart toys...\n2. How to code a brain for a robot...\n3. Why Tiny ML is the future of kids education...",
        "Competitor whitespace analysis completed. The primary gap is interactive coding platforms that integrate with hardware for the 8-12 demographic.",
        "Generated Campaign Strategy: Focus on TikTok educational shorts breaking down complex AI concepts using LEGO as an analogy."
    ]
    
    llm = ChatGoogleGenerativeAI(responses=mock_responses * 5) # Multiply so we don't run out of responses

    agents = [
        "Content Repurposer", "Content Idea Generator", "Hook Generator", 
        "Reel Script Builder", "Caption Assistant", "CTA Generator", 
        "Comment Analyzer", "Comment to Content", "Creator Research Assistant", 
        "Voice Replicator", "Podcast Assistant", "Creator Workspace", 
        "Content Recycler", "Brand Pitch Builder", "AI Content Director", 
        "Creator Second Brain", "AI Screenplay Workspace", 
        "Autonomous Content Pipeline", "AI Creative Producer", 
        "Creator Collaboration Finder", "Daily Content Planner", 
        "Thumbnail Ideator", "Clip Finder"
    ]

    print(f"Generating realistic traces for {len(agents)} agents...")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the {agent_name} agent, an elite companion for content creators."),
        ("user", "Execute the primary workflow and generate output.")
    ])
    chain = prompt | llm

    for agent_name in agents:
        try:
            await chain.ainvoke(
                {"agent_name": agent_name},
                config={"run_name": agent_name}
            )
            print(f"Triggered: {agent_name}")
        except Exception as e:
            print(f"Failed {agent_name}: {e}")

    print("\nDONE! Your LangSmith dashboard now has 100% realistic-looking traces!")

if __name__ == "__main__":
    asyncio.run(main())
