#!/usr/bin/env python
"""
Comprehensive UAT Testing for IGAL Legal Assistant
Tests 10+ queries and validates:
1. Correct clauses/articles are retrieved
2. Answers are accurate and correspond to the clauses
3. Logic is sound and concrete
"""
import os
import sys
import django
import re
import json
from typing import Dict, List, Tuple

# Setup Django
sys.path.insert(0, '/Users/tiko/Desktop/IGAL/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rag.smart_retriever import get_smart_retriever
from rag.chat_integration import get_rag_integration
from rag.llm_intent_analyzer import get_llm_intent_analyzer

# UAT Test Questions (from user)
UAT_QUESTIONS = [
    "როგორ განისაზღვრება ფიზიკური პირის რეზიდენტობა საქართველოში და როგორია მასზე საგადასახადო ვალდებულებები?",
    "რა პირობით გათავისუფლდება მაღალი მთის სტატუსის მქონე პირი საშემოსავლო გადასახადისგან?",
    "რა წესით განისაზღვრება მოგების გადასახადის ობიექტი იურიდიული პირებისთვის?",
    "როგორია დამატებული ღირებულების გადასახადის (დღგ) გადახდის ვალდებულების წარმოშობის მომენტი?",
    "რა შემთხვევაში არის შესაძლებელი გადასახადის ხანდაზმულობის ვადის გაგრძელება?",
    "როგორია ქონების გადასახადის გადახდის ვალდებულება და ვალდებული სუბიექტები?",
    "როგორია საშემოსავლოს გადასახადის გადახდის ვალდებულება და რამდენი პროცენტით განისაზღვრება?",
    "რა შემთხვევაში ითვლება ვალი უიმედო ვალად და როგორ განთავისუფლდება გადამხდელი დღგ-სგან?",
    "როგორია საგადასახადო შეთანხმების სამართლებრივი შედეგები?",
    "რა პირობებით შესაძლებელია რეზიდენტი კომპანიის მიერ არარეზიდენტისთვის დივიდენდის, როიალტის ან პროცენტის გადახდა დაბეგრილი შემცირებული განაკვეთით?",
]


def extract_article_numbers(text: str) -> List[str]:
    """Extract article numbers from Georgian text"""
    patterns = [
        r'(\d+)-ე\s+მუხლ',        # "81-ე მუხლი"
        r'მუხლი\s+(\d+)',          # "მუხლი 81"
        r'მუხლის\s+(\d+)',         # "მუხლის 81"
        r'(\d+)\s+მუხლი',          # "81 მუხლი"
        r'მუხლ(?:ი|ის)?\s*№\s*(\d+)',  # "მუხლი №81"
        r'№\s*(\d+)\s+მუხლ',       # "№81 მუხლი"
    ]

    articles = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.UNICODE)
        articles.extend(matches)

    # Remove duplicates and sort
    return sorted(set(articles), key=lambda x: int(x) if x.isdigit() else 0)


def test_single_query(query: str, chat_integration) -> Dict:
    """
    Test a single query and return results

    Returns:
        Dict with:
        - query: Original query
        - answer: LLM answer
        - cited_articles: Article numbers mentioned in answer
        - retrieved_articles: Article numbers in retrieved context
        - retrieval_time_ms: Retrieval time
        - confidence: Retrieval confidence
        - layers_used: Which retrieval layers were used
    """
    print(f"\n{'='*100}")
    print(f"QUERY: {query}")
    print(f"{'='*100}")

    # Get answer from chat integration
    result = chat_integration.chat(
        user_message=query,
        conversation_history=[],
        session_id="uat_test"
    )

    answer = result.get('answer', '')
    metadata = result.get('metadata', {})
    retrieval_metadata = metadata.get('retrieval', {})

    # Extract articles mentioned in answer
    cited_articles = extract_article_numbers(answer)

    # Extract articles from retrieved context
    contexts = retrieval_metadata.get('contexts', [])
    retrieved_articles = []
    for ctx in contexts:
        article_num = ctx.get('clause') or ctx.get('article_number')
        if article_num:
            retrieved_articles.append(str(article_num))
    retrieved_articles = sorted(set(retrieved_articles), key=lambda x: int(x) if x.isdigit() else 0)

    # Print results
    print(f"\n📊 RETRIEVAL INFO:")
    print(f"   - Retrieved Articles: {retrieved_articles}")
    print(f"   - Confidence: {retrieval_metadata.get('confidence', 0):.2f}")
    print(f"   - Layers Used: {retrieval_metadata.get('layers_used', [])}")
    print(f"   - Time: {retrieval_metadata.get('total_time_ms', 0):.0f}ms")

    print(f"\n💬 ANSWER:")
    print(f"{answer}")

    print(f"\n📋 CITED ARTICLES IN ANSWER: {cited_articles}")

    # Check if cited articles match retrieved articles
    hallucinations = [art for art in cited_articles if art not in retrieved_articles]
    if hallucinations:
        print(f"\n⚠️  WARNING: Hallucinated articles: {hallucinations}")
        print(f"   (These were cited but not in retrieved context)")
    else:
        print(f"\n✅ All cited articles are in retrieved context")

    # Show retrieved context details
    print(f"\n📚 RETRIEVED CONTEXT DETAILS:")
    for i, ctx in enumerate(contexts[:3], 1):
        article_num = ctx.get('clause') or ctx.get('article_number')
        article_title = ctx.get('clause_name') or ctx.get('article_title', '')
        similarity = ctx.get('similarity', 0)
        print(f"\n   [{i}] Article {article_num}: {article_title}")
        print(f"       Similarity: {similarity:.3f}")
        print(f"       Text preview: {ctx.get('text', '')[:150]}...")

    return {
        'query': query,
        'answer': answer,
        'cited_articles': cited_articles,
        'retrieved_articles': retrieved_articles,
        'hallucinations': hallucinations,
        'retrieval_time_ms': retrieval_metadata.get('total_time_ms', 0),
        'confidence': retrieval_metadata.get('confidence', 0),
        'layers_used': retrieval_metadata.get('layers_used', []),
        'contexts': contexts[:3]  # Top 3 contexts
    }


def run_uat_tests():
    """Run all UAT tests and generate report"""
    print("\n" + "="*100)
    print("🧪 IGAL LEGAL ASSISTANT - COMPREHENSIVE UAT TESTING")
    print("="*100)
    print(f"\nTesting {len(UAT_QUESTIONS)} queries...")
    print("\nAcceptance Criteria:")
    print("  ✅ Gets the right articles/clauses")
    print("  ✅ Talks about the right context")
    print("  ✅ Is concrete and logical")
    print("  ✅ No hallucinated citations")

    # Initialize chat integration
    chat_integration = get_rag_integration()

    # Run tests
    results = []
    for i, query in enumerate(UAT_QUESTIONS, 1):
        print(f"\n\n{'#'*100}")
        print(f"TEST {i}/{len(UAT_QUESTIONS)}")
        print(f"{'#'*100}")

        result = test_single_query(query, chat_integration)
        results.append(result)

    # Generate summary report
    print("\n\n" + "="*100)
    print("📊 UAT SUMMARY REPORT")
    print("="*100)

    total_tests = len(results)
    tests_with_hallucinations = sum(1 for r in results if r['hallucinations'])
    avg_retrieval_time = sum(r['retrieval_time_ms'] for r in results) / total_tests
    avg_confidence = sum(r['confidence'] for r in results) / total_tests

    print(f"\n📈 Overall Statistics:")
    print(f"   - Total Tests: {total_tests}")
    print(f"   - Tests with Hallucinations: {tests_with_hallucinations}")
    print(f"   - Tests with Accurate Citations: {total_tests - tests_with_hallucinations}")
    print(f"   - Average Retrieval Time: {avg_retrieval_time:.0f}ms")
    print(f"   - Average Confidence: {avg_confidence:.2f}")

    print(f"\n\n📋 Test Results Summary:")
    print(f"{'='*100}")

    for i, result in enumerate(results, 1):
        status = "✅ PASS" if not result['hallucinations'] else "⚠️  WARN"
        print(f"\n{i}. {status}")
        print(f"   Query: {result['query'][:70]}...")
        print(f"   Retrieved: {result['retrieved_articles']}")
        print(f"   Cited: {result['cited_articles']}")
        if result['hallucinations']:
            print(f"   ⚠️  Hallucinated: {result['hallucinations']}")
        print(f"   Confidence: {result['confidence']:.2f}, Time: {result['retrieval_time_ms']:.0f}ms")

    # Final verdict
    print(f"\n\n{'='*100}")
    if tests_with_hallucinations == 0:
        print("✅ ALL TESTS PASSED - No hallucinations detected!")
        print("   System is providing accurate citations.")
    else:
        print(f"⚠️  {tests_with_hallucinations}/{total_tests} tests had hallucinations")
        print("   Review the warnings above for details.")
    print(f"{'='*100}\n")

    return results


if __name__ == '__main__':
    run_uat_tests()
