#!/usr/bin/env python3
"""
Deep Research AI System - Organized Main Entry Point

This is the main entry point for the Deep Research AI system.
The system is organized into modular components for better maintainability.

Structure:
- config/: Configuration and settings
- models/: Pydantic data models
- tools/: Function tools for agents
- agents/: AI agent definitions
- services/: Business logic and workflows
- utils/: Utility functions
"""

import asyncio
from models import UserPreference
from ai_agents import create_requirements_gathering_agent, planner_agent
from services import ResearchService
from config import DEFAULT_USER_NAME, DEFAULT_MAX_URLS

async def main():
    """Main entry point for the Deep Research AI system"""
    
    # Initialize the research service
    research_service = ResearchService()
    
    # Create user preferences
    user_preferences = UserPreference(
        name=DEFAULT_USER_NAME,
        max_urls=DEFAULT_MAX_URLS
    )
    
    # Create the requirements gathering agent
    requirements_agent = create_requirements_gathering_agent()
    
    # Gather research requirements (uncomment to enable interactive requirements gathering)
    research_requirements = await research_service.gather_requirements(requirements_agent)
    
    # For now, use the predefined research requirements
    # research_requirements = """The business idea is an agentic AI approach for NLP to data fetching. 
    # It will automate the creation of such systems based on user-provided project details. The initial focus for data sources is SQL databases. 
    # The primary value proposition is the automated system design and creation. The revenue model is subscription-based."""
    
    # Execute the research plan if requirements are available
    if research_requirements:
        print("🚀 Starting Deep Research AI System...")
        print(f"👤 User: {user_preferences.name}")
        print(f"📊 Max URLs per search: {user_preferences.max_urls}")
        print(f"🎯 Research Topic: {research_requirements[:100]}...")
        print("-" * 80)
        
        await research_service.execute_research_plan(
            planner_agent, 
            research_requirements, 
            user_preferences
        )
    else:
        print("❌ No research requirements found. Exiting.")

if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main())
