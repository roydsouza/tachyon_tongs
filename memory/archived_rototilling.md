
# Guidance - Agent SDLC for Security

Transitioning an ambitious project like your "Tachyon Tongs" firewall from unstructured "vibe coding" to a disciplined Agentic Engineering methodology is a critical step, especially given the strict reliability and security requirements of the system
.
By leveraging Google AntiGravity as your "Mission Control" to reverse engineer and orchestrate the project
, you can implement a structured Software Development Lifecycle (SDLC) that brings order, transparency, and deterministic governance to the codebase.
Here is a comprehensive guide to your options and the ideal setup for a security-critical agentic project.
1. SDLC Options in the Agentic Era
The industry is currently moving away from prompt-heavy vibe coding toward formal, agentic lifecycles. Your primary SDLC options include:
AC/DC (Agent Centric Development Cycle): Relies on "Guide-Generate-Verify-Solve" loops. It isolates the agent's work in a sandbox, requiring its "inner loop" reasoning to be continuously checked against deterministic guardrails before the "outer loop" of human review occurs
.
AI-DLC (AI-Driven Development Lifecycle): A spec-driven model focused heavily on planning and steering files to define intent before coding begins. Best for large codebases requiring deep local context
.
SDS (Self-Defining Systems): A multi-stage workflow (Spec → Architecture → Algorithms → Code) where human architects review artifacts at every refinement stage
.
BMAD (Brief, Map, Act, Double-Check): A spec-driven enterprise architecture approach that turns static documentation into "executable intent"
.
2. The Ideal SDLC for a Security-Focused Firewall
For a hyper-focused security project like Tachyon Tongs, AC/DC combined with Agentic Test-Driven Development (TDD) is the ideal framework.
Because agents can hallucinate logic or bypass controls to achieve their goals, you must enforce a Scope 3 (Supervised Agency) security level
. This means the agent can handle complex autonomous reasoning, but human-validated approval gates are absolutely mandatory before modifying security boundaries or resource quotas
.
Using AntiGravity, you should structure your workflow as follows:
Structural Decomposition: Use AntiGravity's Planning Mode to map out your current chaotic logic
. Break the system down into LEGO-style "Agent Modules" (e.g., Fetcher, Sanitizer, Analyzer). This reduces the blast radius if an agent fails
.
Agentic TDD (Red-Green-Refactor): In non-deterministic systems, TDD is the only way to build trust. Force the agent to write a failing test first (e.g., "return error when firewall rules are empty"). Then, it writes the minimal code to pass it. This prevents the common failure mode where an agent writes tests that simply validate its own broken logic
.
Workspace Rules: In AntiGravity, explicitly configure workspace rules (.agents/rules/) forbidding the agent from injecting new logic directly into main entry points. Force it to generate modular files instead
.
3. Ideal Filesystem Layout: "Memory as Documentation"
A core failure of vibe-coded projects is relying on the LLM's transient context window, leading to "security debt" and context loss
. The ideal layout uses the "Memory as Documentation" architecture, storing the agent's state in version-controlled Markdown files
.
Divide your root repository into two context layers
:
The Remembrance Layer (Knowledge Persistence):
AGENTS.md (or AGENT.md): The "README for AI." This is the ultimate control plane. For Tachyon Tongs, this must contain strict architectural boundaries, explicit layering rules (e.g., "Sanitizer logic must never leak into the Fetcher"), and data privacy constraints
.
MEMORY.md: Long-term episodic memory. Stores key architectural decisions, standard procedures, and learned lessons across sessions
.
task_plan.md: The working memory. A living document with checklists to track phases and prevent the agent from suffering "goal drift" mid-task
.
notes.md: A scratchpad for intermediate research
.
memory/YYYY-MM-DD.md: Timestamped daily logs of the agent's activities and tool outputs
.
The Personalization Layer (Behavioral Governance):
SOUL.md: Encodes your agent's behavioral principles (e.g., "always prefer deterministic security over probabilistic performance")
.
IDENTITY.md: The agent's name, version, and specific role (e.g., Sentinel vs. Pathogen)
.
4. Ideal Documentation Structure
To untangle chaotic explanations, your documentation must transition from being "passive descriptions" to "executable constraints" that both humans and AI can easily parse
.
Architecture Decision Records (ADRs): Store your documentation alongside your code in a /docs/adr/ directory using sequential files (e.g., ADR-0001.md). ADRs are crucial because they capture the "why" behind a decision, preventing AI agents from blindly undoing your security choices later
. Each ADR must contain:
Title & Number: e.g., ADR-0005: Adopt Tri-Stage Safe-Search Architecture
Status: Proposed, Accepted, Superseded, Deprecated, or Rejected (helps the AI know what is currently active)
.
Context: The constraints, requirements, and problem statement
.
Decision: Specifically what is being done, and by who
.
Consequences: Both the positive and negative trade-offs (e.g., "Increases security but adds 15ms latency")
.
Alternatives Considered: Documenting at least two alternatives prevents the "myopic response" failure mode where agents choose the first workable solution without considering better ones
.
AntiGravity Artifacts: Finally, leverage AntiGravity's native Artifacts. Stop reading raw code diffs to figure out what the AI did. Force the agent to generate Implementation Plans (before coding) and Walkthroughs (after coding)
. You can leave Google-Doc-style comments directly on these artifacts in AntiGravity to negotiate with the agent asynchronously, ensuring you retain total architectural authority
.

# Guidance - Unified Agentic SDLC repository

Based on the "Memory as Documentation" architecture, AntiGravity's specific SDLC requirements, and the actual components of your Tachyon Tongs repository, here is the ideal, unified folder structure.
This structure bridges your deterministic security needs (Open Policy Agent, macOS Sandbox) with the necessary contextual files that keep autonomous AI agents aligned and prevent "Security Debt"
.
tachyon_tongs/
├── .agents/                        # AntiGravity Customization & Hook Layer [3]
│   ├── rules/                      # System constraints and guidelines (e.g., MISSION.md) [3, 4]
│   ├── workflows/                  # On-demand, executable AI workflows (e.g., sentinel-threat-intel.md) [3, 5]
│   └── skills/                     # Progressive disclosure skills loaded only when needed [6, 7]
│
├── agents/                         # In-Band Agent Manifests [8]
│   └── pathogen/
│       └── SKILL.md                # Declarative configuration for the internal Pathogen Red Team [8, 9]
│
├── docs/                           # Human & AI Architectural Memory [10]
│   ├── adr/                        # Architecture Decision Records (e.g., ADR-0001-Triad-Pipeline.md) [11, 12]
│   ├── ARCHITECTURE.md             # System boundaries, OPA, and Apple Sandbox mapping [13, 14]
│   ├── DEPLOYMENT.md               # Builder guides for In-Band and Out-of-Band integration [13, 15]
│   ├── ROADMAP.md                  # Systematic progression of milestones [13]
│   └── STRATEGY.md                 # Operational thesis and continuous improvement protocols [13]
│
├── memory/                         # Episodic Memory Layer [16]
│   └── 2026-03-12.md               # Timestamped daily logs of agent reasoning and tool outputs [16]
│
├── policies/                       # Deterministic Governance Layer [8]
│   └── tool_access.rego            # Semantic intent gating policies for Open Policy Agent (OPA) [8, 17]
│
├── scripts/                        # Administrative Overlays & Orchestration [18]
│   ├── doom_ticker.py              # Terminal-style apocalyptic reporting [18]
│   ├── run_pathogen.py             # Orchestration daemon for the red-team cycle [18]
│   └── zero_day_drill.py           # Continuous adversarial fuzzer against the Guardian Triad [18]
│
├── src/                            # Core Execution Directives [19]
│   ├── substrate_daemon.py         # Autonomous proxy server enforcing OPA capabilities [19]
│   ├── tachyon_client.py           # Out-of-Band integration API (safe_fetch, safe_execute) [19, 20]
│   ├── state_manager.py            # SQLite-backed durable transaction coordinator [19]
│   ├── adk_sentinel.py             # Action Broker and entry point to the air-gapped pipeline [19]
│   └── tri_stage_pipeline.py       # Isolated bounds routing payload retrieval and sanitization [19]
│
├── AGENTS.md                       # The "README for AI" - strict boundaries and instructions [16, 21]
├── EVOLUTION.md                    # The Somatic Ledger: tracks autonomous codebase mutations [22]
├── EXPLOITATION_CATALOG.md         # Master Ledger: Threat vectors discovered by the Sentinel [22]
├── IDENTITY.md                     # Agent name, version, and specific role (The Personalization Layer) [23]
├── MEMORY.md                       # Long-term curated memory (key decisions, standard procedures) [16]
├── notes.md                        # Scratchpad for intermediate agent research [16]
├── README.md                       # Human-facing whitepaper and repository quickstart [13]
├── RUN_LOG.md                      # Cryptographically verified execution logs [22]
├── SITES.md                        # Vetted intelligence destinations (e.g., CISA, GitHub Advisories) [22, 24]
├── SOUL.md                         # Behavioral principles (e.g., "prefer deterministic security") [23]
├── TASKS.md                        # Active engineering backlog, dynamically mutated by the Sentinel [22, 25]
├── task_plan.md                    # Working memory tracking current phases and checklists [16]
└── USER.md                         # Profile of your specific human preferences and technical background [23]
How the Structure Drives the Agentic SDLC
1. The Remembrance & Personalization Layers (Root Markdown Files) The root directory is dominated by Markdown files acting as the agent's brain (AGENTS.md, MEMORY.md, task_plan.md, SOUL.md, IDENTITY.md)
. Because they are plain text, they are version-controllable, transparent, and can be edited by you if the agent's goals drift
. This keeps the agent's context alive without relying on external, opaque databases
.
2. Architecture Decision Records (/docs/adr/) Whenever AntiGravity's agents or your "Engineer" suggest a massive architectural change, the decision is formally written here (e.g., ADR-0005.md)
. This captures the why behind your security constraints (e.g., "Why we isolate the Analyzer from the Fetcher"), preventing future agent sessions from accidentally undoing your security logic to optimize for speed
.
3. AntiGravity Orchestration (/.agents/) This hides your agentic scripts from the main source code. Your global rules/ (like MISSION.md) strictly enforce how the agent should write code, while workflows/ hold your predefined automation chains (like generating reports or cataloging threats)
. skills/ act as "Progressive Disclosure"—only loading specific context into the agent's window when a specific task requires it, drastically reducing token bloat
.
4. Deterministic Execution vs. Agent Logic (/src/ vs /agents/) The raw Python execution infrastructure (/src/) and the declarative security policies (/policies/) are kept entirely separate from the agent's operational logic (/agents/pathogen/SKILL.md)
. This ensures your agents operate purely as configuration data within a mathematically bound sandbox, unable to directly alter the underlying substrate_daemon.py without your explicit review
.
