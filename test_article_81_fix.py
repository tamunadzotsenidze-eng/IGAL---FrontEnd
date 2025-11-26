#!/usr/bin/env python
"""
Test script to verify Article 81 retrieval fix
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/tiko/Desktop/IGAL/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rag.smart_retriever import get_smart_retriever
from rag.llm_intent_analyzer import get_llm_intent_analyzer

def test_article_81_retrieval():
    """Test that Article 81 is correctly retrieved"""
    print("\n" + "=" * 80)
    print("🧪 TESTING ARTICLE 81 RETRIEVAL FIX")
    print("=" * 80)

    # Test query
    query = "როგორია საშემოსავლოს გადასახადის გადახდის ვალდებულება და რამდენი პროცენტით განისაზღვრება?"
    print(f"\nQuery: {query}")
    print()

    # Step 1: Test LLM Intent Detection
    print("STEP 1: Testing LLM Intent Detection")
    print("-" * 80)
    llm_intent_analyzer = get_llm_intent_analyzer()
    llm_intent = llm_intent_analyzer.analyze(query)

    if llm_intent:
        print(f"✅ LLM Intent Detected:")
        print(f"   - Query Type: {llm_intent.query_type}")
        print(f"   - Confidence: {llm_intent.confidence:.2f}")
        print(f"   - Likely Clauses: {llm_intent.likely_clauses}")
        print(f"   - Reasoning: {llm_intent.reasoning}")

        intent_filters = llm_intent_analyzer.convert_to_intent_filters(llm_intent)
        print(f"\n   Intent Filters Created:")
        print(f"   - Target Articles: {intent_filters.get('target_articles')}")
        print(f"   - Document Code: {intent_filters.get('document_code')}")
    else:
        print("❌ LLM Intent NOT detected")
        intent_filters = None

    # Step 2: Test Smart Retriever with Intent Filters
    print("\n\nSTEP 2: Testing Smart Retriever with Intent Filters")
    print("-" * 80)

    smart_retriever = get_smart_retriever()
    result = smart_retriever.retrieve_context(
        question=query,
        conversation_history=None,
        use_openai_fallback=False,
        top_k=5,
        intent_filters=intent_filters
    )

    print(f"\n📊 Retrieval Results:")
    print(f"   - Contexts Retrieved: {len(result.get('contexts', []))}")
    print(f"   - Confidence: {result.get('confidence', 0):.2f}")
    print(f"   - Layers Used: {result.get('layers_used', [])}")
    print(f"   - Time: {result.get('total_time_ms', 0):.0f}ms")

    # Step 3: Check if Article 81 is in results
    print("\n\nSTEP 3: Checking if Article 81 is in Results")
    print("-" * 80)

    found_article_81 = False
    for i, ctx in enumerate(result.get('contexts', []), 1):
        article_num = ctx.get('article_number') or ctx.get('clause')
        article_title = ctx.get('article_title') or ctx.get('clause_name', '')

        print(f"\n[{i}] Article {article_num}: {article_title[:50]}...")
        print(f"    Document: {ctx.get('document_title', '')[:60]}")
        print(f"    Similarity: {ctx.get('similarity', 0):.3f}")
        print(f"    Source: {ctx.get('source', '')}, Layer: {ctx.get('layer', '')}")

        if str(article_num) == '81':
            found_article_81 = True
            print(f"    ✅ FOUND ARTICLE 81!")
            print(f"    Text preview: {ctx.get('text', '')[:200]}...")

    # Final result
    print("\n" + "=" * 80)
    if found_article_81:
        print("✅ SUCCESS: Article 81 correctly retrieved!")
        print("The fix works - LLM intent is now passed to smart_retriever")
    else:
        print("❌ FAILED: Article 81 NOT found in results")
        print("Articles found instead:")
        for ctx in result.get('contexts', []):
            print(f"   - Article {ctx.get('article_number')}: {ctx.get('article_title', '')[:40]}")
    print("=" * 80)
    print()

if __name__ == '__main__':
    test_article_81_retrieval()
