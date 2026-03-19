import unittest
from types import MappingProxyType
from tachyon.enforcement.router import recursive_freeze

class TestFreezeFuzz(unittest.TestCase):
    def test_nested_complex_types(self):
        """Fuzz recursive_freeze with nested and unusual types."""
        data = {
            "a": [1, 2, {"b": 3}],
            "c": {"d": {5, 6}, "e": (7, 8)},
            "f": MappingProxyType({"g": 9})
        }
        
        frozen = recursive_freeze(data)
        
        # Verify Immutability
        self.assertIsInstance(frozen, MappingProxyType)
        self.assertIsInstance(frozen["a"], tuple)
        self.assertIsInstance(frozen["a"][2], MappingProxyType)
        self.assertIsInstance(frozen["c"]["d"], tuple) # Sets converted to tuples
        
        # Mutation should fail
        with self.assertRaises(TypeError):
            frozen["a"][0] = 10
            
        with self.assertRaises(TypeError):
            frozen["c"]["d"] = 11

    def test_already_frozen(self):
        """Ensure already frozen objects are handled correctly."""
        data = MappingProxyType({"a": 1})
        frozen = recursive_freeze(data)
        self.assertEqual(frozen, data)

if __name__ == "__main__":
    unittest.main()
