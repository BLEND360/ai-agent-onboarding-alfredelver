"""Base class for AI agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional,List
from pathlib import Path
from google import genai
import os
from dotenv import load_dotenv
from google.genai.types import FunctionDeclaration, Tool, Part as GeminiPart

load_dotenv()

class BaseAgent(ABC):
    """
    Base class for all AI agents.
    
    Implements Template Method pattern:
    - execute() orchestrates the workflow
    - Subclasses implement specific steps
    """

    def __init__(self, model_name: str = "gemini-2.5-flash",tools:List[Dict]=None):
        """
        Initialize agent.
        
        Args:
            model_name: Gemini model to use
        """
        self.model_name = model_name
        self.model = None
        self.tools = tools or []
        self.tool_functions = {}
        self._configure_model()
    
    def _configure_model(self):
        """Configure Gemini model."""
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")

        self.client = genai.Client(api_key=api_key)

        # Build tool declarations if provided
        if self.tools:
            functions = []
            for tool_schema in self.tools:
                func_decl = FunctionDeclaration(
                    name=tool_schema['name'],
                    description=tool_schema['description'],
                    parameters=tool_schema['parameters']
                )
                functions.append(func_decl)
            self._gemini_tools = [Tool(function_declarations=functions)]
        else:
            self._gemini_tools = None

    def register_tool_function(self, name: str, function):
        """Register actual function for a tool."""
        self.tool_functions[name] = function

    async def execute(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """
        Execute agent workflow (Template Method).
        
        Steps:
        1. Load input context
        2. Process with LLM
        3. Save results
        
        Args:
            input_path: Path to input markdown file
            output_path: Path to save output
            
        Returns:
            Result metadata
        """
        print(f"\n{self.__class__.__name__} starting...")
        
        # Step 1: Load
        context = await self._load_context(input_path)
        
        # Step 2: Process
        result = await self._process(context)
        
        # Step 3: Save
        await self._save_result(result, output_path)
        
        print(f"{self.__class__.__name__} complete")
        
        return {
            'input_path': input_path,
            'output_path': output_path,
            'success': True
        }
    @abstractmethod
    async def _load_context(self, input_path: str) -> Dict[str, Any]:
        """
        Load input context.
        
        Subclasses implement how to read their input.
        """
        pass
    
    @abstractmethod
    async def _process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process context with LLM.
        
        Subclasses implement their specific logic.
        """
        pass
    
    @abstractmethod
    async def _save_result(self, result: Dict[str, Any], output_path: str):
        """
        Save processing result.
        
        Subclasses implement how to save their output.
        """
        pass
    
    async def _call_llm(self, prompt: str) -> str:
        """
        Call Gemini with prompt.

        Helper method for subclasses.

        Args:
            prompt: Prompt to send

        Returns:
            LLM response text
        """
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name, contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"LLM call failed: {e}")
            raise

    async def _call_llm_with_tools(self, prompt: str) -> str:
        """
        Call LLM with tool support.

        Handles function calling loop.
        """
        config = {"tools": self._gemini_tools} if self._gemini_tools else {}
        chat = self.client.aio.chats.create(model=self.model_name, config=config)
        response = await chat.send_message(prompt)

        # Check for function calls
        while response.candidates[0].content.parts:
            part = response.candidates[0].content.parts[0]

            if part.function_call:
                func_call = part.function_call
                func_name = func_call.name
                func_args = dict(func_call.args)

                print(f"   Tool call: {func_name}({func_args})")

                if func_name in self.tool_functions:
                    result = self.tool_functions[func_name](**func_args)
                    print(f"   Tool result: {result}")

                    # Send function result back to LLM
                    response = await chat.send_message(
                        GeminiPart.from_function_response(
                            name=func_name,
                            response={"result": result}
                        )
                    )
                else:
                    raise ValueError(f"Tool {func_name} not registered")
            else:
                return response.text

        return response.text