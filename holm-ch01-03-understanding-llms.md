# Hands-On LLMs — Understanding Language Models (Ch 1-3)

> **Source:** "Hands-On Large Language Models" by Jay Alammar & Maarten Grootendorst (O'Reilly, 2024)
> **Coverage:** Ch 1 (Introduction to LLMs), Ch 2 (Tokens and Embeddings), Ch 3 (Looking Inside LLMs)

---

## Chapter 1: Introduction to Large Language Models

### History of Language AI — The Evolution

```
┌──────────────────────────────────────────────────────────────────┐
│           EVOLUTION OF LANGUAGE AI                               │
│                                                                  │
│  1950s-1990s: RULE-BASED SYSTEMS                                │
│    Hand-crafted rules, grammars, dictionaries                   │
│    ELIZA (1966): Pattern matching for conversation              │
│    Limitation: Can't scale — too many rules needed              │
│                                                                  │
│  2000s: STATISTICAL METHODS                                     │
│    N-gram models, TF-IDF, Naive Bayes                           │
│    Bag-of-Words: Count word frequencies, ignore order          │
│    "The cat sat" → {the:1, cat:1, sat:1}                       │
│    Limitation: No word order, no meaning                        │
│                                                                  │
│  2013: WORD EMBEDDINGS (Word2Vec)                               │
│    Words → dense vectors (50-300 dimensions)                    │
│    king - man + woman ≈ queen (vector arithmetic!)              │
│    Similar words cluster together in vector space              │
│    Limitation: Same word, one embedding (no context)            │
│                                                                  │
│  2017: TRANSFORMER ("Attention Is All You Need")                │
│    Self-attention mechanism: every token attends to every other │
│    Parallel processing (no RNN sequential bottleneck)           │
│    Became the foundation for ALL modern LLMs                    │
│                                                                  │
│  2018: BERT (Encoder-Only, Representation)                      │
│    Bidirectional: reads text left-to-right AND right-to-left    │
│    Best for: Classification, NER, search, embeddings            │
│                                                                  │
│  2018-2020: GPT Series (Decoder-Only, Generative)               │
│    Autoregressive: predicts next token                          │
│    GPT-2 (1.5B params) → GPT-3 (175B params)                   │
│    Best for: Text generation, chat, code, reasoning             │
│                                                                  │
│  2022+: GENERATIVE AI ERA                                       │
│    ChatGPT, GPT-4, Llama, Gemini, Claude, Phi                  │
│    Instruction-tuned, RLHF-aligned, multimodal                 │
│    Open-weight models democratize access                       │
└──────────────────────────────────────────────────────────────────┘
```

### Encoder-Only vs Decoder-Only vs Encoder-Decoder

```
┌──────────────────┬───────────────┬──────────────────────────────┐
│ Architecture     │ Examples      │ Best For                     │
├──────────────────┼───────────────┼──────────────────────────────┤
│ Encoder-Only     │ BERT, RoBERTa │ Classification, NER,         │
│ (Representation) │               │ embeddings, search           │
│                  │               │ Reads text bidirectionally   │
│                  │               │ Output: contextualized       │
│                  │               │ embeddings                   │
├──────────────────┼───────────────┼──────────────────────────────┤
│ Decoder-Only     │ GPT, Llama,   │ Text generation, chat,       │
│ (Generative)     │ Phi, Claude   │ code, reasoning, completion  │
│                  │               │ Reads left-to-right only     │
│                  │               │ Output: next token prediction│
├──────────────────┼───────────────┼──────────────────────────────┤
│ Encoder-Decoder  │ T5, BART,     │ Translation, summarization   │
│ (Sequence-to-Seq)│ Whisper       │ Encoder reads input,         │
│                  │               │ Decoder generates output     │
└──────────────────┴───────────────┴──────────────────────────────┘
```

### Proprietary vs Open Models

```
┌──────────────────┬─────────────────────┬──────────────────────┐
│ Category         │ Examples            │ Characteristics      │
├──────────────────┼─────────────────────┼──────────────────────┤
│ Proprietary      │ GPT-4, Claude,      │ Best quality         │
│                  │ Gemini              │ API-only (no weights)│
│                  │                     │ Pay per token        │
│                  │                     │ Data goes to vendor  │
├──────────────────┼─────────────────────┼──────────────────────┤
│ Open-Weight      │ Llama 3, Phi-3,     │ Weights downloadable │
│                  │ Mistral, Qwen       │ Run locally          │
│                  │                     │ Some commercial      │
│                  │                     │ restrictions         │
├──────────────────┼─────────────────────┼──────────────────────┤
│ Open Source      │ Pythia, OLMo        │ Fully open (code +   │
│                  │                     │ data + training)     │
│                  │                     │ Research-focused     │
└──────────────────┴─────────────────────┴──────────────────────┘
```

---

## Chapter 2: Tokens and Embeddings

### Tokenization — How Text Becomes Numbers

```
THE TOKENIZATION PIPELINE:

  Raw Text → Tokenizer → Token IDs → Embedding Lookup → Vector

  Example: "The cat sat"
    Tokens: ["The", " cat", " sat"]
    IDs:    [464, 3797, 3332]
    Embeddings: [[0.12, -0.05, ...], [0.34, 0.89, ...], ...]

TOKENIZATION METHODS:
  ┌──────────────┬───────────────────────┬──────────────────────┐
  │ Method       │ Example               │ Trade-offs           │
  ├──────────────┼───────────────────────┼──────────────────────┤
  │ Word-level   │ "unbelievable" = 1    │ Huge vocabulary,     │
  │              │                       │ can't handle OOV     │
  ├──────────────┼───────────────────────┼──────────────────────┤
  │ Character    │ "u","n","b","e",...   │ Tiny vocab, but      │
  │              │                       │ very long sequences  │
  ├──────────────┼───────────────────────┼──────────────────────┤
  │ Subword      │ "un", "##believ",     │ Best of both worlds! │
  │ (BPE/Word-  │ "##able"              │ Handles rare words,  │
  │  Piece)      │                       │ manageable vocab     │
  ├──────────────┼───────────────────────┼──────────────────────┤
  │ Byte-level   │ Raw bytes             │ No OOV ever, but     │
  │              │                       │ longer sequences     │
  └──────────────┴───────────────────────┴──────────────────────┘

WHY SUBWORD TOKENIZATION DOMINATES:
  Common words → single token ("the", "cat")
  Rare words   → multiple subword tokens ("tokenization" → "token" + "ization")
  Never produces <UNK> tokens — everything can be represented!
```

### Comparing Tokenizers Across Models

```
┌──────────────┬──────────────┬──────────────────────────────────────┐
│ Model        │ Vocab Size   │ Tokenization of "Hello World"        │
├──────────────┼──────────────┼──────────────────────────────────────┤
│ GPT-4        │ ~100,000     │ [Hello,  World] = 2 tokens          │
│              │ (cl100k_base)│ Efficient for English + code        │
├──────────────┼──────────────┼──────────────────────────────────────┤
│ Llama 2      │ 32,000      │ [Hello,  World] = 2 tokens          │
│              │              │ Less efficient for non-English       │
├──────────────┼──────────────┼──────────────────────────────────────┤
│ Llama 3      │ 128,000     │ [Hello,  World] = 2 tokens          │
│              │              │ Much better multilingual support    │
├──────────────┼──────────────┼──────────────────────────────────────┤
│ Gemini       │ ~256,000    │ [Hello,  World] = 2 tokens          │
│              │              │ SentencePiece tokenizer              │
├──────────────┼──────────────┼──────────────────────────────────────┤
│ GPT-2        │ 50,257      │ [Hello,  World] = 2 tokens          │
│              │              │ Less efficient for code/Unicode     │
└──────────────┴──────────────┴──────────────────────────────────────┘

KEY INSIGHT:
  Larger vocab = fewer tokens per text = cheaper + faster
  But larger vocab = bigger embedding matrix = more parameters
  Llama 3's jump from 32K → 128K vocab was a major quality improvement.
```

### From Token Embeddings to Contextualized Embeddings

```
TOKEN EMBEDDINGS (Static):
  Each token ID maps to a fixed vector.
  "bank" always has the same embedding — whether it means
  "river bank" or "financial bank."
  This is the input to the model.

CONTEXTUALIZED EMBEDDINGS (After Transformer layers):
  After passing through Transformer blocks, each token's embedding
  is updated based on the surrounding context.

  "I sat by the river bank"     → bank embedding = "nature/water"
  "I deposited money in the bank" → bank embedding = "finance"

  This is what makes LLMs powerful — they understand CONTEXT.

  USE CASE: Extract contextualized embeddings from BERT for:
    • Semantic search (embed queries and documents)
    • Text classification (feed embeddings to a classifier)
    • Clustering (group similar texts by embedding proximity)
```

### Text Embeddings (Sentence/Document Level)

```
TOKEN vs TEXT EMBEDDINGS:
  Token embedding: One vector per token (what BERT outputs)
  Text embedding: One vector per sentence/document

HOW TO GET TEXT EMBEDDINGS:
  1. MEAN POOLING: Average all token embeddings in the text
     Simple but loses some information.

  2. [CLS] TOKEN: Use BERT's special [CLS] token embedding
     Trained to represent the whole sequence.

  3. SPECIALIZED EMBEDDING MODELS:
     Models specifically trained for sentence/document embeddings:
     • sentence-transformers (all-MiniLM-L6-v2)
     • Cohere Embed v3
     • OpenAI text-embedding-3-small/large
     • BGE (BAAI General Embedding)

     These use CONTRASTIVE LEARNING:
       "Similar texts should have similar embeddings"
       "Dissimilar texts should have different embeddings"

WORD2VEC AND CONTRASTIVE TRAINING (The Foundation):
  ┌────────────────────────────────────────────────────┐
  │  Word2Vec Training (2013, Mikolov et al.)         │
  │                                                    │
  │  Skip-gram: Use center word to predict context    │
  │  "The cat sat on the mat"                         │
  │  Center: "sat"                                    │
  │  Predict: "The", "cat", "on", "the", "mat"       │
  │                                                    │
  │  The model learns embeddings that make            │
  │  context prediction accurate.                     │
  │                                                    │
  │  Result: king - man + woman ≈ queen               │
  │  (Famous vector arithmetic demonstration)          │
  └────────────────────────────────────────────────────┘

EMBEDDINGS FOR RECOMMENDATION SYSTEMS:
  Alammar shows training song embeddings using the same principle.
  • Embed songs based on listening patterns (users who listen to
    similar songs → similar embeddings)
  • Recommend songs nearest to user's preferences in embedding space
  • Same principle powers Spotify, Netflix, YouTube recommendations
```

---

## Chapter 3: Looking Inside LLMs — Transformer Internals

### The Forward Pass — Step by Step

```
HOW A TRANSFORMER GENERATES ONE TOKEN:

  Input: "The cat sat on the"
         ↓
  ┌─────────────────────────────────────────────────────┐
  │ STEP 1: TOKENIZE                                    │
  │   "The cat sat on the" → [464, 3797, 3332, 322, 262]│
  │                                                     │
  │ STEP 2: EMBEDDING LOOKUP                            │
  │   Each token ID → embedding vector (e.g., 3072-dim) │
  │   Add positional embeddings (so model knows order)  │
  │                                                     │
  │ STEP 3: TRANSFORMER BLOCKS (repeated N times)       │
  │   ┌─────────────────────────────────────┐           │
  │   │ A. SELF-ATTENTION                   │           │
  │   │   Each token looks at ALL tokens    │           │
  │   │   Decides how much to "attend" to   │           │
  │   │   each other token                  │           │
  │   │                                     │           │
  │   │   Q = Query (what am I looking for) │           │
  │   │   K = Key (what do I have)          │           │
  │   │   V = Value (what information to pass)│         │
  │   │                                     │           │
  │   │   Attention(Q,K,V) = softmax(QKᵀ/√d)V           │
  │   │                                     │           │
  │   │ B. FEED-FORWARD (MLP)               │           │
  │   │   Two linear layers with activation │           │
  │   │   Processes each token independently│           │
  │   │                                     │           │
  │   │ C. RESIDUAL CONNECTIONS + NORM      │           │
  │   │   output = LayerNorm(x + Sublayer(x))│          │
  │   │   Enables deep networks (no vanishing│          │
  │   │   gradient)                         │           │
  │   └─────────────────────────────────────┘           │
  │                                                     │
  │ STEP 4: LM HEAD                                     │
  │   Final embedding → linear layer → softmax          │
  │   Output: probability distribution over vocabulary  │
  │   P(next_token) = softmax(logits)                   │
  │   "mat" has probability 0.82                        │
  │                                                     │
  │ STEP 5: SAMPLING / DECODING                         │
  │   Pick the next token from the distribution         │
  │   Greedy: Always pick highest probability           │
  │   Temperature: Scale logits to control randomness   │
  │   Top-k: Only consider top K candidates             │
  │   Top-p (nucleus): Consider candidates until        │
  │     cumulative probability reaches p                │
  └─────────────────────────────────────────────────────┘
```

### KV Caching — Speeding Up Generation

```
PROBLEM: Naive generation recomputes ALL tokens every step.
  Step 1: Process tokens [1, 2, 3, 4, 5] → predict token 6
  Step 2: Process tokens [1, 2, 3, 4, 5, 6] → predict token 7
          (recomputes tokens 1-5 AGAIN!)
  Step 3: Process tokens [1, 2, 3, 4, 5, 6, 7] → predict token 8
          (recomputes tokens 1-6 AGAIN!)
  → O(n²) total computation

SOLUTION: KV CACHE
  Store the Keys (K) and Values (V) for all previous tokens.
  When generating token N+1, only compute Q for the NEW token.
  Reuse cached K and V from previous tokens.

  Step 1: Compute K,V for [1,2,3,4,5]. Cache them. Predict 6.
  Step 2: Compute Q,K,V for [6] ONLY. Append K,V to cache.
          Use full cache to predict 7.
  Step 3: Compute Q,K,V for [7] ONLY. Append to cache.
          Use full cache to predict 8.
  → O(n) total computation (linear, not quadratic!)

TRADE-OFF:
  Speed: Much faster (10-50x for long sequences)
  Memory: Cache grows with sequence length
  → This is why longer contexts cost more memory
```

### Recent Architecture Improvements

```
┌──────────────────────────────────────────────────────────────────┐
│         IMPROVEMENTS SINCE THE ORIGINAL TRANSFORMER              │
│                                                                  │
│  1. GROUPED-QUERY ATTENTION (GQA)                                │
│     Original: Each query has its own key/value head (MQA)       │
│     GQA: Multiple queries share one key/value head              │
│     Benefit: Reduces KV cache size → faster, less memory        │
│     Used by: Llama 2 (70B), Llama 3, Mistral                    │
│                                                                  │
│  2. SLIDING WINDOW ATTENTION                                     │
│     Instead of attending to ALL tokens, attend to last W tokens │
│     Benefit: O(n) attention instead of O(n²)                   │
│     Used by: Mistral, Gemma 2                                    │
│                                                                  │
│  3. ROTARY POSITIONAL EMBEDDINGS (RoPE)                          │
│     Original: Fixed positional embeddings added to tokens       │
│     RoPE: Rotates the query/key vectors based on position       │
│     Benefit: Better generalization to longer sequences          │
│     Used by: Llama, Mistral, Qwen, Phi                          │
│                                                                  │
│  4. SWI-GLU ACTIVATION                                           │
│     Original: ReLU activation in feed-forward layer             │
│     SwiGLU: Gated linear unit with Swish activation             │
│     Benefit: Better performance, smoother gradients             │
│     Used by: Llama, PaLM, Qwen                                   │
│                                                                  │
│  5. RMS NORM (Root Mean Square Normalization)                    │
│     Original: LayerNorm (subtracts mean, divides by std)        │
│     RMSNorm: Only divides by RMS (no mean subtraction)          │
│     Benefit: Faster computation, similar quality                │
│     Used by: Llama, Mistral                                     │
│                                                                  │
│  6. MULTI-HEAD LATENT ATTENTION (MLA)                           │
│     Compresses KV cache into latent space                       │
│     Benefit: Drastic KV cache reduction for long contexts       │
│     Used by: DeepSeek-V2, DeepSeek-V3                           │
└──────────────────────────────────────────────────────────────────┘
```

---

## Interview Q&As

### Q1: "What's the difference between bag-of-words and embeddings?"

"Bag-of-words represents text as a count of each word — 'the cat sat' becomes {the:1, cat:1, sat:1}. It ignores word order and meaning — 'cat sat the' would be identical. Embeddings represent each word as a dense vector (e.g., 300 dimensions) where similar words have similar vectors. Embeddings capture semantic relationships — 'king' and 'queen' are close in embedding space, while 'king' and 'apple' are far apart. Embeddings enable arithmetic: king - man + woman ≈ queen."

### Q2: "Why are subword tokenizers better than word tokenizers?"

"Word tokenizers create huge vocabularies and can't handle unseen words (out-of-vocabulary problem). Subword tokenizers split rare words into common subwords: 'tokenization' → 'token' + 'ization'. This gives a manageable vocabulary (32K-128K) while covering all possible text — no <UNK> tokens. Common words stay as single tokens (efficient), rare words decompose into subword pieces. BPE (Byte-Pair Encoding) and WordPiece are the most popular subword algorithms."

### Q3: "Explain self-attention in simple terms."

"Self-attention lets each token decide how much to 'pay attention' to every other token. Each token creates three vectors: Query (what am I looking for), Key (what do I have), and Value (what to pass along). The attention score is the dot product of Query and Key — high score means 'these tokens are relevant to each other.' The scores are normalized (softmax) and used to weight the Values. The result: each token's new embedding is a weighted sum of all tokens' values, where the weights are attention scores. This is how 'bank' in 'river bank' gets a different representation than 'bank' in 'financial bank.'"

### Q4: "What is KV caching and why does it matter?"

"Without KV caching, generating token N+1 requires recomputing attention for all N previous tokens — O(n²) total. KV caching stores the Keys and Values for all previous tokens, so generating token N+1 only computes Q, K, V for the NEW token. The cached K and V are reused. This reduces total computation from O(n²) to O(n). The trade-off is memory — the KV cache grows with sequence length. This is why longer contexts cost more memory, and why techniques like GQA (Grouped-Query Attention) reduce KV cache size."

### Q5: "How does temperature affect text generation?"

"Temperature scales the logits before softmax. Temperature=1.0 is the default (original distribution). Temperature=0.0 is deterministic (always pick highest probability = greedy). Temperature=2.0 makes the distribution flatter (more random, more diverse). Low temperature (0.1-0.3) is good for factual tasks, code, and structured output. High temperature (0.7-1.0) is good for creative writing and brainstorming. Too high (>1.5) makes output incoherent."
