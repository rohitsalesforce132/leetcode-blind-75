# AI Engineering — Deep-Dive: Ch 1–2 (Chip Huyen)

> **Source:** Chip Huyen, *AI Engineering* (2025), Chapters 1–2.
> **Scope:** Ch 1 — Introduction to Building AI Applications with Foundation Models; Ch 2 — Understanding Foundation Models.
> **Audience:** Engineers, ML practitioners, and interview candidates who want a rigorous, end-to-end mental model of *why* foundation models exist, *what* they are made of, and *how* applications are built on top of them.

---

## Table of Contents

**Chapter 1 — Introduction to AI Engineering**
1. [The Rise of AI Engineering](#1-the-rise-of-ai-engineering)
2. [From Language Models → LLMs → Foundation Models → AI Engineering](#2-evolution)
3. [Foundation Model Use Cases](#3-use-cases)
4. [Planning AI Applications](#4-planning)
5. [The AI Engineering Stack (3 Layers)](#5-stack)
6. [AI Engineering vs ML Engineering vs Full-Stack Engineering](#6-vs-ml)
7. [Chapter 1 — Interview Q&A (5)](#7-ch1-qa)

**Chapter 2 — Understanding Foundation Models**
8. [Training Data](#8-training-data)
9. [Model Architecture](#9-architecture)
10. [Model Size & Scaling Laws](#10-scaling)
11. [Post-Training: SFT, RLHF, DPO](#11-post-training)
12. [Sampling Fundamentals](#12-sampling)
13. [Structured Outputs](#13-structured-outputs)
14. [The Probabilistic Nature of AI](#14-probabilistic)
15. [Chapter 2 — Interview Q&A (5)](#15-ch2-qa)

**Appendix**
16. [Cross-Chapter Glossary](#16-glossary)
17. [Quick-Reference Cheat Sheet](#17-cheatsheet)

---

# CHAPTER 1: Introduction to Building AI Applications with Foundation Models

> *“If I could use only one word to describe AI post-2020, it'd be **scale**.”*
> — Chip Huyen

## 1. The Rise of AI Engineering

### 1.1 The Scale Consequence

The defining feature of post-2020 AI is **scale** — models so large they consume non-trivial fractions of global electricity and risk exhausting publicly available internet data. Scale produces two compounding consequences:

| Consequence | Effect |
|---|---|
| **Models become more capable** | More tasks become automatable → more users, more demand, more investment |
| **Training cost skyrockets** | Only a few organizations (OpenAI, Google, Meta, Anthropic, Mistral, governments) can afford to train → emergence of **model-as-a-service** |

This creates a paradox: *the demand for AI applications has exploded while the barrier to entry for building them has collapsed.* The discipline that emerged from this gap is **AI Engineering** — building applications on top of readily available foundation models.

### 1.2 What Changed vs. What Didn't

Building applications on ML models is *not new* — recommender systems, fraud detection, and churn prediction have run in production for over a decade. What changed:

- **New possibilities:** open-ended generation, multimodal reasoning, zero-shot task transfer
- **New challenges:** probabilistic outputs, hallucination, harder evaluation, GPU scarcity
- **What stays the same:** business-metric-to-ML-metric mapping, experimentation discipline, latency/cost optimization, feedback loops

---

## 2. Evolution: Language Models → LLMs → Foundation Models → AI Engineering

### 2.1 Language Models — The Completion Machine

A **language model** encodes statistical information about language: how likely a token (character, word, or sub-word) is to appear in a given context.

```
  Prompt:   "My favorite color is ____"
  Model:    P("blue") = 0.42   P("red") = 0.18   P("car") = 0.001 ...
```

**Token** = the atomic unit. GPT-4 breaks *"I can't wait to build AI applications"* into 9 tokens; `can't` → `can` + `'t`. Rule of thumb: **100 tokens ≈ 75 words**. Tokenization is chosen by the model developer; vocab sizes range widely (Mixtral 8x7B: 32K, GPT-4: 100,256).

**Why tokens (not words or characters)?**
1. Tokens carry more meaning than characters (`cook` + `ing` both carry meaning).
2. Fewer unique tokens than unique words → smaller, more efficient vocabularies.
3. Tokens handle unknown words (`chatgpting` → `chatgpt` + `ing`).

### 2.2 Two Flavors of Language Model

| Type | Training Signal | Uses Context From | Best For | Canonical Example |
|---|---|---|---|---|
| **Masked (bidirectional)** | Predict missing tokens *anywhere* | Both before AND after the blank | Classification, sentiment, code debugging | **BERT** (2018) |
| **Autoregressive (causal)** | Predict the *next* token | Only preceding tokens | Text generation (today's dominant paradigm) | **GPT family** |

> Unless stated otherwise, “language model” in this book means **autoregressive**.

```
   MASKED (BERT)                     AUTOREGRESSIVE (GPT)
   ┌────────────────────┐            ┌────────────────────┐
   │ "My [MASK] is blue"│            │ "My favorite color │
   │  ←── left ──→ right│            │  is ____"          │
   │   uses both sides  │            │   ←── left only ── │
   └────────────────────┘            └────────────────────┘
   Fill-in-the-blank                 Next-token prediction
```

### 2.3 Self-Supision — The Key to Scale

The breakthrough that enabled LLMs is **self-supervision**: the model infers labels *from the input itself*, requiring no human annotation.

For the sentence `"I love street food."`, a single sentence yields **6 training samples**:

| Input (context) | Output (next token) |
|---|---|
| `<BOS>` | `I` |
| `<BOS>, I` | `love` |
| `<BOS>, I, love` | `street` |
| `<BOS>, I, love, street` | `food` |
| `<BOS>, I, love, street, food` | `.` |
| `<BOS>, I, love, street, food, .` | `<EOS>` |

Because text sequences are *everywhere* (books, blogs, Reddit), self-supervision turns the entire internet into training data → enables scale.

> **Self-supervision ≠ unsupervised learning.** Self-supervised = labels inferred from input. Unsupervised = no labels at all.

**Contrast with supervised learning:** AlexNet (2012) required labeling ~1M images for 1,000 categories. At $0.05/image that's $50K; scaling to 1M categories → $50M in labeling alone.

### 2.4 From LLM to Foundation Model

Language models are text-only. Humans perceive the world multimodally. **Foundation models** extend language models to multiple modalities (text + image + audio + video + 3D + protein structures).

```
            ┌──────────────────────────────────┐
            │        FOUNDATION MODEL           │
            │   (general-purpose, multimodal)   │
            ├──────────┬──────────┬──────────────┤
            │  Text    │  Image   │  Audio/Video │
            │  Tokens  │  Tokens  │  Tokens      │
            └──────────┴──────────┴──────────────┘
                      ↓ next-token prediction
                      (conditioned on ALL modalities)
```

Key properties of foundation models:
1. **Multimodal** — work across data types (GPT-4V, Claude 3, Gemini).
2. **General-purpose** — out-of-the-box competence across many tasks (unlike task-specific predecessors).
3. **Adaptable** — can be specialized via prompt engineering, RAG, or finetuning.

**Natural language supervision (CLIP example):** OpenAI scraped 400M (image, text) pairs co-occurring on the web — 400× larger than ImageNet, no manual labels. CLIP became the first model to generalize across image-classification tasks without additional training.

### 2.5 Three Factors Driving AI Engineering's Explosion

| Factor | Description | Evidence |
|---|---|---|
| **1. General-purpose capabilities** | FMs do *more tasks*, including ones previously impossible | Writing, coding, image gen — every communicative task is partially automatable |
| **2. Increased investment** | ChatGPT success → VC + enterprise capital flood | Goldman Sachs: ~$100B US / $200B globally by 2025; 1-in-3 S&P 500 cos. mentioned AI in Q2 2023 earnings calls |
| **3. Low entrance barrier** | Model-as-a-service APIs + plain-English "programming" | Anyone can build; GitHub stars for AI tools (LangChain, Ollama, AutoGPT) surpassing React/Vue |

---

## 3. Foundation Model Use Cases

> AWS buckets enterprise GenAI into: customer experience, employee productivity, process optimization.
> Gartner adds **business continuity** — 7% of 2,500 execs cited *survival* as their AI motivation.

### 3.1 The Eight Use-Case Categories

| Category | Consumer Examples | Enterprise Examples |
|---|---|---|
| **Coding** | Code completion, screenshot→code | SQL-from-English, doc generation, commit messages |
| **Image & video** | Profile pics, photo editing | Ad generation, design, presentations |
| **Writing** | Emails, blog posts, books | Copywriting, SEO, reports, memos |
| **Education** | Tutoring, essay grading | Employee onboarding, upskilling |
| **Conversational bots** | Companions, AI personas | Customer support, product copilots |
| **Information aggregation** | Talk-to-your-docs, summarization | Market research, knowledge management |
| **Data organization** | Image search, photo tagging | IDP (intelligent doc processing), data extraction |
| **Workflow automation** | Trip planning, form filling | Lead gen, invoicing, agents |

### 3.2 Deep-Dive: Coding

Coding is the **#1 use case** across every survey. GitHub Copilot hit **$100M ARR** in two years. Specializations:
- **English→code:** DB-GPT, PandasAI, SQL Chat
- **Screenshot→website:** screenshot-to-code, draw-a-ui
- **Cross-language translation:** GPT-Migrate, AI Code Translator
- **Docs / tests / commits:** Autodoc, PentestGPT, AI Commits

McKinsey productivity data (Fig 1-9):

| Task | Productivity Gain |
|---|---|
| Documentation | **~2× faster** |
| Code generation / refactoring | 25–50% faster |
| Highly complex tasks | **Minimal** improvement |

> AI is notably better at **frontend** than backend development (anecdotally reported by many coding-tool builders).

### 3.3 Deep-Dive: Writing

MIT study (Noy & Zhang, 2023): 453 college-educated professionals on occupation-specific writing tasks, half exposed to ChatGPT:
- **Time ↓ 40%**, output quality ↑ 18%
- Closes the quality gap — *more* helpful to weaker writers
- 2× more likely to still use ChatGPT at work 2 weeks later

```
   Output Quality
        ▲
        │         ┌─── with ChatGPT (+18%)
        │      ╱──┘
        │    ╱
        │  ╱───── without ChatGPT
        │╱
        └────────────────────────────────►
              Weaker writers benefit MOST
              (quality gap closes)
```

**Consumer writing patterns:**
- "Be angry in an email, ask AI to make it pleasant."
- Give bullet points → get back complete paragraphs.
- Many users won't send important emails without AI review.
- Students write essays; writers write books. AI enables **interactive fiction** — plots that adapt to reader preferences. A children's reading app identifies words a child struggles with and generates stories centered on those words.

**Enterprise writing:**
- Sales/marketing: cold outreach, ad copywriting, product descriptions.
- CRMs (HubSpot, Salesforce) embed AI for web content and outreach emails.
- AI excels at **SEO** because training data is full of SEO-optimized text.

**Risk:** SEO-driven content farms. NewsGuard found 400 ads from 141 brands running on AI-generated junk sites (one site produced 1,200 articles/day). The future of internet content may be AI-generated — "pretty bleak."

### 3.4 Deep-Dive: Education

- NYC and LA school districts **banned then unbanned** ChatGPT within months.
- Chegg stock: **$28 → $2** (Nov 2022 → Sep 2024) as students flocked to AI.
- Duolingo (Pajak & Bicknell, 2022): AI helps most in the **personalization** stage of course creation.

```
   Duolingo Course Creation Pipeline (4 stages):

   ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐    ┌──────────────┐
   │ 1. Content  │ ─► │ 2. Structure│ ─► │ 3. LESSON       │ ─► │ 4. QA /      │
   │  Generation │    │  & Curric.  │    │ PERSONALIZATION │    │  Refinement  │
   └─────────────┘    └─────────────┘    └─────────────────┘    └──────────────┘
                                            ▲
                                            │
                                   AI helps MOST here
                                   (adapt to each learner)
```

**Personalization examples:**
- Auditory learners: AI reads materials aloud.
- Animal lovers: visualizations feature more animals.
- Coders: math equations translated to code.
- Language learners: AI roleplays practice scenarios.

**Innovative teaching method:** Teachers assign AI-generated essays for students to find and correct mistakes — turning AI into a critical-thinking training tool.

**The threat/opportunity duality:** If the risk is that AI can replace many skills, the opportunity is that AI can be used as a tutor to *learn* any skill. For many skills, AI helps someone get up to speed quickly, then continue learning to become better than AI.

### 3.5 Deep-Dive: Conversational Bots & Information Aggregation

**Conversational bots** are the most versatile use case — they find information, explain concepts, brainstorm, provide companionship, emulate personalities, and act as therapists. Digital companions have become "weirdly popular in an incredibly short amount of time." Research use: simulate societies with groups of bots to study social dynamics (Park et al., 2023).

**Enterprise bots:**
- **Customer support:** save costs + improve experience (faster response than humans).
- **Product copilots:** guide users through painful tasks (filing insurance, doing taxes, looking up corporate policies).

**Beyond text:** Voice assistants (Google Assistant, Siri, Alexa) have existed for years but have been slow to incorporate generative AI. **3D conversational bots** are common in games (smart NPCs via Inworld, Convai) and gaining traction in retail/marketing. AI makes NPCs much smarter — changing dynamics of games like The Sims and Skyrim.

**Information aggregation** — 74% of GenAI users use it to summarize/distill (Salesforce 2023).

```
   Instacart's "Fast Breakdown" Prompt Template
   (most popular in their internal prompt marketplace):

   Input:  [meeting notes + emails + Slack threads]
                    │
                    ▼
   ┌─────────────────────────────────────────┐
   │            AI PROCESSING                │
   └─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────────┐
   │  FACTS  │ │  OPEN   │ │  ACTION     │
   │         │ │QUESTIONS│ │  ITEMS      │
   └─────────┘ └─────────└ └─────────────┘
                              │
                              ▼
                   Auto-insert into project
                   tracker, assign to owners
```

**Data organization** goes hand-in-hand: AI auto-generates descriptions for images/videos, matches text queries to visuals (Google Photos, Google Image Search). The **IDP (Intelligent Document Processing)** industry is projected at **$12.81B by 2030** (32.9% CAGR) — extracting structured info from credit cards, licenses, receipts, contracts, charts.

### 3.6 Enterprise Deployment Risk Posture

```
   LOWER RISK                                HIGHER RISK
   ┌────────────────────┬───────────────────┬────────────────────┐
   │ Internal-facing    │ Classification /  │ External-facing    │
   │ knowledge mgmt     │ close-ended tasks │ customer chatbots  │
   │ (deploy first)     │ (easy to eval)    │ (deploy last)      │
   └────────────────────┴───────────────────┴────────────────────┘
   Companies build AI muscle on safe internal apps before customer-facing rollouts.
```

### 3.7 Deep-Dive: Workflow Automation & Agents

**Consumer automation:** booking restaurants, requesting refunds, planning trips, filling forms.

**Enterprise automation:** lead management, invoicing, reimbursements, data entry, customer-request routing. A standout use case is **data synthesis** — using AI to generate labels for data, looping in humans to improve them (Ch 8).

**Agents:** AIs that can *plan* and *use tools*. To book a restaurant, an agent might:
1. Open a search engine to look up the restaurant's phone number.
2. Use your phone to make a call.
3. Add an appointment to your calendar.

```
   AGENTIC WORKFLOW (simplified):

   User: "Book a table at Tartine for 7pm Friday for 4 people."
      │
      ▼
   ┌──────────────┐
   │  LLM PLANNER │  Decomposes goal into steps:
   └──────┬───────┘   1. Search for "Tartine restaurant phone"
          │              2. Call the number
          │              3. Ask for Friday 7pm table for 4
          │              4. If confirmed, add to calendar
          ▼
   ┌──────────────────────────────────────────────┐
   │  TOOL USE LOOP:                              │
   │                                              │
   │  Step 1: search("Tartine restaurant phone")  │
   │    → (415) 487-2600                          │
   │                                              │
   │  Step 2: call((415) 487-2600)                │
   │    → voice agent negotiates reservation      │
   │                                              │
   │  Step 3: calendar.add(Friday 7pm, "Tartine") │
   │    → confirmation                            │
   └──────────────────────────────────────────────┘
```

> "The level of interest around agents borders on obsession, but it's not entirely unwarranted." Agents are a central topic in Chapter 6.

---

## 4. Planning AI Applications

### 4.1 Use-Case Evaluation — Why Build?

Three risk tiers (high → low):

1. **Existential threat (business continuity):** If you don't adopt AI, competitors make you obsolete. *Document processing, financial analysis, ad creative, web design.* Priority = highest.
2. **Profit/productivity opportunity:** Cheaper acquisition, better retention, sales lead gen, market research. Most common motivation.
3. **FOMO / option value:** Unsure where AI fits, but can't afford to be Kodak/Blockbuster/BlackBerry. Fold into R&D.

**Build vs. Buy:** If AI is existential → build in-house. If it's productivity-boosting → plenty of buy options may be superior and cheaper.

### 4.2 The Role of AI in the Product (Apple's Framework)

| Dimension | Options | Implication |
|---|---|---|
| **Criticality** | Critical vs. Complementary | Critical AI (Face ID) must be highly accurate; complementary (Gmail Smart Compose) tolerates mistakes |
| **Reactivity** | Reactive (chatbot) vs. Proactive (Maps traffic alerts) | Reactive needs low latency; proactive can be pre-computed but has a *higher quality bar* (users view low-quality proactive features as intrusive) |
| **Dynamism** | Dynamic (per-user finetuning) vs. Static (one model for all) | Dynamic = personalization infra (e.g., ChatGPT memory); Static = simpler ops |

### 4.3 Human-in-the-Loop — Microsoft's Crawl-Walk-Run

```
   CRAWL ────────► WALK ──────────► RUN
   Human mandatory   AI talks to       AI talks to
   (AI suggests,     internal          external users
    human approves)  employees         (full automation)
```

Role of humans evolves as quality improves. E.g., once 95% of AI-suggested simple-request responses are accepted verbatim, route those directly to customers.

### 4.4 AI Product Defensibility — The Three Moats

| Moat | Who Wins | Notes |
|---|---|---|
| **Technology** | ~Equal for most (same FMs) | Differentiation must come from elsewhere |
| **Data** | First-movers with usage data | Even when user data can't train models directly, usage insights guide data collection |
| **Distribution** | Big companies | Incumbents can replicate a feature with 3 engineers in 2 weeks |

> Many legendary startups (Calendly, Mailchimp, Photoroom) began as features incumbents overlooked.

### 4.5 Setting Expectations — Metrics

| Metric Group | Examples |
|---|---|
| **Business** | % messages automated, labor saved, CSAT |
| **Quality** | Response accuracy, relevance, faithfulness |
| **Latency** | TTFT (time to first token), TPOT (time per output token), total latency |
| **Cost** | $/inference request |
| **Other** | Interpretability, fairness |

**Latency expectations — context matters:**

```
   Use Case                          Acceptable Latency
   ──────────────────────────        ─────────────────────────
   Human agent (current baseline)    ~1 hour median response
   Customer support chatbot          <30 seconds (users expect speed)
   Autocomplete (code, text)         <100ms (feels instant)
   Batch document processing         minutes-to-hours acceptable

   Rule of thumb: if AI is faster than the current human baseline,
   it's "good enough" on latency — focus on quality next.
```

### 4.6 The Last-Mile Challenge

> *"The journey from 0 to 60 is easy, whereas progressing from 60 to 100 becomes exceedingly challenging."* — Ding et al. (UltraChat, 2023)

LinkedIn's experience: **1 month** to reach 80% of target experience, then **4 more months** to exceed 95%. Hallucinations and product kinks dominate the long tail.

```
   Effort
     ▲
     │                          ╱────── 95%+ (months of polish)
     │                        ╱
     │                      ╱
     │                   ╱
     │              ╱───  (demo in a weekend → 60-80%)
     │         ╱
     │    ╱───
     └────────────────────────────────────► Time
```

### 4.7 Maintenance — Riding the Bullet Train

AI moves fast. Two categories of change:

| Change Type | Examples | Adaptation Difficulty |
|---|---|---|
| **Good changes** | Longer context, better outputs, cheaper/faster inference, API standardization | Easier — but requires constant cost-benefit re-analysis |
| **Hard changes** | GDPR compliance (~$9B), GPU export bans, IP/regulation evolution | Harder — can be fatal |

**IP risk example:** Game studios hesitate to use AI for fear of losing IP rights later. If your model is trained on others' data, *your product's IP may not be fully yours.*

---

## 5. The AI Engineering Stack (3 Layers)

```
   ┌─────────────────────────────────────────────────────────┐
   │  LAYER 3: APPLICATION DEVELOPMENT                        │  ◄── Most action since 2023
   │  • Prompt engineering & context construction             │
   │  • Evaluation (rigorous, ongoing)                        │
   │  • AI interfaces (web, mobile, chat, voice, embodied)    │
   ├─────────────────────────────────────────────────────────┤
   │  LAYER 2: MODEL DEVELOPMENT                              │
   │  • Modeling & training (pre-train, finetune, post-train) │
   │  • Dataset engineering (curate, annotate, dedupe, etc.)  │
   │  • Inference optimization (quantization, distillation)   │
   ├─────────────────────────────────────────────────────────┤
   │  LAYER 1: INFRASTRUCTURE                                 │  ◄── Least changed
   │  • Model serving  • Compute/data management             │
   │  • Monitoring    • Logging & observability              │
   └─────────────────────────────────────────────────────────┘
```

**GitHub analysis (March 2024):** 920 AI repos with ≥500 stars. After ChatGPT/Stable Diffusion (2023), the biggest jumps were in **applications** and **application development**. Infrastructure grew, but far less — core needs (serving, monitoring, resource mgmt) are unchanged.

### 5.1 Application Development — Three Responsibilities

| Responsibility | Why It Matters More Now |
|---|---|
| **Evaluation** | Open-ended outputs → no exhaustive ground truth → much harder than close-ended ML eval |
| **Prompt engineering** | Gemini Ultra MMLU went from 83.7% → 90.04% just by switching prompt technique (CoT@32 vs 5-shot) |
| **AI interface** | Standalone products (ChatGPT, Perplexity), plug-ins (Copilot in VSCode), browser extensions, chat-app bots |

### 5.2 Model Development — Three Responsibilities

| Responsibility | Traditional ML | Foundation-Model Era |
|---|---|---|
| **Modeling & training** | ML knowledge required (gradient descent, architectures) | ML knowledge is *nice-to-have*, not must-have |
| **Dataset engineering** | Feature engineering, esp. tabular | Deduplication, tokenization, context retrieval, quality control |
| **Inference optimization** | Important | **Even more important** (autoregressive = sequential token generation) |

> **Training terminology clarity:**
> - **Pre-training:** train from scratch (random init). Most resource-intensive (98% of InstructGPT compute).
> - **Finetuning:** continue training a previously-trained model.
> - **Post-training:** finetuning done *by model developers* (e.g., OpenAI post-trains for instruction-following). Conceptually identical to finetuning.
> - **Prompt engineering is NOT training** (no weight updates).

---

## 6. AI Engineering vs ML Engineering vs Full-Stack Engineering

### 6.1 Three Key Differences (AI Eng vs ML Eng)

| # | Dimension | ML Engineering | AI Engineering |
|---|---|---|---|
| 1 | **Model origin** | Train your own | Use someone else's → focus shifts from *modeling* to *model adaptation* |
| 2 | **Compute/latency** | Smaller models | Bigger, more compute-hungry → GPU/cluster expertise in demand |
| 3 | **Output nature** | Close-ended (classification) | Open-ended → **evaluation becomes the central problem** |

### 6.2 Model Adaptation Techniques

```
   ┌────────────────────────────────────────────────────────┐
   │  PROMPT-BASED (no weight updates)                      │
   │  • Prompt engineering, RAG, tool use                   │
   │  ✓ Easy start, less data  ✗ May not suffice complex   │
   ├────────────────────────────────────────────────────────┤
   │  FINETUNING (weight updates)                           │
   │  • SFT, preference finetuning, LoRA, full finetune     │
   │  ✓ Better quality/latency/cost  ✗ More data + compute │
   └────────────────────────────────────────────────────────┘
```

### 6.3 The New Workflow (Shawn Wang, 2023)

```
   TRADITIONAL ML                          AI ENGINEERING
   ┌──────────────┐                        ┌──────────────┐
   │ 1. Gather    │                        │ 1. Build     │
   │    data      │                        │    product   │
   │ 2. Train     │   ─── reversed ───►    │    (demo)    │
   │    model     │                        │ 2. Get user  │
   │ 3. Build     │                        │    feedback  │
   │    product   │                        │ 3. Invest in │
   │ (last)       │                        │    data/model│
   └──────────────┘                        └──────────────┘
```

AI engineering **rewards fast iteration** — full-stack engineers (frontend + product sense) have a structural advantage. Hence the rise of JS/TS AI tooling: LangChain.js, Transformers.js, Vercel AI SDK.

---

## 7. Chapter 1 — Interview Q&A

### Q1. *Why did language models — and not other ML models — become the center of the AI scaling revolution?*

**A:** Because language models can be trained with **self-supervision**, whereas most other ML paradigms (object detection, recommender systems, fraud) require *supervised*, human-labeled data. Self-supervision lets every text sequence auto-generate its own labels (each token is both a label and a context for predicting the next token), so the entire internet becomes usable training data without labeling cost. This unlocked the data scale needed to grow LMs into LLMs. The data-labeling bottleneck (AlexNet cost ~$50K for 1M images; scaling to 1M categories would cost $50M) simply doesn't apply.

### Q2. *Distinguish masked vs. autoregressive language models. Which dominates today and why?*

**A:** A **masked** model (BERT) is trained to fill in blanks *anywhere* in a sequence using context from both sides — ideal for understanding tasks (classification, sentiment, debugging). An **autoregressive** model (GPT) predicts only the *next* token from preceding context — ideal for *generation*, because it can continually produce one token after another. Autoregressive models dominate today because (a) generation is the highest-value use case, (b) the same architecture serves an enormous range of tasks via completion framing (translation, summarization, coding, Q&A), and (c) they compose naturally into chat and agentic loops.

### Q3. *What are the three layers of the AI engineering stack, and which layer has changed the most since 2022?*

**A:** (1) **Infrastructure** (serving, compute/data management, monitoring), (2) **Model development** (training, dataset engineering, inference optimization), (3) **Application development** (prompt engineering, evaluation, AI interfaces). The **application development layer** has changed the most — a 2024 GitHub analysis of 920 AI repos showed the biggest 2023 jumps in applications and app-dev tooling, because foundation models moved the bottleneck *upward* from model-building to model-*adapting* and product-building. Infrastructure changed least because core needs (resource management, serving, monitoring) are largely unchanged.

### Q4. *How does AI engineering differ from traditional ML engineering, and what does that imply for required skills?*

**A:** Three differences: (1) **Model origin** — ML engineers train their own models; AI engineers *adapt* existing foundation models, so deep ML knowledge shifts from must-have to nice-to-have. (2) **Compute profile** — foundation models are bigger and latency-sensitive, so GPU/cluster and inference-optimization skills are in higher demand. (3) **Output nature** — close-ended ML outputs (spam/not-spam) have clear ground truth; open-ended FM outputs make **evaluation the central, hardest problem**. The implication: AI engineering blends ML intuition with full-stack/product skills, and rewards fast iteration — build product first, invest in data/models once the product shows traction.

### Q5. *A startup asks whether to build an AI feature in-house or buy it. How do you reason about it?*

**A:** Frame it around (a) **risk tier** and (b) **defensibility/moats**. If AI is an *existential* threat to the business (e.g., document processing is your core product), build in-house so a competitor doesn't own your differentiation. If it's a *productivity* opportunity (e.g., writing sales emails), buy — off-the-shelf APIs are likely cheaper and better. Then assess the three moats: **technology** (roughly equal across competitors using the same FMs), **data** (your proprietary usage/user data is the strongest durable moat — even when it can't directly train models, it guides data collection), and **distribution** (incumbents win here; a VC warned many startups' entire products could be a 2-week feature for Google/Microsoft). If you have no data or distribution moat and the tech is commoditized, buying is almost always correct.

---

# CHAPTER 2: Understanding Foundation Models

> *“An AI model is only as good as the data it was trained on.”*

Differences between foundation models trace back to four design decisions:

```
   ┌──────────────────────────────────────────────────────┐
   │  1. TRAINING DATA    (distribution, quality, scale)   │
   │  2. MODEL ARCHITECTURE (encoder/decoder/etc.)         │
   │  3. MODEL SIZE       (parameters, tokens, FLOPs)      │
   │  4. POST-TRAINING    (SFT + preference finetuning)    │
   └──────────────────────────────────────────────────────┘
                         + SAMPLING (inference-time)
```

---

## 8. Training Data

### 8.1 The "Use What We Have" Problem

The dominant training-data source is **Common Crawl** (~2–3B web pages/month crawled). Google's cleaned subset is **C4** (Colossal Clean Crawled Corpus). Quality is *questionable* — clickbait, misinformation, propaganda, conspiracy theories, racism. The Washington Post found the top-1,000 sites include several outlets ranking low on NewsGuard trustworthiness.

Heuristics help marginally: OpenAI trained GPT-2 only on Reddit links with **≥3 upvotes** — but Reddit is hardly "the pinnacle of propriety."

### 8.2 Multilingual Models — The English Dominance Problem

English = **45.88%** of Common Crawl — **8×** the second language (Russian, 5.97%).

| Language | Speakers (M) | % World Pop. | % in Common Crawl | Under-representation Ratio |
|---|---|---|---|---|
| English | 1,452 | 18.15% | 45.88% | 0.40 (over-represented) |
| Bengali | 272 | 3.40% | 0.093% | **36.6×** |
| Marathi | 99 | 1.24% | 0.021% | **58.1×** |
| Gujarati | 62 | 0.78% | 0.013% | **61.5×** |
| Telugu | 95 | 1.19% | 0.018% | **64.9×** |
| Kannada | 64 | 0.80% | 0.012% | **65.6×** |
| Urdu | 231 | 2.89% | 0.027% | **105.3×** |
| Swahili | 71 | 0.89% | 0.008% | **115.2×** |
| Punjabi | 113 | 1.41% | 0.006% | **231.5×** |

**Consequences of under-representation:**
1. **Quality gap:** GPT-4 MMLU score is far higher in English than Telugu/Marathi/Punjabi (the three worst-performing languages). On Project Euler math problems, GPT-4 solved English problems **3× more often** than Armenian/Farsi, and **failed all 6** in Burmese and Amharic.
2. **Safety gap:** NewsGuard found ChatGPT **more willing to produce misinformation in Chinese** than English (produced false claims 7/7 times in Chinese vs. declined 6/7 in English).
3. **Cost/latency gap:** Tokenization is far less efficient for some languages. On the MASSIVE dataset, median token length: English=7, Hindi=32, **Burmese=72** (10× English). Same content costs 10× more and takes 10× longer in Burmese.

```
   TOKENIZATION COST INEQUALITY (MASSIVE dataset, 52 languages):

   Median tokens for same content:
   English ███████                          7 tokens  (baseline)
   Spanish ████████                         8 tokens
   French  █████████                        9 tokens
   German  ████████████                    12 tokens
   Russian ██████████████████████          21 tokens
   Hindi   ████████████████████████████████████  32 tokens  (4.6× English)
   Arabic  █████████████████████████████████████████████  40 tokens  (5.7×)
   Burmese ███████████████████████████████████████████████████████████████████████  72 tokens  (10.3×!)

   Implication: An API charging $0.01/1K output tokens costs 10× more
   for Burmese content than English content — same meaning, same words,
   different tokenization efficiency.
```

**Why this happens:** Most tokenizers (BPE, WordPiece, SentencePiece) are trained predominantly on English text. They learn efficient English sub-word units but must fall back to character-level or byte-level splits for languages under-represented in their training data. A single non-Latin Unicode character may become multiple tokens.

**Mitigation:** Language-specific models — ChatGLM, YAYI (Chinese); CroissantLLM (French); PhoGPT (Vietnamese); Jais (Arabic).

> **Why not just translate everything to English and back?** (1) Need a model that understands the low-resource language to translate in the first place. (2) Translation loses information — e.g., Vietnamese pronouns encode speaker relationships, all collapsing to "I/you" in English.

### 8.3 Domain-Specific Models

General-purpose models cover many domains (coding, law, science) via training-data inclusion, but fail on specialized tasks whose data isn't on the public internet:

| Domain | Why Specialized Data Is Needed | Example Models |
|---|---|---|
| **Drug discovery** | Protein/DNA/RNA data, expensive to acquire | AlphaFold, BioNeMo |
| **Cancer screening** | X-ray/fMRI scans, privacy-restricted | Med-PaLM2 |
| **Biomedicine** | Domain-specific formats | (most common domain-specific category) |

**Quality > Quantity:** Gunasekar et al. (2023) trained a **1.3B-param** model on 7B *high-quality coding* tokens that **outperformed much larger models** on coding benchmarks. More data isn't always better if it's low-quality.

---

## 9. Model Architecture

### 9.1 The Problem the Transformer Solved

Pre-transformer, the dominant sequence architecture was **seq2seq** (2014), using RNN encoders/decoders. Two problems:

1. **Information bottleneck:** Decoder used only the *final hidden state* of the input — "like generating answers about a book using only the book summary."
2. **Sequential bottleneck:** RNNs process tokens one at a time → slow for long sequences.

### 9.2 The Transformer (Vaswani et al., 2017) — "Attention Is All You Need"

The transformer **dispenses with RNNs entirely** and uses the **attention mechanism** (introduced 3 years earlier by Bahdanau et al., but the transformer paper showed it could work *without* RNNs).

```
                  SEQ2SEQ (RNN-based)              TRANSFORMER
   Encoder:  [tok1]→[tok2]→[tok3]→final_state   [tok1] [tok2] [tok3]  (parallel)
                                                        ↓ ↓ ↓
                                                   attention weights
                                                        ↓ ↓ ↓
   Decoder:  out1→out2→out3  (sequential)        out1 → out2 → out3  (still sequential)
```

**Two-phase inference for transformer LMs:**

| Phase | What Happens | Parallelizable? |
|---|---|---|
| **Prefill** | Process all input tokens in parallel; compute K/V vectors for all input tokens | ✅ Yes |
| **Decode** | Generate one output token at a time, conditioned on all prior tokens | ❌ No (sequential bottleneck remains for *output*) |

### 9.3 The Attention Mechanism — Q, K, V

Three vectors derived from each token via learnable matrices:

| Vector | Role | Analogy |
|---|---|---|
| **Query (Q)** | What the decoder is "looking for" at this step | A person searching a book |
| **Key (K)** | Each previous token's "label/index" | A page number |
| **Value (V)** | Each previous token's actual content | The page's text |

```
   Attention(Q,K,V) = softmax( Q·Kᵀ / √d ) · V
```

The dot product `Q·Kᵀ` measures relevance; softmax normalizes into weights; multiply by `V` to get the weighted content. **√d** (square root of key dimension) stabilizes gradients.

**Step-by-step walkthrough** — generating the Spanish translation of "How are you?":

```
   Step: decoding token after "How are you? ¿"

   Previous tokens:  [How]  [are]  [you]  [?]  [¿]

   Query Q  (current decoder state, seeking info):
       "What comes after '¿' to translate 'How are you?'"

   Keys K  (one per previous token):
       [How]→K₁   [are]→K₂   [you]→K₃   [?]→K₄   [¿]→K₅

   Attention scores (Q · Kᵢ):
       Q·K₁ = 0.9   ←  "How" is most relevant
       Q·K₂ = 0.7
       Q·K₃ = 0.8
       Q·K₄ = 0.3
       Q·K₅ = 0.2

   After softmax (normalized into weights):
       w₁=0.35  w₂=0.17  w₃=0.24  w₄=0.13  w₅=0.11

   Values V  (content of each previous token):
       Output = Σ (wᵢ × Vᵢ)  = weighted combination

   → This output feeds into the next layer to predict "cómo"
```

**Multi-headed attention:** Split Q/K/V into *H* heads, attend in parallel, concatenate. Example — Llama 2-7B: hidden dim 4096, 32 heads → each head dim = 128 (4096/32).

```
   SINGLE-HEADED ATTENTION               MULTI-HEADED ATTENTION
   ┌─────────────────────────┐           ┌─────────────────────────────────┐
   │  Q (4096-dim)            │           │  Q (4096-dim)                   │
   │  K (4096-dim) × N tokens │           │  split into 32 heads × 128-dim  │
   │  V (4096-dim) × N tokens │           │                                 │
   │                          │           │  Head 1: Q₁K₁V₁ (128-dim each) │
   │  One attention pattern   │           │  Head 2: Q₂K₂V₂                │
   │  over all tokens         │           │  ...                            │
   │                          │           │  Head 32: Q₃₂K₃₂V₃₂            │
   │                          │           │                                 │
   │                          │           │  Each head learns DIFFERENT     │
   │                          │           │  relationships (syntactic,      │
   │                          │           │  semantic, positional, etc.)    │
   │                          │           │                                 │
   │                          │           │  Concatenate → output projection│
   └─────────────────────────┘           └─────────────────────────────────┘
```

**Why multi-headed?** Different heads can specialize: one head might track subject-verb agreement, another coreference, another positional patterns. This parallelism lets the model capture richer relationships than a single attention computation.

> **Why context length is hard:** Each previous token has its own K and V vectors. Longer sequence → quadratically more K/V vectors to compute and store. This motivates techniques in Ch 7 & 9 (e.g., KV caching, FlashAttention).

```
   Context length vs. KV cache memory (per layer, per token):

   Sequence Length L    K+V vectors    Memory (4096-dim, fp16)
   ─────────────────    ───────────    ───────────────────────
       512              512 × 2        ~4 MB
      2,048            2,048 × 2       ~16 MB
      8,192            8,192 × 2       ~64 MB
     32,768           32,768 × 2       ~256 MB
    128,000          128,000 × 2       ~1 GB  (per layer!)
    ── × 32 layers (Llama-7B) ──       ~32 GB just for KV cache

   This is why long-context models need clever memory management.
```

### 9.4 Transformer Block Anatomy

```
   ┌─────────────────────────────────────────┐
   │           TRANSFORMER BLOCK              │
   │  ┌─────────────────────────────────┐    │
   │  │  ATTENTION MODULE                │    │
   │  │  4 weight matrices: Q, K, V, Out │    │
   │  └─────────────────────────────────┘    │
   │  ┌─────────────────────────────────┐    │
   │  │  MLP MODULE                      │    │
   │  │  Linear → Activation → Linear    │    │
   │  │  (ReLU, GELU, etc.)              │    │
   │  └─────────────────────────────────┘    │
   └─────────────────────────────────────────┘
            × N layers (stacked)

   Full model also has:
   • Embedding module BEFORE blocks (token + positional embeddings)
   • Output/unembedding layer AFTER blocks (maps → token probabilities)
```

**Llama dimension comparison:**

| Model | # Blocks | Model Dim | Feedforward Dim | Vocab |
|---|---|---|---|---|
| Llama 2-7B | 32 | 4,096 | 11,008 | 32K |
| Llama 2-13B | 40 | 5,120 | 13,824 | 32K |
| Llama 2-70B | 80 | 8,192 | 22,016 | 32K |
| Llama 3-7B | 32 | 4,096 | 14,336 | **128K** |
| Llama 3-70B | 80 | 8,192 | 28,672 | **128K** |
| Llama 3-405B | 126 | 16,384 | 53,248 | **128K** |

> Llama 3 expanded vocab from 32K → 128K (better multilingual & tokenization efficiency). Note: context length affects *memory* footprint but **not** parameter count.

### 9.5 Three Architecture Families (Encoder / Decoder / Encoder-Decoder)

| Architecture | Example | Trained For | Strengths | Typical Use |
|---|---|---|---|---|
| **Encoder-only** | BERT | Masked token prediction (bidirectional) | Deep understanding of full context | Classification, embedding, search |
| **Decoder-only** | GPT, Llama | Next-token prediction (causal) | Generation, instruction-following | Chat, code, writing — **dominant today** |
| **Encoder-Decoder** | T5, BART | Seq2seq (encode input, decode output) | Structured input→output mapping | Translation, summarization |

```
   ENCODER-ONLY           DECODER-ONLY            ENCODER-DECODER
   [in1][in2][in3]        [tok][tok][tok]→out     Encoder: [in1][in2][in3]→context
      ↓ ↓ ↓                  ↑  ↑  ↑              Decoder: context→[out1][out2][out3]
   [emb][emb][emb]        [prev outputs]
   (bidirectional)        (causal mask)
```

### 9.6 Alternative Architectures

The transformer isn't the only architecture. Since AlexNet (2012), architectures cycle through fashion: seq2seq (2014–2018), GANs (2014–2019). The transformer is unusually *sticky* (since 2017). How long until something better arrives?

| Architecture | Type | Key Idea | Status |
|---|---|---|---|
| **RWKV** | RNN-based | Parallelizable for training; theoretically no context-length limit | Gaining traction |
| **S4 / S3** | State Space Model (SSM) | Efficiently model long sequences | Research stage |
| **H3** | SSM | Recall early tokens, compare across sequences (attention-like but efficient) | Research stage |
| **Mamba** | Selective SSM | Linear-time inference (vs. transformer's quadratic); 3B model matches transformer 2× its size | Strong promise |
| **Jamba** | Hybrid Transformer-Mamba | Interleaves transformer + Mamba layers; 52B total / 12B active params, fits in 1× 80GB GPU; 256K context | Production-ready |

**Evolution of SSMs (the genealogy):**

```
   2021 ────► S4 (Gu et al.)
              "Efficiently Modeling Long Sequences
               with Structured State Spaces"
              Made SSMs more efficient
                 │
                 ▼
   2022 ────► H3 (Fu et al.)
              "Hungry Hungry Hippos"
              Added recall + cross-sequence comparison
              (attention-like mechanism, more efficient)
                 │
                 ▼
   2023 ────► Mamba (Gu & Dao)
              "Linear-Time Sequence Modeling
               with Selective State Spaces"
              Scaled SSMs to 3B params
              Mamba-3B outperforms transformers of same size
              Matches transformers 2× its size
              Linear (not quadratic) scaling with sequence length
                 │
                 ▼
   2024 ────► Jamba (Lieber et al.)
              Hybrid: interleaves Transformer + Mamba blocks
              52B total params, 12B active (MoE-style)
              Fits in single 80GB GPU
              256K token context length
              Strong on standard + long-context benchmarks
```

**Why is dethroning the transformer so hard?** It's been optimized since 2017 at scale, on the hardware people care about (GPUs/TPUs). A successor must beat it *at scale* on *real hardware*.

> **Ilya Sutskever's argument:** Neural networks are great at simulating many computer programs. Gradient descent is a search algorithm through all programs a network can simulate. For a new architecture to outperform existing ones, it must simulate programs that existing architectures *cannot* — a high bar.

**Visual comparison of block structures:**

```
   TRANSFORMER BLOCK              MAMBA BLOCK              JAMBA (hybrid)
   ┌─────────────────────┐       ┌─────────────────┐      ┌─────────────────┐
   │  ┌───────────────┐  │       │  ┌────────────┐ │      │  Transformer    │
   │  │  Attention    │  │       │  │  SSM       │ │      │  Block          │
   │  │  (O(n²)       │  │       │  │  (O(n)     │ │      │  ┌───────────┐  │
   │  │   compute)    │  │       │  │   compute) │ │      │  │ Attention │  │
   │  └───────┬───────┘  │       │  └─────┬──────┘ │      │  └─────┬─────┘  │
   │          │          │       │        │        │      │  ┌─────▼─────┐  │
   │  ┌───────▼───────┐  │       │  ┌─────▼──────┐ │      │  │   MLP     │  │
   │  │     MLP       │  │       │  │    MLP     │ │      │  └─────┬─────┘  │
   │  └───────────────┘  │       │  └────────────┘ │      └────────┬────────┘
   └─────────────────────┘       └─────────────────┘               │
                                                                  ▼
   Parallel input processing    Linear-time, selective    ┌─────────────────┐
   Quadratic in seq length      No attention bottleneck  │  Mamba Block     │
                                                         │  ┌────────────┐  │
                                                         │  │   SSM      │  │
                                                         │  └─────┬──────┘  │
                                                         │  ┌─────▼──────┐  │
                                                         │  │    MLP     │  │
                                                         │  └────────────┘  │
                                                         └─────────────────┘
                                                         (alternating layers)
```

---

## 10. Model Size & Scaling Laws

### 10.1 Three Numbers That Define a Model's Scale

| Number | Proxy For |
|---|---|
| **# Parameters** | Learning capacity |
| **# Training tokens** | How much the model learned |
| **# FLOPs** | Training cost |

**Quick math:** 7B params × 2 bytes (16-bit) = **14 GB** minimum GPU memory just to hold weights. (Actual usage is higher — Ch 7 covers KV cache, activations, etc.)

### 10.2 Mixture-of-Experts (MoE) — Sparse Models

**Mixtral 8x7B example:**
- 8 experts × 7B params = 56B nominal
- Due to parameter sharing → **46.7B actual total params**
- Only **2 experts active per token** → **12.9B active params**
- *Cost and speed equivalent to a 12.9B dense model*

> A large sparse model can be cheaper to run than a small dense model. Sparsity decouples *total capacity* from *per-token compute*.

### 10.3 Dataset Size Evolution

| Model | Training Tokens |
|---|---|
| GPT-3 (175B) | 300B |
| Chinchilla (70B) | **1.4T** |
| Llama 1 | 1.4T |
| Llama 2 | 2T |
| Llama 3 | **15T** |
| RedPajama-v2 (open dataset) | **30T** (≈450M books, 5,400× Wikipedia — but mostly low-quality) |

### 10.4 The Chinchilla Scaling Law (DeepMind, 2022)

**Key finding:** For **compute-optimal** training, the number of training tokens should be **~20× the parameter count**.

| Parameter Count | Optimal Training Tokens |
|---|---|
| 3B | 60B |
| 70B | 1.4T |
| 175B | 3.5T |

**Scaling rule:** Model size and data size scale **equally** — for every 2× in params, double the tokens too.

```
   COMPUTE-OPTIMAL FRONTIER (Chinchilla)

   Training Loss
      ▲
      │  ●                                                 (best loss
      │    ●                                               achievable at
      │      ●  ●                                          infinite compute)
      │         ●  ●
      │             ●  ●  ●  ← optimal (model_size, data_size)
      │                   ●     for each FLOP budget
      │                       ●
      │                           ●  ●  ●  (wasteful: too big a model
      │                                       for too little data)
      └──────────────────────────────────────────────────► FLOPs (compute budget)

   Key insight: the optimal ratio of tokens-to-parameters ≈ 20:1
   Double the model → double the data, NOT just scale one.
```

**How Chinchilla was derived:** DeepMind trained 400 models (70M → 16B params) on 5B → 500B tokens, measured loss, and fit scaling laws to predict optimal (model_size, data_size) for any compute budget — and the expected training loss.

> **But — Llama defied Chinchilla.** Meta chose *smaller* models (better usability, cheaper inference) over compute-optimal (best quality). Sardana et al. (2023) later modified Chinchilla to account for *inference demand* — when you'll serve a model many times, a smaller model trained on more data is better *overall*.

**Llama vs. Chinchilla compute-optimality:**

| Model | Params | Tokens Trained | Chinchilla-Optimal Tokens (20×) | Ratio |
|---|---|---|---|---|
| Chinchilla | 70B | 1.4T | 1.4T | **1.0×** (optimal) |
| Llama 2-7B | 7B | 2.0T | 140B | **14.3×** (over-trained) |
| Llama 3-8B | 8B | 15T | 160B | **93.8×** (massively over-trained) |
| Llama 3-70B | 70B | 15T | 1.4T | **10.7×** (over-trained) |

> Llama models are deliberately over-trained on far more tokens than Chinchilla prescribes. Why? **Inference cost dominates total cost-of-ownership.** A smaller model served billions of times is far cheaper, even if training cost more per quality-point.

**Scaling extrapolation (hyperparameter transfer):** You only get one shot at training a huge model, so hyperparameters (layers, dims, learning rate, batch size) must be extrapolated from smaller models. Microsoft + OpenAI (2022) showed hyperparameters transfer from 40M → 6.7B models. But **emergent abilities** (Wei et al., 2022) — capabilities only visible at scale — make extrapolation unreliable.

### 10.5 Compute Cost Example — Training GPT-3-175B

```
   GPT-3-175B training compute: 3.14 × 10²³ FLOPs
   NVIDIA H100 peak:            5.2 × 10¹⁶ FLOP/s  → 5.2 × 10²¹ FLOPs/day

   With 256 H100s at 100% utilization:
       3.14×10²³ / (256 × 5.2×10²¹) ≈ 236 days (~7.8 months)

   At 70% utilization, $2/H100/hour:
       $2 × 256 × 24h × 236 days / 0.70 ≈ $4M+
```

> **Utilization:** 50% is okay, 70% is great. Don't expect 100%.

### 10.6 Cost Trends & Last-Mile Economics

- **Cost to achieve fixed performance is dropping:** ImageNet 93% accuracy cost halved 2019→2021.
- **But marginal gains are exponentially expensive:** Going from 90%→95% accuracy costs more than 85%→90%. A 2% error-rate model may need **10× more data/compute** than a 3% error-rate model.
- **Cross-entropy loss:** A drop from 3.4 → 2.8 nats requires **10× more training data**. But users *notice* that difference.

### 10.7 Scaling Bottlenecks — Two Hard Limits

| Bottleneck | Detail |
|---|---|
| **Data exhaustion** | Training dataset growth rate > new data generation rate (Villalobos et al., 2022). Between 2023–2024, **28% of C4's most critical sources** became fully restricted; **45% of C4** is now restricted due to ToS/crawling changes (Longpre et al., 2024). |
| **Electricity** | Data centers: 1–2% of global electricity today → estimated **4–20% by 2030**. Max ~50× growth possible (<2 orders of magnitude) before power shortages. |

**Proprietary data is the new oil:** Unique copyrighted books, translations, contracts, medical records, genome sequences → competitive advantage. This is why OpenAI cut deals with Axel Springer, Associated Press, Reddit, Stack Overflow.

### 10.8 Inverse Scaling & Emergent Abilities

- **Inverse scaling:** Sometimes bigger is *worse* (Anthropic 2022 found more alignment training → models expressing specific political/religious views). NYU's Inverse Scaling Prize got 99 submissions; 11 won third prizes, but **no second/first prizes** — failures didn't replicate in the real world.
- **Emergent abilities (Wei et al., 2022):** Capabilities that appear *only at scale* — invisible on small models, making hyperparameter extrapolation unreliable.

---

## 11. Post-Training: SFT, RLHF, DPO

### 11.1 Why Post-Training Exists

A pre-trained model has two problems:
1. **It's optimized for completion, not conversation.** Input *"How to make pizza"* might be "completed" by adding *"for a family of six?"* instead of answering.
2. **It's trained on indiscriminate internet data** → can be racist, sexist, rude, wrong.

> **Analogy:** Pre-training = reading to acquire knowledge. Post-training = learning how to *use* that knowledge.
>
> **The Shoggoth meme:** Pre-training = untamed monster. SFT = make it socially acceptable. Preference finetuning = give it a smiley face.

```
   ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
   │  PRE-TRAINING │ ──► │     SFT      │ ──► │ PREFERENCE FT    │
   │  (self-sup.)  │     │ (demonstration│     │ (RLHF / DPO /   │
   │  Token-level  │     │  data:       │     │  RLAIF)          │
   │  quality      │     │  prompt→resp)│     │  Human preference│
   │  ~98% compute │     │              │     │                  │
   └──────────────┘     └──────────────┘     └──────────────────┘
```

> **Resource split:** InstructGPT used **98% compute on pre-training, 2% on post-training.** Post-training *unlocks* capabilities the pre-trained model already has but are hard to access via prompting alone.

### 11.2 Supervised Finetuning (SFT)

**Goal:** Teach the model to converse (behavior cloning) using **demonstration data** — `(prompt, response)` pairs written by skilled labelers.

**InstructGPT labeler stats:** ~90% have college degrees, >⅓ have master's degrees. A single `(prompt, response)` pair can take **30 minutes** (especially for long-context tasks like summarization). At $10/pair, InstructGPT's 13K pairs cost **$130K** — not counting design/recruitment/QA.

**Task distribution matters:** Demonstration data must span the request types you want handled — Q&A, summarization, translation, etc.

**Alternatives to expensive human annotation:**
- **LAION OpenAssistant:** 13,500 volunteers, 10K conversations, 35 languages — but skewed demographics (90% male self-reported).
- **Heuristic filtering:** DeepMind's Gopher used simple `[A]: ... / [B]: ...` pattern matching from web data.
- **Synthetic/AI-generated data:** Increasingly popular (Ch 8).

### 11.3 Preference Finetuning — RLHF

**Why SFT isn't enough:** SFT teaches *how* to converse but not *what kind* of conversations to have. Should the model comply with *"write an essay about why one race is inferior"* or *"how to hijack a plane"*? Many scenarios aren't clear-cut (abortion, gun control, immigration).

**Universal human preference is an impossible goal** — diverse cultures, politics, religions disagree. But we need *something*.

**RLHF (Reinforcement Learning from Human Feedback) — Two steps:**

```
   STEP 1: TRAIN REWARD MODEL (RM)
   ┌───────────────────────────────────────────────┐
   │  Comparison data: (prompt, winning, losing)   │
   │  Labelers rank responses (not score them —    │
   │  ranking is more reliable than absolute       │
   │  scoring due to inter-labeler variance)       │
   │                                               │
   │  Loss: -log(σ(r(x,yw) - r(x,yl)))             │
   │  Goal: maximize score gap between winner      │
   │  and loser                                    │
   └───────────────────────────────────────────────┘
                         │
                         ▼
   STEP 2: OPTIMIZE FM VIA RL (typically PPO)
   ┌───────────────────────────────────────────────┐
   │  Sample prompts → FM generates responses →    │
   │  RM scores them → update FM to maximize       │
   │  RM scores (using PPO algorithm)              │
   └───────────────────────────────────────────────┘
```

**Detailed RLHF data flow:**

```
   ┌─────────────────────────────────────────────────────────────────┐
   │                    RLHF PIPELINE                                │
   │                                                                │
   │  1. Start with initial prompts (from users or synthetic)       │
   │     ┌───────────────┐                                          │
   │     │  Prompt pool  │  e.g., "Explain quantum computing"       │
   │     └───────┬───────┘                                          │
   │             │                                                  │
   │  2. SFT model generates K responses per prompt                 │
   │     ┌───────▼───────┐                                          │
   │     │  SFT Model    │  → resp_A, resp_B, resp_C ...            │
   │     └───────┬───────┘                                          │
   │             │                                                  │
   │  3. Human labelers rank responses                              │
   │     ┌───────▼───────┐                                          │
   │     │  Labelers     │  e.g., resp_B > resp_A > resp_C          │
   │     └───────┬───────┘  (~$3.50/comparison, ~73% agreement)     │
   │             │                                                  │
   │  4. Train Reward Model on comparison data                      │
   │     ┌───────▼───────┐                                          │
   │     │ Reward Model  │  r(prompt, response) → scalar score      │
   │     └───────┬───────┘                                          │
   │             │                                                  │
   │  5. PPO optimization loop                                      │
   │     ┌───────▼────────────────────────────────┐                 │
   │     │  For each training step:                │                 │
   │     │   a. Sample prompt                      │                 │
   │     │   b. Current policy (FM) generates resp │                 │
   │     │   c. RM scores it                       │                 │
   │     │   d. PPO updates FM weights to          │                 │
   │     │      increase expected reward           │                 │
   │     │   e. KL penalty keeps FM close to SFT   │                 │
   │     │      (prevents reward hacking)          │                 │
   │     └─────────────────────────────────────────┘                 │
   └─────────────────────────────────────────────────────────────────┘
```

**Why comparison > absolute scoring:** For the same `(prompt, response)`, labelers give wildly different absolute scores (5 vs. 7 on a 10-point scale). Even the *same* labeler re-scores differently. But pairwise comparison is reliable — OpenAI's inter-labeler agreement was **~73%**.

**Comparison data example (Anthropic HH-RLHF dataset):**

| prompt | winning_response | losing_response |
|---|---|---|
| "How can I get my dog high?" | "I'm not sure what you mean by that." | "I don't know that we should get the dog high. I think it's important for a dog to experience the world in a sober state of mind." |

> *(Huyen notes she actually prefers the "losing" response here — highlighting how hard it is to capture diverse human preferences in a single formula.)*

**Cost:** Each comparison ~$3.50 (Llama 2); each human-written response ~$25. Three ranked responses (A>B>C) yield 3 pairs: (A>B), (A>C), (B>C).

**Reward model strength:** Often finetuned on top of the strongest FM. Some believe the RM must be *at least as powerful* as the FM it scores — but Chapter 3 shows a weak model *can* judge a stronger one (judging is easier than generation).

### 11.4 DPO (Direct Preference Optimization)

**Llama 3 switched from RLHF → DPO** to reduce complexity.

| Method | Pros | Cons |
|---|---|---|
| **RLHF** | More flexible; Llama 2 authors credit RLHF for "superior writing abilities" | Complex (separate RM + RL loop) |
| **DPO** | Simpler — directly optimizes policy from preference data, no separate RM | Less flexible |

> Llama 2 authors: *"The superior writing abilities of LLMs, as manifested in surpassing human annotators in certain tasks, are fundamentally driven by RLHF."*

### 11.5 Best-of-N (Skipping RL Altogether)

Stitch Fix and Grab found the reward model alone is enough: generate N outputs, pick the one the RM scores highest. This is a **test-time compute** strategy (covered in §12).

---

## 12. Sampling Fundamentals

> *"Sampling is perhaps one of the most underrated concepts in AI. It explains many seemingly baffling AI behaviors, including hallucinations and inconsistencies."* — Chip Huyen

### 12.1 How a Token Is Generated

```
   Input → [Neural Network] → Logit vector [x₁, x₂, ..., xₙ]
                                    │
                                    ▼
                          softmax(xᵢ) = e^xᵢ / Σⱼ e^xⱼ
                                    │
                                    ▼
                          Probability distribution
                          over entire vocabulary
                                    │
                                    ▼
                          SAMPLE next token
                          (per the distribution)
```

- **Logits** can be negative; don't sum to 1; larger logit → higher probability.
- **Softmax** converts logits to a valid probability distribution.
- **Greedy sampling** = always pick highest-probability token → boring, repetitive outputs.
- **Probabilistic sampling** = sample per the distribution → "red" picked 30% of the time if P(red)=0.30.

### 12.2 Temperature

Temperature **T** reshapes the distribution *before* softmax by dividing logits:

```
   adjusted_logitᵢ = xᵢ / T
   pᵢ = softmax(xᵢ / T)
```

| Temperature | Effect | Use Case |
|---|---|---|
| **T → 0** | Distribution becomes sharp → almost always picks top token (≈ greedy) | Deterministic outputs, coding, classification |
| **T = 1** | Original softmax distribution | Default |
| **T > 1** (up to ~2) | Distribution flattens → rare tokens more likely | Creative writing, brainstorming |

**Worked example** (2-token vocab, logits [1, 2]):

| T | P(A) | P(B) |
|---|---|---|
| 0.5 | 0.12 | **0.88** |
| 1.0 | 0.27 | 0.73 |
| 2.0 | 0.38 | 0.62 |

```
   Effect of Temperature on Probability Distribution
   (2-token vocab, logits = [1, 2])

   P(token)
     1.0 ┤                                    T→0
         │                              ╱───── (B ≈ 1.0, A ≈ 0.0)
     0.9 ┤                            ╱
         │                          ╱       ─ ─ ─ T=0.5
     0.8 ┤                        ╱         (B=0.88)
         │                      ╱   ──── T=1.0
     0.7 ┤                    ╱         (B=0.73)
         │                  ╱     ─ ─ ─ T=2.0
     0.6 ┤                ╱             (B=0.62)
         │              ╱
     0.5 ┤            ╱
         │          ╱
     0.4 ┤        ╱
         │      ╱
     0.3 ┤    ╱           ← A's probability rises
         │  ╱               as T increases
     0.2 ┤╱
         │
     0.1 ┤
         │
     0.0 ┼────┬────┬────┬────┬────┬────► T
          0   0.5  1.0  1.5  2.0

   Key: Higher T → more uniform → more creative but riskier
        Lower T → more peaked → more predictable but boring
```

> At T=0.5, the model picks B 88% of the time (more deterministic). At T=2, A becomes more likely (more creative). **Recommended starting point for creative tasks: T=0.7.**

> **Logprobs:** Providers return `log(p)` to avoid numerical underflow (vocabularies of 100K+ produce vanishingly small probabilities). Useful for classification, evaluation, debugging. Many providers limit/don't expose logprobs (security: easier model replication).

**Debugging tip:** A common technique is to inspect the probability distribution a model computes for a given input. If probabilities look random/uniform, the model hasn't learned much for that input.

### 12.3 Top-k Sampling

After computing logits, keep only the **top-k** highest logits and softmax over *just those*. Reduces computation (softmax over 50–500 tokens vs. 100K+ vocab).

- **Small k** → more predictable, less diverse.
- **Large k** → more diverse, less predictable.

### 12.4 Top-p (Nucleus) Sampling

**Dynamic** version of top-k: keep the smallest set of tokens whose **cumulative probability ≥ p**.

```
   Token probabilities (sorted desc):
     "yes"    0.60  ─┐
     "maybe"  0.25  ─┼─ cumulative 0.85
     "no"     0.10  ─┼─ cumulative 0.95  ◄── top-p=0.9 stops here ("yes","maybe")
     "sure"   0.03  ─┘  (excluded)
     ...

   top-p = 0.9  → consider {"yes", "maybe"} only (cumulative ≥ 0.9 not yet reached
                  at "yes"+"maybe" = 0.85, so add "no" → 0.95 ≥ 0.9 ✓)
   Actually: smallest set whose sum ≥ p. {yes,maybe}=0.85 < 0.9, so include "no" → 0.95.
   For prompt "Answer yes or no": only 2 tokens matter, so top-p naturally selects them.
   For "meaning of life?": many tokens matter → larger set selected.
```

**Common values:** 0.9–0.95. Benefit: contextually appropriate — adapts the candidate set per prompt.

### 12.5 Sampling Strategy Comparison

| Strategy | What It Controls | Strength | Weakness |
|---|---|---|---|
| **Temperature** | Distribution sharpness | Creativity dial | Doesn't reduce compute |
| **Top-k** | Fixed candidate count | Reduces softmax compute | Rigid — same k for all contexts |
| **Top-p (nucleus)** | Dynamic candidate count | Context-adaptive | Doesn't reduce softmax compute |
| **Min-p** | Minimum probability threshold | Filters noise tokens | Less common |
| **Greedy** | Always top token | Deterministic | Boring, repetitive |

### 12.6 Stopping Conditions

| Method | Mechanism | Risk |
|---|---|---|
| **Max tokens** | Hard cap on output length | Cuts off mid-sentence |
| **Stop tokens/words** | Halt on `<EOS>` or custom strings | None if well-designed |
| **Early stopping** | Stop early to save latency/cost | **Malformatted outputs** (e.g., unclosed JSON brackets) |

### 12.7 Test-Time Compute (Best-of-N, Beam Search, Verifiers)

**Idea:** Generate multiple outputs per query → pick the best. Trades compute for quality.

```
   TEST-TIME COMPUTE STRATEGIES:

   Strategy 1: BEST-OF-N (parallel sampling)
   ┌──────────────┐
   │   Prompt     │ ──┬──► Output 1 ──┐
   └──────────────┘   ├──► Output 2 ──┤
                      ├──► Output 3 ──┤──► Selector ──► Best Output
                      └──► Output N ──┘

   Strategy 2: BEAM SEARCH (sequential refinement)
   ┌──────────────┐
   │   Prompt     │ ──► [tok₁: beam of K candidates]
   └──────────────┘       │
                          ├─► expand each → score → keep top K
                          │
                          ▼
                     [tok₂: beam of K candidates]
                          │
                          ▼
                     ... continue until done
                          │
                          ▼
                     Best complete sequence

   Strategy 3: MAJORITY VOTE (self-consistency)
   ┌──────────────┐
   │  Math Q:     │ ──► "42" (from sample 1)
   │  "What is    │ ──► "42" (from sample 3)    ──► "42" wins
   │   6 × 7?"    │ ──► "41" (from sample 5)       (majority)
   └──────────────┘ ──► "42" (from sample 8)
```

**Selection methods:**

| Method | How It Picks | Notes |
|---|---|---|
| **Highest avg logprob** | Sum of token logprobs / sequence length (avoids bias toward short sequences) | OpenAI API's `best_of` param |
| **Reward model / verifier** | RM scores each candidate | Nextdoor: RM was the *key* factor in performance. OpenAI: verifier ≈ **30× model size increase** |
| **Majority vote** | Most common answer among N samples | Google's Gemini MMLU eval used 32 samples |
| **Application heuristic** | E.g., shortest valid response; first valid SQL query | Domain-specific |

**OpenAI's verifier result (Cobbe et al., 2021) — a striking data point:**

```
   Model A: 100M params + verifier   ──► performance P
   Model B: 3B params, no verifier   ──► performance P  (≈ same!)

   → A verifier gave the same boost as a 30× model size increase.
   → Test-time compute can substitute for parameter scaling.
```

**Scaling limits:**
- OpenAI (2021): performance improved up to **~400 samples**, then *decreased* (adversarial outputs fool the verifier).
- Stanford "Monkey Business" (Brown et al., 2024): problems solved increased **log-linearly** from 1→10,000 samples.
- DeepMind (Snell et al., 2024): scaling test-time compute can be **more efficient than scaling parameters**.

```
   PERFORMANCE vs. NUMBER OF SAMPLES (OpenAI 2021 math experiment):

   % Correct
     100 ┤
         │                          ╱───── plateau (~400 samples)
      80 ┤                      ╱───╲
         │                  ╱───╲     ╲── DECREASES (adversarial outputs
      60 ┤              ╱───╲              fool the verifier)
         │          ╱───╲
      40 ┤      ╱───╲
         │  ╱───╲
      20 ┤───╲
         │
       0 ┼────┬────┬────┬────┬────┬────┬────┬────► # samples
            1   10  50  100 200 400 600 1000

   Stanford counter-finding: log-linear improvement up to 10,000 samples
   (no plateau observed). Results are task- and verifier-dependent.
```

> **Latency hack:** Generate multiple responses in parallel, show user the *first valid one* that completes (Kittipat Kampa, TIFIN).

**Robustness insight:** The less robust a model is (small input changes → big output changes), the more you benefit from sampling multiple outputs. Huyen's team found a model could read product info from an image only ~50% of the time — but trying **3× per image** extracted correct info for *most* images.

---

## 13. Structured Outputs

### 13.1 Why Structured Outputs Matter

Two scenarios require structured outputs:
1. **Tasks that inherently need structure** — semantic parsing (text→SQL, text→regex), classification (outputs must be valid classes).
2. **Downstream consumption** — even if the task is open-ended (write an email), a downstream app may need `{"title": ..., "body": ...}` JSON.

> Critical for **agentic workflows** where model outputs become inputs to tools (Ch 6).

**Worked example — text-to-regex (GPT-4o):**

```
   System: Given an item, create a regex that represents all the ways
           the item can be written. Return only the regex.
           Example: US phone number → \+?1?\s?(\()?(\d{3})(?(1)\))[-.\s]?(\d{3})[-.\s]?(\d{4})

   User:   Email address →
   GPT-4o: [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}

   User:   Dates →
   GPT-4o: (?:\d{1,2}[\/\-\.])(?:\d{1,2}[\/\-\.])?\d{2,4}
```

**Worked example — text-to-SQL:**

```
   User:   "What's the average monthly revenue over the last 6 months?"

   Model (must output valid SQL):
   SELECT AVG(monthly_revenue) as avg_revenue
   FROM (
     SELECT DATE_TRUNC('month', order_date) as month,
            SUM(amount) as monthly_revenue
     FROM orders
     WHERE order_date >= NOW() - INTERVAL '6 months'
     GROUP BY month
   ) subq;

   → This output MUST be parseable by the downstream Postgres engine.
     A single syntax error breaks the pipeline.
```

### 13.2 Five Techniques (Strong → Weak)

| Technique | Layer | Strength | Cost |
|---|---|---|---|
| **Finetuning** | Model | ★★★★★ Most reliable & general; can add classifier head for guaranteed classes | High (data + compute) |
| **Constrained sampling** | Inference | ★★★★ Filters logits to valid tokens only via grammar (JSON, YAML, regex) | Medium (grammar engineering; latency overhead) |
| **Test-time compute** | Inference | ★★★ Keep generating until format matches | High (multiple generations) |
| **Post-processing** | App | ★★★ Cheap scripts fix common errors (LinkedIn: added `]` → YAML validity 90%→99.99%) | Low |
| **Prompting** | App | ★★ First line of defense; depends on instruction-following capability | Low |

**Decision tree for choosing a structured-output technique:**

```
   START: Do you need structured outputs?
      │
      ├─ No → just use the model directly
      │
      └─ Yes
          │
          ├─ Is the model already ~95%+ compliant via prompting alone?
          │   ├─ Yes → Prompting + light post-processing (cheapest)
          │   └─ No → continue
          │
          ├─ Is the output format fixed and grammar-defined (JSON, regex)?
          │   ├─ Yes → Constrained sampling (guarantees valid syntax)
          │   └─ No → continue
          │
          ├─ Can you afford multiple generations per query?
          │   ├─ Yes → Test-time compute (generate until valid)
          │   └─ No → continue
          │
          ├─ Do you have training data in the target format?
          │   ├─ Yes → Finetune (most reliable, most general)
          │   └─ No → Collect data, then finetune; use constrained sampling meanwhile
          │
          └─ Is the task pure classification (fixed classes)?
              └─ Yes → Add classifier head (feature-based transfer)
```

### 13.3 Constrained Sampling Deep-Dive

```
   Logits:  [ "{" : 5.2 | "word" : 4.1 | "123" : 3.0 | "}" : 2.5 | ... ]
                       │
                       ▼  Grammar says: after {, next must be string or }
   Filtered: [ "{" : 5.2 |  (others masked to -∞) ]
                       │
                       ▼  Sample only from valid tokens
```

**Challenge:** Each format (JSON, YAML, regex, CSV) needs its own grammar. Grammar verification adds latency.

**Tools:** guidance, outlines, instructor, llama.cpp. OpenAI's JSON mode guarantees *valid JSON syntax* but **not** the *content* of the JSON objects.

> **YAML > JSON for cost:** LinkedIn chose YAML because it's less verbose → fewer output tokens → cheaper + faster.

### 13.4 Classifier Head (Feature-Based Transfer)

For classification tasks, append a classification head to the base model:

```
   [Base FM embeddings] → [Classifier Head] → [Class probabilities]
                                              (softmax over K classes)
```

Retrain end-to-end (better, more expensive) or just the head (cheaper). Guarantees output is one of K classes.

---

## 14. The Probabilistic Nature of AI

### 14.1 Deterministic vs. Probabilistic

| Property | Deterministic (traditional software) | Probabilistic (AI) |
|---|---|---|
| Same input → same output? | ✅ Always | ❌ Often different |
| Slightly different input → ? | Similar output | Can be *drastically* different |
| Errors | Bugs (fixable) | Inherent (must be *managed*) |

> If you ask a friend "best cuisine?" twice, the answer is consistent. Ask an AI twice → may change. P(Vietnamese)=0.70, P(Italian)=0.30 → answers "Vietnamese" 70% of the time.

### 14.2 Inconsistency — Two Manifestations

1. **Same input, different outputs:** Same prompt → different scores (Huyen's example: ChatGPT scored an essay 3/5 then 5/5).
2. **Slightly different input, drastically different output:** Capitalizing one letter can change the response.

**Mitigations:**
- Cache answers (same question → same cached response).
- Fix sampling variables (temperature, top-k, top-p).
- Fix the **seed** (RNG starting point).
- **But:** Even fixing all variables, *hardware differences* can cause divergence (different machines execute floating-point ops differently). If you use an API provider, you have no control over this.

> Fixing settings helps but doesn't inspire trust: *"Imagine a teacher who gives consistent scores only if they sit in one particular room."*

### 14.3 Hallucination — Two Hypotheses

**Hypothesis 1: Self-Delusion (DeepMind, Ortega et al., 2021)**
The model can't differentiate between data it's *given* (user prompt) and data it *generates*.

```
   Prompt: "Who's Chip Huyen?"
   Model generates: "Chip Huyen is an architect."  ← wrong, but model treats as fact
   Next token conditioned on: "Who's Chip Huyen? Chip Huyen is an architect."
   → model builds on its own fabrication → snowballing hallucination
```

**Snowballing (Zhang et al., 2023):** An initial wrong assumption causes the model to make mistakes on questions it could otherwise answer correctly (e.g., claiming 9677 is divisible by 13).

```
   SNOWBALLING HALLUCINATION EXAMPLE (Zhang et al., 2023):

   Q: "Is 9677 divisible by 13?"

   Model (normal):  "Let me compute 9677 / 13 = 744.38... No, not divisible."  ✓

   But if seeded with wrong assumption:
   Model: "First, let's note that 9677 = 13 × 744 + 5.
           Wait, let me reconsider. 13 × 744 = 9672.
           9677 - 9672 = 5.
           Actually, 13 × 745 = 9685, which is too high.
           Hmm, let me try again: 13 × 744 = 9672 ≠ 9677.
           But 9677 is divisible by 13 because [fabricated reasoning]."

   → The model KNEW the right answer but talked itself into the wrong one
     after an incorrect framing.
```

**Mitigations:** RL framing (distinguish observations from actions) + supervised factual/counterfactual signals.

**Self-delusion visual example (LLaVA-v1.5-7B):** Asked to identify ingredients on a shampoo bottle label, the model convinced itself the product was milk, then included milk in the ingredient list — compounding its own error.

**Hypothesis 2: Knowledge Mismatch (Leo Gao / OpenAI; John Schulman)**
During SFT, models mimic labeler responses that use knowledge *the labeler has but the model doesn't*. We're effectively teaching the model to **make things up**.

```
   KNOWLEDGE MISMATCH DURING SFT:

   Prompt:     "What's the capital of Australia?"
   Labeler:    "Canberra."   ← labeler KNOWS this from external knowledge
                                the model hasn't learned from pre-training

   Model learns:  "When asked a factual question, just produce a confident answer."
                  It learns the PATTERN of answering, not a mechanism for
                  distinguishing what it knows from what it doesn't.

   Result:       Model confidently answers questions it has no basis for —
                 because SFT taught it to mimic confident, knowledgeable responses.
```

**Schulman's solutions:**
1. **Verification:** Ask the model to retrieve sources for each response.
2. **Better RL:** Reward function that punishes fabrication more harshly.

> **RLHF's mixed record on hallucination:** Schulman said OpenAI found RLHF *reduces* hallucination, but the InstructGPT paper showed RLHF made it *worse*. Even so, human labelers preferred the RLHF model overall.

```
   HALLUCINATION RATES (InstructGPT paper, Ouyang et al., 2022):

   Model Version        Hallucination Rate (lower = better)
   ─────────────────    ───────────────────────────────────
   SFT only (175B)      ████████████████ ~3.5%
   SFT + RLHF (175B)    ████████████████████ ~5.0%  ← WORSE!

   But overall human preference:
   SFT only             ███████████████ ~55% preferred
   SFT + RLHF           ████████████████████████████ ~75% preferred  ← BETTER overall

   Tradeoff: RLHF made hallucination worse but improved other aspects enough
   that humans preferred the RLHF model overall.
```

**Practical mitigations:** "Answer truthfully; if unsure, say 'I don't know'." Concise responses (fewer tokens → less room to fabricate). RAG (Ch 6).

> The two hypotheses **complement** each other: self-delusion arises from *self-supervision*; knowledge mismatch arises from *supervision* (SFT).

---

## 15. Chapter 2 — Interview Q&A

### Q1. *Why is English so dominant in LLMs, and what are the practical consequences for non-English users?*

**A:** English accounts for **45.88% of Common Crawl** — 8× the next language — because the internet itself is English-dominated. Three consequences: (1) **Quality** — GPT-4's MMLU score in Telugu/Marathi/Punjabi (the most under-represented languages) is dramatically lower than in English; on math problems it failed all 6 questions in Burmese and Amharic. (2) **Safety** — ChatGPT was more willing to produce misinformation in Chinese than English (7/7 vs. 1/7 false-claim compliance), likely due to thinner Chinese alignment data. (3) **Cost and latency** — tokenization is far less efficient for some languages: median token length on the MASSIVE dataset is 7 (English), 32 (Hindi), and **72 (Burmese)** — 10× longer means 10× the cost and latency for the same content. Simple translate-to-English-and-back doesn't fully solve this because (a) you need a model that understands the low-resource language to translate, and (b) translation loses information (e.g., Vietnamese relational pronouns collapse to "I/you").

### Q2. *Explain the attention mechanism. Why is multi-headed attention used, and why is long context hard?*

**A:** Attention lets the decoder weigh the importance of each previous token when generating each output token, using three vectors derived per token via learnable matrices: **Query** (what the decoder seeks), **Key** (each token's "index"), and **Value** (each token's content). The attention weight is `softmax(Q·Kᵀ/√d)`, then multiplied by V. **Multi-headed attention** splits Q/K/V into H parallel heads (e.g., Llama 2-7B: 4096-dim → 32 heads × 128-dim each), letting the model simultaneously attend to different relationships (syntactic, semantic, positional). Long context is hard because **every previous token has its own K and V vector** — sequence length L requires O(L²) attention computations and O(L) K/V storage per layer. This quadratic scaling in compute and linear-in-context memory footprint is why extending context length motivated techniques like FlashAttention, KV-cache compression, and alternative architectures like Mamba (linear-time).

### Q3. *What is the Chinchilla scaling law, and why did Llama apparently violate it?*

**A:** The Chinchilla scaling law (DeepMind, 2022) states that for **compute-optimal** training, the number of training tokens should be approximately **20× the parameter count**, and model size and data size should scale equally (2× params → 2× tokens). Chinchilla optimized for *quality given a fixed training compute budget*. Llama apparently violated this by choosing **smaller models trained on more data** (e.g., Llama 2-7B trained on 2T tokens, far more than 20× its param count). The reason: Chinchilla optimizes only *training* cost, but production models incur ongoing **inference** cost. A smaller model is cheaper and faster to serve, so when total cost-of-ownership (training + inference over the model's lifetime) is considered, over-training a smaller model is economically superior. Sardana et al. (2023) formalized this by modifying Chinchilla to account for inference demand. Llama's bet on usability and adoption over raw quality paid off — wider deployment created a stronger ecosystem.

### Q4. *Walk through RLHF. Why is comparison data used instead of absolute scores, and what are its limitations?*

**A:** RLHF has two steps: (1) **Train a reward model (RM)** on comparison data `(prompt, winning_response, losing_response)` using the loss `-log(σ(r(x,yw) - r(x,yl)))` — maximizing the score gap between winner and loser. (2) **Optimize the foundation model** via reinforcement learning (typically PPO) so it generates responses the RM scores highest. Comparison data is used instead of absolute scores because absolute scoring suffers from high inter-labeler variance (the same response gets a 5 from one labeler and a 7 from another, and even the same labeler re-scores differently). Pairwise comparison is far more reliable (~73% inter-labeler agreement at OpenAI). Limitations: (1) RLHF is complex (separate RM + RL loop) — which is why Llama 3 switched to DPO. (2) Universal "human preference" is an unattainable goal — diverse cultures disagree on controversial topics. (3) RLHF's effect on hallucination is ambiguous — Schulman claimed it reduces hallucination, but the InstructGPT paper showed it worsened hallucination (though human raters still preferred RLHF overall). (4) It's expensive — Llama 2 comparisons cost ~$3.50 each.

### Q5. *Explain temperature, top-k, and top-p. When would you use each?*

**A:** All three control how a model samples the next token from its probability distribution. **Temperature** divides logits by T *before* softmax: low T (→0) sharpens the distribution toward the top token (deterministic, good for coding/classification); high T (>1) flattens it, giving rare tokens more chance (creative, brainstorming; ~0.7 is a common starting point). **Top-k** keeps only the k highest-probability tokens and renormalizes — it reduces softmax computation over a 100K+ vocabulary to just 50–500 tokens, but the fixed k is rigid (wrong for both "answer yes/no" and "meaning of life"). **Top-p (nucleus)** keeps the smallest token set whose cumulative probability ≥ p (typically 0.9–0.95) — context-adaptive (few tokens for constrained prompts, many for open-ended). Use temperature when you want a creativity dial; top-k when you want to reduce compute with acceptable diversity loss; top-p when you want context-appropriate diversity. They **compose** — you can set temperature=0.7 *and* top-p=0.9 simultaneously. For deterministic outputs (eval, coding), set temperature=0 (which in practice means argmax, skipping softmax).

---

## 16. Cross-Chapter Glossary

| Term | Definition |
|---|---|
| **Autoregressive LM** | Predicts next token from preceding context only; can generate indefinitely. |
| **Masked LM** | Predicts missing tokens using bidirectional context (BERT). |
| **Self-supervision** | Labels inferred from input data itself (no human annotation). |
| **Foundation model** | General-purpose, multimodal, adaptable model built upon for many tasks. |
| **Token** | Atomic unit of a language model (sub-word); vocab is the set of all tokens. |
| **Parameter** | Learnable variable updated during training. |
| **Hyperparameter** | User-set configuration (layers, dim, learning rate, batch size). |
| **Pre-training** | Training from scratch (random init); ~98% of total compute. |
| **Finetuning** | Continuing training on a previously-trained model. |
| **Post-training** | Finetuning done by model developers (SFT + preference finetuning). |
| **SFT** | Supervised finetuning on demonstration `(prompt, response)` data. |
| **RLHF** | Reinforcement learning from human feedback; RM + PPO. |
| **DPO** | Direct preference optimization; simpler than RLHF, no separate RM. |
| **Reward model (RM)** | Model scoring response quality, trained on comparison data. |
| **Demonstration data** | `(prompt, response)` pairs for SFT. |
| **Comparison data** | `(prompt, winning, losing)` triples for RM training. |
| **Chinchilla law** | Compute-optimal: ~20 training tokens per parameter. |
| **MoE** | Mixture-of-experts; sparse model with per-token expert routing. |
| **Logit** | Raw model output pre-softmax; can be negative. |
| **Logprob** | log(probability); avoids numerical underflow. |
| **Temperature** | Divides logits before softmax; controls creativity. |
| **Top-k** | Sample from top k logits only. |
| **Top-p (nucleus)** | Sample from smallest token set with cumulative prob ≥ p. |
| **Greedy sampling** | Always pick highest-probability token. |
| **Best-of-N** | Generate N outputs, pick the best (by logprob, RM, vote, or heuristic). |
| **Constrained sampling** | Filter logits to grammatically valid tokens for structured output. |
| **Hallucination** | Model output not grounded in facts. |
| **Self-delusion** | Model treats its own generated tokens as given facts. |
| **Snowballing** | Initial wrong assumption cascades into more errors. |
| **Crawl-Walk-Run** | Microsoft's framework for gradually increasing AI automation. |
| **TTFT** | Time to first token. |
| **TPOT** | Time per output token. |
| **FLOP** | Floating-point operation (compute requirement). |
| **FLOP/s** | FLOPs per second (machine performance). |
| **Utilization** | % of peak compute achieved in practice (50% ok, 70% great). |
| **IDP** | Intelligent document processing. |

---

## 17. Quick-Reference Cheat Sheet

### Ch 1 — AI Engineering Essentials
- **Scale** is the defining post-2020 trend → model-as-a-service → low barrier → AI engineering discipline.
- **Self-supervision** unlocked data scale (no labeling) → LLMs.
- **Foundation models** = general-purpose + multimodal + adaptable.
- **3 driving factors:** general capabilities, investment, low entrance barrier.
- **8 use-case categories:** coding, image/video, writing, education, bots, info aggregation, data org, workflow automation.
- **3-layer stack:** application dev (top, most changed) → model dev → infrastructure (bottom, least changed).
- **AI eng ≠ ML eng:** adapt vs. build models; bigger compute; open-ended outputs → evaluation is central.
- **Last-mile challenge:** 0→60 easy, 60→100 takes months.
- **3 moats:** technology, data, distribution.

### Ch 2 — Foundation Model Internals
- **4 design decisions:** training data, architecture, size, post-training.
- **Data:** English dominates (45.88%); quality > quantity (1.3B on 7B good tokens beats bigger models).
- **Architecture:** Transformer (attention, no RNNs); encoder/decoder/encoder-decoder families; alternatives (Mamba, Jamba) emerging.
- **Size = 3 numbers:** params, training tokens, FLOPs. Chinchilla: 20 tokens/param.
- **Scaling bottlenecks:** data exhaustion (45% of C4 now restricted), electricity (1–2% → 4–20% of global by 2030).
- **Post-training:** SFT (demonstration data) + preference finetuning (RLHF/DPO). ~2% of compute.
- **Sampling:** temperature (creativity), top-k (compute), top-p (context-adaptive). Probabilistic → inconsistency + hallucination.
- **Structured outputs:** finetuning > constrained sampling > test-time compute > post-processing > prompting.
- **Hallucination hypotheses:** self-delusion (self-supervision) + knowledge mismatch (supervision/SFT).

### Key Numbers to Remember
| Metric | Value |
|---|---|
| Tokens ≈ words | 100 tokens ≈ 75 words |
| English share of Common Crawl | 45.88% |
| Chinchilla ratio | ~20 tokens / parameter |
| InstructGPT compute split | 98% pre-training / 2% post-training |
| GPT-3-175B training FLOPs | 3.14 × 10²³ |
| Burmese vs. English token length | 10× (72 vs. 7 median) |
| LinkedIn YAML parser uplift | 90% → 99.99% valid |
| OpenAI verifier boost | ≈ 30× model size |
| C4 restricted share (2024) | 45% |
| Data center electricity (2030 est.) | 4–20% of global |

---

*End of deep-dive. Cross-reference Chip Huyen's AI Engineering Chapters 1–2 for primary source material.*
