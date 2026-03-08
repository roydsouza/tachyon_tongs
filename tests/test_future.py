import unittest
from src.cve_scraper import VulnerabilityScraper
from src.wasm_benchmark import WasmToolRunner
from src.behavior_monitor import PromptBehaviorMonitor, BehaviorAnomalyError

class TestPhase3FutureCapabilities(unittest.TestCase):

    # --- Autonomous Scraping Tests ---
    def test_cve_scraper_fetches_mock(self):
        scraper = VulnerabilityScraper(mode="mock")
        threats = scraper.scrape_new_threats()
        
        self.assertEqual(len(threats), 1)
        self.assertEqual(threats[0]["cve_id"], "CVE-2026-99999")
        
        markdown = scraper._format_markdown_entry(threats[0])
        self.assertIn("CVE-2026-99999", markdown)
        self.assertIn("CRITICAL", markdown)

    # --- WASM execution Tests ---
    def test_wasm_runner_blocks_malicious_capability(self):
        runner = WasmToolRunner()
        # Runner simulates WASI capability restrictions
        result = runner.execute_tool(b"binary_code_with_malicious_sys_call", "test")
        
        self.assertEqual(result["status"], "error")
        self.assertIn("denied", result["error"])

    def test_wasm_runner_executes_safely(self):
        runner = WasmToolRunner()
        result = runner.execute_tool(b"safe_code", "data")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("time_ms", result)

    # --- Behavioral Monitor Tests ---
    def test_behavior_monitor_allows_normal_cot(self):
        monitor = PromptBehaviorMonitor(max_reasoning_steps=5)
        cot = [
            "I need to read the file.",
            "I have read the file. It contains JSON.",
            "The JSON is safe. I will format it."
        ]
        self.assertTrue(monitor.check_chain_of_thought(cot))

    def test_behavior_monitor_blocks_loop_exhaustion(self):
        monitor = PromptBehaviorMonitor(max_reasoning_steps=3)
        cot = [
            "Reading file.",
            "Processing chunk 1.",
            "Processing chunk 2.",
            "Processing chunk 3." # Exceeds 3
        ]
        with self.assertRaises(BehaviorAnomalyError):
            monitor.check_chain_of_thought(cot)

    def test_behavior_monitor_blocks_cyclic_hallucination(self):
        monitor = PromptBehaviorMonitor(max_reasoning_steps=10)
        cot = [
            "Wait, I should check the tools.",
            "Calling fetch.",
            "Wait, I should check the tools.", # Exact repeat
        ]
        with self.assertRaises(BehaviorAnomalyError):
            monitor.check_chain_of_thought(cot)

if __name__ == '__main__':
    unittest.main()
