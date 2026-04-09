# DevelopmentTeam

An AI-powered software development team built with [crewAI](https://crewai.com). Multiple AI agents collaborate to take a product idea from requirements through to tested code — with human review along the way.

## How It Works

The system is organized as a **Flow** that orchestrates four specialized **crews**, each handling a distinct phase of the software development lifecycle:

```
Requirements (PM + BA)  ──►  Technical Design (Tech Lead)  ──►  Development (Developer)  ──►  QA (Writer + Runner)
       ▲                                                                                                 │
       │  Human review & feedback                                                                        │
       └─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                    Issues found? Loop back for fixes (up to 3x)
```

### The Team

| Role | Crew | Responsibility |
|---|---|---|
| **Product Manager** | Requirements | Defines product scope, user stories, and acceptance criteria |
| **Business Analyst** | Requirements | Details specifications, identifies edge cases and gaps |
| **Technical Lead** | Design | Selects tech stack, designs architecture, creates technical specs |
| **Developer** | Development | Implements production-ready code based on the technical design |
| **QA Test Writer** | QA | Writes unit, integration, and API tests |
| **QA Test Runner** | QA | Validates test results, reports issues with root cause analysis |

### Human-in-the-Loop

After the Requirements crew produces a draft, the Flow **pauses for your review**. You can:
- **Approve** — proceed to technical design
- **Give feedback** — the crew revises the requirements based on your input, then asks you again

This loop continues until you're satisfied, so even a rough product idea gets refined into solid requirements before any code is written.

### QA Feedback Loop

After QA testing, if issues are found, the Flow automatically routes back to the Developer for fixes and re-tests. This repeats up to 3 iterations before marking the project complete.

## Getting Started

### Prerequisites

- Python >=3.10, <3.14
- [UV](https://docs.astral.sh/uv/) package manager

### Setup

1. Install dependencies:

```bash
crewai install
```

2. Configure API keys in `.env`:

```
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_API_BASE=your_custom_base_url_here
SERPER_API_KEY=your_serper_key_here
```

3. Edit the `kickoff()` function in `src/development_crew/main.py` with your project details:

```python
dev_flow.kickoff(
    inputs={
        "project_name": "My App",
        "project_description": "A web application that...",
    }
)
```

### Run

```bash
crewai run
```

Outputs are saved to the `output/` directory:
- `requirements.md` — product requirements and specifications
- `technical_design.md` — architecture and technical design document
- `source_code.md` — complete implementation
- `test_report.md` — QA test results and issue analysis

## Project Structure

```
src/development_crew/
├── main.py                                    # Flow orchestration
└── crews/
    ├── requirements_crew/                      # PM + Business Analyst
    │   ├── config/agents.yaml
    │   ├── config/tasks.yaml
    │   └── requirements_crew.py
    ├── design_crew/                            # Technical Lead
    │   ├── config/agents.yaml
    │   ├── config/tasks.yaml
    │   └── design_crew.py
    ├── development_crew/                       # Developer
    │   ├── config/agents.yaml
    │   ├── config/tasks.yaml
    │   └── development_crew.py
    └── qa_crew/                                # QA Writer + QA Runner
        ├── config/agents.yaml
        ├── config/tasks.yaml
        └── qa_crew.py
```

## Customization

- **Agents** — edit `config/agents.yaml` in each crew to adjust roles, goals, and backstories
- **Tasks** — edit `config/tasks.yaml` to change what each agent produces
- **Flow logic** — edit `main.py` to add more review steps, change iteration limits, or modify routing
- **Tools** — add tools like `SerperDevTool`, file I/O, or code execution in the crew `.py` files
- **LLM** — change the model by updating agent `llm` config in `agents.yaml` or the crew Python files
