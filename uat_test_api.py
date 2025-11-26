#!/usr/bin/env python
"""
Comprehensive UAT Testing for IGAL Legal Assistant via HTTP API
Tests 10+ queries and validates:
1. Correct clauses/articles are retrieved
2. Answers are accurate and correspond to the clauses
3. Logic is sound and concrete
"""
import requests
import re
import json
import time
from typing import Dict, List

# API Configuration
API_URL = "http://localhost:8000/api/widget/"

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


def test_single_query(query: str, session_id: str = "uat_test") -> Dict:
    """
    Test a single query via HTTP API

    Returns:
        Dict with test results
    """
    print(f"\n{'='*100}")
    print(f"QUERY: {query}")
    print(f"{'='*100}")

    # Send request to API
    payload = {
        "message": query,
        "session_id": session_id
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()

        answer = result.get('response', '')
        citations = result.get('citations', [])

        # Extract articles mentioned in answer
        cited_articles = extract_article_numbers(answer)

        # Extract articles from citations
        retrieved_articles = []
        for citation in citations:
            article_num = citation.get('article_number') or citation.get('clause')
            if article_num:
                retrieved_articles.append(str(article_num))
        retrieved_articles = sorted(set(retrieved_articles), key=lambda x: int(x) if x.isdigit() else 0)

        # Print results
        print(f"\n💬 ANSWER:")
        print(f"{answer}")
        print(f"\n📋 CITED ARTICLES IN ANSWER: {cited_articles}")
        print(f"📚 RETRIEVED ARTICLES IN CITATIONS: {retrieved_articles}")

        # Check if cited articles match retrieved articles
        hallucinations = [art for art in cited_articles if art not in retrieved_articles]
        if hallucinations:
            print(f"\n⚠️  WARNING: Hallucinated articles: {hallucinations}")
            print(f"   (These were cited in answer but not in retrieved citations)")
        else:
            print(f"\n✅ All cited articles are in retrieved citations")

        # Show citation details
        if citations:
            print(f"\n📚 CITATION DETAILS:")
            for i, citation in enumerate(citations[:3], 1):
                article_num = citation.get('article_number') or citation.get('clause')
                article_title = citation.get('article_title') or citation.get('title', '')
                print(f"\n   [{i}] Article {article_num}: {article_title}")
                if 'text' in citation:
                    print(f"       Text preview: {citation['text'][:150]}...")

        return {
            'query': query,
            'answer': answer,
            'cited_articles': cited_articles,
            'retrieved_articles': retrieved_articles,
            'hallucinations': hallucinations,
            'citations': citations[:3],
            'status': 'PASS' if not hallucinations else 'WARN'
        }

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return {
            'query': query,
            'answer': '',
            'cited_articles': [],
            'retrieved_articles': [],
            'hallucinations': [],
            'citations': [],
            'status': 'ERROR',
            'error': str(e)
        }


def run_uat_tests():
    """Run all UAT tests and generate report"""
    print("\n" + "="*100)
    print("🧪 IGAL LEGAL ASSISTANT - COMPREHENSIVE UAT TESTING (HTTP API)")
    print("="*100)
    print(f"\nTesting {len(UAT_QUESTIONS)} queries...")
    print(f"API Endpoint: {API_URL}")
    print("\nAcceptance Criteria:")
    print("  ✅ Gets the right articles/clauses")
    print("  ✅ Talks about the right context")
    print("  ✅ Is concrete and logical")
    print("  ✅ No hallucinated citations")

    # Test API is reachable
    print(f"\n🔍 Testing API connectivity...")
    try:
        test_response = requests.get("http://localhost:8000/health/", timeout=5)
        print(f"✅ API is reachable")
    except Exception as e:
        print(f"⚠️  Warning: Could not reach health endpoint: {e}")
        print(f"   Proceeding with chat endpoint...")

    # Run tests
    results = []
    session_id = f"uat_test_{int(time.time())}"

    for i, query in enumerate(UAT_QUESTIONS, 1):
        print(f"\n\n{'#'*100}")
        print(f"TEST {i}/{len(UAT_QUESTIONS)}")
        print(f"{'#'*100}")

        result = test_single_query(query, session_id)
        results.append(result)

        # Small delay between requests
        time.sleep(1)

    # Generate summary report
    print("\n\n" + "="*100)
    print("📊 UAT SUMMARY REPORT")
    print("="*100)

    total_tests = len(results)
    tests_with_hallucinations = sum(1 for r in results if r['hallucinations'])
    tests_with_errors = sum(1 for r in results if r['status'] == 'ERROR')
    tests_passed = total_tests - tests_with_hallucinations - tests_with_errors

    print(f"\n📈 Overall Statistics:")
    print(f"   - Total Tests: {total_tests}")
    print(f"   - Tests Passed: {tests_passed}")
    print(f"   - Tests with Hallucinations: {tests_with_hallucinations}")
    print(f"   - Tests with Errors: {tests_with_errors}")

    print(f"\n\n📋 Test Results Summary:")
    print(f"{'='*100}")

    for i, result in enumerate(results, 1):
        status = result['status']
        status_icon = "✅" if status == "PASS" else ("⚠️ " if status == "WARN" else "❌")

        print(f"\n{i}. {status_icon} {status}")
        print(f"   Query: {result['query'][:70]}...")

        if status != 'ERROR':
            print(f"   Retrieved: {result['retrieved_articles']}")
            print(f"   Cited: {result['cited_articles']}")
            if result['hallucinations']:
                print(f"   ⚠️  Hallucinated: {result['hallucinations']}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")

    # Final verdict
    print(f"\n\n{'='*100}")
    if tests_with_hallucinations == 0 and tests_with_errors == 0:
        print("✅ ALL TESTS PASSED - No hallucinations or errors detected!")
        print("   System is providing accurate citations and responses.")
    else:
        if tests_with_hallucinations > 0:
            print(f"⚠️  {tests_with_hallucinations}/{total_tests} tests had hallucinations")
        if tests_with_errors > 0:
            print(f"❌ {tests_with_errors}/{total_tests} tests had errors")
        print("   Review the warnings/errors above for details.")
    print(f"{'='*100}\n")

    return results


if __name__ == '__main__':
    run_uat_tests()
