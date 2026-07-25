# Hands-On LLMs — Applications: Classification, Clustering & Prompt Engineering (Ch 4-6)

> **Source:** "Hands-On Large Language Models" by Jay Alammar & Maarten Grootendorst (O'Reilly, 2024)
> **Coverage:** Ch 4 (Text Classification), Ch 5 (Text Clustering & Topic Modeling), Ch 6 (Prompt Engineering)

---

## Chapter 4: Text Classification

### Three Approaches to Classification with LLMs

```
┌──────────────────────────────────────────────────────────────────┐
│              THREE CLASSIFICATION APPROACHES                     │
│                                                                  │
│  1. REPRESENTATION MODELS (Encoder-only, e.g., BERT)             │
│     Use the model to generate embeddings.                        │
│     Train a classifier on top of embeddings (logistic reg,      │
│     SVM, shallow neural net).                                    │
│     Requires labeled data.                                       │
│     Best for: Fast, cheap, domain-specific classification.       │
│                                                                  │
│  2. EMBEDDING-BASED (Zero-shot / Few-shot)                       │
│     Embed the text and class labels separately.                  │
│     Classify by finding nearest label embedding.                 │
│     No training data needed!                                     │
│     Best for: Quick prototypes, new domains, low-data.           │
│                                                                  │
│  3. GENERATIVE MODELS (Decoder-only, e.g., GPT-4, Phi-3)        │
│     Ask the model directly: "Classify this text: ..."           │
│     No training, no fine-tuning — just prompting.                │
│     Best for: Complex classification, zero-shot, flexibility.    │
└──────────────────────────────────────────────────────────────────┘
```

### Model Selection for Classification

```
┌──────────────────┬───────────┬───────────────────────────────────┐
│ Approach         │ Data Need │ When to Use                       │
├──────────────────┼───────────┼───────────────────────────────────┤
│ Task-specific    │ None      │ When a pre-trained model exists   │
│ (BERT finetuned) │           │ for your exact task (sentiment,   │
│                  │           │ toxicity, etc.)                   │
├──────────────────┼───────────┼───────────────────────────────────┤
│ Supervised       │ Many      │ When you have labeled data and    │
│ Classification   │ labels    │ need high accuracy                │
│ (embed + classifier)│        │                                   │
├──────────────────┼───────────┼───────────────────────────────────┤
│ Zero-shot        │ None      │ Quick prototype, no labeled data  │
│ (embedding match)│           │                                   │
├──────────────────┼───────────┼───────────────────────────────────┤
│ Few-shot (SetFit)│ Few       │ Small labeled dataset (8-64       │
│                  │ labels    │ examples per class)               │
├──────────────────┼───────────┼───────────────────────────────────┤
│ Generative       │ None      │ Complex reasoning, multi-label,   │
│ (GPT-4/T5)       │           │ or no ML pipeline                 │
└──────────────────┴───────────┴───────────────────────────────────┘
```

---

## Chapter 5: Text Clustering and Topic Modeling

### The Standard Clustering Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│           TEXT CLUSTERING PIPELINE (BERTopic)                    │
│                                                                  │
│  STEP 1: EMBED DOCUMENTS                                         │
│    Use a sentence embedding model (all-MiniLM-L6-v2, etc.)      │
│    Each document → dense vector (384 or 768 dims)              │
│                                                                  │
│  STEP 2: DIMENSIONALITY REDUCTION (UMAP)                         │
│    Embeddings are high-dimensional (384+ dims)                   │
│    UMAP reduces to 2-10 dims for clustering                     │
│    Preserves local AND global structure                         │
│    Much faster than t-SNE                                        │
│                                                                  │
│  STEP 3: CLUSTERING (HDBSCAN)                                    │
│    Unlike K-Means, HDBSCAN:                                     │
│    ✓ Doesn't require knowing K in advance                        │
│    ✓ Allows noise points (documents that don't fit any cluster)  │
│    ✓ Finds clusters of varying density                           │
│                                                                  │
│  STEP 4: INSPECT AND LABEL CLUSTERS                              │
│    Find the most representative words for each cluster           │
│    c-TF-IDF: TF-IDF at the cluster level (not document level)   │
│    "Cluster 1: neural, network, deep, learning, transformer"     │
│    → Label: "Deep Learning"                                      │
│                                                                  │
│  OPTIONAL STEP 5: LLM LABELING                                   │
│    Feed cluster's top words to an LLM:                           │
│    "What topic do these words represent: neural, network, deep"  │
│    LLM generates: "Deep Learning and Neural Networks"            │
│    → Much better than keyword labels!                            │
└──────────────────────────────────────────────────────────────────┘
```

### BERTopic: The Modular Framework

```
BERTopic is like LEGO blocks for topic modeling:

  ┌─────────┐   ┌───────────┐   ┌────────┐   ┌─────────┐   ┌──────┐
  │ Embedder│ → │ Dimension │ → │Cluster │ → │Topic Rep│ → │Label │
  │         │   │ Reducer   │   │        │   │         │   │      │
  │ any     │   │ UMAP      │   │ HDBSCAN│   │ c-TF-IDF│   │LLM   │
  │ embed   │   │ PCA       │   │ K-Means│   │ LLM     │   │      │
  │ model   │   │ t-SNE     │   │        │   │         │   │      │
  └─────────┘   └───────────┘   └────────┘   └─────────┘   └──────┘

  Each block is SWAPPABLE:
    Embedder:   OpenAI, Cohere, sentence-transformers, custom
    Reducer:    UMAP (default), PCA, t-SNE
    Clusterer:  HDBSCAN (default), K-Means, hierarchical
    Topic Rep:  c-TF-IDF (default), LLM-based, custom
    Label:      Keyword extraction, LLM generation

  This modularity makes BERTopic incredibly flexible.
```

---

## Chapter 6: Prompt Engineering

### The Basic Ingredients of a Prompt

```
┌──────────────────────────────────────────────────────────────────┐
│              ANATOMY OF A GREAT PROMPT                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐          │
│  │ 1. INSTRUCTION (What to do)                        │          │
│  │    "Translate the following text to French."       │          │
│  │                                                    │          │
│  │ 2. CONTEXT (Background information)                │          │
│  │    "This is for a legal document. Use formal       │          │
│  │     French legal terminology."                     │          │
│  │                                                    │          │
│  │ 3. INPUT (The data to process)                     │          │
│  │    "The plaintiff requests damages for breach      │          │
│  │     of contract."                                  │          │
│  │                                                    │          │
│  │ 4. OUTPUT FORMAT (How to format the response)      │          │
│  │    "Return only the translation, no explanation."  │          │
│  │                                                    │          │
│  │ 5. EXAMPLES (Optional, for few-shot)               │          │
│  │    "Example: 'Hello' → 'Bonjour'"                 │          │
│  └────────────────────────────────────────────────────┘          │
└──────────────────────────────────────────────────────────────────┘
```

### Controlling Output: Temperature, Top-K, Top-P

```
SAMPLING PARAMETERS:
  ┌─────────────┬──────────┬──────────────────────────────────────┐
  │ Parameter   │ Range    │ Effect                               │
  ├─────────────┼──────────┼──────────────────────────────────────┤
  │ Temperature │ 0.0-2.0  │ 0.0 = Deterministic (greedy)        │
  │             │          │ 0.7 = Balanced (most common)        │
  │             │          │ 1.0 = Standard sampling             │
  │             │          │ 1.5+ = Chaotic, creative            │
  ├─────────────┼──────────┼──────────────────────────────────────┤
  │ Top-K       │ 1-1000   │ Only consider top K tokens          │
  │             │          │ K=1 = Greedy (always pick best)     │
  │             │          │ K=40 = Consider 40 best candidates  │
  │             │          │ Low K = Focused, High K = Diverse   │
  ├─────────────┼──────────┼──────────────────────────────────────┤
  │ Top-P       │ 0.0-1.0  │ Only consider tokens until          │
  │ (Nucleus)   │          │ cumulative probability = P          │
  │             │          │ P=0.9 = Consider best tokens that   │
  │             │          │ make up 90% of probability mass     │
  ├─────────────┼──────────┼──────────────────────────────────────┤
  │ Max Tokens  │ 1-N      │ Maximum length of generated output  │
  └─────────────┴──────────┴──────────────────────────────────────┘

RECOMMENDED SETTINGS BY TASK:
  Code Generation:        temp=0.0, top_k=1 (deterministic)
  Factual QA:             temp=0.1-0.3 (low randomness)
  Summarization:          temp=0.3-0.5 (slightly varied)
  Creative Writing:       temp=0.7-1.0 (more creative)
  Brainstorming:          temp=1.0-1.3 (maximum diversity)
```

### Advanced Prompt Engineering Techniques

```
1. IN-CONTEXT LEARNING (Few-Shot Prompting)
   Provide examples in the prompt to show the model what to do.

   "Classify the sentiment of these reviews:
    Review: 'Great product!' → Positive
    Review: 'Terrible quality' → Negative
    Review: 'It was okay' → Neutral
    Review: 'Best purchase ever!' →"

   The model learns the pattern FROM the examples.

2. CHAIN PROMPTING (Multi-Step)
   Break complex tasks into sequential prompts.

   Step 1: "Extract the key entities from this article."
   Step 2: "For each entity, summarize its role."
   Step 3: "Format as a structured JSON."

   Each step's output feeds the next step.

3. CHAIN-OF-THOUGHT (CoT)
   Ask the model to reason step by step.

   "Think step by step before answering."
   "Let's reason about this: First, ... Second, ... Therefore, ..."

   Benefits: Dramatically improves math, logic, and multi-step reasoning.
   Works because the model generates intermediate reasoning tokens
   that improve the final answer.

4. SELF-CONSISTENCY
   Generate MULTIPLE chain-of-thought answers (with temperature > 0).
   Take the MAJORITY VOTE of the answers.
   Reduces errors by averaging out random mistakes.

5. TREE-OF-THOUGHT (ToT)
   Explore MULTIPLE reasoning paths in parallel.
   Build a tree of thoughts, evaluate each branch, prune bad ones.
   Backtrack when a path leads to a dead end.

   Use case: Complex puzzle solving, planning, game playing.

6. CONSTRAINED SAMPLING / GRAMMAR
   Force the model to output in a specific format (JSON, regex, etc.)
   "Only output valid JSON with keys: name, age, email."
   Tools: Guidance, LMQL, Outlines, JSON schema validation.
```

### Reasoning Techniques Comparison

```
┌──────────────────┬──────────────────┬──────────────────────────────┐
│ Technique        │ Token Cost       │ When to Use                  │
├──────────────────┼──────────────────┼──────────────────────────────┤
│ Direct Prompting │ Lowest           │ Simple tasks (translation,   │
│                  │                  │ classification)              │
├──────────────────┼──────────────────┼──────────────────────────────┤
│ Few-Shot         │ Low              │ Pattern-based tasks where    │
│                  │ (examples add    │ examples clarify the format  │
│                  │ tokens)          │                              │
├──────────────────┼──────────────────┼──────────────────────────────┤
│ Chain-of-Thought │ Medium           │ Math, logic, multi-step      │
│                  │ (reasoning adds  │ reasoning                    │
│                  │ tokens)          │                              │
├──────────────────┼──────────────────┼──────────────────────────────┤
│ Self-Consistency │ High (N x CoT)   │ When accuracy is critical    │
│                  │ (generate N      │ and you can afford N times   │
│                  │ answers)         │ the cost                     │
├──────────────────┼──────────────────┼──────────────────────────────┤
│ Tree-of-Thought  │ Highest          │ Complex planning, puzzles,   │
│                  │ (many branches)  │ exploration problems         │
└──────────────────┴──────────────────┴──────────────────────────────┘
```

---

## Interview Q&As

### Q1: "How would you classify text without labeled training data?"

"Three approaches: (1) Zero-shot embedding classification — embed the text and class labels separately, classify by cosine similarity. No training needed. (2) Generative classification — prompt a model like GPT-4 with the text and ask it to classify. (3) Few-shot with SetFit — provide 8-64 examples per class and use SetFit, which is specifically designed for few-shot classification. For quick prototypes, I'd use generative. For production with cost constraints, I'd fine-tune SetFit with a few labeled examples."

### Q2: "Explain how BERTopic works."

"BERTopic is a modular pipeline: (1) Embed documents using a sentence embedding model. (2) Reduce dimensionality with UMAP (faster than t-SNE, preserves structure). (3) Cluster with HDBSCAN (doesn't need pre-specified K, allows noise points). (4) Extract topic representations using c-TF-IDF — TF-IDF at the cluster level instead of document level. (5) Optionally use an LLM to generate human-readable topic labels from the cluster's top keywords. Each step is a swappable module — you can use any embedder, reducer, clusterer, or topic representation method."

### Q3: "What is chain-of-thought prompting and why does it work?"

"Chain-of-thought asks the model to reason step by step before giving the final answer. Instead of 'What is 15 × 17?', you say 'Let's think step by step.' The model generates intermediate reasoning: 'First, 15 × 10 = 150. Then, 15 × 7 = 105. Total: 150 + 105 = 255.' This works because each intermediate token is fed back into the model's context, helping it 'think' through the problem. The model can't solve complex reasoning in a single forward pass, but by generating intermediate steps, each subsequent token prediction builds on accumulated reasoning."

### Q4: "How do temperature, top-K, and top-P differ?"

"Temperature scales the logits before softmax — lower temperature makes the distribution sharper (more deterministic), higher makes it flatter (more random). Top-K limits candidates to the K highest-probability tokens — the model can never pick a low-probability token. Top-P (nucleus sampling) includes all tokens whose cumulative probability exceeds P — adapts dynamically (if one token has 95% probability, only that token is considered). For factual tasks: temp=0.2, top_k=40. For creative: temp=0.8, top_p=0.9. They can be combined."

### Q5: "What is self-consistency and how does it improve over chain-of-thought?"

"Self-consistency generates multiple chain-of-thought answers using temperature > 0 (so each is slightly different), then takes a majority vote. The idea: correct reasoning paths are more likely to converge on the same answer, while incorrect paths diverge randomly. If you generate 5 reasoning chains and 3 arrive at '42', that's more reliable than a single chain arriving at '42'. The cost is N times more tokens, but accuracy improves significantly on math and logic tasks."
