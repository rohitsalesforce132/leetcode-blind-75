# Designing ML Systems — Deployment, Monitoring & Continual Learning (Ch 7-9)

> **Source:** "Designing Machine Learning Systems" by Chip Huyen (O'Reilly, 2022)
> **Pages:** 461 | **This file covers:** Ch 7 (Deployment), Ch 8 (Distribution Shifts & Monitoring), Ch 9 (Continual Learning & Test in Production)
> **Why these 3 chapters:** They cover what happens AFTER model development — the production ML lifecycle that most engineers don't learn in school but is critical for FDE interviews.

---

## TABLE OF CONTENTS

1. [Chapter 7: Model Deployment and Prediction Service](#chapter-7)
2. [Chapter 8: Data Distribution Shifts and Monitoring](#chapter-8)
3. [Chapter 9: Continual Learning and Test in Production](#chapter-9)
4. [MLOps vs AI Engineering Comparison](#comparison)

---

## Chapter 7: Model Deployment and Prediction Service

### 4 ML Deployment Myths (Huyen Debunks)

```
┌──────────────────────────────────────────────────────────────────┐
│              ML DEPLOYMENT MYTHS                                  │
│                                                                  │
│  MYTH 1: "You only deploy one or two models at a time"          │
│  REALITY: Companies have HUNDREDS or THOUSANDS of models.       │
│  Netflix has 1000+ models in production. Google Search          │
│  uses thousands of models simultaneously.                        │
│  IMPLICATION: Model management is a real challenge.              │
│  You need versioning, rollback, A/B testing infrastructure.     │
│                                                                  │
│  MYTH 2: "If we don't do anything, model performance stays"     │
│  REALITY: Models degrade over time. Data distributions shift.   │
│  A model that was 95% accurate at launch may drop to 70%        │
│  within months. This is called MODEL DECAY.                      │
│  IMPLICATION: You need monitoring and retraining pipelines.     │
│                                                                  │
│  MYTH 3: "You won't need to update models as much"              │
│  REALITY: Many companies retrain DAILY or even HOURLY.          │
│  Twitter retrained recommendation models hourly.                 │
│  IMPLICATION: Automated retraining is essential.                │
│                                                                  │
│  MYTH 4: "Most ML engineers don't need to worry about scale"    │
│  REALITY: Scale affects everyone. Even a startup with 10K       │
│  users needs to handle inference latency, batch processing,     │
│  and model updates.                                              │
│  IMPLICATION: Infrastructure skills are mandatory.              │
└──────────────────────────────────────────────────────────────────┘
```

### Batch Prediction vs Online Prediction

```
┌──────────────────────────────────────────────────────────────────┐
│              BATCH vs ONLINE PREDICTION                            │
│                                                                  │
│  BATCH PREDICTION:                                               │
│    Pre-compute predictions for all users, store results.         │
│    Users read from pre-computed results.                         │
│                                                                  │
│    Example: Netflix recommendations computed nightly.            │
│    User opens app → reads pre-computed recommendations.          │
│                                                                  │
│    Pros:                                                         │
│    ✓ High throughput (process millions at once)                 │
│    ✓ Low latency at read time (just a lookup)                   │
│    ✓ Can use expensive models (time isn't critical)             │
│    ✓ Easy to debug (replay batch)                               │
│                                                                  │
│    Cons:                                                        │
│    ✗ Stale predictions (hours/days old)                          │
│    ✗ Can't personalize to current session context               │
│    ✗ Wasteful (computes for inactive users)                     │
│                                                                  │
│  ONLINE PREDICTION:                                              │
│    Compute prediction on-demand when user makes a request.       │
│                                                                  │
│    Example: Google Search ranking computed per query.            │
│    User searches → model ranks results in real-time.             │
│                                                                  │
│    Pros:                                                         │
│    ✓ Fresh predictions (uses latest data)                       │
│    ✓ Can use session context (what user did 2 min ago)          │
│    ✓ Only computes for active users                             │
│                                                                  │
│    Cons:                                                        │
│    ✗ Strict latency requirement (<100ms for web)                │
│    ✗ Needs always-on infrastructure                            │
│    ✗ Harder to debug (can't replay easily)                      │
│    ✗ Must handle traffic spikes                                 │
│                                                                  │
│  HYBRID APPROACH (Most Production Systems):                     │
│    Batch pre-compute base recommendations.                      │
│    Online model re-ranks using session context.                 │
│    Best of both worlds.                                          │
└──────────────────────────────────────────────────────────────────┘
```

### Model Compression Techniques

```
Huyen covers 4 compression techniques (critical for edge/mobile deployment):

1. LOW-RANK FACTORIZATION
   Decompose large weight matrices into smaller ones.
   Original: W (m×n) → U (m×k) × V (k×n), where k << min(m,n)
   Speedup: 2-5x depending on rank
   Quality: ~1-2% drop

2. KNOWLEDGE DISTILLATION
   Train a small "student" model to mimic a large "teacher" model.
   Teacher: 1B parameters, 95% accuracy
   Student: 100M parameters, 92% accuracy (learned from teacher's soft outputs)
   Deploy student → 10x faster, 1/10th the memory

3. PRUNING
   Remove weights/neurons that contribute least.
   Unstructured: Remove individual weights (creates sparse matrices)
   Structured: Remove entire channels/layers (hardware-friendly)
   Speedup: 2-10x with minimal quality loss

4. QUANTIZATION
   Reduce numerical precision:
   FP32 (4 bytes) → FP16 (2 bytes) → INT8 (1 byte) → INT4 (0.5 bytes)
   4x size reduction per step. Quality: 1-5% drop per step.
   CRITICAL for deploying on mobile devices.
```

### Cloud vs Edge Deployment

```
┌──────────────────────┬─────────────────────┬─────────────────────┐
│ Aspect               │ Cloud               │ Edge                │
├──────────────────────┼─────────────────────┼─────────────────────┤
│ Latency              │ Higher (network)    │ Lower (local)       │
│ Bandwidth            │ Needs connection    │ Works offline       │
│ Compute power        │ Unlimited (GPU/TPU) │ Limited (mobile)    │
│ Privacy              │ Data leaves device  │ Data stays on device│
│ Cost                 │ Pay per use         │ Free (user's device)│
│ Updates              │ Instant             │ Requires app update │
│ Model size           │ Unlimited           │ <50MB (mobile)      │
│ Battery              │ N/A                 │ Must be efficient   │
│ Best for             │ Large models,       │ Real-time, private, │
│                      │ batch, RAG, LLMs    │ offline, small models│
└──────────────────────┴─────────────────────┴─────────────────────┘
```

---

## Chapter 8: Data Distribution Shifts and Monitoring

### Why Models Fail in Production

```
┌──────────────────────────────────────────────────────────────────┐
│           CAUSES OF ML SYSTEM FAILURES                            │
│                                                                  │
│  SOFTWARE SYSTEM FAILURES (60% of failures):                     │
│    • Dependency failure (library breaks)                         │
│    • Deployment failure (wrong version deployed)                 │
│    • Hardware failure (GPU crash)                                │
│    • Downtime (server crash, network outage)                     │
│    → Fix with traditional DevOps/SRE practices                   │
│                                                                  │
│  ML-SPECIFIC FAILURES (40% of failures, growing):               │
│    • Data distribution shift (world changes, model doesn't)     │
│    • Edge cases (inputs model never saw in training)            │
│    • Degenerate feedback loops (model influences its own input) │
│    • Training-serving skew (different preprocessing pipelines)  │
│    → Fix with ML monitoring and continual learning               │
│                                                                  │
│  HUYEN'S KEY QUOTE:                                              │
│  "ML systems often fail silently."                               │
│  → Unlike software (crash, error, 500), ML degrades              │
│    gradually without any explicit error signal.                  │
│  → You need PROACTIVE monitoring to detect silent decay.         │
└──────────────────────────────────────────────────────────────────┘
```

### Types of Data Distribution Shifts

```
┌──────────────────────────────────────────────────────────────────┐
│           DATA DISTRIBUTION SHIFTS                                │
│                                                                  │
│  Given: Input X, Output Y, the model learns P(Y|X)              │
│                                                                  │
│  Three types of shifts:                                          │
│                                                                  │
│  1. COVARIATE SHIFT: P(X) changes, P(Y|X) stays same            │
│     Training: Photos taken in good lighting                      │
│     Production: Photos taken in bad lighting                     │
│     → Input distribution changed, but the relationship           │
│       between input and output is the same.                      │
│                                                                  │
│  2. LABEL SHIFT: P(Y) changes, P(X|Y) stays same                │
│     Training: 10% spam emails                                    │
│     Production: 30% spam emails (spammers got aggressive)        │
│     → The fraction of each class changed.                        │
│                                                                  │
│  3. CONCEPT DRIFT: P(Y|X) changes                                │
│     Training: "sick" = COVID symptoms in 2020                    │
│     Production: "sick" = different symptoms in 2023              │
│     → The relationship between input and output changed.         │
│     → This is the HARDEST to detect and fix.                     │
│                                                                  │
│  REAL-WORLD EXAMPLES:                                            │
│    • COVID: Shopping behavior shifted overnight                  │
│    • Seasonal: Winter fashion ≠ summer fashion                   │
│    • Trends: Slang evolves, user preferences change              │
│    • Competitor: Competitor launches → user behavior shifts      │
│    • Regulations: New law changes what's acceptable              │
└──────────────────────────────────────────────────────────────────┘
```

### Detecting Distribution Shifts

```
TECHNIQUES:

1. STATISTICAL DISTANCE METRICS
   Compare training vs production distributions using:
   • KL Divergence
   • JS Divergence
   • Population Stability Index (PSI)
   • Wasserstein Distance
   PSI > 0.2 → significant shift detected

2. FEATURE-LEVEL MONITORING
   Track statistics of each feature over time:
   • Mean, std, min, max, percentiles
   • Missing value rate
   • Cardinality (number of unique values)
   Alert if any deviates beyond threshold

3. NULL HYPOTHESIS TESTING
   Null: Production distribution = Training distribution
   Use Kolmogorov-Smirnov test, chi-square test
   If p < 0.05 → reject null → distribution shifted

4. PERFORMANCE-BASED DETECTION
   Monitor model's actual performance (accuracy, F1, etc.)
   If it drops beyond threshold → investigate
   CHALLENGE: Need ground truth labels, which may be delayed
```

### Monitoring Toolbox

```
┌──────────────────────────────────────────────────────────────────┐
│              ML MONITORING METRICS                                │
│                                                                  │
│  OPERATIONAL METRICS (same as traditional software):             │
│    • Latency (P50, P95, P99)                                    │
│    • Throughput (requests/sec)                                  │
│    • CPU/GPU utilization                                        │
│    • Memory usage                                               │
│    • Error rate (500s, timeouts)                                │
│                                                                  │
│  ML-SPECIFIC METRICS:                                            │
│    • Prediction distribution (are outputs changing?)             │
│    • Feature drift (are inputs changing?)                        │
│    • Model accuracy (if labels available)                        │
│    • Confidence score distribution                               │
│    • Input/output correlation                                    │
│                                                                  │
│  ML-SPECIFIC ALERTS:                                             │
│    • "Accuracy dropped from 92% to 85% overnight"                │
│    • "Feature 'user_age' mean shifted from 35 to 42"            │
│    • "Model is predicting 3x more 'positive' than usual"         │
│    • "Null rate for feature 'income' went from 5% to 20%"       │
│                                                                  │
│  TOOLS:                                                          │
│    Evidently AI: Open-source drift detection                     │
│    Arize: ML observability platform                              │
│    Fiddler: Model monitoring                                     │
│    WhyLabs: Data quality monitoring                              │
│    Prometheus + Grafana: General metrics + dashboards            │
└──────────────────────────────────────────────────────────────────┘
```

### Degenerate Feedback Loops

```
A DANGEROUS ML-SPECIFIC FAILURE:

  1. Recommendation model shows popular items more often
  2. Users click on popular items (because they're shown more)
  3. Model learns: "these items are MORE popular"
  4. Model shows them EVEN MORE → popularity compounds
  5. Long-tail items NEVER get shown → filter bubble

  This is a DEGENERATE FEEDBACK LOOP:
  The model's output influences the data it trains on.

SOLUTIONS:
  • Exploration: Occasionally show random items (epsilon-greedy)
  • Position bias correction: Discount clicks by position rank
  • Two-tower models: Separate "interest" from "exposure"
  • Counterfactual evaluation: "What WOULD have happened?"

INTERVIEW CONNECTION: "This is exactly why my AgentGuard project
 includes output diversity checks — to prevent the agent from
 always choosing the same tool."
```

---

## Chapter 9: Continual Learning and Test in Production

### The 4 Stages of Continual Learning

```
┌──────────────────────────────────────────────────────────────────┐
│        4 STAGES OF CONTINUAL LEARNING MATURITY                    │
│                                                                  │
│  STAGE 0: NO CONTINUAL LEARNING (Manual retraining)              │
│    • Model trained once, deployed, never updated                 │
│    • Performance degrades over time                              │
│    • When it breaks: Hire consultants to retrain from scratch    │
│    → Most companies start here. It's the "grocery store" story.  │
│                                                                  │
│  STAGE 1: MODEL-AS-IS RETRAINING                                │
│    • Retrain periodically (weekly/monthly) from scratch          │
│    • Same model architecture, same hyperparameters               │
│    • New data is added to training set                           │
│    • Human validates before deployment                           │
│    → Good for stable environments                                │
│                                                                  │
│  STAGE 2: STATEFUL TRAINING (Fine-tuning)                       │
│    • Don't train from scratch — continue from last checkpoint    │
│    • Fine-tune on new data (incremental learning)                │
│    • Faster than retraining from scratch                         │
│    • Risk: Catastrophic forgetting (model forgets old patterns) │
│    → Most mature companies are here                              │
│                                                                  │
│  STAGE 3: CONTINUAL LEARNING (Automated)                         │
│    • Model adapts in micro-batches (every 512-1024 samples)      │
│    • Champion model stays in production                          │
│    • Challenger model is trained on new data                     │
│    • If challenger beats champion → swap automatically           │
│    • If challenger fails → discard, keep champion                │
│    → Cutting edge (few companies fully here)                     │
└──────────────────────────────────────────────────────────────────┘
```

### Champion vs Challenger Pattern

```
    ┌─────────────┐
    │  CHAMPION   │ ← Current production model
    │  (Model A)  │ ← Serves 100% of traffic
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐
    │  CHALLENGER │ ← Trained on new data
    │  (Model B)  │ ← NOT serving traffic yet
    └──────┬──────┘
           │
           ▼
    ┌─────────────────────┐
    │  Evaluate Challenger │
    │  - A/B test          │
    │  - Shadow mode       │
    │  - Canary release    │
    └──────┬──────────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
  BETTER?      WORSE?
     │           │
     ▼           ▼
  SWAP!      DISCARD
  Model B    Keep Model A
  becomes    as champion
  champion

This pattern is THE foundation of production ML lifecycle management.
```

### Test in Production Methods

```
┌──────────────────────────────────────────────────────────────────┐
│              TEST IN PRODUCTION METHODS                            │
│                                                                  │
│  1. SHADOW DEPLOYMENT                                            │
│     New model runs alongside production model.                   │
│     Both make predictions, but only production model's           │
│     predictions are shown to users.                              │
│     Compare: if shadow model predicts differently, log it.       │
│     Risk: Zero (users never see new model's output)              │
│     Use case: Validate new model before any user impact          │
│                                                                  │
│  2. A/B TESTING                                                  │
│     Split traffic: 90% → Model A, 10% → Model B                 │
│     Compare metrics (CTR, accuracy, revenue)                     │
│     Statistical significance: need enough samples                │
│     Risk: 10% of users see potentially worse model               │
│     Use case: Compare two models in production                   │
│                                                                  │
│  3. CANARY RELEASE                                               │
│     Start with 1% → 5% → 10% → 50% → 100%                       │
│     Monitor at each step. Rollback if metrics degrade.           │
│     Risk: Minimal (small percentage, gradual increase)           │
│     Use case: Safely deploy any model update                     │
│                                                                  │
│  4. INTERLEAVING                                                 │
│     Mix results from both models in the SAME user session.       │
│     Model A: results [1, 3, 5, 7]                               │
│     Model B: results [2, 4, 6, 8]                               │
│     Interleaved: [1, 2, 3, 4, 5, 6, 7, 8]                      │
│     Measure which results get clicked more.                      │
│     Faster than A/B testing (fewer samples needed).              │
│     Use case: Search ranking, recommendation comparison          │
│                                                                  │
│  5. BANDITS                                                      │
│     Dynamically allocate traffic based on performance.           │
│     If Model B is winning → give it more traffic.                │
│     Converges faster than A/B testing.                           │
│     Risk: Early losers never recover (explore vs exploit).       │
│     Use case: News recommendation, ad optimization              │
└──────────────────────────────────────────────────────────────────┘
```

### How Often to Retrain?

```
Huyen's framework for retraining frequency:

┌──────────────────┬─────────────────────┬─────────────────────────┐
│ Retrain Freq     │ When Appropriate    │ Examples                │
├──────────────────┼─────────────────────┼─────────────────────────┤
│ Never            │ Static environment  │ Digit recognition       │
│ Annually         │ Slow change         │ Tax rules               │
│ Quarterly        │ Moderate change     │ Seasonal products       │
│ Monthly          │ Regular change      │ Credit scoring          │
│ Weekly           │ Fast change         │ Content trends          │
│ Daily            │ Very fast change    │ News, social media      │
│ Hourly           │ Real-time relevance │ Twitter recs, ads       │
│ Per-request      │ Near-zero latency   │ Rare (most don't need)  │
└──────────────────┴─────────────────────┴─────────────────────────┘

HUYEN'S ADVICE:
  "Start with the longest interval that makes sense.
   If weekly retraining gives no improvement over monthly,
   stick with monthly. Don't add complexity for no gain."

KEY INSIGHT: Retraining frequency is an INFRASTRUCTURE problem,
  not a MODEL problem. The hard part isn't training — it's
  the pipeline that:
  1. Collects new data
  2. Validates data quality
  3. Trains the model
  4. Evaluates the model
  5. Deploys if better
  ... ALL AUTOMATICALLY
```

---

## MLOps vs AI Engineering Comparison

```
┌────────────────────┬────────────────────────┬──────────────────────┐
│ Aspect             │ Designing ML Systems   │ AI Engineering       │
│                    │ (DMLS, 2022)           │ (AI Eng, 2024)       │
├────────────────────┼────────────────────────┼──────────────────────┤
│ Focus              │ Traditional ML          │ Foundation models    │
│                    │ (XGBoost, neural nets) │ (LLMs, diffusion)    │
│ Data               │ Feature engineering    │ RAG + context        │
│ Training           │ Train from scratch     │ Fine-tune pretrained  │
│ Deployment         │ Serve predictions      │ API + self-hosted    │
│ Monitoring         │ Data drift, accuracy   │ Hallucination, cost  │
│ Evaluation         │ Precision, recall, F1  │ AI-as-judge, human   │
│ Infrastructure     │ Feature stores, MLflow │ Vector DBs, vLLM     │
│ Key challenge      │ Distribution shift     │ Hallucination        │
│ Retraining         │ Continual learning     │ RAG update + finetune│
│ Cost               │ Training compute       │ Inference tokens     │
│ Failure mode       │ Silent decay           │ Hallucination, cost  │
│ Best for           │ Tabular, CV, classical │ Text, code, agents   │
└────────────────────┴────────────────────────┴──────────────────────┘

THEY ARE COMPLEMENTARY:
  DMLS teaches you PRODUCTION ML FUNDAMENTALS.
  AI Engineering teaches you FOUNDATION MODEL SPECIFICS.
  Together: Complete MLOps + AI engineering knowledge.
```

---

## Interview Q&As

### Q1: "How do you handle model degradation in production?"

"I implement continual learning — the champion/challenger pattern. The current production model (champion) serves all traffic. A new model (challenger) is trained on recent data. The challenger is evaluated via shadow deployment (runs alongside champion, predictions compared but not shown to users). If it performs better, I gradually deploy via canary release (1% → 5% → 50% → 100%). If it's worse, I discard it and keep the champion. The key is that this entire pipeline is automated — data collection, training, evaluation, and deployment."

### Q2: "What's the difference between covariate shift and concept drift?"

"Covariate shift means the input distribution P(X) changed but the relationship P(Y|X) stayed the same. Example: a model trained on daytime photos deployed at night. Concept drift means P(Y|X) itself changed — the relationship between input and output is different. Example: 'sick' meant COVID symptoms in 2020 but different symptoms in 2023. Concept drift is harder to detect because the model's input hasn't changed — only what the correct output should be."

### Q3: "How would you deploy an ML model with zero downtime?"

"I'd use blue-green deployment. Two identical environments (blue and green) run simultaneously. The current model serves from blue. I deploy the new model to green, run health checks and shadow evaluation. When green is verified healthy, I switch the load balancer to route all traffic to green. Blue stays warm as fallback. If any issue arises, I switch back to blue instantly — zero downtime, instant rollback."

### Q4: "What is a degenerate feedback loop and how do you prevent it?"

"A degenerate feedback loop occurs when a model's output influences the data it trains on, creating a self-reinforcing cycle. Example: a recommendation model shows popular items more → users click them more → model thinks they're even more popular → shows them even more. I prevent it with exploration (epsilon-greedy: occasionally show random items), position bias correction (discount clicks based on rank position), and counterfactual evaluation (estimate what would have happened without the bias)."

### Q5: "Batch prediction vs online prediction — when would you use each?"

"I use batch prediction when predictions can be stale (hours old is OK), there's high throughput need, and I can afford to compute for all users. Example: nightly product recommendations. I use online prediction when freshness matters, I need session context, and latency is acceptable. Example: search ranking. Most production systems use hybrid: batch pre-computes base predictions, online model re-ranks using real-time context."

### Q6: "How do you detect data distribution shifts?"

"Three approaches. First, statistical distance metrics: compute Population Stability Index (PSI) or KL divergence between training and production feature distributions. PSI > 0.2 indicates significant shift. Second, feature-level monitoring: track mean, std, percentiles, and null rates for each feature. Alert on threshold violations. Third, performance monitoring: if model accuracy or confidence scores deviate significantly, investigate the underlying data distribution. Tools like Evidently AI or Arize automate this."

### Q7: "What are the 4 stages of continual learning?"

"Stage 0: No retraining (model degrades, manual fix). Stage 1: Model-as-is retraining (retrain from scratch periodically with same architecture). Stage 2: Stateful training (fine-tune from last checkpoint — faster, but risk of catastrophic forgetting). Stage 3: Automated continual learning (champion/challenger with micro-batch updates, automatic swap if challenger wins). Most companies are at Stage 1-2. The challenge isn't the model — it's the infrastructure to automate the entire pipeline."

---

> **Next:** Foundations (Ch 1-3) → `dmls-ch01-03-foundations.md`
> Model Development (Ch 4-6) → `dmls-ch04-06-development.md`
> Infrastructure (Ch 10-11) → `dmls-ch10-11-infrastructure-human.md`
