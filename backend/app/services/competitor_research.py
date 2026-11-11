"""Live competitor discovery and source-linked competitive research.

Tavily supplies web search results. The selected LLM extracts structured findings
only from those retrieved results; every citation is restricted to a known source ID.
"""
from __future__ import annotations

from typing import Literal
import re

import httpx
from pydantic import BaseModel, Field

from app.config import settings
from app.services.agent_llm import generate_structured


class CompetitorDiscovery(BaseModel):
    competitors: list[str] = Field(default_factory=list, max_length=12)


class CompetitorFinding(BaseModel):
    name: str
    summary: str
    positioning: str
    products_and_features: list[str] = Field(default_factory=list)
    pricing_observations: list[str] = Field(default_factory=list)
    differentiators: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    limitations_or_gaps: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"] = "low"
    caveats: list[str] = Field(default_factory=list)


class ResearchSynthesis(BaseModel):
    market_overview: str
    competitive_themes: list[str] = Field(default_factory=list)
    pitch_opportunities: list[str] = Field(default_factory=list)
    findings: list[CompetitorFinding] = Field(default_factory=list)


def _search_tavily(query: str, max_results: int = 5) -> list[dict]:
    if not settings.TAVILY_API_KEY:
        raise ValueError("Live research is not configured. Add TAVILY_API_KEY to backend/.env.")
    response = httpx.post(
        "https://api.tavily.com/search",
        json={
            "api_key": settings.TAVILY_API_KEY,
            "query": query,
            "search_depth": "advanced",
            "max_results": max_results,
            "include_answer": False,
            "include_raw_content": False,
        },
        timeout=25.0,
    )
    response.raise_for_status()
    payload = response.json()
    return [
        {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": (item.get("content", "") or "")[:1800],
            "score": item.get("score"),
            "published_date": item.get("published_date"),
        }
        for item in payload.get("results", [])
        if item.get("url") and item.get("content")
    ]


def _normalise_names(names: list[str], exclude: str) -> list[str]:
    excluded = exclude.casefold().strip()
    output, seen = [], {excluded}
    for name in names:
        clean = re.sub(r"\s+", " ", name).strip(" \t\r\n,.;")
        key = clean.casefold()
        if clean and key not in seen and len(clean) <= 100:
            output.append(clean)
            seen.add(key)
        if len(output) >= 10:
            break
    return output


def run_competitor_research(
    company_name: str,
    industry: str,
    competitors: list[str],
    research_mode: str,
    provider: str,
) -> dict:
    """Discover and research competitors; citations can only reference retrieved URLs."""
    company = company_name.strip()
    if not company:
        raise ValueError("company_name is required")
    if research_mode not in {"automatic", "manual", "both"}:
        raise ValueError("research_mode must be automatic, manual or both")

    source_rows: list[dict] = []
    discovery_candidates: list[str] = []
    if research_mode in {"automatic", "both"}:
        discovery_query = (
            f"leading competitors and alternatives to {company} in {industry or 'its market'} "
            "companies products"
        )
        discovery_sources = _search_tavily(discovery_query, 8)
        source_rows.extend(discovery_sources)
        discovery_payload = "\n".join(
            f"TITLE: {s['title']}\nURL: {s['url']}\nSNIPPET: {s['content']}"
            for s in discovery_sources
        )
        discovered = generate_structured(
            provider=provider,
            schema=CompetitorDiscovery,
            system_prompt=(
                "Identify actual competing companies explicitly supported by the supplied "
                "search results. Exclude the subject company, customers, publishers and "
                "products that are not companies. Do not use outside knowledge. Return JSON."
            ),
            user_prompt=f"Subject company: {company}\nIndustry: {industry}\nSearch results:\n{discovery_payload}",
        )
        discovery_candidates = discovered.competitors

    manual_candidates = competitors if research_mode in {"manual", "both"} else []
    selected = _normalise_names(
        (discovery_candidates if research_mode != "manual" else []) + manual_candidates,
        company,
    )
    if not selected:
        raise ValueError("No competitors were found. Try manual mode or provide competitor names.")

    for name in selected:
        source_rows.extend(_search_tavily(
            f"{name} official website products features pricing positioning {industry}",
            4,
        ))

    unique_sources, seen_urls = [], set()
    for source in source_rows:
        url = source["url"]
        if url not in seen_urls:
            seen_urls.add(url)
            unique_sources.append({**source, "source_id": f"S{len(unique_sources) + 1}"})
    source_context = "\n\n".join(
        f"ID: {s['source_id']}\nTITLE: {s['title']}\nURL: {s['url']}\n"
        f"PUBLISHED: {s.get('published_date') or 'Not provided'}\nCONTENT: {s['content']}"
        for s in unique_sources
    )
    synthesis = generate_structured(
        provider=provider,
        schema=ResearchSynthesis,
        system_prompt=(
            "You are a careful competitive-intelligence analyst. Use only the supplied "
            "search-result content. Do not infer unavailable pricing, market share, customer "
            "counts, performance or feature claims. Say 'not found in retrieved sources' "
            "when evidence is absent. Every finding must cite one or more exact source IDs "
            "that support it. Never invent IDs or URLs. Keep competitor identities distinct. "
            "Return only schema-conforming JSON."
        ),
        user_prompt=(
            f"Subject company: {company}\nIndustry: {industry or 'Not specified'}\n"
            f"Competitors to research: {', '.join(selected)}\n\n"
            f"RETRIEVED WEB SOURCES:\n{source_context}"
        ),
    )
    valid_ids = {s["source_id"] for s in unique_sources}
    findings = []
    for finding in synthesis.findings:
        item = finding.model_dump()
        item["source_ids"] = [sid for sid in item["source_ids"] if sid in valid_ids]
        if not item["source_ids"]:
            item["caveats"] = item["caveats"] + [
                "No valid source ID was returned for this finding; treat it as unverified."
            ]
            item["confidence"] = "low"
        findings.append(item)

    cited_ids = {sid for finding in findings for sid in finding["source_ids"]}
    citations = [
        {
            "source_id": s["source_id"],
            "title": s["title"],
            "url": s["url"],
            "published_date": s.get("published_date"),
            "snippet": s["content"],
            "used_in_report": s["source_id"] in cited_ids,
        }
        for s in unique_sources
    ]
    return {
        "company_name": company,
        "industry": industry,
        "research_mode": research_mode,
        "discovered_competitors": _normalise_names(discovery_candidates, company),
        "competitors_researched": selected,
        "market_overview": synthesis.market_overview,
        "competitive_themes": synthesis.competitive_themes,
        "pitch_opportunities": synthesis.pitch_opportunities,
        "findings": findings,
        "sources": citations,
        "evidence_policy": (
            "Citations are restricted to URLs returned by web search. Source linking is "
            "validated programmatically; semantic support still requires human review."
        ),
    }
