"""ORIN AI Agent - Main agent for handling queries and tasks."""

from typing import Dict, Any, List, Optional
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory

from app.config import settings
from app.rag import document_manager, ORINRetriever
from .tools import (
    search_documents_tool,
    fetch_user_data_tool,
    search_chat_history_tool,
    create_api_response_tool,
    get_and_clear_rag_sources,
    reset_rag_sources
)


class ORINAgent:
    """Main ORIN AI Agent for handling office queries."""
    
    def __init__(self, user_context: Dict[str, Any] = None):
        """Initialize the ORIN agent."""
        self.user_context = user_context or {}
        model_name = settings.openai_model or "gpt-4o-mini"
        self.llm = ChatOpenAI(
            temperature=0.1,
            model=model_name,
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
        # Convert user context to a safe string representation
        user_context_str = str(self.user_context).replace('{', '{{').replace('}', '}}')
        
        system_message = f"""You are ORIN, an AI assistant for government and private offices. Your primary goal is to help staff and citizens by providing accurate information and resolving queries efficiently.

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
- When you use the search_documents tool, DO NOT mention sources or citations in your main response text - the system will automatically extract and display sources separately
- Focus on providing clear, direct answers based on the retrieved information

User Context: {user_context_str}
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
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
            # Clear any previous RAG source tracking before processing
            reset_rag_sources()

            # Run the agent
            result = self.agent_executor.invoke({"input": user_input})
            
            # Extract and format sources from the agent's response
            response_text = result["output"]
            print(f"DEBUG: Agent response text: {response_text}")  # Debug log

            rag_sources = get_and_clear_rag_sources()
            print(f"DEBUG: RAG sources collected: {rag_sources}")
            sources = self._format_sources(rag_sources, response_text)
            print(f"DEBUG: Formatted sources returned: {sources}")
            clean_response = self._clean_response(response_text)
            
            print(f"DEBUG: Extracted sources: {sources}")  # Debug log
            print(f"DEBUG: Clean response: {clean_response}")  # Debug log
            
            # Store chat history in vector store for future reference (optional)
            if self.user_context.get("user_id"):
                try:
                    document_manager.add_chat_history(
                        user_query=user_input,
                        ai_response=clean_response,
                        user_id=self.user_context["user_id"],
                        department=self.user_context.get("department")
                    )
                except Exception as e:
                    # If vector store is not available, continue without storing chat history
                    print(f"Warning: Could not store chat history: {e}")
            
            return {
                "response": clean_response,
                "sources": sources,
                "success": True,
                "metadata": {
                    "user_context": self.user_context,
                    "tools_used": self._extract_tools_used(result)
                }
            }
        
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error while processing your request: {str(e)}",
                "sources": [],
                "success": False,
                "error": str(e)
            }
    
    def _extract_tools_used(self, result: Dict[str, Any]) -> List[str]:
        """Extract tools that were used in the agent execution."""
        steps = result.get("intermediate_steps", [])
        tools = []
        for step in steps:
            try:
                action = step[0]
                if hasattr(action, "tool"):
                    tools.append(action.tool)
            except Exception:
                continue
        return tools

    def _format_sources(self, rag_sources: List[Dict[str, Any]], response_text: str) -> List[Dict[str, Any]]:
        """Create a clean list of unique sources for the UI."""
        formatted: List[Dict[str, Any]] = []
        seen = set()

        # Prefer metadata captured during tool execution
        for source in rag_sources:
            filename = source.get("filename") or source.get("source") or "Unknown source"
            doc_type = source.get("document_type")
            department = source.get("department")
            source_path = source.get("source")

            key = (filename, doc_type, department, source_path)
            if key in seen or filename == "Unknown source":
                continue
            seen.add(key)
            formatted.append({
                "filename": filename,
                "document_type": doc_type,
                "department": department,
                "source": source_path
            })

        if formatted:
            return formatted

        # Fallback to parsing legacy response format
        legacy_sources = self._extract_sources(response_text)
        for entry in legacy_sources:
            key = (entry, None, None, None)
            if key in seen:
                continue
            seen.add(key)
            formatted.append({
                "filename": entry,
                "document_type": None,
                "department": None,
                "source": None
            })
        return formatted
    
    def _extract_sources(self, response_text: str) -> List[str]:
        """Extract source information from the response text."""
        sources = []
        if "--- SOURCES ---" in response_text:
            # Extract sources section
            sources_section = response_text.split("--- SOURCES ---")[1].strip()
            lines = sources_section.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('•'):
                    source = line[1:].strip()  # Remove bullet point
                    if source:  # Only add non-empty sources
                        sources.append(source)
                elif line and not line.startswith('•') and sources:
                    # This might be a continuation of the last source
                    # But let's not include it to avoid confusion
                    break
        print(f"DEBUG: Sources extracted from text: {sources}")  # Debug log
        print(f"DEBUG: Original response text contains sources: {'--- SOURCES ---' in response_text}")  # Debug log
        return sources
    
    def _clean_response(self, response_text: str) -> str:
        """Remove source citations from the main response text."""
        if "--- SOURCES ---" in response_text:
            return response_text.split("--- SOURCES ---")[0].strip()
        return response_text.strip()
    
    def update_context(self, new_context: Dict[str, Any]):
        """Update user context."""
        self.user_context.update(new_context)
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()


def create_agent_for_user(user_context: Dict[str, Any]) -> ORINAgent:
    """Factory function to create an agent for a specific user."""
    return ORINAgent(user_context=user_context)