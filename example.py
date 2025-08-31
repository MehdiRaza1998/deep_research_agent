#!/usr/bin/env python3
"""
Example demonstrating the Deep Research Agentic AI system.

This shows the new workflow:
1. User gives idea to Requirements Gathering Agent (with SQLite session)
2. Requirements Gathering Agent asks up to 3 questions
3. Requirements confirmed → Planner Agent creates research plan
4. Planner hands off to Lead Orchestrator Agent
5. Lead Orchestrator uses other agents as tools (Search, Analysis, Reports)
6. Final research report returned
"""

import asyncio
import os
from dotenv import load_dotenv
from src.deep_research_orchestrator import DeepResearchOrchestrator


async def main():
    """Example usage of the Deep Research system."""
    
    # Load environment variables
    load_dotenv()
    
    # Check for API keys
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Please set GEMINI_API_KEY in your .env file")
        return
    
    if not os.getenv("TAVILY_API_KEY"):
        print("❌ Please set TAVILY_API_KEY in your .env file")
        return
    
    # Initialize the orchestrator
    print("🔧 Initializing Deep Research System...")
    orchestrator = DeepResearchOrchestrator()
    
    # Example business idea
    business_idea = "An AI-powered personal fitness coach app that creates personalized workout plans"
    
    print(f"\n💡 Researching: {business_idea}")
    print("-" * 60)
    
    try:
        # Step 1: Start requirements gathering
        print("🔍 Step 1: Requirements Gathering")
        initial_response = orchestrator.start_requirements_gathering(business_idea)
        
        # Step 2: Interactive requirements gathering (simulated)
        print("\n🤔 Step 2: Interactive Questions")
        question_count = 0
        max_questions = 3
        
        # Simulate user responses for demo
        demo_responses = [
            "Our target market is fitness enthusiasts aged 25-45 who want personalized workout plans",
            "We plan to monetize through subscription model and premium features",
            "Our main competitive advantage is AI personalization and real-time feedback"
        ]
        
        while question_count < max_questions:
            if initial_response.get("requirements_confirmed", False):
                break
                
            print(f"\nQuestion {question_count + 1}:")
            print(initial_response["conversation_history"][-1])
            
            # Use demo response
            user_response = demo_responses[question_count] if question_count < len(demo_responses) else "No additional details"
            print(f"Demo Response: {user_response}")
            
            # Ask follow-up question
            follow_up = orchestrator.ask_follow_up_question(user_response)
            question_count += 1
            
            if follow_up.get("requirements_confirmed", False):
                break
        
        # Step 3: Complete requirements gathering
        print("\n✅ Step 3: Completing Requirements")
        requirements = orchestrator.complete_requirements_gathering()
        
        # Step 4: Conduct research
        print("\n🔍 Step 4: Conducting Research")
        report = await orchestrator.conduct_research(requirements)
        
        print("\n📊 RESEARCH COMPLETED")
        print("=" * 60)
        print(report)
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
