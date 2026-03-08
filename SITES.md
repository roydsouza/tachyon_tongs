# 🌐 Sentinel Threat Intel Sources

This file maintains the active list of high-value targets that the **Sentinel Agent** monitors for emerging Agent Hijacking and Prompt Injection vectors. 

The Sentinel autonomously updates this list as it discovers new, credible sources of AI security research.

## 📡 Primary Feeds (High Signal / High Trust)

- **[CISA AI Security Advisories](https://www.cisa.gov)**
  - *Focus:* Nation-state level threats, standardized mitigation strategies.
- **[GitHub Advisory Database](https://github.com/advisories?query=ecosystem%3Aactions)**
  - *Focus:* Supply-chain attacks, vulnerable agent libraries (e.g., LangChain, AutoGPT).
- **[NIST NVD (National Vulnerability Database)](https://nvd.nist.gov/)**
  - *Focus:* Formalized CVEs related to LLM sandbox escapes and framework vulnerabilities.

## 🔬 Research & Bleeding-Edge (High Noise / High Value)

- **[arXiv - cs.CR (Cryptography and Security)](https://arxiv.org/list/cs.CR/recent)**
  - *Focus:* Academic papers on theoretical Indirect Prompt Injection (IPI), memory poisoning, and adversarial attacks.
- **[Google Project Zero](https://googleprojectzero.blogspot.com/)**
  - *Focus:* Zero-day exploits, deep-dive sandbox escape methodologies.
- **[DEF CON / Black Hat Publication Archives](https://defcon.org/)**
  - *Focus:* Offensive security presentations targeting AI infrastructure.

## 🕵️ LLM Specific Bug Bounties & Disclosures

- **[Huntr (AI Bug Bounty Platform)](https://huntr.ml/)**
  - *Focus:* Real-world exploits reported by researchers against models and agent frameworks.
- **[LMSYS Chatbot Arena Blog](https://lmsys.org/blog/)**
  - *Focus:* Jailbreak trends and model alignment vulnerabilities observed in the wild.

---
*Note: The Sentinel is strictly prohibited from pulling active exploit payloads (proofs-of-concept) into the host execution environment. All scraping runs through the Tri-Stage Fetcher-Sanitizer pipeline.*
