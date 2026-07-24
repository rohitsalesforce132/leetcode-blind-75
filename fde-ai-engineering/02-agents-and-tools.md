# Chapter 2: Agents, Tool Harness & Function Calling

> **Interview questions:** "What is an AI agent?" / "Explain tool calling" / "How does an agentic harness work?"

---

## 1. What Is an AI Agent?

**Analogy:** A regular LLM chat is like calling a smart friend on the phone. They can only talk. An agent is like hiring that friend as an employee — they can talk AND take actions in the real world (search the web, query a database, send an email, run code).

```
REGULAR LLM CALL:
    User: "What's the weather in Mumbai?"
    LLM: "I don't have real-time data. (Or worse, it hallucinates.)"

AGENT WITH TOOLS:
    User: "What's the weather in Mumbai?"
    LLM: "Let me check." → calls get_weather("Mumbai") → "It's 32°C and sunny in Mumbai."

THE DIFFERENCE:
    LLM = brain only (can think, can't act)
    Agent = brain + hands (can think AND take actions via tools)
```

**Formal definition:** An AI agent is an LLM wrapped in a loop that can:
1. **Reason** about what to do next
2. **Act** by calling external tools/APIs
3. **Observe** the result and decide the next step
4. **Repeat** until the task is complete

---

## 2. Function Calling / Tool Calling

### What Is Function Calling?

Function calling is the mechanism that lets an LLM "call" external functions. The LLM doesn't execute code itself — it outputs a **structured request** saying "I want to call this function with these arguments," and YOUR code executes it.

```
Step-by-step:

1. You give the LLM a system prompt + available tools (function definitions)
2. The LLM decides it needs to call a tool
3. The LLM outputs structured JSON: {"function": "get_weather", "args": {"city": "Mumbai"}}
4. YOUR code parses this, executes the actual function
5. YOUR code returns the result to the LLM
6. The LLM uses the result to generate the final answer

┌──────┐                      ┌─────┐                     ┌──────────┐
│ User │ ──"Weather in Mumbai"│ LLM │                     │ Weather  │
│      │ ──────────────────>  │     │                     │ API      │
└──────┘                      │     │                     └────┬─────┘
                              │     │  "I need to call     │    │
                              │     │   get_weather(Mumbai)"    │
                              │     │  ─────────────────────    │
                              │     │                         │
                              │     │  <── 32°C, sunny ──────│    │
                              │     │                         │
                              │     │  "It's 32°C and sunny   │
                              │     │   in Mumbai!"           │
                              └─────┘                         │
```

### How to Define Tools

```python
# You define tools as JSON schema. The LLM sees these definitions.

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g. 'Mumbai'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_database",
            "description": "Search the customer database by name or email",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        }
    }
]
```

### Complete Function Calling Example

```python
import openai

# Step 1: Define the actual Python function
def get_weather(city: str, unit: str = "celsius") -> dict:
    """Real implementation — calls a weather API."""
    # (Simulated)
    return {"city": city, "temperature": 32, "unit": "°C", "condition": "sunny"}

# Step 2: Define tools for the LLM
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
            },
            "required": ["city"]
        }
    }
}]

# Step 3: Make the LLM call
response = openai.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Mumbai?"}],
    tools=tools,
)

# Step 4: Check if the LLM wants to call a tool
message = response.choices[0].message

if message.tool_calls:
    for tool_call in message.tool_calls:
        func_name = tool_call.function.name       # "get_weather"
        func_args = json.loads(tool_call.function.arguments)  # {"city": "Mumbai"}

        # Step 5: Execute the actual function
        result = get_weather(**func_args)          # Call our Python function

        # Step 6: Feed the result back to the LLM
        messages.append(message)                    # Add LLM's tool call to history
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)           # Give LLM the result
        })

    # Step 7: Get final response
    final_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )
    print(final_response.choices[0].message.content)
    # "It's 32°C and sunny in Mumbai."
```

---

## 3. The Agentic Loop (ReAct Pattern)

### What Is ReAct?

**ReAct = Reasoning + Acting.** The agent reasons about what to do, takes an action, observes the result, and repeats.

```
┌─────────────────────────────────────────────────────────┐
│                    AGENTIC LOOP                         │
│                                                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌──────┐ │
│  │  THOUGHT │──>│  ACTION  │──>│ OBSERVE  │──>│ LOOP?│ │
│  │          │   │          │   │          │   │      │ │
│  │ "I need  │   │ call     │   │ Result:  │   │ More │ │
│  │ weather  │   │ get_     │   │ 32°C     │   │ steps│ │
│  │ data"    │   │ weather()│   │ sunny    │   │ needed│ │
│  └─────────┘   └─────────┘   └─────────┘   └──┬───┘ │
│                                               │      │
│                                  ┌────────────┘      │
│                                  ▼                    │
│                              ┌─────────┐              │
│                              │  ANSWER  │             │
│                              │ "32°C"  │             │
│                              └─────────┘              │
└───────────────────────────────────────────────────────┘
```

### ReAct in Action — A Real Example

```
User: "Compare the weather in Mumbai and Delhi, and tell me which is hotter."

ITERATION 1:
  Thought: "I need to get weather for both cities."
  Action:  get_weather("Mumbai")
  Observe: {"temp": 32, "condition": "sunny"}

ITERATION 2:
  Thought: "Now I need Delhi's weather."
  Action:  get_weather("Delhi")
  Observe: {"temp": 38, "condition": "hot"}

ITERATION 3:
  Thought: "Delhi is 38°C, Mumbai is 32°C. Delhi is hotter by 6°C."
  Answer:  "Delhi is hotter at 38°C compared to Mumbai's 32°C. The difference is 6°C."

THE LOOP:
  while not done:
      thought = llm.reason(context)          # Think
      if thought.is_final_answer:
          return thought.answer              # Done!
      action_result = execute(thought.tool)  # Act
      context.add(action_result)             # Observe
```

### Complete Agentic Harness Implementation

```python
import json

class Agent:
    """A minimal but complete agentic harness."""

    def __init__(self, model, tools, system_prompt, max_iterations=10):
        self.model = model
        self.tools = tools                    # Dict: name → callable
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.messages = [{"role": "system", "content": system_prompt}]

    def run(self, user_input: str) -> str:
        """The agentic loop."""
        self.messages.append({"role": "user", "content": user_input})

        for i in range(self.max_iterations):
            print(f"\n--- Iteration {i+1} ---")

            # Step 1: Call LLM with current context
            response = self._call_llm()
            message = response.choices[0].message

            # Step 2: Does the LLM want to call a tool?
            if not message.tool_calls:
                # No tool call → LLM is giving final answer
                self.messages.append(message)
                return message.content

            # Step 3: Execute each tool call
            self.messages.append(message)  # Save LLM's tool request

            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                print(f"  Tool: {func_name}({func_args})")

                if func_name in self.tools:
                    # Execute the actual function
                    result = self.tools[func_name](**func_args)
                else:
                    result = {"error": f"Unknown tool: {func_name}"}

                print(f"  Result: {result}")

                # Step 4: Feed result back to LLM
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

        return "Max iterations reached without final answer."

    def _call_llm(self):
        """Call the LLM API."""
        return openai.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self._get_tool_definitions(),
        )

    def _get_tool_definitions(self):
        """Convert tool callables to OpenAI tool format."""
        # In practice, you'd define these as JSON schemas
        return [{"type": "function", "function": {"name": name, ...}}
                for name in self.tools]


# --- USAGE ---
agent = Agent(
    model="gpt-4o",
    tools={
        "get_weather": get_weather,
        "search_web": search_web,
        "query_database": query_database,
    },
    system_prompt="You are a helpful assistant. Use tools when needed."
)

answer = agent.run("Compare weather in Mumbai and Delhi.")
print(answer)
```

---

## 4. Types of Agents

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT TYPES                              │
├──────────────────┬──────────────────────────────────────────┤
│ Type             │ How It Works                              │
├──────────────────┼──────────────────────────────────────────┤
│ ReAct Agent      │ Think → Act → Observe → Repeat            │
│                  │ (Most common. Used by LangChain, etc.)   │
├──────────────────┼──────────────────────────────────────────┤
│ Plan-and-Execute │ Plan all steps FIRST, then execute each   │
│                  │ (Better for complex multi-step tasks)     │
├──────────────────┼──────────────────────────────────────────┤
│ Multi-Agent      │ Multiple agents with different roles      │
│                  │ (Researcher + Writer + Reviewer)          │
├──────────────────┼──────────────────────────────────────────┤
│ Code Execution   │ Agent writes and runs Python code         │
│                  │ (Like ChatGPT Code Interpreter)           │
├──────────────────┼──────────────────────────────────────────┤
│ RAG Agent        │ Searches knowledge base before answering  │
│                  │ (Most common FDE agent)                   │
└──────────────────┴──────────────────────────────────────────┘
```

---

## 5. Common Tools for FDE Agents

| Tool Category | Example Tools | Use Case |
|--------------|--------------|----------|
| Data Query | SQL query, Elasticsearch, MongoDB | Customer data lookup |
| Web Access | Web search, URL fetch, web scraper | Real-time information |
| File I/O | Read/write files, CSV/JSON parse | Document processing |
| Code Execution | Python sandbox, shell execution | Data analysis, computations |
| Communication | Send email, Slack message, API call | Notifications, integrations |
| Knowledge Base | Vector search, RAG retrieval | Answer from company docs |
| Calendar/CRM | Salesforce, HubSpot, Jira | Customer workflow automation |

---

## 6. Challenges with Agents

### Challenge 1: Infinite Loops

```
Problem: Agent calls a tool, gets an error, calls it again, gets the same error,
         repeats forever.

Solution:
  - max_iterations limit (always set this!)
  - Track errors and break if same error repeats 3 times
  - "If you get an error 3 times, explain the problem to the user"
```

### Challenge 2: Hallucinated Tool Calls

```
Problem: LLM invents a tool name or argument that doesn't exist.

Example: LLM calls "get_temperature" but the tool is named "get_weather"
         LLM passes city="Mumbai, India" but the API expects city="Mumbai"

Solution:
  - Validate tool name and arguments before executing
  - Return a helpful error message: "Unknown tool. Available: get_weather, search_web"
  - Use structured output (JSON schema enforcement)
```

### Challenge 3: Cost Control

```
Problem: Each iteration calls the LLM → each call costs money.
         A 10-iteration agent costs 10× a single LLM call.

Solution:
  - Cheaper model for simple iterations (GPT-4o-mini)
  - Summarize conversation history to reduce token count
  - Cache tool results to avoid re-querying
  - Set max_iterations
```

---

## 7. Frameworks Comparison

| Framework | Description | Best For |
|-----------|-------------|----------|
| **LangChain** | Full-featured agent framework. Chains, tools, memory. | Rapid prototyping, many integrations |
| **LangGraph** | State-machine agents with graphs. Better control. | Complex multi-step workflows |
| **CrewAI** | Multi-agent collaboration. Roles + tasks. | Team-of-agents scenarios |
| **AutoGen** | Microsoft's multi-agent framework. | Research, code generation |
| **Pydantic AI** | Type-safe agents with Pydantic validation. | Production systems needing reliability |
| **Custom** | Your own loop (like the one above). | Full control, minimal dependencies |

**FDE recommendation:** Start with a custom loop for understanding. Use LangChain/CrewAI for production. Many teams are moving away from heavy frameworks to lightweight custom loops.

---

## Interview Q&A

**Q: "What is an AI agent?"**
A: An AI agent is an LLM wrapped in a loop that can reason, act, and observe. Unlike a plain LLM call where the model only generates text, an agent can call external tools — query databases, search the web, run code — to accomplish multi-step tasks. The core pattern is ReAct: the model reasons about what to do (Thought), calls a tool (Action), sees the result (Observation), and repeats until it has enough information to answer.

**Q: "How does function calling work under the hood?"**
A: Function calling is a structured output capability. I define tools as JSON schemas with names, descriptions, and parameter types. The LLM is fine-tuned to output a structured JSON object when it determines a tool should be called. My code parses this JSON, executes the actual Python function, and feeds the result back as a "tool" role message. The LLM then generates the final answer using that result. The LLM never executes code itself — it outputs a request that my harness executes.

**Q: "What is an agentic harness?"**
A: The harness is the orchestration code around the LLM. It manages the message history, handles tool dispatch, enforces safety limits (max iterations), and controls the overall workflow. Think of the LLM as the brain and the harness as the body — the harness executes actions the LLM decides on. A good harness handles errors gracefully, limits costs, and provides observability into what the agent is doing.

**Q: "How do you prevent agents from getting stuck in loops?"**
A: Four strategies: (1) Always set a max_iterations limit as a hard stop. (2) Track error patterns — if the same tool fails the same way 3 times, break. (3) Include retry guidance in the system prompt: "If a tool fails, try a different approach." (4) Use a token budget — if total tokens consumed exceeds N, stop and return what you have.

**Q: "When would you use a multi-agent system vs a single agent?"**
A: Single agent for linear tasks (lookup → answer). Multi-agent for tasks that benefit from specialization — a researcher agent gathers data, a writer agent drafts the response, a reviewer agent checks for quality. Multi-agent shines when different steps need different system prompts, tools, or models. But multi-agent adds complexity and cost, so I only use it when the task genuinely can't be solved by one agent.

**Q: "What tools would you build for an enterprise FDE agent?"**
A: For enterprise, I'd build: (1) A SQL query tool for customer data lookup. (2) A vector search tool for knowledge base / documentation. (3) A web search tool for real-time information. (4) An action tool (send email, update CRM, create ticket). (5) A code execution tool for data analysis. (6) A human-escalation tool for when the agent isn't confident. The key is giving the agent just enough tools — too many tools confuse it and degrade performance.
