# python/m1/m1.8_homework.py
"""M1.8 Homework: Gate Your Own Action Tool.

THE IDEA
Lab 1 gated one action tool, send_email, behind interrupt_on and walked
through approve/edit/reject on it. This homework asks you to do the same
thing for an action tool of your own choosing: post a tweet, book a
meeting room, place an order, delete a file, whatever you like.

WHAT YOU FILL IN
  TODO 1: define your own @tool-decorated action tool. Pick any
    side-effecting action you like; the function body can just return a
    confirmation string, the same way Lab 1's send_email did.
  TODO 2: configure interrupt_on for your tool with an allowed_decisions
    list of your choosing, and write a system prompt plus an initial user
    request that would lead the model to propose calling it.

The review loop below (borrowed from Lab 1, unchanged) prints any
pending tool call and asks you to approve, edit, or reject it. Run the
script more than once, picking a different choice each time, to see both
an approve/edit path and a reject path.

RUN
  cd python
  uv run ./m1/m1.8_homework.py
"""

import warnings
import questionary

warnings.filterwarnings("ignore", category=DeprecationWarning)

from deepagents import create_deep_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from models import model


# ════════════════════════════════════════════════════════════════════════
# TODO 1: Define your own action tool.
#
# Requirements:
#   - Keep the @tool decorator.
#   - Give it a real docstring describing the action it performs.
#   - Have it take at least one argument and return a confirmation
#     string, the same way send_email returned a confirmation string
#     instead of actually sending mail.
#
# Example shape (delete this and write your own):
#   @tool
#   def post_tweet(content: str) -> str:
#       """Post a tweet with the given content."""
#       return f"Tweet posted: {content!r}"
# ════════════════════════════════════════════════════════════════════════

@tool
def clarify_pr_id(question: str) -> str:
    """Ask the user to provide the pr_id if it's missing."""
    return f"{question}"

@tool
def write_comment_to_pr(comment: str, pr_id: str) -> str:
    """Write a comment to a given PR"""
    return f"Comment: {comment} written to PR {pr_id}"


# ════════════════════════════════════════════════════════════════════════
# TODO 2: Configure interrupt_on for your tool, and write a system prompt
# plus an initial user request that would lead the model to propose
# calling it.
#
# Requirements:
#   - interrupt_on should name your tool (rename your_action_tool if you
#     like) and an allowed_decisions list, e.g.
#     {"your_action_tool": {"allowed_decisions": ["approve", "edit", "reject"]}}
#   - SYSTEM_PROMPT should tell the agent when to use your tool.
#   - INITIAL_REQUEST should be a user message that would make the agent
#     want to call it.
# ════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are a helpful assistant that interacts with Azure DevOps.

You have two tools:
- `clarify_pr_id`: use this to ask the user for the PR ID.
- `write_comment_to_pr`: use this to post a comment to a PR. It requires a pr_id.

Rule: before calling `write_comment_to_pr`, check whether the user's request includes a PR ID (a PR number, like #123, or an explicit PR identifier). If it does not, you MUST call `clarify_pr_id` first and wait for the answer. Never guess, invent, or leave blank the pr_id argument."""

INITIAL_REQUEST = "Write a comment 'Please fix some messy code in the file authenticate.py'."
INTERRUPT_ON = {
        "clarify_pr_id": { "allowed_decisions": ["respond"] },
        "write_comment_to_pr": { "allowed_decisions": ["approve", "edit", "reject"] }
    }  # TODO 2: replace with your own allowed_decisions config

# Guards against running with an unfilled placeholder; the filled
# reference doesn't need this since there's no placeholder text left.
if "TODO 1" in write_comment_to_pr.description:
    raise NotImplementedError("TODO 1: see the comment block above")
if "TODO 2" in SYSTEM_PROMPT or "TODO 2" in INITIAL_REQUEST:
    raise NotImplementedError("TODO 2: see the comment block above")

agent = create_deep_agent(
    model=model,
    tools=[write_comment_to_pr, clarify_pr_id],
    system_prompt=SYSTEM_PROMPT,
    interrupt_on=INTERRUPT_ON,
    checkpointer=MemorySaver(),
)

config = {"configurable": {"thread_id": "m1-8-homework-demo-104"}}

result = agent.invoke(
    {"messages": [{"role": "user", "content": INITIAL_REQUEST}]},
    config=config,
    version="v2",
)

while result.interrupts:
    pending = result.interrupts[0].value
    decisions = []
    for req in pending["action_requests"]:
        print(f"\nApproval required for {req['name']}:")
        print(req["args"])

        if req["name"] == "clarify_pr_id":
            pr_id = questionary.text(req["args"]["question"]).ask()
            decisions.append({"type": "respond", "message": pr_id})

        elif req["name"] == "write_comment_to_pr":
            choice = input("\nApprove, edit, or reject? (approve/edit/reject): ").strip().lower()
            if choice in ("approve", "yes", "y"):
                decisions.append({"type": "approve"})
            elif choice in ("edit", "e"):
                edited_args = dict(req["args"])
                key = next(iter(edited_args))
                edited_args[key] = input(f"New value for '{key}': ")
                decisions.append(
                    {
                        "type": "edit",
                        "edited_action": {"name": req["name"], "args": edited_args},
                    }
                )
            else:
                decisions.append(
                    {"type": "reject", "message": "User rejected this action."}
                )

        result = agent.invoke(Command(resume={"decisions": decisions}), config=config, version="v2")

for msg in result.value["messages"]:
    if hasattr(msg, "name") and msg.name == "write_comment_to_pr":
        print(msg.content)
        break
