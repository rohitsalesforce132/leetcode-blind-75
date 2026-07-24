# Chapter 4: MCP (Model Context Protocol)

> **Interview questions:** "What is MCP?" / "When should you use MCP?" / "How does MCP compare to regular function calling?"

---

## 1. What Is MCP?

**Analogy:** Before USB, every device had its own connector — Sony had Sony ports, Apple had FireWire, printers had parallel ports. You needed a different cable for everything. USB standardized this: one connector type for everything. **MCP is USB for AI tools.**

**MCP = Model Context Protocol.** Released by Anthropic in late 2024. It's an open standard that lets any AI model connect to any external tool, data source, or API — using the same standard interface.

```
BEFORE MCP (The Problem):
┌────────┐      ┌──────────────────────────────────────┐
│ Claude │ ──── │ Custom integration A (custom code)    │
└────────┘      ├──────────────────────────────────────┤
┌────────┐      │ Custom integration B (custom code)    │
│ GPT-4  │ ──── │                                        │
└────────┘      ├──────────────────────────────────────┤
┌────────┐      │ Custom integration C (custom code)    │
│ Llama  │ ──── │                                        │
└────────┘      └──────────────────────────────────────┘

  Every model × every tool = N × M custom integrations.

WITH MCP (The Solution):
┌────────┐                                      ┌──────────┐
│ Claude │ ──┐                               ┌──│ Database │
└────────┘   │                               │  └──────────┘
┌────────┐   │     ┌──────────────┐          │  ┌──────────┐
│ GPT-4  │ ──┼──── │   MCP        │ ──────── │──│ Slack    │
└────────┘   │     │   Protocol    │          │  └──────────┘
┌────────┐   │     │  (standard)   │          │  ┌──────────┐
│ Llama  │ ──┘     └──────────────┘          └──│ GitHub   │
└────────┘                                      └──────────┘

  Every model connects to every tool via ONE standard protocol.
  N + M integrations instead of N × M.
```

---

## 2. How MCP Works

### The Architecture

```
┌──────────────┐          ┌──────────────┐          ┌──────────────┐
│  MCP HOST    │          │  MCP CLIENT  │          │  MCP SERVER  │
│  (App)       │          │  (Protocol   │          │  (Tool       │
│              │          │   Layer)     │          │   Provider)  │
│              │          │              │          │              │
│  Claude      │ ◄──────► │  Translates  │ ◄──────► │  GitHub      │
│  Desktop     │          │  between     │          │  Server      │
│  Cursor      │          │  host and    │          │              │
│  VS Code     │          │  server      │          │  Slack       │
│              │          │              │          │  Server      │
│              │          │              │          │              │
│              │          │              │          │  Database    │
│              │          │              │          │  Server      │
└──────────────┘          └──────────────┘          └──────────────┘
```

### The Three Primitives of MCP

MCP servers expose three types of capabilities:

```
1. TOOLS (Actions the AI can take)
   "query_database", "send_slack_message", "create_github_issue"
   → Like function calling, but standardized.

2. RESOURCES (Data the AI can read)
   "file:///reports/q3.pdf", "github://repo/issues"
   → Read-only data sources the AI can access on demand.

3. PROMPTS (Reusable prompt templates)
   "code_review_prompt", "incident_analysis_template"
   → Pre-defined prompt templates for specific workflows.
```

### MCP Communication Flow

```
1. HOST (Claude Desktop) starts and connects to MCP servers
       │
       ▼
2. MCP CLIENT discovers what the server offers:
       "What tools/resources/prompts do you have?"
       │
       ▼
3. MCP SERVER responds with its capabilities:
       tools: ["query_db", "insert_record"]
       resources: ["database://schema"]
       │
       ▼
4. User asks Claude: "Show me all open tickets"
       │
       ▼
5. HOST (Claude) decides to call tool "query_db"
       │
       ▼
6. MCP CLIENT sends standardized request:
       {"method": "tools/call", "params": {"name": "query_db", "arguments": {"sql": "SELECT * FROM tickets"}}}
       │
       ▼
7. MCP SERVER executes the query and returns result
       │
       ▼
8. Claude formats the answer for the user
```

---

## 3. When to Use MCP vs Regular Function Calling

This is the #1 MCP interview question. Here's the decision framework:

### Use REGULAR Function Calling when:

```
1. SINGLE MODEL, FEW TOOLS
   You're building one app with GPT-4o and 5 custom tools.
   Function calling is simpler. No need for a protocol layer.

2. TIGHTLY COUPLED SYSTEM
   Your tools are specific to your application (query_my_custom_db).
   Nobody else would ever use these tools.

3. SIMPLE ARCHITECTURE
   One LLM, one set of tools, one application.
   Adding MCP would be over-engineering.

4. NEED MAXIMUM CONTROL
   You want custom error handling, retry logic, logging on every tool call.
   Function calling gives you full control.
```

### Use MCP when:

```
1. MULTIPLE MODELS NEED THE SAME TOOLS
   You have Claude, GPT-4o, and Llama all needing GitHub access.
   Write ONE MCP server → all three models use it.

2. REUSABILITY ACROSS TEAMS/PROJECTS
   Your company builds a "Customer Data MCP Server" once.
   Every team's AI agent can use it without custom integration.

3. ECOSYSTEM / MARKETPLACE
   You want your tools to work with Claude Desktop, Cursor, VS Code,
   and any MCP-compatible client without writing custom code for each.

4. STANDARDIZATION
   Multiple teams building AI agents → standardize on MCP so everyone
   uses the same tool interface.

5. DYNAMIC TOOL DISCOVERY
   You want the AI to discover available tools at runtime instead of
   hardcoding them. MCP servers advertise their capabilities.
```

### Decision Matrix

```
                    ┌──────────────────┬──────────────────┐
                    │  Few Tools       │  Many Tools      │
  ┌────────────────┼──────────────────┼──────────────────┤
  │                │                  │                  │
  │  Single Model  │  Function Call   │  Function Call   │
  │                │  (simplest)      │  (group tools)   │
  │                │                  │                  │
  ├────────────────┼──────────────────┼──────────────────┤
  │                │                  │                  │
  │  Multi-Model   │  Function Call   │  MCP             │
  │                │  (per model)     │  (write once,    │
  │                │                  │   use anywhere)  │
  │                │                  │                  │
  └────────────────┴──────────────────┴──────────────────┘
```

---

## 4. Building an MCP Server

```python
# A minimal MCP server using the official Python SDK
from mcp import Server, Tool
import json

server = Server("my-tools")

# Define a tool
@server.tool("query_database")
async def query_database(sql: str) -> str:
    """Execute a SQL query and return results."""
    # Your actual database code here
    results = await db.execute(sql)
    return json.dumps(results)

# Define a resource
@server.resource("config://app-settings")
async def get_config() -> str:
    """Return application configuration."""
    return json.dumps({"version": "1.0", "max_users": 1000})

# Define a prompt template
@server.prompt("code-review")
async def code_review_prompt(code: str) -> str:
    """Generate a code review prompt."""
    return f"Review this code for security, performance, and style:\n\n{code}"

# Run the server
if __name__ == "__main__":
    server.run()  # Listens for MCP requests via stdio or SSE
```

### Connecting Claude Desktop to Your MCP Server

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "my-database": {
      "command": "python3",
      "args": ["/path/to/my_mcp_server.py"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

---

## 5. MCP vs Custom APIs — Tradeoffs

| Factor | MCP | Custom Function Calling |
|--------|-----|------------------------|
| **Setup effort** | Higher (define server, protocol) | Lower (define JSON schema) |
| **Reusability** | Write once, use with any MCP client | Per-model, per-app |
| **Standardization** | Open standard, growing ecosystem | Your own format |
| **Control** | Less (protocol constrains you) | Full control |
| **Performance** | IPC overhead (stdio/SSE) | Direct function call |
| **Ecosystem** | Works with Claude, Cursor, VS Code, etc. | Only your app |

---

## 6. Real-World MCP Use Cases for FDE

### Use Case 1: Enterprise Data Access Layer

```
COMPANY "ACME CORP" has:
  - Salesforce (CRM data)
  - ServiceNow (ticketing)
  - Jira (engineering)
  - Confluence (docs)
  - Internal PostgreSQL (custom data)

WITHOUT MCP:
  Each AI agent needs custom integration for each system.
  5 systems × 4 AI agents = 20 custom integrations.

WITH MCP:
  Build 1 MCP server per system (5 servers).
  All 4 AI agents connect to all 5 servers via MCP.
  5 + 4 = 9 connections (not 20). Much simpler.
```

### Use Case 2: FDE Customer Deployment

```
As an FDE deploying at a customer site, you need the AI to access
their internal systems. Every customer has different systems.

WITHOUT MCP:
  Write custom code for each customer's systems. Months of work.

WITH MCP:
  Check if MCP servers exist for their systems (Salesforce, SAP, etc.)
  Configure the AI client to connect to those MCP servers.
  Deployment time: weeks → days.
```

---

## Interview Q&A

**Q: "What is MCP and why does it exist?"**
A: MCP is the Model Context Protocol — an open standard by Anthropic for connecting AI models to external tools and data. It exists because before MCP, every AI model × every tool required a custom integration — an N×M problem. MCP standardizes the interface so any model can connect to any tool. You build one MCP server for your database, and Claude, GPT-4o, Cursor, and any MCP-compatible client can use it without custom code.

**Q: "When would you use MCP vs regular function calling?"**
A: Function calling for single-model, single-app scenarios with few tools — it's simpler and gives full control. MCP when you need reuse across multiple models, multiple teams, or want to plug into the ecosystem (Claude Desktop, Cursor, VS Code). The rule of thumb: if you're building tools only your app uses, function calling. If you're building tools that multiple AI clients should access, MCP.

**Q: "What are the three primitives of MCP?"**
A: Tools (actions the AI can take — like function calls), Resources (data the AI can read — like file URIs), and Prompts (reusable prompt templates for specific workflows). Tools are the most common — they're the standardized version of function calling. Resources are for giving the AI access to data without it needing to explicitly call a function.

**Q: "Is MCP production-ready for enterprise?"**
A: It's early but maturing fast. The protocol is well-designed and the SDK is solid. Major concerns for enterprise: (1) Security — the MCP server has access to your systems, so it needs proper auth. (2) Governance — who can create MCP servers? (3) Performance — IPC adds latency. For enterprise, I'd use MCP for internal tooling and development workflows first, then expand to customer-facing systems as the ecosystem matures.

**Q: "How does MCP handle security and authentication?"**
A: MCP servers run locally (stdio transport) or remotely (SSE transport). For local servers, security is simpler — the server runs as your user with your permissions. For remote servers, you need authentication. The MCP spec supports OAuth and API keys. The server is responsible for enforcing its own access control. For enterprise, I'd put the MCP server behind an API gateway with proper auth and rate limiting.
