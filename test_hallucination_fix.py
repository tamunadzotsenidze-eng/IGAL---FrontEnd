#!/usr/bin/env python3
"""Test if English prompt fixes hallucinations"""
import requests
import json

API_URL = "http://localhost:8000/api/widget/"

# Test queries that previously hallucinated
TESTS = [
    {
        "query": "რა განაკვეთით იბეგრება საშემოსავლო გადასახადი?",
        "expected": "Should cite only retrieved articles",
        "previous_issue": "None - worked before"
    },
    {
        "query": "როგორია დღგ-ის გადახდის ვალდებულების წარმოშობის მომენტი?",
        "expected": "Should NOT cite 166 if not retrieved",
        "previous_issue": "Cited 166, but retrieved 4"
    },
    {
        "query": "როგორია საშემოსავლოს გადასახადის გადახდის ვალდებულება?",
        "expected": "Should NOT cite 81 if not retrieved",
        "previous_issue": "Cited 81, but didn't retrieve it"
    }
]

print("=" * 100)
print("🧪 TESTING HALLUCINATION FIX (English Prompt)")
print("=" * 100)
print()

for i, test in enumerate(TESTS, 1):
    print(f"TEST {i}/{len(TESTS)}")
    print(f"Query: {test['query']}")
    print(f"Previous issue: {test['previous_issue']}")
    print()
    
    response = requests.post(API_URL, json={
        "message": test['query'],
        "session_id": f"hallucination_test_{i}"
    }, timeout=30)
    
    result = response.json()
    answer = result.get('response', '')
    citations = result.get('citations', [])
    
    # Extract cited articles from answer
    import re
    cited_in_answer = set(re.findall(r'(\d+)-ე მუხლ', answer))
    retrieved_articles = set(str(c.get('article_number')) for c in citations if c.get('article_number'))
    
    # Check for hallucinations
    hallucinated = cited_in_answer - retrieved_articles
    
    if hallucinated:
        status = f"❌ HALLUCINATION: Cited {hallucinated} but not retrieved"
    elif cited_in_answer and cited_in_answer.issubset(retrieved_articles):
        status = f"✅ GOOD: All cited articles {cited_in_answer} were retrieved"
    else:
        status = "⚠️  NO CITATIONS in answer"
    
    print(f"Status: {status}")
    print(f"Answer preview: {answer[:200]}...")
    print()
    print("-" * 100)
    print()

print("=" * 100)
print("✅ TESTS COMPLETE")
print("=" * 100)
