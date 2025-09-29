"""ORIN AI Agent - Main agent for handling queries and tasks."""

from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory

from app.config import settings
from app.rag import document_manager, ORINRetriever
from .tools import (
    search_documents_tool,
    fetch_user_data_tool,
    search_chat_history_tool,
    create_api_response_tool
)


class ORINAgent:
    """Main ORIN AI Agent for handling office queries."""
    
    def __init__(self, user_context: Dict[str, Any] = None):
        """Initialize the ORIN agent."""
        self.user_context = user_context or {}
        self.llm = ChatOpenAI(
            temperature=0.1,
            model="gpt-3.5-turbo-16k",
            openai_api_key=settings.openai_api_key
        )
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=5  # Keep last 5 exchanges
        )
        self.tools = self._setup_tools()
        self.agent_executor = self._create_agent()
    
    def _setup_tools(self) -> List[Tool]:
        """Setup tools for the agent."""
        return [
            search_documents_tool,
            search_chat_history_tool,
            fetch_user_data_tool,
            create_api_response_tool,
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create the agent executor."""
        system_message = """You are ORIN, an AI assistant for government and private offices. Your primary goal is to help staff and citizens by providing accurate information and resolving queries efficiently.

Your capabilities include:
1. Searching through official documents and policies using RAG (Retrieval-Augmented Generation)
2. Accessing chat histories to provide consistent responses
3. Fetching personalized user data when properly authenticated
4. Providing general information and assistance

Guidelines:
- Always prioritize accuracy and official information
- For personalized requests, ensure proper authentication
- Be professional and helpful in your responses
- If unsure, clearly state limitations and suggest alternatives
- Keep responses concise but comprehensive
- Reference sources when providing official information

User Context: {user_context}
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message.format(user_context=self.user_context)),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )
    
    def query(self, user_input: str) -> Dict[str, Any]:
        """Process user query and return response."""
        try:
            # Run the agent
            result = self.agent_executor.invoke({"input": user_input})
            
            # Store chat history in vector store for future reference
            if self.user_context.get("user_id"):
                document_manager.add_chat_history(
                    user_query=user_input,
                    ai_response=result["output"],
                    user_id=self.user_context["user_id"],
                    department=self.user_context.get("department")
                )
            
            return {
                "response": result["output"],
                "success": True,
                "metadata": {
                    "user_context": self.user_context,
                    "tools_used": self._extract_tools_used(result)
                }
            }
        
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error while processing your request: {str(e)}",
                "success": False,
                "error": str(e)
            }
    
    def _extract_tools_used(self, result: Dict[str, Any]) -> List[str]:
        """Extract tools that were used in the agent execution."""
        # This would extract tool usage from the result
        # Implementation depends on how the agent executor stores this information
        return []
    
    def update_context(self, new_context: Dict[str, Any]):
        """Update user context."""
        self.user_context.update(new_context)
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()


def create_agent_for_user(user_context: Dict[str, Any]) -> ORINAgent:
    """Factory function to create an agent for a specific user."""
    return ORINAgent(user_context=user_context)