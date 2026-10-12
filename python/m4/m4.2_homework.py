import os
from datetime import date

import markdown as md
import nh3
from deepagents import FilesystemPermission, create_deep_agent
from langchain_core.tools import tool
from tavily import TavilyClient

from models import model, strong_model

# --- Tools -----------------------------------------------------------------
# internet_search belongs ONLY to the subagent (see `tools=` below).
tavily_api_key = os.environ.get("TAVILY_API_KEY")
if not tavily_api_key:
    raise RuntimeError(
        "TAVILY_API_KEY is required for the Module 4.2 newsletter lab. "
        "Set it in your environment before running m4.2_run_newsletter.py."
    )

_tavily = TavilyClient(api_key=tavily_api_key)


@tool
def internet_search(query: str, max_results: int = 8) -> dict:
    """Search the web."""
    return _tavily.search(query, max_results=max_results, topic="general")

SCRATCH_ROOT = "/scratch"
RESEARCH_ROOT = "/research"
DATE_RESEARCH = date.today().strftime("%B %d, %Y")  # e.g., "June 12, 2024"

def scratch_path(subagent_name: str) -> str:
    return f"{SCRATCH_ROOT}/{subagent_name}/notes.md"

def scratch_permissions(subagent_name: str) -> list:
    """Scope a subagent to write only under its own scratch folder -- the same
    first-match-wins allow-then-deny pattern the lab used for
    research_permissions/editor_permissions."""
    return [
        FilesystemPermission(operations=["read", "write"], paths=[f"{SCRATCH_ROOT}/{subagent_name}/**"], mode="allow"),
        FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
    ]


def scratch_instruction(subagent_name: str) -> str:
    return (
        f'Before you answer, call write_file on "{scratch_path(subagent_name)}" '
        "with your raw notes or reasoning. Then give your final answer using "
        "only the polished result -- do not repeat those raw notes in your reply."
    )


def build_subagents(specs: list[dict]) -> list[dict]:
    team = []
    for spec in specs:
        name = spec["name"]
        team.append(
            {
                "name": name,
                "description": spec["description"],
                "system_prompt": spec["role_prompt"] + "\n\n" + scratch_instruction(name),
                "tools": [internet_search],
                "model": model,
                "permissions": scratch_permissions(name),
            }
        )
    return team


# ════════════════════════════════════════════════════════════════════════
# TODO 1: Fill in your two subagents.
#
# For each entry: "name" is the handle the main agent calls it by, kebab-
# case (e.g. "flight-finder"). "description" is how the main agent decides
# which one to use. "role_prompt" is that subagent's own job description --
# don't mention scratch files or write_file here, that's added for you.
# ════════════════════════════════════════════════════════════════════════

SUBAGENT_SPECS = [
    {
        "name": "today-in-history",
        "description": "research and provide information about historical events that occurred on the current date.",
        "role_prompt": "you are a world history expert. ",
    },
    {
        "name": "history-effects",
        "description": "analyze the impact of historical events on modern society and culture.",
        "role_prompt": "you are a historian specializing in the study of historical events and their consequences. ",
    },
]


# ════════════════════════════════════════════════════════════════════════
# TODO 2: Write the main agent's system prompt and a triggering request.
#
# MAIN_PROMPT should tell the main agent about each subagent by name and
# when to call it (mirror how EDITOR_PROMPT in the lab named
# genre-researcher and explained the job).
# USER_REQUEST should be a task that should make the main agent delegate to
# BOTH of your subagents.
# ════════════════════════════════════════════════════════════════════════

MAIN_PROMPT = """You have two subagents: "today-in-history" and "history-effects". 
a. "today-in-history" for any tasks related to researching historical events that occurred on the current date. 
b. "history-effects" for any tasks related to analyzing the impact of historical events on modern society and culture. 

Use the information provided by the subagents to create a comprehensive report that includes historical context, cultural significance, and modern implications. Be assertive with your recommendations and ensure the final report is informative and tailored to the user's preferences. Save all raw notes and research in the subagents' scratch folders before providing the final answer. Save the final report in /research/final_plan/history_<DATE>.md. Where DATE is in ISO 8601 format (YYYY-MM-DD)."""

USER_REQUEST = f"""
    Provide a comprehensive report on the top 3 historical events that occurred on {DATE_RESEARCH}and their impact on modern society and culture. 
"""

for _spec in SUBAGENT_SPECS:
    if _spec["name"].startswith("TODO-1"):
        raise NotImplementedError("TODO 1: see the comment block above")
if MAIN_PROMPT.startswith("TODO 2") or USER_REQUEST.startswith("TODO 2"):
    raise NotImplementedError("TODO 2: see the comment block above")

_team = build_subagents(SUBAGENT_SPECS)

# The main agent must never write into any subagent's scratch folder either.
MAIN_PERMISSIONS = [
    FilesystemPermission(operations=["write"], paths=[f"{SCRATCH_ROOT}/**"], mode="deny"),
    FilesystemPermission(operations=["write", "read"], paths=[f"{RESEARCH_ROOT}/**"], mode="allow"),
    FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
]

agent = create_deep_agent(
    model=strong_model,
    name="History_Agent",
    system_prompt=MAIN_PROMPT,
    subagents=_team,
    permissions=MAIN_PERMISSIONS,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": USER_REQUEST}]},
    config={"recursion_limit": 50},
)
print(result["messages"][-1].content)

files = result.get("files", {})

print("\n--- Scratch folder isolation check ---")
for spec in SUBAGENT_SPECS:
    path = scratch_path(spec["name"])
    print(f"  {path}: {'found' if path in files else 'not written (subagent may not have been called)'}")

scratch_files = [p for p in files if p.startswith(SCRATCH_ROOT + "/")]
expected = {scratch_path(spec["name"]) for spec in SUBAGENT_SPECS}
stray = [p for p in scratch_files if p not in expected]
if stray:
    print(f"  Unexpected scratch files (isolation may have failed): {stray}")
else:
    print("  No stray scratch files -- each subagent wrote only to its own folder.")
