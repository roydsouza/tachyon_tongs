# 📘 EXPLOITATION CATALOG

This file is the single source of truth for internet-born AI/LLM terror.

### CVE-2026-22708
- **Source:** Unknown Source
- **Date Discovered:** 2026-03-12T04:44:34.475338
- **Description:** Cursor is a code editor built for programming with AI. Prior to 2.3, hen the Cursor Agent is running in Auto-Run Mode with Allowlist mode enabled, certain shell built-ins can still be executed without appearing in the allowlist and without requiring user approval.
This allows an attacker via indirect or direct prompt injection to poison the shell environment by setting, modifying, or removing environment variables that influence trusted commands. This vulnerability is fixed in 2.3.

### CVE-2025-54135
- **Source:** Unknown Source
- **Date Discovered:** 2026-03-12T04:44:34.475315
- **Description:** Cursor is a code editor built for programming with AI. Cursor allows writing in-workspace files with no user approval in versions below 1.3.9, If the file is a dotfile, editing it requires approval but creating a new one doesn't. Hence, if sensitive MCP files, such as the .cursor/mcp.json file don't already exist in the workspace, an attacker can chain a indirect prompt injection vulnerability to hijack the context to write to the settings file and trigger RCE on the victim without user approval. This is fixed in version 1.3.9.

### CVE-2025-54130
- **Source:** Unknown Source
- **Date Discovered:** 2026-03-12T04:44:34.472324
- **Description:** Cursor is a code editor built for programming with AI. Cursor allows writing in-workspace files with no user approval in versions less than 1.3.9. If the file is a dotfile, editing it requires approval but creating a new one doesn't. Hence, if sensitive editor files, such as the .vscode/settings.json file don't already exist in the workspace, an attacker can chain a indirect prompt injection vulnerability to hijack the context to write to the settings file and trigger RCE on the victim without user approval. This is fixed in version 1.3.9.

### CVE-TEST-001
- **Source:** Unit Test
- **Date Discovered:** 2026-03-11T18:40:44.915236
- **Description:** No description.

### CVE-2025-58372
- **Source:** Unknown Source
- **Date Discovered:** 2026-03-09T20:38:59.202515
- **Description:** Roo Code is an AI-powered autonomous coding agent that lives in users' editors. Versions 3.25.23 and below contain a vulnerability where certain VS Code workspace configuration files (.code-workspace) are not protected in the same way as the .vscode folder. If the agent was configured to auto-approve file writes, an attacker able to influence prompts (for example via prompt injection) could cause malicious workspace settings or tasks to be written. These tasks could then be executed automatically when the workspace is reopened, resulting in arbitrary code execution. This issue is fixed in version 3.26.0.

### CVE-2025-58371
- **Source:** Unknown Source
- **Date Discovered:** 2026-03-09T20:38:59.202510
- **Description:** Roo Code is an AI-powered autonomous coding agent that lives in users' editors. In versions 3.26.6 and below, a Github workflow used unsanitized pull request metadata in a privileged context, allowing an attacker to craft malicious input and achieve Remote Code Execution (RCE) on the Actions runner. The workflow runs with broad permissions and access to repository secrets. It is possible for an attacker to execute arbitrary commands on the runner, push or modify code in the repository, access secrets, and create malicious releases or packages, resulting in a complete compromise of the repository and its associated services. This is fixed in version 3.26.7.

### CVE-2020-17500
- **Source:** Unknown Source
- **Date Discovered:** 2026-03-09T20:38:59.202500
- **Description:** Barco TransForm NDN-210 Lite, NDN-210 Pro, NDN-211 Lite, and NDN-211 Pro before 3.8 allows Command Injection (issue 1 of 4). The NDN-210 has a web administration panel which is made available over https. The logon method is basic authentication. There is a command injection issue that will result in unauthenticated remote code execution in the username and password fields of the logon prompt. The NDN-210 is part of Barco TransForm N solution and includes the patch from TransForm N version 3.8 onwards.

### CVE-2020-11545
- **Source:** Unknown Source
- **Date Discovered:** 2026-03-09T20:38:59.202496
- **Description:** Project Worlds Official Car Rental System 1 is vulnerable to multiple SQL injection issues, as demonstrated by the email and parameters (account.php), uname and pass parameters (login.php), and id parameter (book_car.php) This allows an attacker to dump the MySQL database and to bypass the login authentication prompt.

### CVE-2020-10106
- **Source:** Unknown Source
- **Date Discovered:** 2026-03-09T20:38:59.202492
- **Description:** PHPGurukul Daily Expense Tracker System 1.0 is vulnerable to SQL injection, as demonstrated by the email parameter in index.php or register.php. The SQL injection allows to dump the MySQL database and to bypass the login prompt.

### CVE-2021-3942
- **Source:** Unknown Source
- **Date Discovered:** 2026-03-09T20:38:59.202488
- **Description:** Certain HP Print products and Digital Sending products may be vulnerable to potential remote code execution and buffer overflow with use of Link-Local Multicast Name Resolution or LLMNR.

### CVE-2021-21960
- **Source:** Unknown Source
- **Date Discovered:** 2026-03-09T20:38:59.202485
- **Description:** A stack-based buffer overflow vulnerability exists in both the LLMNR functionality of Sealevel Systems, Inc. SeaConnect 370W v1.3.34. A specially-crafted network packet can lead to remote code execution. An attacker can send a malicious packet to trigger this vulnerability.

### CVE-2020-17467
- **Source:** Unknown Source
- **Date Discovered:** 2026-03-09T20:38:59.202480
- **Description:** An issue was discovered in FNET through 4.6.4. The code for processing the hostname from an LLMNR request doesn't check for '\0' termination. Therefore, the deduced length of the hostname doesn't reflect the correct length of the actual data. This may lead to Information Disclosure in _fnet_llmnr_poll in fnet_llmnr.c during a response to a malicious request of the DNS class IN.

### CVE-2025-53002
- **Source:** Unknown Source
- **Date Discovered:** 2026-03-09T20:38:59.202475
- **Description:** LLaMA-Factory is a tuning library for large language models. A remote code execution vulnerability was discovered in LLaMA-Factory versions up to and including 0.9.3 during the LLaMA-Factory training process. This vulnerability arises because the `vhead_file` is loaded without proper safeguards, allowing malicious attackers to execute arbitrary malicious code on the host system simply by passing a malicious `Checkpoint path` parameter through the `WebUI` interface. The attack is stealthy, as the victim remains unaware of the exploitation. The root cause is that the `vhead_file` argument is loaded without the secure parameter `weights_only=True`. Version 0.9.4 contains a fix for the issue.

### CVE-2025-46725
- **Source:** Unknown Source
- **Date Discovered:** 2026-03-09T20:38:59.202466
- **Description:** Langroid is a Python framework to build large language model (LLM)-powered applications. Prior to version 0.53.15, `LanceDocChatAgent` uses pandas eval() through `compute_from_docs()`. As a result, an attacker may be able to make the agent run malicious commands through `QueryPlan.dataframe_calc]`) compromising the host system. Langroid 0.53.15 sanitizes input to the affected function by default to tackle the most common attack vectors, and added several warnings about the risky behavior in the project documentation.

### CVE-2024-52803
- **Source:** Unknown Source
- **Date Discovered:** 2026-03-09T20:38:59.202325
- **Description:** LLama Factory enables fine-tuning of large language models. A critical remote OS command injection vulnerability has been identified in the LLama Factory training process. This vulnerability arises from improper handling of user input, allowing malicious actors to execute arbitrary OS commands on the host system. The issue is caused by insecure usage of the `Popen` function with `shell=True`, coupled with unsanitized user input. Immediate remediation is required to mitigate the risk. This vulnerability is fixed in 0.9.1.

