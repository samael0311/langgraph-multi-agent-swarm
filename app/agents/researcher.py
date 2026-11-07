from typing import Dict, Any, List
from app.state import SwarmState, EvidenceItem
from app.tools.search import LiveSearchTool


class ResearcherAgent:
    """
    Specialized Web Research Agent.
    Executes multi-hop searches across web and enterprise sources,
    extracts factual snippets, and formats evidence citations.
    """

    def __init__(self, search_tool: LiveSearchTool = None):
        self.search_tool = search_tool or LiveSearchTool()

    def research(self, state: SwarmState) -> Dict[str, Any]:
        """
        Executes targeted research based on user query and plan constraints.
        """
        queries = [
            state.user_query,
            f"{state.user_query} enterprise architecture benchmarks",
        ]
        
        # If in a revision loop, add targeted queries from audit feedback
        if state.audit and state.audit.missing_citations:
            for missing in state.audit.missing_citations[:2]:
                queries.append(f"{missing} authoritative data")

        collected_evidence: List[EvidenceItem] = list(state.evidence)
        seen_urls = {item.url for item in collected_evidence}

        for q in queries:
            results = self.search_tool.search(q)
            for res in results:
                if res.url not in seen_urls:
                    seen_urls.add(res.url)
                    collected_evidence.append(res)

        return {
            "evidence": collected_evidence,
            "status": "research_completed",
            "current_step": state.current_step + 1,
        }
