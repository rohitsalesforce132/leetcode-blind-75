# Chapter 8: Interview Q&A Cheat Sheet

> **Use this the night before your interview.** Every question has a 2-sentence "quick answer" and a deeper explanation.

---

## 🧠 LLM Fundamentals

**Q: How does an LLM work?**
A: It's a transformer neural network trained to predict the next token. It converts text to embeddings, processes them through attention layers that understand context, and outputs a probability distribution over the vocabulary.

**Q: What is self-attention?**
A: Each token "looks at" all previous tokens to understand relationships — like connecting a pronoun to the noun it refers to. Multi-head attention runs this in parallel from different perspectives (grammar, meaning, reasoning).

**Q: What causes hallucinations?**
A: LLMs are probabilistic token predictors, not fact databases. They generate the most *likely* next token, not the most *truthful* one. Reduce with RAG, low temperature, system prompts ("say I don't know"), and structured output.

**Q: What is the context window?**
A: How much text the model can process at once (input + output). GPT-4o: 128K tokens, Claude 3.5: 200K, Gemini 1.5: 1M+. Larger isn't always better — "lost in the middle" problem where models miss info in the middle of long contexts.

**Q: What is temperature?**
A: Controls randomness in token selection. Temp=0: always pick most likely (deterministic, good for code/facts). Temp=0.7: some randomness (chat). Temp=1+: high creativity (poetry).

**Q: GPT-4o vs open-source — how do you choose?**
A: Five factors: (1) Data sensitivity (open-source if data can't leave network), (2) Cost at volume (open-source 10-50× cheaper), (3) Latency (self-hosted can be faster), (4) Quality (GPT-4o/Claude for frontier), (5) Compliance (regulated industries need self-hosted).

**Q: What is quantization?**
A: Reducing weight precision from FP16 (16-bit) to INT4 (4-bit). Shrinks model 4× in memory. A 70B model goes from 140GB to 35GB. Slight quality drop (1-3%) but massive cost savings.

---

## 🤖 Agents & Tools

**Q: What is an AI agent?**
A: An LLM wrapped in a loop that can reason, act via external tools, observe results, and repeat until the task is done. Unlike a plain LLM call, an agent can query databases, search the web, and execute code.

**Q: How does function calling work?**
A: I define tools as JSON schemas. The LLM outputs a structured request ("call get_weather(city=Mumbai)"). My code parses this, executes the real function, and feeds the result back. The LLM never runs code — it outputs a request my harness executes.

**Q: What is an agentic harness?**
A: The orchestration code around the LLM — manages messages, dispatches tools, enforces limits (max iterations), handles errors. The LLM is the brain; the harness is the body.

**Q: How do you prevent infinite loops?**
A: (1) max_iterations hard stop, (2) detect repeated errors (same failure 3× → break), (3) token budget limit, (4) system prompt guidance ("try different approach on failure").

**Q: ReAct vs Plan-and-Execute?**
A: ReAct thinks one step at a time (good for adaptive tasks). Plan-and-Execute creates a full plan upfront, then executes each step (better for complex multi-step tasks where you need the big picture first).

**Q: What tools would you build for an enterprise agent?**
A: (1) SQL query for customer data, (2) Vector search for docs, (3) Web search, (4) Code execution, (5) Action tools (send email, update CRM), (6) Human escalation. Keep tools minimal — too many confuses the model.

---

## 🎯 Context Engineering

**Q: What is context engineering?**
A: The systematic design of everything in the LLM's context window — system prompt, RAG docs, conversation history, tools, output format. Not just "prompt wording" but managing the entire token budget for maximum performance at minimum cost.

**Q: How do you handle long conversations?**
A: Hybrid strategy: (1) Summarize old messages with a cheap model, (2) Keep recent 6-10 messages verbatim, (3) Store key facts in vector DB for on-demand retrieval. This keeps context under 20K tokens even for long conversations.

**Q: How do you structure RAG context?**
A: Quality over quantity. Retrieve 20 → rerank with cross-encoder → keep top 3-5. Compress each to relevant paragraphs. Format with source citations. Add system instruction: "Answer ONLY from context. If not in context, say I don't know."

**Q: Few-shot vs zero-shot?**
A: Zero-shot for straightforward tasks. Few-shot for custom categories, specific formatting, or edge cases. Always include 1-2 edge-case examples in few-shot to calibrate the model.

**Q: How do you minimize token costs?**
A: (1) Summarize history with cheap model, (2) Rerank RAG results to fewer docs, (3) Route simple tasks to GPT-4o-mini, (4) Cache common queries and tool results.

---

## 🔌 MCP (Model Context Protocol)

**Q: What is MCP?**
A: An open standard by Anthropic for connecting AI models to external tools and data. Like "USB for AI tools." Write one MCP server → any MCP-compatible client (Claude, Cursor, VS Code) can use it.

**Q: When to use MCP vs function calling?**
A: Function calling for single-model, single-app scenarios (simpler, more control). MCP for multi-model reuse, ecosystem compatibility, or standardizing tools across teams. Rule: if only your app uses these tools → function calling. If multiple AI clients should access them → MCP.

**Q: What are MCP's three primitives?**
A: Tools (actions — like function calls), Resources (data sources the AI can read), Prompts (reusable templates).

---

## 🔧 Fine-Tuning

**Q: Is fine-tuning required?**
A: No. 90% of the time, prompt engineering + RAG is sufficient. Fine-tune only when you need to change model BEHAVIOR (format, tone, task specialization) and simpler methods can't reach the target accuracy.

**Q: Fine-tuning vs RAG?**
A: RAG for KNOWLEDGE (facts, data, documents — changes frequently). Fine-tuning for BEHAVIOR (output format, tone, domain language — stable patterns). You can do both: RAG for knowledge + fine-tuned model for behavior.

**Q: What is LoRA?**
A: Freezes the original model and trains tiny adapter weights (~10M params vs 7B). 10-100× cheaper. Runs on a single consumer GPU. Adapters are swappable at runtime. Quality is 1-3% below full fine-tuning.

**Q: What is catastrophic forgetting?**
A: Model forgets general skills when fine-tuned on a specific task. Prevent with: LoRA (preserves original), mixed training data (10-20% general), lower learning rate.

**Q: How much data do you need to fine-tune?**
A: For LoRA: 500-10,000 high-quality examples minimum. More is better but quality matters more than quantity. For format/style tasks, 500 examples can be enough.

---

## 🏋️ Training From Scratch

**Q: How are LLMs trained?**
A: Six stages: (1) Data collection (15T+ tokens from web, books, code), (2) Tokenization (BPE/SentencePiece), (3) Pre-training (next-token prediction, months on thousands of GPUs), (4) SFT (chat format, 100K-1M Q&A pairs), (5) RLHF/DPO (alignment), (6) Evaluation & deployment.

**Q: Pre-training vs fine-tuning?**
A: Pre-training: all params from scratch, 15T tokens, $50M+, months. Fine-tuning: start from pre-trained, adjust some params, 500-10K examples, $5-$500, hours-days.

**Q: What is RLHF?**
A: Reinforcement Learning from Human Feedback. Collect human preferences (which response is better), train a reward model, use PPO to optimize LLM toward higher rewards. Makes the model helpful + harmless + honest.

**Q: What is DPO?**
A: Direct Preference Optimization. Simpler alternative to RLHF — skip the reward model, directly optimize from preference data. More stable, faster, becoming the default.

**Q: Would you train from scratch for a customer?**
A: Almost never. $50M+ for pre-training with no advantage over fine-tuning Llama 3.1. The right approach: take a strong base model, fine-tune with LoRA on customer data. $5-$500, days not months, 95%+ of the value.

---

## 🚀 System Design & Production

**Q: How do you serve an LLM in production?**
A: Use vLLM or TGI for high-throughput inference with continuous batching and KV cache. Put behind a load balancer with rate limiting. Use quantized models (INT4/FP16) to reduce VRAM. Auto-scale GPU instances based on request queue depth.

**Q: How do you evaluate LLM performance?**
A: (1) Task-specific metrics (accuracy, BLEU, ROUGE), (2) LLM-as-judge (GPT-4o scores outputs), (3) Human evaluation (gold standard), (4) Benchmark suites (MMLU, HumanEval, MT-Bench), (5) A/B testing in production.

**Q: How do you monitor an LLM in production?**
A: Track: (1) Latency (P50, P95, P99), (2) Token usage and cost, (3) Error rates (timeouts, refusals), (4) Hallucination rate (sample and audit), (5) User satisfaction (thumbs up/down), (6) Tool call success rate.

**Q: How do you handle PII in LLM pipelines?**
A: (1) PII detection and redaction before sending to LLM, (2) Self-hosted models for sensitive data, (3) Data processing agreements with API providers, (4) No logging of PII in prompts/responses, (5) On-premise deployment for regulated data.

---

## 💡 Pro Tips for the Interview

### The "I Don't Know" Framework
```
If you don't know an answer:
  "I haven't worked with [X] directly, but based on my understanding of [Y],
   I'd approach it by [Z]. Let me think through this..."

  → Shows honesty + reasoning ability.
  → Better than making something up.
```

### The "Yes, And" Technique
```
When the interviewer mentions a technology:
  "Yes, and I'd also consider [alternative] because [reason]."

  Example: "We use LangChain."
  You: "Yes, LangChain is great for prototyping. And I'd also consider
  a custom harness for production because it gives more control over
  error handling and reduces dependency overhead."
```

### Always Have an Opinion
```
FDEs are hired for judgment. Don't just list options — RECOMMEND one.

BAD: "You could use RAG or fine-tuning, depending on the situation."
GOOD: "I'd start with RAG because it's faster to implement, cheaper,
       and handles knowledge updates. I'd only add fine-tuning if the
       model's output format consistency is below 95%."
```

### The Cost-Awareness Signal
```
Always mention cost implications. This is what separates engineers from tourists.

"For this use case, I'd use GPT-4o-mini instead of GPT-4o.
 At 2B tokens/month, that saves $11,250/month — $135K/year.
 The quality difference for simple Q&A is negligible."
```

### Bring It Back to the Customer
```
FDEs exist to solve CUSTOMER problems. Always connect technical answers to impact.

"The reason I'd choose LoRA over full fine-tuning isn't just cost —
 it's deployment speed. A customer can go live in 2 days with LoRA
 instead of 2 weeks with full fine-tuning. Speed to value matters
 when you're deploying at customer sites."
```

---

## Quick Reference: Decision Trees

### "Should I fine-tune?"
```
Is prompt engineering + RAG good enough?
  YES → Done. Don't fine-tune.
  NO ↓
Is the problem about KNOWLEDGE (facts, data)?
  YES → Improve RAG (more docs, better retrieval, reranking)
  NO ↓
Is the problem about BEHAVIOR (format, tone, task)?
  YES → Fine-tune with LoRA
  NO ↓
Does LoRA fine-tuning solve it?
  YES → Done.
  NO → Consider full fine-tuning or a different/larger base model
```

### "Which model should I use?"
```
Is data extremely sensitive?
  YES → Self-hosted (Llama 3.1 8B/70B)
  NO ↓
Is cost critical at high volume?
  YES → GPT-4o-mini or self-hosted
  NO ↓
Need frontier reasoning quality?
  YES → GPT-4o or Claude 3.5 Sonnet
  NO ↓
Need 1M+ context?
  YES → Gemini 1.5 Pro
  NO → GPT-4o-mini (default workhorse)
```

### "Agent vs single LLM call?"
```
Can the task be done in one LLM call?
  YES → Single call. Don't add complexity.
  NO ↓
Does it need external data (DB, web, files)?
  YES → Add tools. Start with RAG.
  NO ↓
Does it need multi-step reasoning?
  YES → Agent with ReAct loop
  NO ↓
Do multiple specialized roles need to collaborate?
  YES → Multi-agent system
```
