# Hands-On LLMs — Training & Fine-Tuning Language Models (Ch 10-12)

> **Source:** "Hands-On Large Language Models" by Jay Alammar & Maarten Grootendorst (O'Reilly, 2024)
> **Coverage:** Ch 10 (Creating Text Embedding Models), Ch 11 (Fine-Tuning Representation Models), Ch 12 (Fine-Tuning Generation Models)

---

## Chapter 10: Creating Text Embedding Models

### Contrastive Learning — The Core Principle

```
┌──────────────────────────────────────────────────────────────────┐
│              CONTRASTIVE LEARNING                                │
│                                                                  │
│  GOAL: Train a model to produce similar embeddings for           │
│  semantically similar texts and different embeddings for         │
│  dissimilar texts.                                               │
│                                                                  │
│  THE TRAINING SIGNAL:                                            │
│    POSITIVE PAIR: (query, relevant_document)                    │
│      → Maximize cosine similarity                               │
│    NEGATIVE PAIR: (query, irrelevant_document)                  │
│      → Minimize cosine similarity                               │
│                                                                  │
│  EXAMPLE:                                                        │
│    Query: "How to train a dog"                                  │
│    Positive: "Dog training tips for beginners"  ← PULL CLOSER   │
│    Negative: "Best pasta recipes"               ← PUSH APART    │
│                                                                  │
│  TYPES OF NEGATIVES:                                             │
│    In-batch negatives: Other documents in the same batch         │
│    Hard negatives: Documents that are similar but not relevant   │
│      (e.g., "How to train a cat" — similar but wrong)            │
│    Hard negatives are CRITICAL for good embeddings.              │
└──────────────────────────────────────────────────────────────────┘
```

### SBERT Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│              SBERT (Sentence-BERT)                               │
│                                                                  │
│  PROBLEM WITH BERT FOR EMBEDDINGS:                              │
│    BERT requires cross-encoding: concatenate query + document   │
│    and pass through BERT. This is O(N×M) for N queries and      │
│    M documents — too slow for search.                           │
│                                                                  │
│  SBERT SOLUTION:                                                 │
│    Encode query and document SEPARATELY through BERT,           │
│    then pool (average) the token embeddings.                    │
│    Compare using cosine similarity.                             │
│                                                                  │
│  ┌──────┐         ┌──────┐                                      │
│  │Query │→ BERT → │Embed │                                      │
│  │      │         │  A   │                                      │
│  └──────┘         └──┬───┘                                      │
│                      │ cos(A,B)                                 │
│  ┌──────┐         ┌──┴───┐                                      │
│  │ Doc  │→ BERT → │Embed │                                      │
│  │      │         │  B   │                                      │
│  └──────┘         └──────┘                                      │
│                                                                  │
│  Speedup: 10,000x for search (embed docs offline, only embed    │
│  query at runtime, compare with vector math)                    │
│                                                                  │
│  Now O(N+M) instead of O(N×M)                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Loss Functions for Embedding Training

```
┌──────────────────────┬──────────────────────────────────────────┐
│ Loss Function        │ When to Use                              │
├──────────────────────┼──────────────────────────────────────────┤
│ MultipleNegatives    │ You have positive pairs (query, doc)    │
│ RankingLoss (MNRL)   │ Other docs in batch become negatives     │
│                      │ automatically.                           │
│                      │ BEST for general-purpose embeddings.     │
│                      │ Fast training, great results.            │
├──────────────────────┼──────────────────────────────────────────┤
│ CosineSimilarityLoss │ You have similarity scores (0-1) for    │
│                      │ pairs of texts.                          │
│                      │ Use when you have graded relevance.      │
├──────────────────────┼──────────────────────────────────────────┤
│ ContrastiveLoss      │ You have labeled positive/negative pairs│
│                      │ Explicitly defined.                      │
├──────────────────────┼──────────────────────────────────────────┤
│ TripletLoss          │ You have (anchor, positive, negative)   │
│                      │ triplets.                                │
│                      │ Pushes positive closer than negative.    │
├──────────────────────┼──────────────────────────────────────────┤
│ CachedMultipleNeg    │ For large batches without memory limits │
│ RankingsLoss         │ Uses gradient caching.                   │
└──────────────────────┴──────────────────────────────────────────┘
```

### Augmented SBERT (ANGEL)

```
TECHNIQUE: Use a cross-encoder to improve a bi-encoder.

  Phase 1: Train bi-encoder (SBERT) on small labeled dataset.
  Phase 2: Use cross-encoder (BERT) to score MANY more pairs.
  Phase 3: Train bi-encoder on the cross-encoder's scores.

  WHY: Cross-encoder is slow but accurate. Bi-encoder is fast
       but needs more data. Use cross-encoder to "teach" bi-encoder.

  RESULT: Bi-encoder that performs close to cross-encoder quality
          but runs 10,000x faster at search time.
```

---

## Chapter 11: Fine-Tuning Representation Models

### Fine-Tuning BERT for Classification

```
┌──────────────────────────────────────────────────────────────────┐
│         FINE-TUNING BERT FOR CLASSIFICATION                       │
│                                                                  │
│  ARCHITECTURE:                                                   │
│  ┌───────────────────────────────────────────┐                   │
│  │ Input: "This movie was terrible"          │                   │
│  │          ↓                                │                   │
│  │ [CLS] This movie was terrible [SEP]       │                   │
│  │          ↓                                │                   │
│  │ BERT (12 layers, 110M params)             │                   │
│  │          ↓                                │                   │
│  │ [CLS] embedding (768 dims)                │                   │
│  │          ↓                                │                   │
│  │ Linear classifier (768 → 2)              │                   │
│  │          ↓                                │                   │
│  │ [0.9, 0.1] → Negative                    │                   │
│  └───────────────────────────────────────────┘                   │
│                                                                  │
│  FREEZING STRATEGIES:                                            │
│  Full fine-tuning: Update ALL BERT parameters (best quality)     │
│  Partial freezing: Freeze early layers (faster, less overfitting)│
│    - Freeze embeddings + first N layers                          │
│    - Fine-tune last M layers + classifier                        │
│  Linear probing: Freeze ALL BERT, only train classifier (fastest)│
│                                                                  │
│  WHY FREEZE?                                                     │
│    - Less compute (fewer parameters to update)                   │
│    - Less memory (no gradients for frozen layers)                │
│    - Prevents catastrophic forgetting                            │
│    - Good for small datasets (avoids overfitting)                │
└──────────────────────────────────────────────────────────────────┘
```

### SetFit: Few-Shot Classification

```
┌──────────────────────────────────────────────────────────────────┐
│              SetFit (Sentence Transformer Fine-Tuning)            │
│                                                                  │
│  PROBLEM: You only have 8-64 labeled examples per class.         │
│  BERT fine-tuning overfits with so little data.                  │
│                                                                  │
│  SetFit SOLUTION: Two-phase training:                            │
│                                                                  │
│  PHASE 1: Contrastive Fine-Tuning                                │
│    Generate pairs from the few labeled examples:                 │
│    - Positive pairs: Same class examples                         │
│    - Negative pairs: Different class examples                    │
│    Fine-tune sentence transformer on these pairs.                │
│    Result: Better embeddings that cluster by class.              │
│                                                                  │
│  PHASE 2: Classification Head                                    │
│    Train a simple classifier (logistic regression or MLP)        │
│    on the fine-tuned embeddings.                                 │
│                                                                  │
│  RESULTS:                                                        │
│    - 8 labeled examples → 85%+ accuracy                          │
│    - 64 labeled examples → 92%+ accuracy                         │
│    - Approaches full BERT fine-tuning with 100x less data        │
│                                                                  │
│  WHY IT WORKS:                                                   │
│    Contrastive learning is data-efficient.                       │
│    From 8 examples, you can generate ~28 positive pairs          │
│    and many negative pairs — amplifying the signal.              │
└──────────────────────────────────────────────────────────────────┘
```

### Named Entity Recognition (NER)

```
NER: Find and classify named entities in text.

  Input:  "Apple was founded by Steve Jobs in California"
  Output: [ORG: Apple] [PER: Steve Jobs] [LOC: California]

FINE-TUNING FOR NER:
  Token classification task (classify each token):

  Token:    Apple  was  founded  by  Steve  Jobs  in  California
  Label:    B-ORG   O    O       O   B-PER   I-PER  O  B-LOC

  BIO LABELING SCHEME:
    B-XXX = Beginning of entity
    I-XXX = Inside entity (continuation)
    O     = Outside any entity

  TRAINING:
    Fine-tune BERT with a token classification head.
    Each token → 768-dim embedding → linear layer → NER labels.
    Loss: Cross-entropy at token level.
```

---

## Chapter 12: Fine-Tuning Generation Models

### The Three LLM Training Steps

```
┌──────────────────────────────────────────────────────────────────┐
│         THE THREE LLM TRAINING STEPS                             │
│                                                                  │
│  STEP 1: PRETRAINING (Language Modeling)                         │
│  ────────────────────────────────────────                        │
│    Train on TRILLIONS of tokens (web text, books, code).        │
│    Objective: Predict next token.                               │
│    Data: Unlabeled (self-supervised).                           │
│    Cost: $1M-$100M+ (massive GPU clusters).                     │
│    Output: BASE MODEL (good at completing text, bad at          │
│            following instructions).                              │
│                                                                  │
│    Base model input: "What is the capital of France?"           │
│    Base model output: "What is the capital of Germany?"         │
│    (It continues the pattern — generates another question)      │
│                                                                  │
│  STEP 2: SUPERVISED FINE-TUNING (SFT)                           │
│  ────────────────────────────────────────                        │
│    Train on instruction-response pairs.                         │
│    Objective: Predict next token given instruction.             │
│    Data: Labeled (human-written instructions + responses).      │
│    Cost: $100-$10K (small dataset, few epochs).                 │
│    Output: INSTRUCTION MODEL (follows instructions,             │
│            generates helpful responses).                         │
│                                                                  │
│    SFT model input: "What is the capital of France?"           │
│    SFT model output: "The capital of France is Paris."          │
│                                                                  │
│  STEP 3: PREFERENCE TUNING (Alignment / RLHF / DPO)             │
│  ────────────────────────────────────────                        │
│    Train on human preferences (which response is better?).      │
│    Objective: Generate preferred responses more often.          │
│    Data: Preference pairs (chosen vs rejected).                 │
│    Cost: $100-$10K.                                              │
│    Output: ALIGNED MODEL (safe, helpful, honest).               │
│                                                                  │
│    Without alignment: Model might be toxic, unhelpful,          │
│    or hallucinate freely.                                        │
│    With alignment: Model follows safety guidelines,             │
│    refuses harmful requests, provides helpful answers.          │
└──────────────────────────────────────────────────────────────────┘
```

### Full Fine-Tuning vs Parameter-Efficient Fine-Tuning (PEFT)

```
┌────────────────────┬───────────────────┬──────────────────────────┐
│ Aspect             │ Full Fine-Tuning  │ PEFT (LoRA/QLoRA)       │
├────────────────────┼───────────────────┼──────────────────────────┤
│ Parameters Updated │ ALL (billions)    │ Small adapter (0.1-1%)  │
│ Memory Required    │ Very High         │ Low (fit on 1 GPU)      │
│ Training Speed     │ Slow              │ Fast                     │
│ Quality            │ Best              │ Near-identical (95-99%) │
│ Storage Per Task   │ Full model copy   │ Small adapter (MB)      │
│ Switch Tasks       │ Swap entire model │ Hot-swap adapters       │
│ Risk of Forgetting │ High              │ Low (base frozen)       │
│ Best For           │ Large research    │ Production, domain      │
│                    │ labs              │ adaptation, most teams  │
└────────────────────┴───────────────────┴──────────────────────────┘
```

### LoRA and QLoRA Deep Dive

```
┌──────────────────────────────────────────────────────────────────┐
│              LoRA (Low-Rank Adaptation)                          │
│                                                                  │
│  INSIGHT: Weight updates during fine-tuning have low            │
│  "intrinsic rank" — they can be approximated by much            │
│  smaller matrices.                                               │
│                                                                  │
│  ORIGINAL: W (d×d) = 4096×4096 = 16.7M params per layer        │
│                                                                  │
│  LoRA: ΔW = A × B  where A is (d×r), B is (r×d)                │
│         r = 8, 16, 32, 64 (rank)                                │
│         Params: 2 × d × r = 2 × 4096 × 16 = 131K (0.8%!)       │
│                                                                  │
│  TRAINING:                                                       │
│    Freeze original W.                                            │
│    Only train A and B (the low-rank matrices).                  │
│    Output = Wx + ABx (original + adaptation)                    │
│                                                                  │
│  ─────────────────────────────────────────────                   │
│  QLoRA (Quantized LoRA)                                          │
│                                                                  │
│  Additional optimization: Quantize the BASE model to 4-bit.     │
│    - Base model: 4-bit NF4 (NormalFloat4) — frozen             │
│    - LoRA adapters: FP32 — trainable                            │
│    - Result: Train 7B model on a single 16GB GPU!              │
│                                                                  │
│  NF4 (NormalFloat4):                                            │
│    Quantization designed for normally-distributed weights.      │
│    Better than uniform INT4 quantization.                       │
│    Information loss is minimal for weight values.               │
│                                                                  │
│  QLoRA TRAINING PIPELINE:                                        │
│  1. Load base model in 4-bit (NF4)                              │
│  2. Add LoRA adapters (rank=16, alpha=32)                       │
│  3. Train adapters on instruction data                          │
│  4. Merge adapters back into base model (optional)             │
│  5. Deploy merged model                                         │
└──────────────────────────────────────────────────────────────────┘
```

### Preference Tuning: RLHF vs DPO

```
┌──────────────────────────────────────────────────────────────────┐
│              RLHF vs DPO                                         │
│                                                                  │
│  RLHF (Reinforcement Learning from Human Feedback):              │
│  ────────────────────────────────────────────────                │
│    Phase 1: Collect preferences (humans rank responses)         │
│    Phase 2: Train REWARD MODEL on preferences                   │
│    Phase 3: Use PPO to optimize LLM against reward model        │
│                                                                  │
│    Complexity: VERY HIGH                                         │
│    - Need separate reward model                                  │
│    - PPO is unstable, requires careful tuning                   │
│    - 4 models in memory (actor, critic, ref, reward)            │
│    - The original ChatGPT method                                 │
│                                                                  │
│  DPO (Direct Preference Optimization):                           │
│  ────────────────────────────────────────────────                │
│    Phase 1: Collect preferences (same as RLHF)                  │
│    Phase 2: Directly fine-tune LLM on preferences               │
│             (NO reward model, NO RL)                            │
│                                                                  │
│    Complexity: MUCH LOWER                                        │
│    - Just supervised learning on preference pairs               │
│    - Only 2 models in memory (policy, reference)                │
│    - Stable training (no PPO instability)                       │
│    - The method that's replacing RLHF                           │
│                                                                  │
│  DPO LOSS FUNCTION:                                              │
│    L = -log σ(β log(π(y_chosen)/π_ref(y_chosen))                │
│              - β log(π(y_rejected)/π_ref(y_rejected)))           │
│                                                                  │
│    Intuition: Increase probability of chosen responses          │
│    relative to the reference model, decrease probability of     │
│    rejected responses. β controls how far from reference.       │
│                                                                  │
│  COMPARISON:                                                     │
│  ┌──────────────┬───────────────┬──────────────────┐            │
│  │ Aspect       │ RLHF          │ DPO              │            │
│  ├──────────────┼───────────────┼──────────────────┤            │
│  │ Complexity   │ Very High     │ Low              │            │
│  │ Stability    │ Unstable (PPO)│ Stable           │            │
│  │ Models Needed│ 4             │ 2                │            │
│  │ Quality      │ Best          │ Comparable       │            │
│  │ Adoption     │ Decreasing    │ Increasing       │            │
│  └──────────────┴───────────────┴──────────────────┘            │
└──────────────────────────────────────────────────────────────────┘
```

### Evaluating Generative Models

```
EVALUATION LANDSCAPE:

  1. WORD-LEVEL METRICS (Traditional NLP):
     BLEU: N-gram overlap (machine translation)
     ROUGE: Recall-oriented overlap (summarization)
     METEOR: Alignment-based metric
     Limitation: Bad at semantic similarity (synonyms scored as wrong)

  2. BENCHMARKS (Standardized test suites):
     MMLU: 57 subjects, multiple-choice (general knowledge)
     HumanEval: Python coding problems
     GSM8K: Grade-school math word problems
     HellaSwag: Commonsense reasoning
     TruthfulQA: Tendency to hallucinate
     MT-Bench: Multi-turn conversation quality

  3. LEADERBOARDS:
     Hugging Face Open LLM Leaderboard: Automated benchmark runs
     Chatbot Arena: Human votes (Elo rating) — most trusted

  4. AUTOMATED EVALUATION (LLM-as-Judge):
     Use GPT-4 to evaluate other models' outputs.
     "Rate this response from 1-10 for helpfulness."
     Faster than human eval, but has biases (verbosity bias, position bias).

  5. HUMAN EVALUATION:
     Gold standard but slow and expensive.
     Used by Chatbot Arena (crowdsourced pairwise votes).
```

---

## Interview Q&As

### Q1: "Explain LoRA and why it's useful."

"LoRA (Low-Rank Adaptation) freezes the original model weights and adds small trainable low-rank matrices (A and B) alongside each weight matrix. Instead of updating W (4096×4096 = 16.7M params), LoRA trains A (4096×16) and B (16×4096) = 131K params — 0.8% of the original. The output becomes Wx + ABx. This makes fine-tuning 10-100x cheaper in memory and compute, enabling fine-tuning of 7B+ models on a single GPU. Multiple LoRA adapters can be hot-swapped for different tasks without storing multiple full models."

### Q2: "What is QLoRA and how does it differ from LoRA?"

"QLoRA combines LoRA with 4-bit quantization of the base model. The base model weights are stored in 4-bit NF4 (NormalFloat4) format and frozen. Only the LoRA adapters are trained in FP32. This means you can fine-tune a 7B parameter model on a single 16GB GPU. NF4 is a quantization scheme designed for normally-distributed weight values, minimizing information loss. The key innovation: you get near-full-precision fine-tuning quality at a fraction of the memory cost."

### Q3: "What is the difference between RLHF and DPO?"

"RLHF requires three steps: train a reward model on human preferences, then use reinforcement learning (PPO) to optimize the LLM against the reward model. It needs 4 models in memory (actor, critic, reference, reward) and PPO is notoriously unstable. DPO (Direct Preference Optimization) skips the reward model and RL entirely — it directly fine-tunes the LLM on preference pairs using a simple loss function that increases the probability of chosen responses and decreases rejected ones. DPO is simpler, more stable, and produces comparable quality. The field is moving from RLHF toward DPO."

### Q4: "What are the three stages of LLM training?"

"Stage 1 is pretraining — train on trillions of tokens using next-token prediction (self-supervised). This produces a base model that's good at completing text but bad at following instructions. Stage 2 is supervised fine-tuning (SFT) — train on instruction-response pairs so the model learns to follow instructions and be helpful. Stage 3 is preference tuning (RLHF or DPO) — align the model with human values (safe, honest, helpful) using preference data. Each stage uses less data and compute than the previous one."

### Q5: "How does SetFit achieve good classification with very few examples?"

"SetFit uses two phases. Phase 1: Contrastive fine-tuning — from 8 labeled examples per class, it generates positive pairs (same class) and negative pairs (different class), fine-tuning a sentence transformer. This creates better embeddings that cluster by class. Phase 2: Train a simple classifier on the fine-tuned embeddings. The key insight is that contrastive learning amplifies the signal from few examples — 8 examples per class generates ~28 positive pairs, and many more negative pairs. SetFit approaches full BERT fine-tuning accuracy with 100x less labeled data."
