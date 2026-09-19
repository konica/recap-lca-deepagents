# python/m2/m2.2_homework.py
"""M2.2 Homework: Configure Your Own Filesystem Backend.

THE IDEA
The lab wired up one fixed setup: a CompositeBackend routing a single
reference file to local disk with a permission rule denying all writes
to it. This homework asks you to pick your own small file-based task and
configure a backend for it however you like: StateBackend,
FilesystemBackend, or a CompositeBackend mixing both. There's no single
right backend or topic here, that's the point. Two students doing this
homework could end up with completely different setups.

WHAT YOU FILL IN
  TODO 1: pick a topic for a small text file (a packing list, a journal,
    a recipe box, meeting notes, whatever), seed it with some starting
    content the same way the lab pre-populates reference/chinook-sales.md,
    and configure ANY backend you like for the agent to use.
  TODO 2: write a task message that has the agent read your file and then
    write or edit it in some way, and (optionally) add one or more
    FilesystemPermission rules that change what the agent is allowed to
    do to it.

RUN
  cd python
  uv run ./m2/m2.2_homework.py
"""

from pathlib import Path

from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend, StateBackend

from models import model


# ════════════════════════════════════════════════════════════════════════
# TODO 1: Configure a backend for a topic of your choosing.
#
# Requirements:
#   - Pick a small file-based task: a packing list, a journal, a recipe
#     box, meeting notes, whatever fits your topic.
#   - Create a seed file (or files) with some starting content, the same
#     way the lab pre-populates reference/chinook-sales.md.
#   - Configure ANY backend you like: StateBackend(), FilesystemBackend(),
#     or a CompositeBackend() routing between them. It does not need to
#     match the lab's setup.
#
# Example shape (delete this and write your own):
#   my_dir = Path(__file__).parent / "my_files"
#   my_dir.mkdir(exist_ok=True)
#   (my_dir / "notes.md").write_text("...")
#   backend = FilesystemBackend(root_dir=str(my_dir), virtual_mode=True)
# ════════════════════════════════════════════════════════════════════════

skill_dir = Path(__file__).parent / "skills"
skill_dir.mkdir(exist_ok=True)
(skill_dir / "setup-python-venv").mkdir(exist_ok=True)
(skill_dir / "setup-python-venv" / "SKILL.md").write_text("""
---
name: setup-python-venv
description: Use when running, installing, or adding Python packages for any project in this sandbox, when creating a virtual environment, or when a venv fails with "failed to symlink ... Operation not permitted (os error 1)" on a /c/... mounted path.
---

# Python venvs in this sandbox

Project directories live on a mounted drive (`/c/...`) that refuses symlink
creation. Any venv created inside the project fails:

```
error: failed to symlink file from /usr/bin/python3.14 to
/c/.../project/.venv/bin/python: Operation not permitted (os error 1)
```

Home (`/home/agent`) allows symlinks. So: **the venv always lives at
`~/.venvs/<project-name>`, never in the project.**

## Rules

1. **`uv` is the only Python package manager.** `uv add`, `uv sync`,
   `uv run`, `uv lock`. Never `pip install`, `python -m venv`, `poetry`,
   `conda`, or `virtualenv` for a project's dependencies.
2. **Never create `.venv` in the project.** It fails, and a half-created
   `.venv/` left behind confuses later runs — delete it if you find one.
3. **Prefix `UV_PROJECT_ENVIRONMENT` on every uv command.** Each Bash call
   is a fresh shell, so `export` does not survive to the next command.
4. **Never set `UV_PROJECT_ENVIRONMENT` globally** (shell profile,
   `/etc/sandbox-persistent.sh`). It holds one value and would silently
   point every other project at the wrong venv.
""")
backend = CompositeBackend(
        default=StateBackend(),
        routes={
            "/skills/": FilesystemBackend(
                root_dir=str(skill_dir),
                virtual_mode=True,
            ),
        },
    ) 
  # TODO 1: replace with a StateBackend, FilesystemBackend, or CompositeBackend


# ════════════════════════════════════════════════════════════════════════
# TODO 2: Write the task, and optionally a permission rule.
#
# Write a user message that has the agent read your file, then write or
# edit it. If you want to demonstrate permissions, add one or more
# FilesystemPermission rules to the permissions list below. Leaving it
# empty and skipping permissions entirely is also a valid choice.
# ════════════════════════════════════════════════════════════════════════

TASK = "Tell me the purpose of the skill `setup-python-venv` in the `skills` folder. Then create a new file to summarize that purpose"  # TODO 2: replace with your own task message
permissions: list[FilesystemPermission] = [
    FilesystemPermission(
      operations=["write"],
      paths=["/skills/setup-python-venv/SKILL.md"],
      mode="deny",
    ),
]  # TODO 2 (optional): add rules here

if backend is None:
    raise NotImplementedError("TODO 1: see the comment block above")
if TASK is None:
    raise NotImplementedError("TODO 2: see the comment block above")

agent = create_deep_agent(
    model=model,
    backend=backend,
    permissions=permissions,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": TASK}]},
    config={"configurable": {"thread_id": "homework-m2.2_homework"}},
)

print(result["messages"][-1].content)
