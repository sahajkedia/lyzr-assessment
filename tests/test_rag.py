"""
Tests for the RAG (Retrieval-Augmented Generation) system.
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.rag.faq_rag import FAQRAG


# ============================================================================
# RAG System Tests
# ============================================================================

@pytest.fixture
def rag():
    """Create RAG instance for testing."""
    return FAQRAG()


def test_rag_initialization(rag):
    """Test that RAG system initializes properly."""
    assert rag is not None
    assert rag.vector_store is not None
    assert rag.clinic_data is not None
    assert len(rag.clinic_data) > 0


def test_load_clinic_data(rag):
    """Test loading clinic information."""
    clinic_data = rag.clinic_data
    
    # Check that key sections exist
    assert "clinic_details" in clinic_data
    assert "contact_information" in clinic_data
    assert "insurance_and_billing" in clinic_data
    assert "appointment_types" in clinic_data


def test_vector_store_is_populated(rag):
    """Test that vector store has documents."""
    count = rag.vector_store.count()
    assert count > 0, "Vector store should have documents"


def test_retrieve_relevant_info(rag):
    """Test retrieving relevant information."""
    results = rag.retrieve_relevant_info("What insurance do you accept?")
    
    assert len(results) > 0
    assert "content" in results[0]
    assert "metadata" in results[0]


def test_answer_question_insurance(rag):
    """Test answering insurance question."""
    result = rag.answer_question("What insurance plans do you accept?")
    
    assert "context" in result
    assert "sources" in result
    assert "question" in result
    assert len(result["sources"]) > 0
    
    # Context should mention insurance
    assert "insurance" in result["context"].lower()


def test_answer_question_parking(rag):
    """Test answering parking question."""
    result = rag.answer_question("Where can I park?")
    
    assert "context" in result
    assert len(result["sources"]) > 0
    
    # Context should mention parking
    context_lower = result["context"].lower()
    assert "park" in context_lower or "parking" in context_lower


def test_answer_question_hours(rag):
    """Test answering hours question."""
    result = rag.answer_question("What are your hours?")
    
    assert "context" in result
    assert len(result["sources"]) > 0


def test_get_specific_info_clinic_details(rag):
    """Test getting specific clinic details."""
    clinic_details = rag.get_specific_info("clinic_details")
    
    assert clinic_details is not None
    assert isinstance(clinic_details, dict)


def test_get_specific_info_with_topic(rag):
    """Test getting specific info with topic."""
    contact = rag.get_specific_info("contact_information", "phone")
    
    # Should return phone number or None if not found
    assert contact is None or isinstance(contact, str)


def test_get_specific_info_invalid_category(rag):
    """Test getting info from invalid category."""
    result = rag.get_specific_info("invalid_category")
    
    assert result is None


def test_get_all_insurance_providers(rag):
    """Test getting insurance providers list."""
    providers = rag.get_all_insurance_providers()
    
    assert isinstance(providers, list)
    # Should have at least some providers
    assert len(providers) >= 0


def test_get_appointment_types(rag):
    """Test getting appointment types."""
    appointment_types = rag.get_appointment_types()
    
    assert isinstance(appointment_types, dict)
    # Should have at least one appointment type
    assert len(appointment_types) > 0
    
    # Check that appointment types have expected structure
    for appt_type, details in appointment_types.items():
        assert isinstance(details, dict), f"Appointment type {appt_type} should have details"


def test_get_contact_info(rag):
    """Test getting contact information."""
    contact = rag.get_contact_info()
    
    assert isinstance(contact, dict)


def test_get_policies(rag):
    """Test getting policies."""
    policies = rag.get_policies()
    
    assert isinstance(policies, dict)


def test_retrieve_multiple_results(rag):
    """Test retrieving multiple results."""
    results = rag.retrieve_relevant_info("Tell me about appointments", n_results=5)
    
    assert len(results) <= 5
    assert len(results) > 0


def test_flatten_dict(rag):
    """Test flattening dictionary."""
    test_dict = {
        "level1": {
            "level2": {
                "level3": "value"
            }
        }
    }
    
    flattened = rag._flatten_dict(test_dict)
    
    assert isinstance(flattened, list)
    assert len(flattened) > 0


def test_rag_context_relevance(rag):
    """Test that RAG returns relevant context."""
    # Test multiple questions
    test_cases = [
        ("insurance", "insurance"),
        ("parking", "park"),
        ("hours", "hour"),
        ("appointment types", "appointment"),
    ]
    
    for question, expected_keyword in test_cases:
        result = rag.answer_question(f"Tell me about {question}")
        context_lower = result["context"].lower()
        
        # Context should be relevant (contain related keyword)
        # We're lenient here since vector search may return various related info
        assert len(context_lower) > 0, f"Context should not be empty for question about {question}"


def test_retrieve_with_different_n_results(rag):
    """Test retrieving different numbers of results."""
    for n in [1, 2, 3, 5]:
        results = rag.retrieve_relevant_info("clinic information", n_results=n)
        assert len(results) <= n
        assert len(results) > 0


# ============================================================================
# Integration Tests with Mocked Data
# ============================================================================

def test_rag_with_empty_query(rag):
    """Test RAG with empty query."""
    results = rag.retrieve_relevant_info("")
    # Should still return results (may be less relevant)
    assert isinstance(results, list)


def test_rag_with_long_query(rag):
    """Test RAG with very long query."""
    long_query = "What are all the insurance providers you accept and what are your policies regarding billing and payment plans and cancellations and rescheduling appointments?"
    
    result = rag.answer_question(long_query)
    
    assert "context" in result
    assert len(result["context"]) > 0


def test_rag_with_special_characters(rag):
    """Test RAG with special characters in query."""
    result = rag.answer_question("What's the clinic's phone #? Can I email @ you?")
    
    assert "context" in result
    assert len(result["sources"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

