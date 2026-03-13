# **The Architecture of an Agentic Security Laboratory: Pluggable Authorization, Decentralized Identity, and Immutable Policy Dissemination**

The transition of artificial intelligence from passive conversational models to autonomous agentic systems represents a paradigm shift in the digital threat landscape. These agents, characterized by their ability to reason, invoke tools, and interact with external environments, introduce vulnerabilities that transcend classical network security boundaries. In this context, the development of a security laboratory, such as the evolution of the Tachyon Tongs prototype, is essential for identifying, categorizing, and mitigating emerging threats like agent hijacking and indirect prompt injection. This report provides an exhaustive technical analysis of the architectural requirements for such a laboratory, emphasizing the necessity of a pluggable policy plane, a decentralized identity layer for policy attestation, and a resilient, permanent infrastructure for the dissemination of security intelligence.

## **The Taxonomic Framework of Emerging Agentic Threats**

The primary mission of an agentic security laboratory is to dissect the mechanics of vulnerabilities that specifically exploit the autonomy and tool-access capabilities of large language model (LLM) agents. Traditional security controls, which rely on the distinction between code and data, are fundamentally challenged by LLMs that treat instructions and inputs as a single continuous stream of tokens.1 This architectural lack of separation creates the foundation for indirect prompt injection (IDPI) and agent hijacking, where malicious instructions are embedded within legitimate data—such as emails, calendar invites, or scraped web content—ingested by the agent.2

## **Agent Hijacking and Persistent Manipulation**

Agent hijacking represents the most sophisticated incarnation of this threat, moving beyond simple one-off manipulation to achieve persistent control over an agent's reasoning and actions.2 Unlike direct prompt injection, hijacking often persists across sessions and does not require continuous interaction from the attacker.4 For example, an attacker can embed a directive in a public-facing website that, when scraped by a research agent, poisons its internal execution preferences to over-collect data or rerooute its reasoning paths.4 This "workflow poisoning" transforms a benign tool into a malicious pivot point, allowing for systematic data exfiltration through standard collaboration features, often without triggering traditional firewall alerts.4

## **Analysis of Critical Agentic Vulnerabilities**

The research conducted within the laboratory must align with emerging industry standards, specifically the OWASP Top 10 for LLMs. The evolution of these risks reflects the growing complexity of agentic pipelines.

| Vulnerability ID | Vulnerability Name | Primary Mechanism of Action | Potential Impact on Agents |
| :---- | :---- | :---- | :---- |
| **LLM01:2025** | Prompt Injection | Blending of user input with system instructions to override intent. | Complete agent takeover and tool misuse. |
| **LLM02:2025** | Sensitive Info Disclosure | Failure to sanitize PII or credentials in LLM responses. | Unauthorized credential leakage and privacy breaches. |
| **LLM05:2025** | Insecure Output Handling | Direct execution of LLM-generated code or commands without validation. | Remote code execution (RCE) on the host system. |
| **LLM06:2025** | Excessive Agency | Granting agents autonomous access to sensitive tools without human-in-the-loop gates. | Data destruction and unauthorized transactions. |
| **LLM08:2025** | Insecure Plugin Design | Vulnerabilities in RAG pipelines where retrieved context poisons reasoning. | Retrieval-based attacks steering agent decisions. |

6

The case of CVE-2025-53773, involving GitHub Copilot and Visual Studio Code, illustrates the real-world consequences of these vulnerabilities. Attackers were able to exploit Copilot's ability to modify local settings by embedding instructions in source code comments, effectively enabling a "YOLO mode" that granted unrestricted shell command execution.9 This demonstrates that AI agents possessing file-writing and code-execution privileges will inherently seek pathways to modify their own permissions if not constrained by an external, immutable policy layer.9

## **Architecting a Pluggable Policy Evaluation Plane**

A core requirement for a research laboratory is the ability to benchmark different authorization strategies. By making the policy engine pluggable, the laboratory can invoke multiple evaluators—such as the Open Policy Agent (OPA) and AWS Cedar—to compare their performance, safety guarantees, and expressiveness in the face of identical attack vectors.10

## **The Philosophical Divergence: OPA vs. Cedar**

The decision to leverage both OPA and Cedar is driven by their fundamentally different design philosophies. OPA, using the Rego language, is a general-purpose policy-as-code engine designed for flexibility across the entire software stack.11 It excels in scenarios requiring complex data transformations and the inspection of arbitrary JSON inputs.11 However, Rego's logical programming nature (extending Datalog) presents a steep learning curve and potential nondeterminism if not meticulously authored.11

In contrast, Cedar was developed specifically for fine-grained application authorization with a focus on safety, readability, and performance.11 Cedar is the first policy language built from the ground up to be formally verified using automated reasoning and tested rigorously through differential random testing against a Lean specification.10 This formal verification ensures that Cedar policies always terminate and are deterministic, making it the superior choice for high-assurance security boundaries where "deny trumps allow" must be mathematically guaranteed.13

## **Comparative Performance and Safety Metrics**

| Metric | Open Policy Agent (Rego) | AWS Cedar |
| :---- | :---- | :---- |
| **Language Logic** | Datalog-based (Predicate logic) | Declarative (Entity-Attribute-Action) |
| **Formal Verification** | None (Relies on testing) | Formally specified in Lean; verified Rust core |
| **Latency** | Milliseconds (Variable by complexity) | Sub-millisecond (Bounded latency) |
| **Safety Constraints** | Turing-complete-like; high expressiveness | Intentionally bounded; no regex/I/O |
| **Implementation** | Go, WebAssembly | Rust (Native), Go (Wasm/Native SDK) |
| **Primary Use Case** | Kubernetes, CI/CD, General Logic | Fine-grained App Auth, RBAC, ABAC |

11

For a research-oriented laboratory, the pluggable architecture should utilize Go-based SDKs to maintain consistency with the existing Tachyon Tongs infrastructure. The cedar-go implementation, maintained by StrongDM, provides a native Go library that allows for the embedding of the Cedar authorizer directly into agentic workflows.10 Simultaneously, the OPA Go SDK enables high-level APIs for query evaluation, ensuring that the laboratory can utilize OPA for its broad interoperability while reserving Cedar for safety-critical guardrails.17

## **The Role of OPAL in Dynamic Policy Distribution**

The utility of these engines is significantly enhanced when paired with the Open Policy Administration Layer (OPAL). OPAL acts as a real-time control plane that manages the distribution of policies and data to the distributed agents.19 By using a websocket pub/sub architecture, OPAL ensures that as soon as the security laboratory identifies a new attack pattern and updates its Git-based policy repository, the updated rules are pushed instantly to all active agentic firewalls.21 This "live update" capability is essential for mitigating fast-moving agent hijacking campaigns that exploit fleeting vulnerabilities in external data sources.19

## **Cryptographic Integrity and Identity-Based Policy Attestation**

A research laboratory must ensure that every published security rule and policy is verifiable and resistant to tampering. Traditional cryptographic methods, such as PGP, are often hampered by the operational complexity of key distribution and the risk of key loss.23 The evolution toward identity-based signing, pioneered by the Sigstore project, offers a more resilient alternative for the laboratory's discovering.23

## **Sigstore: Moving Beyond Long-Lived Keys**

Sigstore simplifies the signing process by utilizing ephemeral, short-lived key pairs bound to a verifiable OpenID Connect (OIDC) identity.23 When a researcher publishes a new policy set, they can use the cosign tool to sign the artifact using their GitHub or Google identity.23 Sigstore's certificate authority, Fulcio, issues a temporary certificate, and the signing event is recorded in Rekor, an immutable transparency log.23 This architecture provides a permanent, auditable record of the policy's origin and integrity without requiring the researcher to manage long-lived private keys.23

## **Leveraging the Ethereum Ecosystem for Decentralized Trust**

The laboratory can further strengthen its trust model by integrating Ethereum-based naming and attestation services. This synergy allows for a decentralized "chain of custody" for security intelligence that is independent of any single hosting provider or platform.15

1. **Ethereum Name Service (ENS)**: ENS allows the laboratory to map human-readable names (e.g., lab.tachyontongs.eth) to the cryptographic identities used in the signing process.29 By storing a researcher's public key or Sigstore identity in an ENS text record, users can verify that a policy was indeed authored by the lab.29  
2. **Ethereum Attestation Service (EAS)**: EAS provides a generalized protocol for making "attestations"—structured, signed claims about data.28 The laboratory can use EAS to create attestations that a particular policy has passed formal verification or that a specific agent behavior has been categorized as malicious.33 These attestations can be stored on-chain for maximum visibility or off-chain for cost efficiency, while still maintaining cryptographic provability.28

## **Standardized Schemas for Policy Attestation**

A critical function of the laboratory is the creation of standardized schemas to make security results interoperable and comparable. Recent initiatives like the "EveryEvalEver" metadata schema, built with input from NIST and Hugging Face, provide a blueprint for recording the provenance and parameters of AI evaluations.35

| Schema Component | Technical Definition | Role in Policy Attestation |
| :---- | :---- | :---- |
| **Policy UID** | bytes32 | Unique identifier for the specific rule or policy file. |
| **Attester Identity** | address / OIDC | The verified address or identity of the security researcher. |
| **Verification Level** | uint8 | Range from 1 (unverified) to 5 (formally verified in Lean). |
| **Threat Category** | string | Mapping to OWASP Top 10 (e.g., "LLM01: Prompt Injection"). |
| **Audit Hash** | bytes32 | Merkle root of the full audit log stored on Arweave. |

34

## **Resilient Dissemination: Architecting the Public Repository**

The final requirement for the security laboratory is a public dissemination platform that is economical yet resilient to the high-volume DDoS attacks often directed at security research sites. Attackers may employ "Economic Denial of Sustainability" (EDoS) tactics, exploiting the auto-scaling features of centralized clouds to incur massive costs for the target.38

## **Distributed Resilience with Cloudflare and Edge Services**

Cloudflare represents the gold standard for economical DDoS resilience. Its edge network can intercept hyper-volumetric attacks (which grew by 700% in 2025\) before they reach the origin.40 By leveraging Cloudflare's unmetered DDoS mitigation and Web Application Firewall (WAF), the laboratory can protect its discovery portal from the unpredictable traffic spikes associated with high-profile security releases.42

## **Permanent and Censorship-Resistant Hosting: Arweave and Fleek**

For the long-term archival of security policies and research findings, decentralized storage protocols offer distinct advantages over traditional shared hosting. Arweave’s "pay once, store forever" model is particularly suited for security researchers who wish to ensure their data remains available and untampered for centuries without ongoing subscription costs.43 By paying a one-time fee (approximately $5–$10 per GB in 2026 projections), the laboratory can archive its entire history on the "Permaweb".44

Fleek complements this by providing a decentralized edge computing layer that integrates with Arweave and IPFS.46 Fleek allows the laboratory to host a high-performance, censorship-resistant website where the content is served from a global edge network but ultimately backed by immutable decentralized storage.46 This hybrid model—Cloudflare for front-line DDoS defense and Fleek/Arweave for backend data integrity—creates a fortress for security intelligence.46

## **Cost-Effectiveness Comparison for Hosting Research Artifacts**

| Hosting Type | Provider Example | Resilience Profile | 2026 Cost Outlook |
| :---- | :---- | :---- | :---- |
| **Centralized Shared** | AccuWeb / Hostinger | Basic Firewall; vulnerable to volumetric DDoS. | $2-$5 / Month |
| **Centralized Edge** | Cloudflare Pages | Best-in-class DDoS/WAF; high global speed. | Free Tier / $20+ Pro |
| **Decentralized Perm** | Arweave / Fleek | High Censorship Resistance; Permanent Data. | $5-$10 / GB (Lifetime) |
| **Cloud Object** | Amazon S3 | Metered bandwidth; vulnerable to EDoS/Surge costs. | $0.276 / GB / Year \+ Egress |

44

## **Blueprint for Implementation: The Integrated Laboratory**

The successful extension of Tachyon Tongs into a full-scale research laboratory requires the integration of these disparate components into a cohesive pipeline. The laboratory should not only filter traffic but also generate telemetry that feeds back into the policy creation process.

## **Step 1: Pluggable Core with Go-Based Dispatching**

The laboratory's core evaluation engine should be refactored into a Go-based dispatcher. This dispatcher will receive authorization requests from the agent harness and route them to both OPA and Cedar. The research value of the laboratory is maximized when the dispatcher logs discrepancies in decision-making: for instance, a scenario where OPA allows a request that Cedar's formal schema forbids.13

## **Step 2: Automated Signing and Attestation via CI/CD**

Integrating Sigstore into the laboratory's CI/CD pipeline ensures that every time a researcher commits a new policy to the Git repository, it is automatically signed using their OIDC identity.23 Simultaneously, the pipeline should trigger an EAS attestation on an L2 blockchain, providing a "seal of verification" that is indexed and searchable by other security tools.28

## **Step 3: Global Dissemination and Monitoring**

Discoveries should be published as "Signed Artifacts" to a Fleek-hosted portal. By utilizing ENS to point to the latest Arweave transaction, the laboratory maintains a decentralized yet user-friendly interface.29 The monitoring of these published rules by other researchers—enabled by the transparency logs of Sigstore and the public nature of Arweave—creates a feedback loop that rapidly hardens agentic systems against novel attacks like recursive loop exhaustion and context window poisoning.53

The creation of an agentic security laboratory marks the beginning of a move toward "Self-Defending AI." By combining the formal rigor of Cedar, the administrative agility of OPAL, the decentralized trust of Sigstore and Ethereum, and the permanent resilience of the Permaweb, the Tachyon Tongs laboratory will serve as a critical foundation for securing the autonomous digital future. The findings generated will not only protect individual agentic networks but will contribute to a global, cryptographically verified repository of security intelligence that evolves alongside the agents it protects.

#### **Works cited**

1. Indirect Prompt Injection: The Hidden Threat Breaking Modern AI Systems | Lakera, accessed March 13, 2026, [https://www.lakera.ai/blog/indirect-prompt-injection](https://www.lakera.ai/blog/indirect-prompt-injection)  
2. Technical Blog: Strengthening AI Agent Hijacking Evaluations \- NIST, accessed March 13, 2026, [https://www.nist.gov/news-events/news/2025/01/technical-blog-strengthening-ai-agent-hijacking-evaluations](https://www.nist.gov/news-events/news/2025/01/technical-blog-strengthening-ai-agent-hijacking-evaluations)  
3. Fooling AI Agents: Web-Based Indirect Prompt Injection Observed in the Wild \- Unit 42, accessed March 13, 2026, [https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/](https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/)  
4. Agent Hijacking: How Prompt Injection Leads to Full AI System Compromise | Straiker, accessed March 13, 2026, [https://www.straiker.ai/blog/agent-hijacking-how-prompt-injection-leads-to-full-ai-system-compromise](https://www.straiker.ai/blog/agent-hijacking-how-prompt-injection-leads-to-full-ai-system-compromise)  
5. The AI Agents That Trust Too Much: Are Your Agentic Workflows Vulnerable To Attack? PART 2 \- Splx.ai, accessed March 13, 2026, [https://splx.ai/blog/indirect-prompt-injection-agentic-ai-security](https://splx.ai/blog/indirect-prompt-injection-agentic-ai-security)  
6. Zero Trust, Agent Zero: Your New AI Agent Might Be Your Biggest Security Vulnerability, accessed March 13, 2026, [https://www.impactanalytics.ai/blog/zero-trust-agentic-ai](https://www.impactanalytics.ai/blog/zero-trust-agentic-ai)  
7. What are the OWASP Top 10 risks for LLMs? | Trend Micro (US), accessed March 13, 2026, [https://www.trendmicro.com/en\_us/what-is/ai/owasp-top-10.html](https://www.trendmicro.com/en_us/what-is/ai/owasp-top-10.html)  
8. OWASP Top 10 LLM, Updated 2025: Examples and Mitigation Strategies \- Oligo Security, accessed March 13, 2026, [https://www.oligo.security/academy/owasp-top-10-llm-updated-2025-examples-and-mitigation-strategies](https://www.oligo.security/academy/owasp-top-10-llm-updated-2025-examples-and-mitigation-strategies)  
9. Prompt Injection Attacks in Large Language Models and AI Agent Systems: A Comprehensive Review of Vulnerabilities, Attack Vectors, and Defense Mechanisms \- MDPI, accessed March 13, 2026, [https://www.mdpi.com/2078-2489/17/1/54](https://www.mdpi.com/2078-2489/17/1/54)  
10. cedar-policy \- GitHub, accessed March 13, 2026, [https://github.com/cedar-policy](https://github.com/cedar-policy)  
11. OPA vs Cedar vs Zanzibar: 2025 Policy Engine Guide \- Oso, accessed March 13, 2026, [https://www.osohq.com/learn/opa-vs-cedar-vs-zanzibar](https://www.osohq.com/learn/opa-vs-cedar-vs-zanzibar)  
12. An Empirical Study of Policy-as-Code Adoption in Open-Source Software Projects \- arXiv, accessed March 13, 2026, [https://arxiv.org/html/2601.05555v1](https://arxiv.org/html/2601.05555v1)  
13. MCP Access Control: OPA vs Cedar Comparison \- Natoma, accessed March 13, 2026, [https://natoma.ai/blog/mcp-access-control-opa-vs-cedar-the-definitive-guide](https://natoma.ai/blog/mcp-access-control-opa-vs-cedar-the-definitive-guide)  
14. Implementation of the Cedar Policy Language \- GitHub, accessed March 13, 2026, [https://github.com/cedar-policy/cedar](https://github.com/cedar-policy/cedar)  
15. \[Sandbox\] Cedar Policy · Issue \#371 · cncf/sandbox \- GitHub, accessed March 13, 2026, [https://github.com/cncf/sandbox/issues/371](https://github.com/cncf/sandbox/issues/371)  
16. cedar-policy/cedar-go: Golang implementation of the Cedar Policy Language \- GitHub, accessed March 13, 2026, [https://github.com/cedar-policy/cedar-go](https://github.com/cedar-policy/cedar-go)  
17. Integrating OPA \- Open Policy Agent, accessed March 13, 2026, [https://openpolicyagent.org/docs/integration](https://openpolicyagent.org/docs/integration)  
18. opa command \- github.com/open-policy-agent/opa \- Go Packages, accessed March 13, 2026, [https://pkg.go.dev/github.com/open-policy-agent/opa](https://pkg.go.dev/github.com/open-policy-agent/opa)  
19. Policy Engine Showdown \- OPA vs. OpenFGA vs. Cedar \- Permit.io, accessed March 13, 2026, [https://www.permit.io/blog/policy-engine-showdown-opa-vs-openfga-vs-cedar](https://www.permit.io/blog/policy-engine-showdown-opa-vs-openfga-vs-cedar)  
20. Welcome to OPAL | OPAL, accessed March 13, 2026, [https://docs.opal.ac/](https://docs.opal.ac/)  
21. Design | OPAL, accessed March 13, 2026, [https://docs.opal.ac/overview/design](https://docs.opal.ac/overview/design)  
22. Multiple Policy-Engine Support | Permit.io Documentation, accessed March 13, 2026, [https://docs.permit.io/integrations/policy-engines/overview/](https://docs.permit.io/integrations/policy-engines/overview/)  
23. Sigstore: Overview, accessed March 13, 2026, [https://docs.sigstore.dev/about/overview/](https://docs.sigstore.dev/about/overview/)  
24. Frequently asked questions \- Sigstore, accessed March 13, 2026, [https://docs.sigstore.dev/about/faq/](https://docs.sigstore.dev/about/faq/)  
25. Home · Sigstore, accessed March 13, 2026, [https://www.sigstore.dev/](https://www.sigstore.dev/)  
26. Overview \- Sigstore, accessed March 13, 2026, [https://docs.sigstore.dev/cosign/signing/overview/](https://docs.sigstore.dev/cosign/signing/overview/)  
27. Sigstore Quickstart with Cosign, accessed March 13, 2026, [https://docs.sigstore.dev/quickstart/quickstart-cosign/](https://docs.sigstore.dev/quickstart/quickstart-cosign/)  
28. Welcome to EAS | Ethereum Attestation Service, accessed March 13, 2026, [https://docs.attest.org/](https://docs.attest.org/)  
29. Ens Meaning Crypto: A Plain-english Guide to The Ethereum Name Service, accessed March 13, 2026, [https://westafricatradehub.com/crypto/ens-meaning-crypto-a-plain-english-guide-to-the-ethereum-name-service/](https://westafricatradehub.com/crypto/ens-meaning-crypto-a-plain-english-guide-to-the-ethereum-name-service/)  
30. A COMPREHENSIVE GUIDE TO ETHEREUM NAME SERVICE (ENS) IN CRYPTOCURRENCY | by El Gringo MD | Medium, accessed March 13, 2026, [https://medium.com/@El\_Gringo1776/a-comprehensive-guide-to-ethereum-name-service-ens-in-cryptocurrency-29b94943e41e](https://medium.com/@El_Gringo1776/a-comprehensive-guide-to-ethereum-name-service-ens-in-cryptocurrency-29b94943e41e)  
31. Ethereum Name Service (ENS) Integration \- easyDNS Knowledge Base, accessed March 13, 2026, [https://kb.easydns.com/knowledge/ethereum-name-service-ens-integration/](https://kb.easydns.com/knowledge/ethereum-name-service-ens-integration/)  
32. ethereum-attestation-service/eas-contracts \- GitHub, accessed March 13, 2026, [https://github.com/ethereum-attestation-service/eas-contracts](https://github.com/ethereum-attestation-service/eas-contracts)  
33. Attestations /ˌaˌteˈstāSH(ə)n; are structured pieces of information signed by an entity about something. \- EAS, accessed March 13, 2026, [https://docs.attest.org/docs/core--concepts/attestations](https://docs.attest.org/docs/core--concepts/attestations)  
34. Attestation Framework \- OMA3 Developer Docs, accessed March 13, 2026, [https://docs.oma3.org/attestations](https://docs.oma3.org/attestations)  
35. Why Noma Security is helping build a standard for ai evaluation reporting, accessed March 13, 2026, [https://noma.security/blog/why-noma-security-is-helping-build-a-standard-for-ai-evaluation-reporting/](https://noma.security/blog/why-noma-security-is-helping-build-a-standard-for-ai-evaluation-reporting/)  
36. Create a Schema | Ethereum Attestation Service \- EAS, accessed March 13, 2026, [https://docs.attest.org/docs/tutorials/create-a-schema](https://docs.attest.org/docs/tutorials/create-a-schema)  
37. Schemas | Ethereum Attestation Service, accessed March 13, 2026, [https://docs.attest.org/docs/core--concepts/schemas](https://docs.attest.org/docs/core--concepts/schemas)  
38. Enhancing public cloud resilience: an analytical review of detection and mitigation strategies against economic denial of sustainability attacks \- University of Portsmouth Research Portal, accessed March 13, 2026, [https://researchportal.port.ac.uk/en/publications/enhancing-public-cloud-resilience-an-analytical-review-of-detecti/](https://researchportal.port.ac.uk/en/publications/enhancing-public-cloud-resilience-an-analytical-review-of-detecti/)  
39. Economic DDoS on serverless : r/webdev \- Reddit, accessed March 13, 2026, [https://www.reddit.com/r/webdev/comments/1nbc8e1/economic\_ddos\_on\_serverless/](https://www.reddit.com/r/webdev/comments/1nbc8e1/economic_ddos_on_serverless/)  
40. Cloudflare's 2025 Q3 DDoS threat report \-- including Aisuru, the apex of botnets, accessed March 13, 2026, [https://blog.cloudflare.com/ddos-threat-report-2025-q3/](https://blog.cloudflare.com/ddos-threat-report-2025-q3/)  
41. Cloudflare recognized as a 'Leader' in The Forrester Wave for DDoS Mitigation Solutions, accessed March 13, 2026, [https://blog.cloudflare.com/cloudflare-is-named-a-leader-in-the-forrester-wave-for-ddos-mitigation-solutions/](https://blog.cloudflare.com/cloudflare-is-named-a-leader-in-the-forrester-wave-for-ddos-mitigation-solutions/)  
42. Slay the DDoS monster with CloudFlare and Rackspace Technology, accessed March 13, 2026, [https://www.rackspace.com/blog/year-slay-ddos-monster-cloud](https://www.rackspace.com/blog/year-slay-ddos-monster-cloud)  
43. Arweave Price Prediction: $15 Rally and 2026-2030 Forecast | KuCoin, accessed March 13, 2026, [https://www.kucoin.com/news/flash/arweave-price-prediction-15-rally-and-2026-2030-forecast](https://www.kucoin.com/news/flash/arweave-price-prediction-15-rally-and-2026-2030-forecast)  
44. Where Blockchain Data Actually Lives (IPFS, Arweave & The 2026 Storage War) \- Medium, accessed March 13, 2026, [https://medium.com/coinmonks/where-blockchain-data-actually-lives-ipfs-arweave-the-2026-storage-war-4319361f512a](https://medium.com/coinmonks/where-blockchain-data-actually-lives-ipfs-arweave-the-2026-storage-war-4319361f512a)  
45. The Decentralized Storage War: Filecoin vs. Arweave | CoinMarketCap, accessed March 13, 2026, [https://coinmarketcap.com/academy/article/the-decentralized-storage-war-filecoin-vs-arweave](https://coinmarketcap.com/academy/article/the-decentralized-storage-war-filecoin-vs-arweave)  
46. Fleek: Web3 Decentralized Edge Computing Platform | Fleek Whitepaper \- Bitget, accessed March 13, 2026, [https://www.bitget.com/price/fleek/whitepaper](https://www.bitget.com/price/fleek/whitepaper)  
47. Best Fleek Alternatives & Competitors \- SourceForge, accessed March 13, 2026, [https://sourceforge.net/software/product/Fleek/alternatives](https://sourceforge.net/software/product/Fleek/alternatives)  
48. CDN-on-Demand: An Affordable DDoS Defense via Untrusted Clouds \- Network and Distributed System Security (NDSS) Symposium, accessed March 13, 2026, [https://www.ndss-symposium.org/wp-content/uploads/2017/09/cdn-on-demand-affordable-ddos-defense-via-untrusted-clouds.pdf](https://www.ndss-symposium.org/wp-content/uploads/2017/09/cdn-on-demand-affordable-ddos-defense-via-untrusted-clouds.pdf)  
49. Best Cheap Web Hosting in 2026 \- CNET, accessed March 13, 2026, [https://www.cnet.com/tech/services-and-software/best-cheap-web-hosting/](https://www.cnet.com/tech/services-and-software/best-cheap-web-hosting/)  
50. Comparison of storage costs between Arweave and Filecoin, and the changing patterns of social storage costs | 大鱼元宇宙 on Binance Square, accessed March 13, 2026, [https://www.binance.com/en/square/post/29771856445553](https://www.binance.com/en/square/post/29771856445553)  
51. Securing Artifacts: Keyless Signing with Sigstore and CI/MON \- Cycode, accessed March 13, 2026, [https://cycode.com/blog/securing-artifacts-keyless-signing-with-sigstore-and-ci-mon/](https://cycode.com/blog/securing-artifacts-keyless-signing-with-sigstore-and-ci-mon/)  
52. Rootstock Attestation Service Starter Guide, accessed March 13, 2026, [https://dev.rootstock.io/dev-tools/attestations/ras/](https://dev.rootstock.io/dev-tools/attestations/ras/)  
53. The OWASP Top 10 for LLM Agents: Why autonomous workflows are breaking traditional security models : r/AI\_Agents \- Reddit, accessed March 13, 2026, [https://www.reddit.com/r/AI\_Agents/comments/1r92sqs/the\_owasp\_top\_10\_for\_llm\_agents\_why\_autonomous/](https://www.reddit.com/r/AI_Agents/comments/1r92sqs/the_owasp_top_10_for_llm_agents_why_autonomous/)  
54. sigstore is a project with the goal of providing a public good / non-profit service to improve the open source software supply chain by easing the adoption of cryptographic software signing, backed by transparency log technologies., accessed March 13, 2026, [https://www.sigstore.dev/docs/what\_is\_sigstore](https://www.sigstore.dev/docs/what_is_sigstore)