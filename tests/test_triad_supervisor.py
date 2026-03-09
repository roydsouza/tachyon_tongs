import unittest
from unittest.mock import patch, MagicMock
from src.adk_sentinel import create_supervisor_graph, run_supervisor

class TestTriadSupervisor(unittest.TestCase):
    """
    Ensures that the Triad Split successfully isolates 
    the Scout, Analyst, and Engineer ADK Agents.
    """
    
    def test_supervisor_graph_construction(self):
        # When creating the graph
        graph = create_supervisor_graph()
        
        # Then the three exact Triad nodes should exist without Privilege Collapse
        self.assertIn("Scout", graph.nodes)
        self.assertIn("Analyst", graph.nodes)
        self.assertIn("Engineer", graph.nodes)
        
        # And the topology must strictly air-gap the Scout from the Engineer
        self.assertIn("Analyst", graph.edges["Scout"])
        self.assertIn("Engineer", graph.edges["Analyst"])
        
    @patch('src.agents.scout_agent.VulnerabilityScraper.scrape_new_threats')
    def test_supervisor_routes_scraped_threats(self, mock_scrape):
        mock_scrape.return_value = [{"cve_id": "TEST-1", "description": "foo"}]
        
        # When the Supervisor is run
        final_state = run_supervisor("", run_scraper=True)
        
        # The Scout extracted it
        self.assertIn("scraped_threats", final_state)
        # The Analyst parsed it
        self.assertEqual(final_state["analysis"]["status"], "success")
        self.assertIn("TEST-1", final_state["analysis"]["threats_found"][0])
        # The Engineer verified it
        self.assertTrue(final_state["final_output"]["verified"])
