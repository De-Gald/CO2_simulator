import unittest
from explore_simulation import explore_simulation, WrongWellLocationException
from unittest.mock import patch


@patch(
    'python.desktop.plotting.plot_trapping_distribution'
)
class TestExploreSimulation(unittest.TestCase):
    def test_different_well_locations_positive(self, _) -> None:
        explore_simulation((487000.0, 6721000.0))

    def test_different_well_locations_negative(self, _) -> None:
        with self.assertRaises(WrongWellLocationException):
            explore_simulation((487000.0, -5.0))
