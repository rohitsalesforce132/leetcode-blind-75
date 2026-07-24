# Chapter 5: Fine-Tuning — When, Why, How

> **Interview questions:** "Is fine-tuning required?" / "When should you fine-tune vs use RAG?" / "Explain LoRA and QLoRA."

---

## 1. The Decision: Do You Even Need Fine-Tuning?

**90% of the time, you DON'T need fine-tuning.** This is the most important answer in any AI interview.

```
┌──────────────────────────────────────────────────────────┐
│  THE HIERARCHY OF LLM CUSTOMIZATION                      │
│  (Try top first. Only go down if the top doesn't work.)  │
│                                                          │
│  1. PROMPT ENGINEERING    Cost: $0   Effort: Hours       │
│     "Write better system prompts"                        │
│     Solves: 60% of problems                              │
│     ↓ (If prompts aren't enough)                         │
│                                                          │
│  2. FEW-SHOT EXAMPLES     Cost: $0   Effort: Hours       │
│     "Show the model examples of good outputs"            │
│     Solves: 15% more                                     │
│     ↓ (If examples in context aren't enough)             │
│                                                          │
│  3. RAG (Retrieval)       Cost: $$   Effort: Days        │
│     "Give the model relevant documents"                  │
│     Solves: 15% more                                     │
│     ↓ (If knowledge retrieval isn't enough)              │
│                                                          │
│  4. FINE-TUNING            Cost: $$$  Effort: Weeks      │
│     "Train the model on your specific data"              │
│     Solves: 8% more                                      │
│     ↓ (If fine-tuning isn't enough)                      │
│                                                          │
│  5. PRE-TRAIN FROM SCRATCH  Cost: $$$$$ Effort: Months   │
│     "Train a model from nothing"                         │
│     Solves: 2% of cases                                  │
└──────────────────────────────────────────────────────────┘
```

### When Fine-Tuning IS the Right Answer

```
Fine-tune when you need to change HOW the model BEHAVES, not WHAT it knows:

✓ FINE-TUNE FOR:
  - OUTPUT FORMAT: "Always respond in our proprietary JSON schema"
  - TONE/STYLE: "Write in our brand voice — concise, technical, no fluff"
  - TASK SPECIALIZATION: "Be excellent at classifying support tickets"
  - DOMAIN LANGUAGE: "Understand telecom/networking terminology natively"
  - REDUCED LATENCY: "Small fine-tuned model beats large model + long prompt"

✗ DON'T FINE-TUNE FOR:
  - KNOWLEDGE: "Know about our company's Q3 earnings" → Use RAG instead
  - CURRENT EVENTS: "Know today's news" → Use web search + RAG
  - COMPLEX REASONING: "Solve novel math problems" → Use a bigger model
  - ONE-OFF TASKS: "Do this one weird thing" → Use prompt engineering
  - SMALL DATASETS: "I have 50 examples" → Use few-shot prompting instead
```

### RAG vs Fine-Tuning Decision Framework

```
                    ┌──────────────────────────────────────┐
                    │  Does the task need KNOWLEDGE         │
                    │  (facts, data, documents)?            │
                    └──────────────┬───────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────┐
                    │               YES                     │
                    │         → USE RAG                     │
                    │  (Retrieve relevant docs,             │
                    │   inject into context)                │
                    └──────────────────────────────────────┘

                    ┌──────────────────────────────────────┐
                    │  Does the task need BEHAVIOR change   │
                    │  (format, tone, style, specialization)?│
                    └──────────────┬───────────────────────┘
                                   │
                    ┌──────────────▼───────────────────────┐
                    │               YES                     │
                    │         → FINE-TUNE                   │
                    │  (Train on examples of desired        │
                    │   behavior)                           │
                    └──────────────────────────────────────┘

    PRO TIP: You can do BOTH. RAG for knowledge + fine-tuned model for behavior.
```

---

## 2. Fine-Tuning Methods Explained

### Full Fine-Tuning

```
WHAT: Retrain ALL parameters of the model on your data.

Original Model (7B params) + Your Data → Updated Model (7B params)

      ┌──────────────────────────┐
      │  ALL 7B parameters       │ ← ALL weights get updated
      │  get updated via         │
      │  backpropagation         │
      └──────────────────────────┘

PROS: Maximum quality improvement.
CONS: Extremely expensive. Need to store full model copy. Catastrophic forgetting
      (model forgets old skills). Full GPU cluster required.

COST: $1,000-$10,000+ for a 7B model.
HARDWARE: 4-8 A100/H100 GPUs
```

### LoRA (Low-Rank Adaptation) — The Game Changer

```
WHAT: Instead of updating all 7B parameters, freeze the original model
      and train TINY "adapter" weights on top.

Original Model (7B params, FROZEN) + LoRA Adapter (10M params, TRAINED)

      ┌──────────────────────────┐
      │  Original 7B params      │ ← FROZEN (not changed)
      │  (frozen, not updated)   │
      └─────────────┬────────────┘
                    │
      ┌─────────────▼────────────┐
      │  LoRA Adapter            │ ← Only this is trained!
      │  (~10M params)           │   0.1% of original model size
      │  Tiny weight matrices    │
      └──────────────────────────┘

HOW IT WORKS (Intuition):
  Original weight matrix W: [768 × 768] = 589,000 params
  LoRA decomposes the UPDATE into two small matrices:
    A: [768 × 8]  = 6,144 params
    B: [8 × 768]  = 6,144 params
  Total: 12,288 params instead of 589,000 → 48× fewer!

  The update = A × B added to the original weight.
  At inference: merge LoRA adapter back into model (zero overhead).

PROS:
  - 10-100× cheaper than full fine-tuning
  - Trains on a single GPU (even a consumer GPU)
  - Adapter is tiny (~50MB). Can have many adapters for different tasks.
  - No catastrophic forgetting (original model is preserved)
  - Can hot-swap adapters at runtime

CONS:
  - Slightly less quality than full fine-tuning (~1-3% lower)
  - Need to choose "rank" (r) hyperparameter

COST: $5-$100 for a 7B model (vs $1,000-$10,000 for full FT)
HARDWARE: 1 GPU (RTX 3090/4090 is enough for 7B model)
```

### QLoRA (Quantized LoRA) — Even Cheaper

```
WHAT: LoRA + quantize the frozen base model to 4-bit.

Original Model (7B, quantized to 4-bit = 3.5GB) + LoRA Adapter (16-bit)

      ┌──────────────────────────┐
      │  Original 7B @ 4-bit     │ ← FROZEN + compressed (3.5GB instead of 14GB)
      │  (frozen, 4-bit quantized│
      └─────────────┬────────────┘
                    │
      ┌─────────────▼────────────┐
      │  LoRA Adapter (16-bit)   │ ← Trained in full precision
      │  (~10M params)           │
      └──────────────────────────┘

PROS:
  - Can fine-tune a 70B model on a single 48GB GPU!
  - 7B model on a 8GB GPU (consumer laptop!)
  - Nearly same quality as full LoRA

CONS:
  - Training is ~30% slower than regular LoRA
  - Slight additional quality loss (~1%)

COST: $1-$50 for a 7B model
HARDWARE: 1 consumer GPU (8GB+ VRAM)
```

---

## 3. Fine-Tuning Pipeline (Step by Step)

### Step 1: Prepare Your Dataset

```jsonl
// training_data.jsonl — each line is one training example
{"messages": [{"role": "system", "content": "Classify the ticket priority."}, {"role": "user", "content": "Server down, prod offline"}, {"role": "assistant", "content": "{\"priority\": \"P1\", \"reason\": \"Production outage\"}"}]}
{"messages": [{"role": "system", "content": "Classify the ticket priority."}, {"role": "user", "content": "Need password reset"}, {"role": "assistant", "content": "{\"priority\": \"P4\", \"reason\": \"Routine access request\"}"}]}
{"messages": [{"role": "system", "content": "Classify the ticket priority."}, {"role": "user", "content": "Dashboard showing stale data"}, {"role": "assistant", "content": "{\"priority\": \"P3\", \"reason\": "Data inconsistency, non-blocking\"}"}]}

// You need: 500-10,000 examples minimum (more is better)
// Format: OpenAI chat format (system/user/assistant messages)
```

### Step 2: Split the Data

```python
# Always split into train/validation/test
# Train: 80% (model learns from this)
# Validation: 10% (tune hyperparameters)
# Test: 10% (final evaluation, never shown during training)

from sklearn.model_selection import train_test_split

data = load_jsonl("training_data.jsonl")
train, temp = train_test_split(data, test_size=0.2, random_state=42)
val, test = train_test_split(temp, test_size=0.5, random_state=42)
```

### Step 3: Fine-Tune with LoRA (Using HuggingFace)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer

# Load base model
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")

# Apply LoRA
lora_config = LoraConfig(
    r=16,                    # Rank (higher = more capacity, more params)
    lora_alpha=32,           # Scaling factor (usually 2× rank)
    target_modules=["q_proj", "v_proj"],  # Which layers to adapt
    lora_dropout=0.05,       # Regularization
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)

# Train
trainer = SFTTrainer(
    model=model,
    args=TrainingArguments(
        output_dir="./my-finetuned-model",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        learning_rate=2e-4,
        save_steps=100,
        fp16=True,            # Mixed precision (faster)
    ),
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)

trainer.train()

# Save the LoRA adapter (tiny! ~50MB)
model.save_pretrained("./my-lora-adapter")
```

### Step 4: Evaluate

```python
# Load test set and evaluate
# Compare base model vs fine-tuned model on:
#   - Accuracy on your task
#   - Format compliance (does it output valid JSON?)
#   - Hallucination rate
#   - General capability (didn't forget how to be helpful)

# Key metrics:
#   BLEU/ROUGE: text similarity (for summarization)
#   Exact match: for classification
#   LLM-as-judge: use GPT-4o to score outputs
```

### Step 5: Deploy

```python
# Option A: Merge LoRA into base model and deploy
from peft import PeftModel
base_model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
model = PeftModel.from_pretrained(base_model, "./my-lora-adapter")
merged_model = model.merge_and_unload()  # LoRA weights merged into base
merged_model.save_pretrained("./my-merged-model")

# Option B: Deploy with vLLM with LoRA hot-swapping
# vLLM can serve multiple LoRA adapters on one base model
# Switch adapters at runtime per request
```

---

## 4. Fine-Tuning Use Cases for FDE Customers

### Use Case 1: Custom Output Format

```
Customer: "We need the LLM to always output our proprietary incident JSON format."

BEFORE fine-tuning (prompt-based):
  System prompt includes 2000 tokens of format instructions.
  Model gets it right 85% of the time. Sometimes adds preamble text.

AFTER fine-tuning:
  Fine-tuned on 5000 examples of correctly formatted output.
  Model gets it right 99.5% of the time. No preamble. Always valid JSON.
  System prompt shrinks from 2000 → 200 tokens (saves tokens/cost).
```

### Use Case 2: Domain-Specific Language

```
Customer: Telecom company. The LLM doesn't understand their jargon.
  "BGP peering" "5G NR" "BSS/OSS" "MPLS VPN"

BEFORE: Model gives generic explanations. Sometimes wrong about telecom specifics.

AFTER fine-tuning on telecom Q&A:
  Model natively understands telecom terminology.
  Responses are more accurate and use correct jargon.
  Customers trust the AI more because it "speaks their language."
```

### Use Case 3: Cost Reduction via Model Shrinking

```
Customer is using GPT-4o at $10/1M tokens. Monthly bill: $50,000.

Option 1: Fine-tune Llama-3.1-8B on 10,000 GPT-4o outputs.
  Fine-tuned 8B model matches GPT-4o quality ON THIS SPECIFIC TASK.
  Self-host on 2 GPUs: $2,000/month.
  Savings: $48,000/month → $576,000/year.

This is called "distillation" — teach a small model to mimic a large one.
```

---

## 5. Catastrophic Forgetting — The Hidden Risk

```
PROBLEM:
  You fine-tune a model on your task (ticket classification).
  It becomes excellent at ticket classification.
  But it FORGETS how to do general reasoning, code generation, etc.

BEFORE FINE-TUNING:
  Model can classify tickets AND write code AND translate languages.

AFTER FINE-TUNING:
  Model is great at classifying tickets.
  But it can't write code anymore. It forgot.

SOLUTIONS:
  1. Mix in general data with your fine-tuning data (10-20% general data)
  2. Use LoRA (preserves original model — swap adapters per task)
  3. Use a lower learning rate (less aggressive updates)
  4. Evaluate on BOTH task-specific AND general benchmarks
```

---

## 6. OpenAI Fine-Tuning API (For Comparison)

```python
# OpenAI makes it very easy — but it's proprietary
import openai
import json

# Step 1: Upload training data
file = openai.files.create(
    file=open("training_data.jsonl", "rb"),
    purpose="fine-tune"
)

# Step 2: Create fine-tuning job
job = openai.fine_tuning.jobs.create(
    training_file=file.id,
    model="gpt-4o-mini-2024-07-18",   # Base model to fine-tune
    hyperparameters={
        "n_epochs": 3,
    }
)

# Step 3: Wait for completion (they email you)
# Step 4: Use the fine-tuned model
response = openai.chat.completions.create(
    model="ft:gpt-4o-mini:my-company::xxx",  # Your fine-tuned model
    messages=[{"role": "user", "content": "New ticket: server down"}]
)
```

---

## Interview Q&A

**Q: "Is fine-tuning required for most AI projects?"**
A: No. For 90% of use cases, prompt engineering + RAG is sufficient and far more cost-effective. I'd only consider fine-tuning when I need to change the model's BEHAVIOR — output format, tone, or task specialization — and prompt engineering can't achieve the target accuracy. Fine-tuning is for when you've exhausted simpler approaches and have a clear, measurable gap that behavior change would close.

**Q: "When would you choose RAG over fine-tuning?"**
A: Almost always for knowledge tasks. RAG injects real-time, updatable facts into the context. Fine-tuning bakes knowledge into weights, which becomes stale. RAG is also cheaper, faster to implement, and allows citing sources. I'd fine-tune only for format/style/tone — things that are about behavior, not knowledge.

**Q: "Explain LoRA in simple terms."**
A: LoRA freezes the original model and trains tiny "adapter" weights alongside it. Instead of updating 7 billion parameters, you train just 10 million — a 700× reduction. The adapter learns a low-rank approximation of the changes needed. At inference, the adapter is merged back into the model with zero overhead. This makes fine-tuning 10-100× cheaper — you can fine-tune a 7B model on a single consumer GPU for under $50.

**Q: "What is catastrophic forgetting and how do you prevent it?"**
A: When you fine-tune on a specific task, the model can forget general capabilities — it becomes a specialist but loses its broad skills. I prevent it by: (1) mixing 10-20% general data into the fine-tuning set, (2) using LoRA adapters that preserve the original model, (3) using a lower learning rate, and (4) evaluating on both task-specific and general benchmarks after fine-tuning.

**Q: "How would you decide between OpenAI fine-tuning vs open-source LoRA?"**
A: OpenAI fine-tuning when I want zero infrastructure overhead and the data can be sent to a third party. Open-source LoRA when: (1) data is sensitive (can't leave our network), (2) I want to own the model and not depend on OpenAI, (3) cost at scale favors self-hosting, or (4) I need the flexibility of hot-swappable adapters for different tasks. For FDE customers, open-source LoRA is often the better choice because it gives control and cost predictability.
