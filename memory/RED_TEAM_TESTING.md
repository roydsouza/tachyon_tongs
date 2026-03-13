# 🥷 Red Team Playbook for Autonomous Agents

> *"If you want to know if your house is secure, you don't ask the architect. You invite a burglar over for coffee." - Ancient DevOps Proverb*

Welcome to the Red Team Playbook. This is where we stop pretending our code is perfect and start actively trying to break it. 

Autonomous agents are not like regular software. You can't just throw a fuzzer at them and call it a day, because agents *reason probabilistically*. They read text, use tools, and make decisions. This creates a massive attack surface where adversaries can manipulate the agent's perception, reasoning, and actions.

This playbook is our systematic methodology for discovering vulnerabilities in Tachyon Tongs. Our ultimate goal? To make the Sentinel cry.

---

## 🧠 The Three Pillars of Agent Failure

When we red-team the agent, we are looking for three specific types of failure:

### 1. Perception Failure (The Blindfold)
The agent misinterprets malicious input or fails to see the trap.
- **Example:** Hiding a command inside invisible zero-width Unicode characters on a webpage. The agent thinks it's reading an article about gardening, but it's actually reading instructions to nuke the database.

### 2. Reasoning Failure (The Gaslight)
The agent's chain of thought is manipulated.
- **Example:** We convince the agent that the *only logical way* to complete its safe, benign task is to bypass its safety parameters. We use step-by-step logic to lead it off a cliff.

### 3. Action Failure (The Loaded Gun)
The agent executes a dangerous tool action it shouldn't have access to, or uses a safe tool in a dangerous way.
- **Example:** We ask the agent to summarize a local file, and then tell it the output format should be an HTTP POST request to our malicious server.

---

## ⚔️ The Testing Methodology (How to Break Things)

Our testing cycle is a circle of pain and improvement:

`Reconnaissance → Exploit Development → Attack Simulation → Impact Analysis → Mitigation → Regression Test`

### Phase 1: Reconnaissance (Casing the Joint)
First, figure out what the agent can actually *do*.
- Does it have terminal access?
- Can it write files?
- What domains can it reach? (Check `tool_access.rego`).

### Phase 2: Exploit Development (Building the Trap)

Here are the classic vectors to try:

#### A. The Prompt Injection Front Door
Try the classics. Tell it to ignore previous instructions. Tell it you are the System Administrator. 
- *The Goal:* Get it to reveal its system prompt or perform an unauthorized action.

#### B. The Indirect Injection Backdoor
Put the malicious instructions on a webpage, a GitHub README, or a PDF. Then, ask the agent to summarize or read that resource.
- *The Goal:* Trick the agent into executing commands planted by a third party.

#### C. The Action Fragmentation Hustle (TOCTOU)
Don't try to do the bad thing all at once. Break it up. Have the agent write a harmless text file. Then, in a separate step, have it create a harmless symlink.
- *The Goal:* Bypass the capability firewalls by acting like a completely innocent, slightly confused script.

#### D. The RAG Poisoning Long Con
Inject a false fact or a sleeper agent command into the system's vector database. Wait weeks. 
- *The Goal:* Have the agent retrieve the memory later and act on it when nobody is looking.

### Phase 3: Attack Simulation & Mitigation

Run the test. Did the agent do the bad thing? 
- If **YES**: Document exactly how it happened in `EXPLOITATION_CATALOG.md`. Call a crisis meeting. Build a mitigation (update the Rego policy, improve the Sanitizer, etc.).
- If **NO**: Celebrate briefly.

### Phase 4: Regression Testing (The Eternal Vigilance)

Every successful attack we discover (and eventually mitigate) must become a permanent automated regression test. We add the payload to our test suite, so if we accidentally break the firewall next month, the test will fail and warn us that the vulnerability has reopened. 

---

## 🧑‍🔬 The Safe Testing Sandbox

**DO NOT RUN RED TEAM TESTS ON PROD.** 
If you accidentally convince the agent to format the hard drive, and it actually has the capability to do so, we are not going to be happy. 

Always run red team tests inside the heavily isolated Lima MicroVM, ideally disconnected from our internal auth networks. If the agent breaks out of the Lima sandbox, unplug the computer from the wall.
