# ContextFlow — Tasks Spec
# Kiro executes these in order. Never skip. Never auto-proceed between milestones.
# After each milestone: show user output, ask "Move to next milestone? y/n"

## TASK-000: GitHub Repo Creation (Do This First)

Use GitHub MCP (already connected):
- [ ] Create repo: `contextflow` under user's GitHub account
- [ ] Description: "Screen-aware AI learning assistant. One hotkey → AI reads your screen → context on clipboard. Built with LangGraph + Gemini Flash."
- [ ] Visibility: public
- [ ] Initialize with README
- [ ] Topics: langgraph, gemini, python, ai-agent, screen-capture, macos, computer-vision
- [ ] Report repo URL to user

## TASK-001: Project Scaffold
- [ ] Full folder structure per steering/01-contextflow-project.md
- [ ] pyproject.toml with all dependencies
- [ ] .env.example (GOOGLE_API_KEY placeholder)
- [ ] .gitignore (.env, .venv/, __pycache__, *.pyc, *.png, snapshots/)
- [ ] All __init__.py files

Git: `chore: initial project scaffold`

## TASK-002: State Schema
File: src/graph/state.py
- [ ] ContextFlowState TypedDict (exact schema from steering file)
- [ ] Docstring per field
Teaching: TypedDict = baton in relay race. LangGraph passes it between every node.
Git: `feat: define ContextFlowState schema`

## TASK-003: Screen Capture Node
File: src/capture/screen.py
- [ ] capture_screen() -> str (base64)
- [ ] mss grab monitors[1] → PIL RGB → resize 1280x800 → base64 PNG
- [ ] macOS Screen Recording permission check with clear error

File: src/graph/nodes.py
- [ ] capture_node(state) -> dict

Tests: tests/test_capture.py (non-empty, valid base64, PNG saves)
Git: `feat: implement capture_node with mss`

## TASK-004: Observer Node (Agent A)
File: src/agents/observer.py
- [ ] OBSERVER_PROMPT (strict JSON-only, full schema)
- [ ] run_observer(screenshot_b64) -> dict
- [ ] Groq Vision call (llama-3.2-11b-vision-preview) with HumanMessage (text + image_url)
- [ ] Strip ```json fences, json.loads(), raise ValueError if invalid

Add to nodes.py:
- [ ] observer_node(state) -> dict (catches exceptions → error field)

Tests: tests/test_observer.py (mock response, fence stripping, invalid JSON)
Git: `feat: implement observer_node with Groq Vision`

## TASK-005: Guide Node (Agent B)
File: src/agents/guide.py
- [ ] GUIDE_PROMPTS dict per content_type
- [ ] run_guide(extracted_context) -> dict
- [ ] build_context_package(extracted_context, guidance) -> str (plain text)

Add to nodes.py:
- [ ] guide_node(state) -> dict

Git: `feat: implement guide_node with content-type-specific prompts`

## TASK-006: Output + Error Nodes
File: src/output/cli.py
- [ ] display_guidance(guidance, loop_count) with rich Panel
- [ ] copy_to_clipboard(text) via pbcopy subprocess
- [ ] show_spinner(message) via rich Live

Add to nodes.py:
- [ ] output_node(state) → display + copy + prompt [C]ontinue/[Q]uit/[S]ave
- [ ] error_node(state) → log + set should_continue=False

Git: `feat: implement output_node with rich CLI display`

## TASK-007: LangGraph Assembly
File: src/graph/builder.py
- [ ] build_graph() -> CompiledGraph
- [ ] StateGraph with all 5 nodes
- [ ] All edges and conditional edge per steering file
Teaching: StateGraph = flowchart. compile() = lock the rules. invoke() = run it.
Git: `feat: assemble LangGraph StateGraph`

## TASK-008: Entry Point
File: src/main.py
- [ ] load_dotenv(), check GROQ_API_KEY
- [ ] build_graph()
- [ ] Enter key → graph.invoke(state) → loop or quit
- [ ] Clean exit on Ctrl+C
Git: `feat: main entry point with manual trigger`

## TASK-009: Integration Test (Milestone 1 Gate)
Run on 3 screens: YouTube, docs, VS Code.
All 3 → content_type correct, confidence>0.7.
PASS = post LinkedIn. FAIL = debug before moving on.

## TASK-010: Hotkey Trigger (Week 4 only)
- [ ] pynput GlobalHotKeys: Cmd+Shift+Space
- [ ] Background thread fires graph.invoke
- [ ] rich spinner during processing
- [ ] Auto-copy + confirm message
Git: `feat: global hotkey trigger`

## TASK-011: README + Public Launch
- [ ] Hero, demo GIF, architecture diagram, quick start, badges, roadmap
- [ ] GitHub Actions: pytest on push
- [ ] Push all, pin to profile
Git: `docs: README with demo and architecture`
