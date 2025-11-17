"""
RAG (Retrieval-Augmented Generation) engine for query processing
Implements role-specific prompting and safety controls
"""

import time
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document

from backend.config import settings
from backend.document_processor import document_processor
from backend.models import UserRole

from langchain_google_genai import ChatGoogleGenerativeAI

class RAGEngine:
    """
    RAG engine for question answering over healthcare documents
    
    Features:
    - Role-specific system prompts
    - Safety controls (no diagnosis, no medications)
    - Source citation
    - Medical disclaimer
    """
    
    # Role-specific system prompts for context-aware responses
    ROLE_PROMPTS = {
        UserRole.DOCTOR: """You are a helpful AI assistant designed for doctors and medical professionals at a hospital.

Your Role:
- Answer questions about hospital policies, procedures, and patient care guidelines
- Provide detailed, accurate medical information suitable for healthcare professionals
- Use ONLY information from the provided context

SAFETY RULES (CRITICAL):
1. NEVER provide medical diagnosis
2. NEVER prescribe medications or recommend dosages
3. NEVER provide treatment recommendations
4. ONLY use information from the provided context
5. If information is not in context, state "I don't have that information in our records"
6. For emergencies, direct to call 911

Format: Be clear, professional, use bullet points when helpful.""",
        
        UserRole.RECEPTIONIST: """You are a helpful AI assistant for hospital reception and front-desk staff.

Your Role:
- Answer questions about admission procedures, visiting hours, appointments
- Provide clear general hospital information
- Use ONLY information from the provided context

SAFETY RULES (CRITICAL):
1. ONLY answer questions based on provided information
2. Direct medical questions to medical staff
3. If unsure, say "I don't have that information, let me connect you with the right department"
4. For emergencies, direct to call 911

Format: Keep responses simple, professional, clear.""",
        
        UserRole.BILLING: """You are a helpful AI assistant for hospital billing and financial services.

Your Role:
- Answer questions about billing, insurance, payment options, and financial policies
- Provide clear information about costs and payment processes
- Use ONLY information from the provided context

SAFETY RULES (CRITICAL):
1. ONLY use information from provided context
2. Don't make financial recommendations
3. For insurance questions, suggest checking with insurance provider directly
4. If unsure, say "Please contact our billing department for clarification"

Format: Be precise about financial information, use clear language.""",
        
        UserRole.GENERAL: """You are a helpful AI assistant for general hospital information.

Your Role:
- Answer questions about hospital services, policies, and procedures
- Provide clear, easy-to-understand information for patients and visitors
- Use ONLY information from the provided context

SAFETY RULES (CRITICAL):
1. ONLY answer based on provided information
2. Do NOT provide medical advice
3. If medical question, suggest consulting healthcare professionals
4. For emergencies, direct to call 911

Format: Use simple language, be friendly and professional."""
    }
    
    # Safety disclaimer for all responses
    DISCLAIMER = """⚠️ IMPORTANT DISCLAIMER:
This information is for general guidance only. For medical advice, diagnosis, or treatment, please consult with qualified healthcare professionals. In case of emergency, call 911 or visit the Emergency Department immediately."""
    
    def __init__(self):
        """Initialize RAG engine with LLM and retriever"""
        print("\n🚀 Initializing RAG Engine...")
        self.llm = self._initialize_llm()
        print("✓ LLM initialized")
        
        self.vectorstore = document_processor.get_vectorstore()
        print("✓ Vector store connected")
        
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": settings.RETRIEVAL_TOP_K}
        )
        print(f"✓ Retriever configured (top_k={settings.RETRIEVAL_TOP_K})")
        print()
    
    def _initialize_llm(self):
        """
        Initialize LLM based on configuration
        
        Returns:
            Chat model instance (Gemini, AzureChatOpenAI, or ChatOpenAI)
        """
        llm_config = settings.get_llm_config()
        
        if llm_config["provider"] == "gemini":
            print("✓ Using Gemini chat model...")
            return ChatGoogleGenerativeAI(
                google_api_key=llm_config["api_key"],
                model=llm_config["model"],
                temperature=settings.LLM_TEMPERATURE,
                max_output_tokens=settings.LLM_MAX_OUTPUT_TOKENS
            )
        elif llm_config["provider"] == "azure":
            print("✓ Using Azure OpenAI chat model...")
            return AzureChatOpenAI(
                azure_endpoint=llm_config["azure_endpoint"],
                api_key=llm_config["api_key"],
                api_version=llm_config["api_version"],
                azure_deployment=llm_config["deployment_name"],
                model=llm_config["model"],
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS
            )
        else:  # OpenAI fallback
            print("✓ Using OpenAI chat model...")
            return ChatOpenAI(
                api_key=llm_config["api_key"],
                model=llm_config["model"],
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=settings.LLM_MAX_TOKENS
            )
    
    def _create_prompt_template(self, user_role: UserRole) -> PromptTemplate:
        """
        Create role-specific prompt template
        
        Args:
            user_role: User role for context
        
        Returns:
            PromptTemplate instance
        """
        role_context = self.ROLE_PROMPTS.get(
            user_role,
            self.ROLE_PROMPTS[UserRole.GENERAL]
        )
        
        template = f"""{role_context}

===== CONTEXT FROM DOCUMENTS =====
{{context}}

===== USER QUESTION =====
{{question}}

===== RESPONSE =====
Provide a clear, detailed response based ONLY on the context above.
Include relevant details and use bullet points if appropriate.
DO NOT make up information not in the context."""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    # def query(
    #     self,
    #     question: str,
    #     user_role: UserRole = UserRole.GENERAL,
    #     include_sources: bool = True
    # ) -> Dict[str, Any]:
    #     """
    #     Process a question using RAG pipeline
        
    #     Args:
    #         question: User question
    #         user_role: User role for context-aware response
    #         include_sources: Whether to include source documents
        
    #     Returns:
    #         Dictionary with answer, sources, and metadata
    #     """
    #     start_time = time.time()
    #     self.vectorstore = document_processor.get_vectorstore()
    #     self.retriever = self.vectorstore.as_retriever(
    #         search_kwargs={"k": settings.RETRIEVAL_TOP_K}
    #     )
        
    #     # Create role-specific prompt
    #     prompt_template = self._create_prompt_template(user_role)
        
    #     # Create retrieval chain
    #     qa_chain = RetrievalQA.from_chain_type(
    #         llm=self.llm,
    #         chain_type="stuff",
    #         retriever=self.retriever,
    #         return_source_documents=include_sources,
    #         chain_type_kwargs={"prompt": prompt_template}
    #     )
        
    #     # Execute query
    #     try:
    #         result = qa_chain.invoke({"query": question})
    #     except Exception as e:
    #         return {
    #             "question": question,
    #             "answer": f"❌ Error processing query: {str(e)}",
    #             "sources": [],
    #             "user_role": user_role.value,
    #             "disclaimer": self.DISCLAIMER,
    #             "processing_time_seconds": round(time.time() - start_time, 2)
    #         }
        
    #     # Process sources
    #     sources = []
    #     if include_sources and "source_documents" in result:
    #         sources = self._process_sources(result["source_documents"])
        
    #     elapsed_time = time.time() - start_time
        
    #     return {
    #         "question": question,
    #         "answer": result["result"],
    #         "sources": sources,
    #         "user_role": user_role.value,
    #         "disclaimer": self.DISCLAIMER,
    #         "processing_time_seconds": round(elapsed_time, 2)
    #     }
    




    def query(
        self,
        question: str,
        user_role: UserRole = UserRole.GENERAL,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Process a question using RAG pipeline with tool support
        
        Args:
            question: User question
            user_role: User role for context-aware response
            include_sources: Whether to include source documents
        
        Returns:
            Dictionary with answer, sources, and metadata
        """
        
        start_time = time.time()
        
        self.vectorstore = document_processor.get_vectorstore()
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": settings.RETRIEVAL_TOP_K}
        )
        
        # Get tool schemas for LLM
        from backend.tools.registry import tool_registry
        tool_schemas = tool_registry.get_all_schemas()
        
        # Create prompt template
        prompt_template = self._create_prompt_template(user_role)
        
        # Enhance prompt with tool information
        tool_info = ""
        if tool_schemas:
            tool_info = """
===== AVAILABLE TOOLS =====
The following tools are available to enhance your response:
    """
            for i, schema in enumerate(tool_schemas, 1):
                func = schema.get("function", {})
                tool_info += f"{i}. {func.get('name')}: {func.get('description')}\n"
            
            tool_info += """
IMPORTANT: If the user asks about:
- Current time, date, or day → Use get_current_datetime
- Patient age from birthdate → Use calculate_age
- Hospital department hours → Use get_working_hours
- Hospital policies or procedures → Use search_internal_docs
- Health information from web → Use web_search

When you use a tool, mention it in your response like:
"Using get_current_datetime to check..." or "Searching hospital docs for..."
===== END TOOLS =====
    """
        
        # Update template
        original_template = prompt_template.template
        if "AVAILABLE TOOLS" not in original_template:
            original_template = original_template.replace(
                "===== RESPONSE =====",
                f"{tool_info}\n===== RESPONSE ====="
            )
            prompt_template.template = original_template
        
        # Create chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=include_sources,
            chain_type_kwargs={"prompt": prompt_template}
        )
        
        # Execute query
        try:
            result = qa_chain.invoke({"query": question})
        except Exception as e:
            return {
                "question": question,
                "answer": f"❌ Error processing query: {str(e)}",
                "sources": [],
                "user_role": user_role.value,
                "disclaimer": self.DISCLAIMER,
                "processing_time_seconds": round(time.time() - start_time, 2),
                "tools_used": []
            }
        
        # Process sources
        sources = []
        if include_sources and "source_documents" in result:
            sources = self._process_sources(result["source_documents"])
        
        # Check if any tools were mentioned in response
        tools_used = self._extract_tools_used(result.get("result", ""))
        
        elapsed_time = time.time() - start_time
        
        return {
            "question": question,
            "answer": result.get("result", ""),
            "sources": sources,
            "user_role": user_role.value,
            "disclaimer": self.DISCLAIMER,
            "processing_time_seconds": round(elapsed_time, 2),
            "tools_used": tools_used
        }

    def _extract_tools_used(self, response: str) -> List[str]:
        """Extract which tools were mentioned in response"""
        from backend.tools.registry import tool_registry
        
        tools_used = []
        tool_names = tool_registry.get_tool_names()
        
        for tool_name in tool_names:
            if tool_name.lower() in response.lower():
                tools_used.append(tool_name)
        
        return tools_used


    
    
    def _process_sources(self, source_documents: List[Document]) -> List[Dict[str, Any]]:
        """
        Process source documents into structured format
        
        Args:
            source_documents: List of retrieved documents
        
        Returns:
            List of source dictionaries
        """
        sources = []
        
        for i, doc in enumerate(source_documents):
            # Extract filename from path
            filename = doc.metadata.get("source", "unknown")
            if "/" in filename or "\\" in filename:
                filename = filename.split("/")[-1].split("\\")[-1]
            
            chunk_index = doc.metadata.get("chunk_index", i)
            
            # Create content preview (first 200 chars)
            content_preview = doc.page_content[:200]
            if len(doc.page_content) > 200:
                content_preview += "..."
            
            sources.append({
                "filename": filename,
                "chunk_index": chunk_index,
                "relevance_score": round(1.0 - (i * 0.1), 2),
                "content_preview": content_preview
            })
        
        return sources




# # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# Create global instance
# rag_engine = RAGEngine()



# # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# # NEW (lazy initialization):
# _rag_engine_instance = None

# def get_rag_engine():
#     """Get or create RAG engine instance"""
#     global _rag_engine_instance
#     if _rag_engine_instance is None:
#         _rag_engine_instance = RAGEngine()
#     return _rag_engine_instance

# # For backward compatibility
# rag_engine = get_rag_engine()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # 
