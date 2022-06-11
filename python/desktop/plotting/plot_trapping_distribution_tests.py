import unittest
from plot_trapping_distribution import plot_trapping_distribution
import numpy as np


class TestPlotTrappingDistribution(unittest.TestCase):
    def test_plot_positive(self) -> None:
        plot_trapping_distribution(np.ones((11, 8)), np.ones((1, 11)))

    def test_plot_negative(self) -> None:
        with self.assertRaises(TypeError):
            plot_trapping_distribution(np.array([1, 2, 3], [1]))
