#!/bin/bash
# Test Georgian tax questions against production API

API_URL="https://igal-backend-qnv4kru4hq-ey.a.run.app/api/widget/"

echo "🧪 Testing IGAL RAG System with Georgian Tax Questions"
echo "======================================================="
echo ""

# Array of questions
declare -a questions=(
    "როგორ განისაზღვრება ფიზიკური პირის რეზიდენტობა საქართველოში"
    "მაღალი მთის სტატუსის გადასახადი"
    "მოგების გადასახადის ობიექტი იურიდიული პირებისთვის"
    "დღგ გადახდის ვალდებულება"
    "გადასახადის ხანდაზმულობა"
    "ქონების გადასახადი"
    "საშემოსავლო გადასახადი პროცენტი"
    "უიმედო ვალი დღგ"
    "საგადასახადო შეთანხმება"
    "დივიდენდი არარეზიდენტი შემცირებული განაკვეთი"
)

counter=1
for question in "${questions[@]}"; do
    echo "[$counter/10] Testing: $question"
    echo "---"

    # Send request to API
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"message\":\"$question\",\"session_id\":\"test_rag_$counter\"}")

    # Check if response contains answer
    if echo "$response" | grep -q '"response"'; then
        answer=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('response', '')[:200])" 2>/dev/null)

        if [ ! -z "$answer" ]; then
            echo "✅ Answer received:"
            echo "$answer..."
            echo ""
        else
            echo "❌ Empty response"
            echo ""
        fi
    else
        echo "❌ Error: $response"
        echo ""
    fi

    ((counter++))
    sleep 2  # Rate limiting
done

echo "======================================================="
echo "✅ Testing complete!"
