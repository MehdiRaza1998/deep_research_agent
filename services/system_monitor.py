from agents.lifecycle import RunHooks

class SystemMonitor(RunHooks):
    """System monitor for tracking agent activities and performance"""
    
    def __init__(self):
        self.active_agents = []
        self.tool_usage = {}
        self.handoffs = 0
    
    async def on_agent_start(self, context, agent):
        """Called when an agent starts working"""
        self.active_agents.append(agent.name)
        print(f"🌅 SYSTEM: {agent.name} is now working")
        print(f"   Active agents so far: {self.active_agents}")
    
    async def on_llm_start(self, context, agent, system_prompt, input_items):
        """Called when an agent starts thinking"""
        print(f"📞 SYSTEM: {agent.name} is thinking...")
    
    async def on_llm_end(self, context, agent, response):
        """Called when an agent finishes thinking"""
        print(f"🧠✨ SYSTEM: {agent.name} finished thinking")
    
    async def on_tool_start(self, context, agent, tool):
        """Called when a tool starts being used"""
        tool_name = tool.name
        if tool_name not in self.tool_usage:
            self.tool_usage[tool_name] = 0
        self.tool_usage[tool_name] += 1
        print(f"🔨 SYSTEM: {tool_name} used {self.tool_usage[tool_name]} times")
    
    async def on_tool_end(self, context, agent, tool, result):
        """Called when a tool finishes being used"""
        print(f"✅🔨 SYSTEM: {agent.name} finished using {tool.name}")
    
    async def on_handoff(self, context, from_agent, to_agent):
        """Called when there's a handoff between agents"""
        self.handoffs += 1
        print(f"🏃‍♂️➡️🏃‍♀️ HANDOFF #{self.handoffs}: {from_agent.name} → {to_agent.name}")
    
    async def on_agent_end(self, context, agent, output):
        """Called when an agent completes their work"""
        print(f"✅ SYSTEM: {agent.name} completed their work")
        print(f"📊 STATS: {len(self.active_agents)} agents used, {self.handoffs} handoffs")
