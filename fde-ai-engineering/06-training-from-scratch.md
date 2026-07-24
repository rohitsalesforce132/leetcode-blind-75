# Chapter 6: Training Models From Scratch

> **Interview questions:** "How are LLMs trained?" / "Explain the full training pipeline" / "What is pre-training?"

---

## 1. The Complete Training Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                  THE 6 STAGES OF LLM TRAINING               │
│                                                             │
│  Stage 1: DATA COLLECTION                                   │
│  Stage 2: TOKENIZATION                                      │
│  Stage 3: PRE-TRAINING (the big one)                        │
│  Stage 4: SUPERVISED FINE-TUNING (SFT)                      │
│  Stage 5: RLHF / DPO (Alignment)                            │
│  Stage 6: EVALUATION & DEPLOYMENT                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Stage 1: Data Collection & Preparation

### What Data Goes Into Pre-Training?

```
DATA SOURCES (for a model like Llama 3):
┌───────────────────────────────────────────────────┐
│ Source                     % of Training Data     │
├───────────────────────────────────────────────────┤
│ Web pages (Common Crawl)   67%                    │
│ Code (GitHub)              4.5%                   │
│ Books                      4.5%                   │
│ Wikipedia + Wikidata       4.5%                   │
│ STEM papers (arXiv)        2.5%                   │
│ News articles              2%                     │
│ Other (legal, medical)     15%                    │
└───────────────────────────────────────────────────┘

TOTAL: ~15 Trillion tokens (Llama 3.1)
       That's ~11 million novels worth of text.
```

### Data Quality Pipeline

```
Raw Web Data (100 PB)
    │
    ▼
[QUALITY FILTERING]
    - Remove spam, ads, adult content
    - Language detection (keep only target languages)
    - Deduplication (remove exact and near-duplicate documents)
    - Quality classifier (ML model scores text quality)
    - Remove PII (personally identifiable information)
    │
    ▼
Clean Data (~15T tokens)
    │
    ▼
[MIXING]
    - Blend sources in specific ratios
    - Oversample high-quality data (code, math, science)
    - Undersample low-quality data
    │
    ▼
Final Training Mix (ready for pre-training)
```

### Why Data Quality Matters More Than Quantity

```
"Garbage in, garbage out."

Model trained on 1T tokens of high-quality data
    BEATS
Model trained on 10T tokens of mixed-quality data.

Phi-3 (Microsoft): Trained on only 3.3T tokens of EXTREMELY high quality data.
  → Matches models trained on 10T+ tokens of average data.

Quality > Quantity is the #1 lesson in LLM training since 2023.
```

---

## 3. Stage 2: Tokenization

### What Is Tokenization?

```
Text: "The cat sat on the mat"

Tokenization: Split into sub-word units.

Token-level: ["The", " cat", " sat", " on", " the", " mat"]

Token IDs:   [464, 3756, 3537, 319, 262, 2631]

Each ID maps to a row in the embedding matrix.

Why sub-words (not full words)?
    - Handles rare words: "uncharacteristically" → "un" + "character" + "istic" + "ally"
    - Handles typos: "teh" → "te" + "h" (not an unknown word)
    - Multilingual: handles non-English text efficiently
    - Balance: not too many tokens (like characters) or too few (like full words)
```

### Popular Tokenizers

```
BPE (Byte Pair Encoding):
    Start with individual characters.
    Merge most frequent pairs iteratively.
    Used by: GPT-4, Llama

WordPiece:
    Similar to BPE but uses likelihood-based scoring.
    Used by: BERT

SentencePiece:
    Language-agnostic. Works directly on raw bytes.
    Used by: Llama, T5, Mistral
```

---

## 4. Stage 3: Pre-Training (The Main Event)

### What Happens During Pre-Training?

```
TASK: Next Token Prediction (Self-Supervised)

Given: "The cat sat on the"
Predict: "mat" (or "floor", "chair", etc.)

The model sees this sequence:
  Token 1: "The"      → predict token 2
  Token 2: " cat"     → predict token 3
  Token 3: " sat"     → predict token 4
  ...
  Token 5: " the"     → predict token 6

EVERY token is a training example.
"Attention mask" ensures the model can only see PREVIOUS tokens (causal).
```

### The Training Loop

```
for each batch of documents:
    1. Tokenize documents → sequences of token IDs
    2. Truncate/pad to fixed length (e.g., 8192 tokens)
    3. Feed through model → get predictions for each position
    4. Compare predictions to actual next tokens (cross-entropy loss)
    5. Backpropagate loss through all layers
    6. Update weights using optimizer (AdamW)
    7. Repeat for 4 TRILLION tokens

This takes MONTHS on THOUSANDS of GPUs.
```

### Scale of Pre-Training

```
Model: Llama 3.1 70B
  Parameters: 70,000,000,000
  Training tokens: 15,000,000,000,000 (15T)
  GPUs: 16,000 × NVIDIA H100
  Duration: ~50 days
  Cost: ~$600M-$1B+
  Power: ~50 MW (enough for a small city)

Model: Llama 3.1 8B (smaller)
  Parameters: 8,000,000,000
  Training tokens: 15,000,000,000,000 (15T)
  GPUs: ~1,000 × H100
  Duration: ~50 days
  Cost: ~$50M-$100M
```

### Distributed Training Strategies

```
1. DATA PARALLELISM
   ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐
   │GPU 1 │   │GPU 2 │   │GPU 3 │   │GPU 4 │
   │      │   │      │   │      │   │      │
   │Batch │   │Batch │   │Batch │   │Batch │
   │  A   │   │  B   │   │  C   │   │  D   │
   └──┬───┘   └──┬───┘   └──┬───┘   └──┬───┘
      └──────────┴──────────┴──────────┘
                 │
           Sync gradients
            after each step
   Each GPU has a FULL COPY of the model.
   Different data on each GPU.
   Simple but limited by model size (must fit in single GPU's VRAM).

2. TENSOR PARALLELISM
   Split each WEIGHT MATRIX across GPUs.

   GPU 1 holds: left half of every weight matrix
   GPU 2 holds: right half of every weight matrix

   Model too big for one GPU → split individual layers.
   Requires high-speed GPU interconnect (NVLink).

3. PIPELINE PARALLELISM
   Split the MODEL across GPUs — different LAYERS on different GPUs.

   GPU 1: Layers 1-20    → GPU 2: Layers 21-40 → GPU 3: Layers 41-60

   Data flows through GPUs like an assembly line.
   Each GPU processes different layers of the same model.

COMBINED (3D Parallelism):
   Real training uses all three simultaneously.
   16,000 GPUs → split into groups, each handling a slice of
   data, model layers, and weight matrices.
```

---

## 5. Stage 4: Supervised Fine-Tuning (SFT)

### The Goal: Make It Chat

```
Base Model after pre-training:
  Input: "What is the capital of France?"
  Output: "What is the capital of Germany?" (just text completion — unhelpful)

  The base model just COMPLETES text. It doesn't know how to ANSWER questions.

SFT teaches it the chat format:
  Input: "What is the capital of France?"
  Output: "The capital of France is Paris." (actually answers the question!)
```

### SFT Training Data

```jsonl
{"messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2+2?"},
    {"role": "assistant", "content": "2+2 equals 4."}
]}
{"messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Write a Python function to reverse a string."},
    {"role": "assistant", "content": "def reverse(s): return s[::-1]"}
]}
// Need ~100,000 to 1,000,000 high-quality examples
// These are often written by human experts or generated by GPT-4
```

### SFT Training Process

```
1. Freeze most of the model (or use LoRA)
2. Only compute loss on the ASSISTANT tokens (not user tokens)
3. Train for 2-5 epochs
4. Learning rate: ~2e-5 (much lower than pre-training)
5. Result: Model follows instructions, answers questions
```

---

## 6. Stage 5: RLHF / DPO (Alignment)

### The Problem SFT Doesn't Solve

```
SFT teaches the model to ANSWER. But sometimes it answers:
  - Harmfully: "How do I hack a website?" → gives actual instructions
  - Hallucinates: Makes up facts confidently
  - Verbosity: Gives 10 paragraphs when 1 sentence suffices
  - Bias: Shows cultural/gender/racial bias

ALIGNMENT teaches the model to be:
  Helpful (answers well)
  Harmless (refuses dangerous requests)
  Honest (admits uncertainty)
```

### RLHF (Reinforcement Learning from Human Feedback)

```
STEP 1: Collect Human Preferences
  For a given prompt, generate 2-4 different responses.
  Human annotator ranks them: Response A > Response B > Response C.

  Prompt: "How do I make a bomb?"
  A: "Here are the steps..." ← REJECTED (harmful)
  B: "I can't help with that." ← PREFERRED

STEP 2: Train a Reward Model
  Train a separate model to predict human preferences.
  Input: (prompt, response) → Output: score (how good is this response?)

STEP 3: Reinforcement Learning (PPO)
  Use the reward model to score the LLM's outputs.
  LLM generates responses → reward model scores them →
  LLM adjusts to maximize reward.

  This is PPO (Proximal Policy Optimization) — the same algorithm
  used in game-playing AI.

  RESULT: Model becomes helpful + harmless + honest.
```

### DPO (Direct Preference Optimization) — The Modern Alternative

```
PROBLEM WITH RLHF:
  - Complex (need separate reward model + PPO training)
  - Unstable (RL is notoriously hard to stabilize)
  - Expensive

DPO SIMPLIFIES IT:
  Skip the reward model entirely.
  Directly optimize the LLM using the preference data.
  "This response is better than that one" → adjust weights directly.

  DPO is:
  - Simpler (no separate reward model)
  - More stable (no RL instability)
  - Faster (fewer training steps)
  - Almost as good as RLHF

  DPO is becoming the DEFAULT for new models (Mistral, Zephyr, etc.)
```

---

## 7. Scaling Laws (Chinchilla)

```
THE CHINCHILLA SCALING LAW (DeepMind, 2022):

  "For optimal training, you need ~20 tokens per parameter."

  Model Size    Optimal Tokens    Optimal Compute
  ─────────────────────────────────────────────────
  1B params     20B tokens        ~100 GPU-days
  10B params    200B tokens       ~1,000 GPU-days
  70B params    1.4T tokens       ~10,000 GPU-days
  405B params   8T tokens         ~100,000 GPU-days

  KEY INSIGHT: Many models were UNDERTRAINED.
  Llama 3 broke this rule by training on 15T tokens for a 405B model
  (37 tokens/param) and showed continued improvement.

  TAKEAWAY: Data quality + quantity matters as much as model size.
```

---

## 8. Training Infrastructure

### What You Need to Train a Model

```
FOR A 7B MODEL (pre-training from scratch):
  - ~1,000 H100 GPUs
  - ~50 days
  - ~$50M-$100M
  - Massive data pipeline (15T+ tokens)
  - Distributed training software (DeepSpeed, FSDP, Megatron)

FOR A 7B MODEL FINE-TUNING (SFT + LoRA):
  - 1 consumer GPU (RTX 4090, 24GB VRAM)
  - ~1-3 days
  - ~$5-$100
  - HuggingFace Transformers + PEFT + TRL

FOR A 7B MODEL FINE-TUNING (full SFT):
  - 4-8 A100 GPUs
  - ~1-3 days
  - ~$500-$5,000

THE GAP IS MASSIVE:
  Pre-training = corporate-scale effort ($50M+)
  Fine-tuning = individual effort ($5-$100)
```

---

## 9. Open-Source Training Tools

| Tool | What It Does | When to Use |
|------|-------------|-------------|
| **HuggingFace Transformers** | Model loading, training APIs | Standard for all model training |
| **DeepSpeed** | Distributed training optimization | Training large models on multiple GPUs |
| **FSDP** (PyTorch) | Fully Sharded Data Parallel | Training models too big for one GPU |
| **Megatron-LM** | NVIDIA's large-model training framework | Frontier-scale pre-training |
| **TRL** (Transformers RL) | SFT + RLHF/DPO fine-tuning | Fine-tuning chat models |
| **PEFT** (Param-Efficient FT) | LoRA, QLoRA adapters | Efficient fine-tuning on minimal hardware |
| **Axolotl** | Config-driven fine-tuning | Easy reproducible fine-tuning |
| **Unsloth** | 2× faster LoRA fine-tuning | When you need speed on limited hardware |

---

## 10. The Full Pipeline at a Glance

```
┌────────────────────────────────────────────────────────────┐
│                   PRE-TRAINING                             │
│                                                            │
│  Raw Web (15T tokens)                                     │
│  → Filter → Dedup → Mix                                   │
│  → Tokenize                                               │
│  → Train (next-token prediction)                          │
│  → Base Model                                             │
│  Cost: $50M+ | GPUs: 1,000-16,000 | Time: Months          │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────┐
│                   SUPERVISED FINE-TUNING                   │
│                                                            │
│  100K-1M human Q&A examples                              │
│  → Format as chat (system/user/assistant)                 │
│  → Train (only compute loss on assistant tokens)          │
│  → Instruct Model                                         │
│  Cost: $1K-$50K | GPUs: 4-8 | Time: Hours-Days            │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────┐
│                   ALIGNMENT (RLHF/DPO)                     │
│                                                            │
│  100K-500K human preference pairs                         │
│  → Train reward model (RLHF) OR                            │
│  → Direct preference optimization (DPO)                   │
│  → Aligned Model                                          │
│  Cost: $10K-$100K | GPUs: 8-16 | Time: Days               │
└──────────────────────────────┬─────────────────────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────┐
│                   EVALUATION & DEPLOYMENT                  │
│                                                            │
│  Evaluate on benchmarks (MMLU, HumanEval, MT-Bench)        │
│  → Quantize (FP16 → INT4)                                 │
│  → Deploy with vLLM/TGI                                   │
│  → Monitor in production                                  │
│  Cost: Eval = $$ | Deploy = $$$$ (ongoing GPU costs)      │
└────────────────────────────────────────────────────────────┘
```

---

## Interview Q&A

**Q: "Can you walk me through how an LLM is trained from scratch?"**
A: It's a six-stage process. First, data collection — you gather trillions of tokens from web, books, code, and academic papers, then filter for quality and deduplicate. Second, tokenization — convert text into sub-word token IDs using BPE or SentencePiece. Third, pre-training — the model learns next-token prediction on trillions of tokens using self-attention. This produces a base model that can complete text but doesn't follow instructions. Fourth, supervised fine-tuning on high-quality Q&A pairs to teach it the chat format. Fifth, alignment via RLHF or DPO to make it helpful, harmless, and honest. Finally, evaluation on benchmarks and deployment.

**Q: "What's the difference between pre-training and fine-tuning?"**
A: Pre-training trains ALL parameters from scratch on massive data (trillions of tokens) to learn language and general knowledge. It costs $50M+ and takes months. Fine-tuning starts from a pre-trained model and adjusts some parameters on specific data (thousands to millions of examples) to specialize behavior. It costs $5-$5,000 and takes hours to days. Pre-training teaches the model language; fine-tuning teaches it a specific job.

**Q: "What is RLHF and why is it important?"**
A: RLHF is Reinforcement Learning from Human Feedback. After SFT, the model can answer questions but might be harmful, hallucinate, or give low-quality answers. RLHF works by collecting human preferences — showing annotators two responses and asking which is better — training a reward model on these preferences, then using PPO to optimize the LLM to maximize the reward. The result is a model that aligns with human values: helpful, harmless, honest. DPO is a simpler alternative that skips the reward model.

**Q: "How are models trained on multiple GPUs?"**
A: Three strategies combined: (1) Data parallelism — each GPU has a full model copy but processes different data batches, syncing gradients after each step. (2) Tensor parallelism — split individual weight matrices across GPUs (for models too big for one GPU). (3) Pipeline parallelism — assign different layers to different GPUs in an assembly-line pattern. Large training runs combine all three — 16,000 GPUs each handling a slice of data, layers, and matrices.

**Q: "What are Chinchilla scaling laws?"**
A: DeepMind found that for compute-optimal training, you need about 20 tokens per parameter. A 70B model should be trained on 1.4T tokens. Many early models (GPT-3, original Llama) were undertrained — they had too many parameters for their data. Llama 3 broke this by training on 15T tokens for a 405B model, showing that more data continues to improve quality well beyond the Chinchilla ratio.

**Q: "Could you train a model from scratch for an FDE customer?"**
A: For 99.9% of enterprise customers, no — pre-training costs $50M+ and provides no advantage over fine-tuning an existing model. The right approach is to take a strong open-source base model (Llama 3.1) and fine-tune it with LoRA on the customer's specific data. This costs $5-$500 instead of $50M, takes days not months, and delivers 95%+ of the value. I'd only recommend pre-training if the customer's domain is so unusual that no existing model handles it (e.g., a non-human language, or purely proprietary symbolic notation).
