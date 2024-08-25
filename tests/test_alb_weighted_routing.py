import unittest
from alb_weighted_routing import calculate_combined_utilization

class TestALBWeightedRouting(unittest.TestCase):
    
    def test_calculate_combined_utilization(self):
        cpu = 70.0
        memory = 50.0
        expected_combined = 60.0
        self.assertEqual(calculate_combined_utilization(cpu, memory), expected_combined)

if __name__ == "__main__":
    unittest.main()
