"""
Test script för Personality Assessment API
Kör detta för att testa API:et utan frontend
"""

import requests
import json
from typing import List, Dict

API_URL = "http://localhost:8000"

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_subheader(text: str):
    """Print formatted subheader"""
    print(f"\n{'-'*70}")
    print(f"  {text}")
    print(f"{'-'*70}\n")

def test_health_check():
    """Test health check endpoint"""
    print_header("🏥 Testing Health Check")

    response = requests.get(f"{API_URL}/health")

    if response.status_code == 200:
        print("✅ Health check successful!")
        print(json.dumps(response.json(), indent=2))
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_get_assessment_types():
    """Test getting available assessment types"""
    print_header("📋 Getting Available Assessment Types")

    response = requests.get(f"{API_URL}/api/v1/assessment/types")

    if response.status_code == 200:
        data = response.json()
        print("✅ Available assessment types:\n")

        for assessment in data['assessment_types']:
            print(f"ID: {assessment['id']}")
            print(f"Name: {assessment['name']}")
            print(f"Description: {assessment['description']}")
            print(f"Dimensions: {assessment['dimensions']}")
            print(f"Recommended Questions: {assessment['recommended_questions']}")
            print()

        return True
    else:
        print(f"❌ Failed to get assessment types: {response.status_code}")
        return False

def test_complete_assessment_flow():
    """Test complete assessment flow with automated answers"""
    print_header("🧠 Testing Complete Assessment Flow")

    # Step 1: Start assessment
    print_subheader("Step 1: Starting Assessment")

    start_data = {
        "user_id": "test_user_001",
        "assessment_type": "big_five",
        "language": "sv",
        "num_questions": 10  # Mindre antal för snabbare test
    }

    print(f"Request: {json.dumps(start_data, indent=2)}\n")

    response = requests.post(
        f"{API_URL}/api/v1/assessment/start",
        json=start_data
    )

    if response.status_code != 200:
        print(f"❌ Failed to start assessment: {response.status_code}")
        print(response.text)
        return False

    assessment_data = response.json()
    assessment_id = assessment_data['assessment_id']
    questions = assessment_data['questions']

    print(f"✅ Assessment started!")
    print(f"Assessment ID: {assessment_id}")
    print(f"Total Questions: {assessment_data['total_questions']}\n")

    # Step 2: Display questions and simulate answers
    print_subheader("Step 2: Answering Questions")

    answers = []

    for i, question in enumerate(questions, 1):
        print(f"\nFråga {i}/{len(questions)}")
        print(f"Dimension: {question['dimension']}")
        print(f"Text: {question['question_text']}")

        if question['scale_type'] == 'likert':
            print("\nAlternativ:")
            for j, option in enumerate(question['options'], 1):
                print(f"  {j}. {option}")

            # Simulera svar (variera mellan 2-5 för realistiska resultat)
            simulated_answer = (i % 4) + 2  # Ger 2,3,4,5,2,3,4,5...
            print(f"\n🤖 Simulerat svar: {simulated_answer}")

            answers.append({
                "assessment_id": assessment_id,
                "question_id": question['question_id'],
                "answer": simulated_answer
            })

    print(f"\n✅ Alla {len(answers)} frågor besvarade!")

    # Step 3: Submit answers
    print_subheader("Step 3: Submitting Answers")

    submit_data = {
        "assessment_id": assessment_id,
        "answers": answers
    }

    print("Skickar in svar för analys...")
    print("(Detta kan ta 10-30 sekunder beroende på AI-analys)\n")

    response = requests.post(
        f"{API_URL}/api/v1/assessment/submit",
        json=submit_data
    )

    if response.status_code != 200:
        print(f"❌ Failed to submit assessment: {response.status_code}")
        print(response.text)
        return False

    result = response.json()

    # Step 4: Display results
    print_header("📊 ASSESSMENT RESULTS")

    print(f"Assessment ID: {result['assessment_id']}")
    print(f"User ID: {result['user_id']}")
    print(f"Type: {result['assessment_type']}\n")

    print_subheader("Sammanfattning")
    print(result['summary'])

    print_subheader("Personlighetspoäng")
    for score in result['scores']:
        print(f"\n{score['dimension']}")
        print(f"  Poäng: {score['score']:.1f}/100", end="")
        if score.get('percentile'):
            print(f" (Percentil: {score['percentile']})")
        else:
            print()
        print(f"  Tolkning: {score['interpretation']}")

    print_subheader("Styrkor")
    for i, strength in enumerate(result['strengths'], 1):
        print(f"{i}. {strength}")

    print_subheader("Utvecklingsområden")
    for i, area in enumerate(result['development_areas'], 1):
        print(f"{i}. {area}")

    print_subheader("Rekommendationer")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"{i}. {rec}")

    # Step 5: Test retrieving result
    print_subheader("Step 5: Testing Result Retrieval")

    response = requests.get(f"{API_URL}/api/v1/assessment/result/{assessment_id}")

    if response.status_code == 200:
        print(f"✅ Successfully retrieved result for assessment {assessment_id}")
    else:
        print(f"❌ Failed to retrieve result: {response.status_code}")
        return False

    print_header("✅ ALL TESTS PASSED!")
    return True

def run_interactive_assessment():
    """Run interactive assessment with user input"""
    print_header("🎯 Interactive Assessment Mode")

    # Choose assessment type
    print("Välj assessment typ:")
    print("1. Big Five (OCEAN)")
    print("2. DISC")
    print("3. Jung/MBTI")
    print("4. Comprehensive")

    choice = input("\nDitt val (1-4): ").strip()

    type_map = {
        "1": "big_five",
        "2": "disc",
        "3": "jung_mbti",
        "4": "comprehensive"
    }

    assessment_type = type_map.get(choice, "big_five")

    # Get number of questions
    num_questions = input("Antal frågor (10-100, default 20): ").strip()
    num_questions = int(num_questions) if num_questions else 20

    # Start assessment
    print("\n🚀 Startar assessment...")

    start_data = {
        "user_id": f"user_{hash(str(input('Ditt namn: ')))}",
        "assessment_type": assessment_type,
        "language": "sv",
        "num_questions": num_questions
    }

    response = requests.post(f"{API_URL}/api/v1/assessment/start", json=start_data)

    if response.status_code != 200:
        print(f"❌ Kunde inte starta assessment: {response.status_code}")
        return

    assessment_data = response.json()
    assessment_id = assessment_data['assessment_id']
    questions = assessment_data['questions']

    print(f"\n✅ Assessment startad! ID: {assessment_id}\n")

    # Answer questions
    answers = []

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*70}")
        print(f"Fråga {i}/{len(questions)}")
        print(f"{'='*70}")
        print(f"\n{question['question_text']}\n")

        if question['scale_type'] == 'likert' and question.get('options'):
            for j, option in enumerate(question['options'], 1):
                print(f"  {j}. {option}")

            while True:
                try:
                    answer = int(input(f"\nDitt svar (1-{len(question['options'])}): "))
                    if 1 <= answer <= len(question['options']):
                        break
                    print("Ogiltigt val, försök igen.")
                except ValueError:
                    print("Ange ett nummer.")

            answers.append({
                "assessment_id": assessment_id,
                "question_id": question['question_id'],
                "answer": answer
            })

    # Submit
    print("\n\n🔄 Analyserar dina svar...")
    print("(Detta kan ta 10-30 sekunder)\n")

    response = requests.post(
        f"{API_URL}/api/v1/assessment/submit",
        json={"assessment_id": assessment_id, "answers": answers}
    )

    if response.status_code != 200:
        print(f"❌ Kunde inte skicka in svar: {response.status_code}")
        return

    result = response.json()

    # Display results (same as automated test)
    print_header("📊 DINA RESULTAT")

    print_subheader("Sammanfattning")
    print(result['summary'])

    print_subheader("Personlighetspoäng")
    for score in result['scores']:
        print(f"\n{score['dimension']}")
        print(f"  Poäng: {score['score']:.1f}/100")
        print(f"  {score['interpretation']}")

    print_subheader("Dina Styrkor")
    for i, strength in enumerate(result['strengths'], 1):
        print(f"{i}. {strength}")

    print_subheader("Utvecklingsområden")
    for i, area in enumerate(result['development_areas'], 1):
        print(f"{i}. {area}")

    print_subheader("Rekommendationer")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"{i}. {rec}")

    print_header("✅ Tack för att du genomförde testet!")

def main():
    """Main test function"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║         🧠 Personality Assessment API - Test Suite             ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    print("\nVälj test mode:")
    print("1. Automated Tests (snabbt, simulerade svar)")
    print("2. Interactive Assessment (du svarar själv)")
    print("3. Quick Tests (health + types)")

    choice = input("\nDitt val (1-3): ").strip()

    try:
        if choice == "1":
            # Run automated tests
            if not test_health_check():
                return

            if not test_get_assessment_types():
                return

            test_complete_assessment_flow()

        elif choice == "2":
            # Run interactive assessment
            run_interactive_assessment()

        elif choice == "3":
            # Quick tests
            test_health_check()
            test_get_assessment_types()

        else:
            print("Ogiltigt val")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Kunde inte ansluta till API:et")
        print("Kontrollera att servern körs på http://localhost:8000")
        print("\nStarta servern med: python api_main.py")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
