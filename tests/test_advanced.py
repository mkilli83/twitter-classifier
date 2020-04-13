# -*- coding: utf-8 -*-

from .context import src

import unittest


class AdvancedTestSuite(unittest.TestCase):
    """Advanced test cases."""

    def test_simple(self):
        self.assertIsNone(src.core.validation_of_ci())


if __name__ == '__main__':
    unittest.main()
