"""Unit Tests for the module"""
import logging

from django.test import TestCase

LOGGER = logging.getLogger(name="django-custom-storage")


class TestCase(TestCase):
    """Test Case for django-custom-storage"""

    def setUp(self):
        """Set up common assets for tests"""
        LOGGER.debug("Tests setUp")

    def tearDown(self):
        """Remove Test Data"""
        LOGGER.debug("Tests tearDown")

    def test_fake(self):
        """Test return passed """
        LOGGER.debug("Fake Test")
        self.assertEqual(0, 0)
