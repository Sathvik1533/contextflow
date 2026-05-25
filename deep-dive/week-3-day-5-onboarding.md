# Week 3 — Day 5 (May 25, 2026)
## TASK-012: Onboarding + User Profile + Morning Briefing

---

## What Changed — File by File

### NEW FILE: `src/onboarding/profile.py`
**What it is:** The entire onboarding system lives here.  
**What it does:** 4 jobs in one file.

```
load_or_create_profile()          ← front door. Called once at startup.
│
├── profile.json EXISTS?
│   ├── YES → _load_profile()           ← reads from disk
│   │          _show_morning_briefing() ← prints recap to terminal
│   │          return profile dict
│   │
│   └── NO  → _run_onboarding()         ← asks 3 questions
│              _analyze_terminal_for_profile()  ← reads shell history silently
│              _save_profile()           ← writes ~/.contextflow/profile.json
│              return profile dict

update_profile_after_session()    ← called AFTER graph finishes (in main.py)
                                     increments session_count, saves topics_seen
```

**Key concept in this file — Fallback guarantee:**
```python
# Terminal analysis never crashes even if no history file exists
except Exception:
    return {"detected_stack": None, "signals": []}
```
External signals (terminal, git, network) are always optional. Pipeline always runs.

---

### CHANGED: `src/main.py`

**Before (old code):**
```python
user_intent = input("   → ").strip()   # bare Python input
if not user_intent:
    user_intent = "general learning"

initial_state = {
    "user_intent": user_intent,
    # no profile, no user_level
    ...
}
```

**After (new code):**
```python
# Step 1: load profile (onboarding on first launch, briefing on return)
from src.onboarding.profile import load_or_create_profile
profile = load_or_create_profile()
user_level = profile.get("user_level", "intermediate")

# Step 2: ask intent — fallback to saved goal if user presses Enter
user_intent = console.input("→ ").strip()
if not user_intent:
    user_intent = profile.get("goal", "general learning")

# Step 3: inject both into state
initial_state = {
    "user_intent": user_intent,
    "user_level": user_level,   # ← NEW
    "profile": profile,         # ← NEW
    ...
}

# Step 4: after graph finishes — update profile with session data
from src.onboarding.profile import update_profile_after_session
update_profile_after_session(profile, result.get("session_history", []))
```

**Why `user_level` AND `profile` both in state?**  
- `user_level` → guide_node reads it in one line: `state.get("user_level")`  
- `profile` → future nodes that need role, stack, goal, session_count  
Extracting frequently-used values saves every node from digging into nested dicts.

---

### CHANGED: `src/graph/state.py`

**Added two new fields to ContextFlowState:**
```python
class ContextFlowState(TypedDict):
    user_level: str   # "beginner" | "intermediate" | "advanced"
    profile: dict     # full profile dict from ~/.contextflow/profile.json

    # ... all existing fields unchanged below
```

**Why state.py must be updated whenever you add new data to the flow:**  
LangGraph's TypedDict is the contract. If a field isn't declared here, it cannot pass between nodes. Think of it as: state.py is the blueprint of the pipe system. You must add a pipe before you can flow water through it.

---

### CHANGED: `src/graph/nodes.py`

**In guide_node — one line added:**
```python
# Before:
guidance = run_guide(filtered_context, user_intent, session_history)

# After:
user_level = state.get("user_level", "intermediate")  # read from state
guidance = run_guide(filtered_context, user_intent, session_history, user_level)
```

**Why `.get("user_level", "intermediate")` not `state["user_level"]`?**  
`.get()` with a default never crashes if the key is missing. `state["user_level"]` raises KeyError if it's absent. Always use `.get()` for state reads in nodes — defensive, never crashes the pipeline.

---

### CHANGED: `src/capture/terminal.py`

**Removed two `print()` calls that leaked raw text:**
```python
# Before (wrong):
print("⚠️  Could not find shell history file")

# After (correct):
# silently return empty result — terminal missing is expected, not an error
return result
```

**Why this matters:** `print()` ignores Rich formatting. It also outputs to stdout which can break piped commands. Silent fallbacks are always better than noisy warnings for expected missing states.

---

## The Complete Data Flow — TASK-012

```
DISK                      main.py                    LangGraph Graph
─────────────────         ──────────────────         ────────────────────
                          startup:
~/.contextflow/
profile.json  ──read──→  load_or_create_profile()
                              │
                         First launch?
                         YES → 3 questions + terminal analysis
                         NO  → load + morning briefing
                              │
                         profile = {
                           user_level: "beginner",
                           goal: "learning LangGraph",
                           stack: "Python",
                           session_count: 3,
                           ...
                         }
                              │
                         initial_state = {
                           user_level: "beginner",  ──────────→ capture_node
                           profile: {...},           ──────────→ observer_node
                           user_intent: "...",       ──────────→ guide_node
                           ...                                       │
                         }                               reads: user_level
                                                         passes to: run_guide()
                                                                      │
                                                         context_package contains:
                                                         "My level: beginner"
                              │
                    graph finishes
                              │
                    update_profile_after_session()
                              │
profile.json  ←write──  session_count +1
                         topics_seen updated
                         recent_titles updated
                              │
NEXT RUN:
profile.json  ──read──→  morning briefing:
                         "Welcome back. Session #4
                          Last topic: LangGraph nodes
                          Goal: learning LangGraph"
```

---

## Concepts You Learned Today

### 1. Separation of Concerns
Each file has one job:
- `profile.py` → disk I/O and user interaction
- `main.py` → startup and shutdown orchestration  
- `nodes.py` → pipeline work only
- `state.py` → data contract between nodes

**Apply to every project:** Split responsibilities at the file level. A file that does 3 different kinds of work is a file you'll regret later.

### 2. Fallback Guarantee Pattern
```python
try:
    # try to get bonus signal from external source
    result = get_terminal_data()
except Exception:
    return {"detected_stack": None}   # always return something, never crash
```
External signals (terminal, git, network, APIs) must never block the core flow.  
**Apply to every project:** Every call to something external goes in a try/except with a safe default return.

### 3. State vs Persistence
| | LangGraph State | profile.json |
|---|---|---|
| Lives in | Memory (RAM) | Disk |
| Duration | One pipeline run | Across all runs forever |
| Who writes | Nodes (return dicts) | `_save_profile()` in profile.py |
| Who reads | Any node via `state.get()` | `_load_profile()` at startup |

**Apply to every project:** Know which data is session-scoped and which is persistent. Mix them up and you get either data loss or memory bloat.

### 4. Why Nodes Don't Write to Disk
`output_node` runs once per capture cycle. If the session has 3 captures, it runs 3 times. If it wrote to disk, `session_count` would go up 3 times. Main.py runs once at the end — correct place for once-per-session work.

**Apply to every project:** Side effects (disk, API, email, database) belong at the orchestration layer, not inside loops.

### 5. `parents=True, exist_ok=True`
```python
PROFILE_DIR.mkdir(parents=True, exist_ok=True)
```
- `parents=True` → create all missing parent directories too
- `exist_ok=True` → don't crash if directory already exists  
**Apply to every project:** Always pair these two when creating directories. Never assume a path exists.

---

## Tests Added — `tests/test_onboarding.py`

| Test | What it proves |
|------|---------------|
| `test_save_and_load_round_trip` | profile.json survives a save+load without data loss |
| `test_save_creates_directory_if_missing` | first-ever launch on clean machine works |
| `test_saved_file_is_valid_json` | file can be opened by any JSON tool |
| `test_increments_session_count` | session_count goes up exactly 1 per session |
| `test_updates_topics_seen` | topic tracking counts correctly |
| `test_keeps_last_10_recent_titles` | rolling window doesn't grow infinitely |
| `test_empty_session_history_still_increments_count` | empty sessions still count |
| `test_skips_unknown_content_types_in_topics` | "unknown" never pollutes topics_seen |
| `test_returns_dict_with_required_keys` | terminal analysis always returns correct shape |
| `test_handles_no_terminal_history_gracefully` | no history file = no crash |
| `test_detects_python_from_commands` | pip/python/pytest → detected as Python |
| `test_detects_javascript_from_npm` | npm/npx → detected as JavaScript/React |
| `test_returns_empty_on_exception` | any crash in terminal analysis = safe empty return |

**Total: 39/39 tests passing (26 existing + 13 new)**

---

## What's Next — TASK-013 (ChromaDB Memory Agent)

**One new concept:** ChromaDB is a vector database.  
Normal databases find exact matches. ChromaDB finds *similar* matches.

```
Normal DB query:   "find where title = 'LangGraph nodes'"
                   → returns exact match or nothing

ChromaDB query:    "find captures similar to 'how does state flow between nodes'"
                   → returns: LangGraph nodes, state management, TypedDict tutorial
                   → even if none of them used those exact words
```

**Where it connects to existing code:**
- After `guide_node` runs → embed the capture summary → store in ChromaDB
- Before `guide_node` runs → search ChromaDB for related past captures → inject into Guide prompt
- Guide says: "You've seen this topic 3 times — going deeper this time"

**Files that will change:**
- NEW: `src/agents/memory.py`
- CHANGED: `src/graph/nodes.py` (guide_node reads memory before running)
- CHANGED: `src/graph/state.py` (new field: `memory_context`)

---

## Git Commit Reference

```
bb90de2  feat: TASK-012 — onboarding, user profile, morning briefing (39/39 tests)
e40210b  fix: resolve all P0+P1 flaws — dead node, token bloat, intent layer, deps
faad145  feat: add content parser, fix 10 bugs, add 10 features — 21/21 tests passing
```

---

*Next session: say "start TASK-013" — I will recap this file first, then build ChromaDB step by step.*
