# Repo Task Graph Request

Objective: Build a code task graph for the SR8 benchmark lane.

Scope:
- Add eval module
- Add benchmark corpus loader
- Add regression comparison

Constraints:
- Keep CLI stable
- Do not add network services

Context Package:
- Current CLI commands
- Existing receipt persistence tests

Authority Context:
- cto

Dependencies:
- Typer app wiring
- pytest coverage

Assumptions:
- Local filesystem only

Success Criteria:
- Tasks can be ordered by dependency

Output Contract:
- Code task graph artifact
- Markdown plan

Target Class:
- code_task_graph
