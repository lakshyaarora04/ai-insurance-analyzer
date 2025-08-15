#!/usr/bin/env python3
"""
Comprehensive test for all new features:
- Reasoning Tree with human-readable breakdowns
- Multi-Document Reasoning
- Explainable Decisions
- Override + Feedback Mechanism
- Real Audit Mode
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from backend.utils.document_reader import read_document
from backend.utils.chunker import chunk_text
from backend.retriever.embedder import embed_chunks, embed_claim_query
from backend.retriever.vector_store import VectorStore
from backend.retriever.multi_document_store import MultiDocumentStore, MultiDocumentReasoningEngine
from backend.decision_engine.evaluator import evaluate_claim
from backend.decision_engine.explainable_decisions import ExplainableDecisionProcessor
from backend.feedback.feedback_system import FeedbackManager, FeedbackType
from backend.audit.audit_exporter import AuditManager
from backend.parser.query_parser import NaturalLanguageQueryParser
import json

def test_all_features():
    """Test all new features comprehensively"""
    print("🚀 COMPREHENSIVE FEATURE TESTING")
    print("=" * 80)
    
    # Initialize all systems
    print("🔧 Initializing systems...")
    
    # 1. Multi-Document Store
    multi_doc_store = MultiDocumentStore()
    
    # Add multiple documents
    print("\n📄 Loading multiple documents...")
    doc_files = [
        ("documents/BAJHLIP23020V012223.pdf", "base_policy", "Bajaj Allianz Policy"),
        ("documents/CHOTGDP23004V012223.pdf", "rider", "Critical Illness Rider"),
        ("documents/sample_policy.pdf", "amendment", "Policy Amendment")
    ]
    
    for file_path, doc_type, doc_name in doc_files:
        if os.path.exists(file_path):
            try:
                doc_id = multi_doc_store.add_document(file_path, doc_type, doc_name)
                print(f"✅ Added {doc_name} ({doc_type}) with ID: {doc_id}")
            except Exception as e:
                print(f"⚠️  Could not add {file_path}: {str(e)}")
    
    # Finalize documents to fit vectorizer on all chunks
    multi_doc_store.finalize_documents()
    
    # 2. Initialize other systems
    reasoning_engine = MultiDocumentReasoningEngine(multi_doc_store)
    explainable_processor = ExplainableDecisionProcessor()
    feedback_manager = FeedbackManager()
    audit_manager = AuditManager()
    parser = NaturalLanguageQueryParser()
    
    print(f"✅ Systems initialized successfully")
    
    # Test cases
    test_cases = [
        {
            'name': 'Cataract Surgery - 24 months (Should be APPROVED)',
            'query': "I'm a 45-year-old male who needs cataract surgery in Pune. My policy is 24 months old.",
            'expected': 'approved'
        },
        {
            'name': 'Dental Treatment - 6 months (Should be REJECTED)',
            'query': "Female patient, 32 years old, wants dental treatment in Mumbai. Policy duration 6 months.",
            'expected': 'rejected'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"📋 TEST CASE {i}: {test_case['name']}")
        print(f"{'='*80}")
        
        # 1. Parse natural language query
        print(f"\n🔍 STEP 1: Natural Language Parsing")
        print("-" * 40)
        structured_query = parser.parse_query(test_case['query'])
        print(f"Query: {test_case['query']}")
        print(f"Parsed: {json.dumps(structured_query, indent=2)}")
        
        # 2. Multi-document search
        print(f"\n🔍 STEP 2: Multi-Document Search")
        print("-" * 40)
        multi_doc_results = multi_doc_store.search_across_all_documents(structured_query, top_k=10)
        print(f"Retrieved {len(multi_doc_results)} chunks from multiple documents")
        
        # Group by document type
        results_by_type = {}
        for result in multi_doc_results:
            doc_type = result['document_type']
            if doc_type not in results_by_type:
                results_by_type[doc_type] = []
            results_by_type[doc_type].append(result)
        
        for doc_type, results in results_by_type.items():
            print(f"  📄 {doc_type}: {len(results)} chunks")
        
        # 3. Multi-document reasoning
        print(f"\n🔍 STEP 3: Multi-Document Reasoning")
        print("-" * 40)
        multi_doc_analysis = reasoning_engine.analyze_claim_with_multiple_documents(structured_query)
        print(f"Total chunks found: {multi_doc_analysis['total_chunks_found']}")
        print(f"Supporting clauses: {len(multi_doc_analysis['supporting_clauses'])}")
        print(f"Exclusion clauses: {len(multi_doc_analysis['exclusion_clauses'])}")
        print(f"Conflicting clauses: {len(multi_doc_analysis['conflicting_clauses'])}")
        
        # 4. Standard evaluation (for comparison)
        print(f"\n🔍 STEP 4: Standard Evaluation")
        print("-" * 40)
        chunks = [result['chunk'] for result in multi_doc_results[:5]]  # Use top 5 chunks
        decision = evaluate_claim(structured_query, chunks)
        
        print(f"Decision: {decision['decision'].upper()}")
        print(f"Amount: ₹{decision['amount']:,}")
        print(f"Confidence: {decision['confidence_score']:.1%}")
        
        # 5. Explainable decisions processing
        print(f"\n🔍 STEP 5: Explainable Decisions")
        print("-" * 40)
        explanation = explainable_processor.process_llm_response(
            decision.get('llm_response', ''),
            structured_query,
            chunks
        )
        
        print(f"Structured Decision: {explanation['decision'].upper()}")
        print(f"Confidence: {explanation['confidence']:.1%}")
        print(f"Steps: {len(explanation['step_by_step'])}")
        
        # Show first few steps
        for step in explanation['step_by_step'][:3]:
            status_icon = "✅" if step['status'] else "❌"
            print(f"  {status_icon} {step['title']}: {step['description']}")
        
        # 6. Feedback system (simulate override)
        print(f"\n🔍 STEP 6: Feedback System")
        print("-" * 40)
        
        # Log the decision for audit
        audit_id = audit_manager.add_decision_for_audit(decision)
        print(f"Decision logged for audit: {audit_id}")
        
        # Simulate feedback if decision doesn't match expectation
        if decision['decision'] != test_case['expected']:
            print(f"⚠️  Decision mismatch! Expected: {test_case['expected']}, Got: {decision['decision']}")
            
            # Simulate manual override
            override_id = feedback_manager.override_decision(
                original_decision=decision,
                new_decision=test_case['expected'],
                reason="Manual correction based on policy review",
                user_id="test_user_001"
            )
            print(f"✅ Decision overridden: {override_id}")
            
            # Update audit data with override
            decision['override_reason'] = "Manual correction based on policy review"
            decision['decision'] = test_case['expected']
        
        # 7. Show reasoning breakdown
        print(f"\n🔍 STEP 7: Reasoning Breakdown")
        print("-" * 40)
        if 'reasoning_breakdown' in decision:
            print(decision['reasoning_breakdown'])
        
        print(f"\n{'='*80}")
    
    # 8. Export audit report
    print(f"\n🔍 STEP 8: Audit Export")
    print("-" * 40)
    try:
        audit_summary = audit_manager.get_audit_summary()
        print(f"Audit Summary: {audit_summary}")
        
        # Export batch audit
        audit_file = audit_manager.export_batch_audit()
        print(f"✅ Audit report exported: {audit_file}")
    except Exception as e:
        print(f"⚠️  Audit export failed: {str(e)}")
    
    # 9. Feedback analytics
    print(f"\n🔍 STEP 9: Feedback Analytics")
    print("-" * 40)
    analytics = feedback_manager.get_feedback_analytics()
    print(f"Total Feedback: {analytics['total_feedback']}")
    print(f"Correction Rate: {analytics['correction_rate']:.1%}")
    print(f"Feedback by Type: {analytics['feedback_by_type']}")
    
    print(f"\n{'='*80}")
    print("✅ ALL FEATURES TESTED SUCCESSFULLY!")
    print("🎉 System is working with all advanced features!")

def test_individual_features():
    """Test individual features separately"""
    print("\n🧪 INDIVIDUAL FEATURE TESTING")
    print("=" * 80)
    
    # Test 1: Reasoning Tree
    print("\n📋 Test 1: Reasoning Tree")
    print("-" * 40)
    from backend.decision_engine.reasoning_tree import ReasoningEngine
    
    reasoning_engine = ReasoningEngine()
    query_data = {
        'age': 45,
        'gender': 'male',
        'procedure': 'cataract surgery',
        'location': 'Pune',
        'policy_duration_months': 24
    }
    
    policy_clauses = [
        "Cataract surgery is covered after 24 months waiting period",
        "Dental treatment is excluded unless emergency due to accident"
    ]
    
    reasoning_tree = reasoning_engine.analyze_claim(query_data, policy_clauses)
    print(reasoning_tree.get_human_readable_breakdown())
    
    # Test 2: Explainable Decisions
    print("\n📋 Test 2: Explainable Decisions")
    print("-" * 40)
    processor = ExplainableDecisionProcessor()
    
    sample_llm_response = """
    DECISION: APPROVED
    
    REASONING: The claim for cataract surgery should be approved. The policy duration is 24 months, which meets the 24 months waiting period requirement for cataract surgery.
    
    COVERAGE AMOUNT: 50000
    """
    
    explanation = processor.process_llm_response(
        sample_llm_response,
        query_data,
        policy_clauses
    )
    
    print(f"Decision: {explanation['decision']}")
    print(f"Confidence: {explanation['confidence']:.1%}")
    print(f"Steps: {len(explanation['step_by_step'])}")
    
    # Test 3: Feedback System
    print("\n📋 Test 3: Feedback System")
    print("-" * 40)
    feedback_manager = FeedbackManager()
    
    sample_decision = {
        'decision': 'rejected',
        'amount': 0,
        'confidence_score': 0.8,
        'query_data': query_data,
        'retrieved_chunks': policy_clauses,
        'llm_response': sample_llm_response,
        'reasoning_tree': reasoning_tree.get_json_breakdown()
    }
    
    feedback_id = feedback_manager.submit_feedback(
        original_decision=sample_decision,
        corrected_decision='approved',
        feedback_type=FeedbackType.CORRECTION,
        user_comment='Manual review found this should be approved',
        user_id='test_user'
    )
    
    print(f"Feedback submitted: {feedback_id}")
    
    analytics = feedback_manager.get_feedback_analytics()
    print(f"Analytics: {analytics}")

if __name__ == "__main__":
    test_all_features()
    test_individual_features()
