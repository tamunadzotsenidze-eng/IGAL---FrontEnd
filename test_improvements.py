#!/usr/bin/env python3
"""
Test the improvements to Intent Analyzer and conversational prompt
"""
import requests
import json

API_URL = "http://localhost:8000/api/widget/"

# Test queries that previously failed (returned "no info found")
TEST_QUERIES = [
    {
        "query": "რა განაკვეთით იბეგრება საშემოსავლო გადასახადი?",
        "expected_clause": "81",
        "previous_result": "SUCCESS - this one worked before"
    },
    {
        "query": "როგორია დღგ-ის განაკვეთი?",
        "expected_clause": "164",
        "previous_result": "FAIL - said 'no info found'"
    },
    {
        "query": "როგორია ქონების გადასახადის გადახდის ვალდებულება?",
        "expected_clause": "202 or 203",
        "previous_result": "SUCCESS - this one worked"
    }
]

print("=" * 100)
print("🧪 TESTING IMPROVEMENTS")
print("=" * 100)
print()

for i, test in enumerate(TEST_QUERIES, 1):
    print(f"TEST {i}/{ len(TEST_QUERIES)}")
    print(f"Query: {test['query']}")
    print(f"Expected clause: {test['expected_clause']}")
    print(f"Previous: {test['previous_result']}")
    print()
    
    # Send request
    response = requests.post(API_URL, json={
        "message": test['query'],
        "session_id": f"test_improvements_{i}"
    })
    
    result = response.json()
    answer = result.get('response', '')
    citations = result.get('citations', [])
    
    # Check result
    cited_clauses = [c.get('article_number') for c in citations if c.get('article_number')]
    
    if "სამწუხაროდ" in answer or "არ არის" in answer:
        status = "❌ FAIL (no info found)"
    elif cited_clauses:
        status = f"✅ SUCCESS (clauses: {', '.join(cited_clauses)})"
    else:
        status = "⚠️  PARTIAL (answered but no citations)"
    
    print(f"Result: {status}")
    print(f"Answer: {answer[:150]}...")
    print()
    print("-" * 100)
    print()

print("=" * 100)
print("✅ TESTS COMPLETE")
print("=" * 100)
