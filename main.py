import asyncio
from legal_consult_agent.agent import graph

async def main():
    print("Starting chatbot...")
    print("=" * 50)
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "q", "quit", "bye"]:
            print("Exiting chatbot...")
            break
        else:
            config = {"configurable": {"thread_id": "1"}}
            res = await graph.ainvoke(
                input={"question": user_input},
                config=config,
            )
            print(f"AI: {res['messages'][-1].content}")

if __name__ == "__main__":
    asyncio.run(main())
