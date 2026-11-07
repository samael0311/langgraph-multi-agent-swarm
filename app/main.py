import argparse
import sys
import uvicorn
from app.api import app
from app.state import SwarmState
from app.graph import compile_swarm_graph


def run_cli_research(query: str):
    """Executes a standalone research cycle directly from the command line."""
    print(f"\n[SWARM INIT] Starting autonomous research swarm for query: '{query}'")
    swarm = compile_swarm_graph()
    
    state = SwarmState(
        task_id="cli_task_001",
        user_query=query,
        constraints=["Grounded citations required", "Deterministic math verification"],
    )
    
    config = {"configurable": {"thread_id": "cli_session_1"}}
    result = swarm.invoke(state, config=config)
    
    print("\n" + "=" * 60)
    print("SWARM EXECUTION DELIVERABLE")
    print("=" * 60)
    if result.get("final_report"):
        print(result["final_report"].markdown_content)
    else:
        print(f"Status: {result.get('status')}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="LangGraph Multi-Agent Swarm CLI & Microservice")
    parser.add_argument("--query", type=str, help="Execute direct CLI research on this topic")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="FastAPI host")
    parser.add_argument("--port", type=int, default=8000, help="FastAPI port")
    parser.add_argument("--serve", action="store_true", help="Start the FastAPI microservice server")

    args = parser.parse_args()

    if args.query:
        run_cli_research(args.query)
    elif args.serve or len(sys.argv) == 1:
        print(f"Starting LangGraph Multi-Agent Swarm Server on http://{args.host}:{args.port}")
        uvicorn.run("app.api:app", host=args.host, port=args.port, reload=False)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
