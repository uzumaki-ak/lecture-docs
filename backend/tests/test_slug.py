import pytest
from app.utils.slug_generator import generate_slug
from unittest.mock import MagicMock

def test_slug_generation():
    """Test basic slug generation"""
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = None
    
    slug = generate_slug("My Awesome Project", db_mock)
    assert slug == "my-awesome-project"

def test_slug_special_chars():
    """Test slug with special characters"""
    db_mock = MagicMock()
    db_mock.query().filter().first.return_value = None
    
    slug = generate_slug("Test! @#$% Project 123", db_mock)
    assert slug == "test-project-123"

def test_slug_uniqueness():
    """Test slug collision handling"""
    db_mock = MagicMock()
    # Simulate existing slug
    db_mock.query().filter().first.side_effect = [True, True, None]
    
    slug = generate_slug("duplicate", db_mock)
    assert slug == "duplicate-2"
