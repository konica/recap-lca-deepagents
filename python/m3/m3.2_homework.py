# python/m3/m3.2_homework.py
"""M3.2 Homework: Bundle a Reference File Into Your Skill.

THE IDEA
The lab's two skills (qualify-lead and draft-pitch) are each a single flat
SKILL.md file with everything inline. But the lesson also covered a third
stage of progressive disclosure: a skill can point to supporting files (a
reference doc, a template, a script) that live alongside SKILL.md and that
the agent only reads when it actually needs them, instead of stuffing
everything into the system prompt up front. This homework asks you to write
a skill for a topic or workflow YOU pick (not sales) that bundles a SECOND
file with details the agent needs but that aren't in SKILL.md itself, then
confirm from the trace that the agent actually called `read_file` on that
second file before answering, rather than guessing.

WHAT YOU FILL IN
  TODO 1: write your own SKILL.md content. It must instruct the agent to
    read a `reference.md` file (in the same skill directory) for specific
    details it needs, and must NOT restate those details inline. The `name`
    field in your frontmatter must exactly match SKILL_NAME below.
  TODO 2: write reference.md's content: the specific facts, numbers, or
    template your skill's instructions point to and depend on.
  TODO 3: write a system prompt and a user question that should activate
    your skill.

RUN
  cd python
  uv run ./m3/m3.2_homework.py
"""

import tempfile
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend

from models import model

# This name becomes the skill's directory name. It must exactly match the
# `name:` field you write in the frontmatter inside build_skill_md() below.
SKILL_NAME = "master-agent-engineer"
REFERENCE_PATH = f"/skills/{SKILL_NAME}/reference.md"


# ════════════════════════════════════════════════════════════════════════
# TODO 1: Write your own SKILL.md content.
#
# Requirements:
#   - YAML frontmatter with `name` (must equal SKILL_NAME above) and
#     `description` (a specific sentence describing WHEN to use this skill).
#   - Steps that tell the agent to open `reference.md` (in this same skill
#     directory) for the specific details it needs to do the task well.
#   - Do NOT put those details in SKILL.md itself; if the agent could do
#     the task correctly without ever reading reference.md, this doesn't
#     exercise progressive disclosure.
#
# Example shape (delete this and write your own):
#   return """---
#   name: your-skill-name
#   description: Use when the user wants to ...
#   ---
#
#   # Your Skill Title
#
#   **Step 1: ...**: ...
#   **Step 2: ...**: before proceeding, read reference.md in this skill's
#     directory for the exact ... to use. Do not guess these.
#   """
# ════════════════════════════════════════════════════════════════════════

def build_skill_md() -> str:
    """TODO 1: return your own SKILL.md content as a string."""
    return """---
name: master-agent-engineer
description: Use when the user wants to how to build and master the agent engineer
---

# Master Agent Engineer

## What is the agent engineer?
It's a job that the engineer apply the LLM capabilities into building the autonomous agent. 

## How to build agent engineer
1. Get familiar with the SDLC
2. Learn knowledge about AI/ML, especially LLM
3. Build RAG system to understand the semantic search and evalate that system
4. Build the chatbot to know the reasoning ability of the model, how model guide to call tool, how to interact with the world via the action execution and ...
5. How to build a reliable agent with LangChain and get LangChain Agent Engineer certificate.

### Get more details
Read ./reference.md
"""


# ════════════════════════════════════════════════════════════════════════
# TODO 2: Write reference.md's content.
#
# This should contain the specific facts your SKILL.md pointed to and
# depends on: a rubric, a set of numbers, a template, a checklist. Specific
# enough that an answer produced without reading it would visibly differ
# from one produced with it.
# ════════════════════════════════════════════════════════════════════════

def build_reference_md() -> str:
    """TODO 2: return the content of your skill's reference.md."""
    return """
LangChain Certified Agent Engineer
Exam guide: format, rules, and what each section covers.
ARRIVE EARLY
Please join your exam session at least 15 minutes before your scheduled start time. This window is used for ID check, room scan, and
system verification with your proctor.
If you join more than 10 minutes after your scheduled start time you will be marked as a no-show and will need to reschedule the
exam at full cost.
This is a 2-hour exam taken solo and proctored, with a dedicated LangSmith organization provisioned for you. It is structured around the
Agent Development Lifecycle (ADLC). The exam is semi-open-book: you may consult a small set of LangChain-owned resources, but
no general search, AI assistants, or second screens.
Exam-day logistics
You will receive two invites in relation to this exam. The first will be an invite to take the test itself in a proctored environment,
accompanied by a calendar invite for your scheduled slot.
The second will be an email invite to a dedicated LangSmith organization, sent roughly two hours before your scheduled start time.
This org is used to answer several of the questions on the exam.
If you have not received either invite by two hours before your start time, contact certification-support@langchain.dev for
assistance.
If, when you accept the LangSmith invite, you see an error such as "the invite is no longer available", you are likely still logged into a
LangSmith org that uses SSO. Log out of that org first, then accept the invite by signing in with email or Google rather than SSO.
"""


# Write the skill to a scratch directory so it's discoverable through a
# FilesystemBackend, the same mechanism the lab uses for python/m3/skills/.
_tmp_root = Path(tempfile.mkdtemp(prefix="m3_2_homework_"))
_skill_dir = _tmp_root / "skills" / SKILL_NAME
_skill_dir.mkdir(parents=True, exist_ok=True)
(_skill_dir / "SKILL.md").write_text(build_skill_md())
(_skill_dir / "reference.md").write_text(build_reference_md())

backend = FilesystemBackend(root_dir=str(_tmp_root), virtual_mode=True)
print(f"Skill files written to: {_skill_dir}")


# ════════════════════════════════════════════════════════════════════════
# TODO 3: Write a system prompt and a triggering question.
#
# SYSTEM_PROMPT: give the agent a persona of your choosing (a name, a
# voice, anything you want).
# USER_QUESTION: a question that should match your skill's `description`
# closely enough that the agent activates it.
# ════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are a helpful expert with the lot of experience about build reliable agentic system."""
USER_QUESTION = "I'm a layman. I know what is the agent engineer? Which skill do I need to build? Which certificate should I get?"

agent = create_deep_agent(
    model=model,
    name="Homework_Agent",
    backend=backend,
    skills=["/skills"],
    system_prompt=SYSTEM_PROMPT,
)

THREAD = {"configurable": {"thread_id": "homework-102"}}

result = agent.invoke({"messages": [{"role": "user", "content": USER_QUESTION}]}, config=THREAD)
print(result["messages"][-1].content)

read_calls = [
    call
    for msg in result["messages"]
    for call in getattr(msg, "tool_calls", [])
    if call["name"] == "read_file"
]
reference_was_read = any(call["args"].get("file_path") == REFERENCE_PATH for call in read_calls)
print(f"\n--- Did the agent read {REFERENCE_PATH}? {reference_was_read} ---")
if not reference_was_read:
    print(
        "It didn't. Either SKILL.md isn't clearly telling it to, or the "
        "task is answerable without the details in reference.md."
    )
