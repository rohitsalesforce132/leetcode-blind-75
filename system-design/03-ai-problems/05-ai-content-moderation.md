# Design an AI Content Moderation System

> **Analogy:** Airport security with multiple checkpoints. First a metal detector (fast, automated, catches most cases). Then a pat-down (ML model, catches nuanced cases). Then manual inspection by a security officer (human review for edge cases).

---

## 1. Requirements

### Functional Requirements
- Automatically detect and remove: hate speech, spam, PII, NSFW content, violence
- Process text, images, and video
- Support multiple languages
- Human-in-the-loop (HITL) review for borderline cases
- Escalation workflow for serious violations
- Policy engine — configurable rules per region/product

### Non-Functional Requirements
- **Latency:** < 100ms for text, < 500ms for images (real-time moderation)
- **Scale:** 10B+ content items/day
- **Accuracy:** > 99% precision for auto-remove (false positives are VERY costly)
- **Recall:** > 95% (catch almost all violations)
- **Cost:** GPU inference is expensive — must be efficient

---

## 2. The Multi-Layer Architecture

Content moderation is never a single model. It's a **cascade of filters**, each more expensive than the last:

```
Incoming Content (post, comment, image)
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: Rule-Based Filter (Heuristics)                │
│  - Banned word lists, regex patterns                    │
│  - Exact match against known-bad URLs                   │
│  - Rate-based spam detection (same text from 1000 IPs)  │
│  Cost: ~$0 per item | Latency: <1ms                     │
│  Catches: ~60% of obvious violations                    │
└───────────────────────┬─────────────────────────────────┘
                        │ passes filter
                        ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 2: Lightweight ML Classifier                     │
│  - Fast text classifier (DistilBERT, fastText)          │
│  - Pre-trained image classifier (MobileNet)             │
│  Cost: ~$0.0001/item | Latency: 5-20ms                  │
│  Catches: ~30% more violations                          │
└───────────────────────┬─────────────────────────────────┘
                        │ borderline or uncertain
                        ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 3: Heavy ML Model (GPU)                          │
│  - Large language model for nuanced hate speech         │
│  - Object detection for image/video (YOLO, CLIP)        │
│  Cost: ~$0.01/item | Latency: 50-200ms                  │
│  Catches: ~8% more violations                           │
└───────────────────────┬─────────────────────────────────┘
                        │ still uncertain or high-severity
                        ▼
┌─────────────────────────────────────────────────────────┐
│  LAYER 4: Human Review Queue (HITL)                     │
│  - Human moderators review flagged content              │
│  - Escalation: legal threats, violence, CSAM            │
│  Cost: ~$0.50-5.00/item | Latency: minutes to hours     │
│  Catches: the final ~2%                                  │
└─────────────────────────────────────────────────────────┘
```

**Key Insight:** Each layer filters out clear cases, so only a small fraction reaches the expensive layers. Layer 1 catches 60% for nearly zero cost. Only 2% ever needs human review.

---

## 3. Architecture Diagram

```
┌────────┐     ┌──────────────┐     ┌─────────────────────────┐
│ Client │ ──> │ API Gateway  │ ──> │ Moderation Orchestrator  │
│ (post) │     │ (Rate Limit) │     │ (decision engine)        │
└────────┘     └──────────────┘     └──────────┬──────────────┘
                                                │
                    ┌───────────────────────────┼──────────────────┐
                    │                           │                  │
                    ▼                           ▼                  ▼
           ┌──────────────┐          ┌──────────────┐    ┌──────────────┐
           │ Rule Engine  │          │ ML Inference │    │ Review Queue │
           │ (Redis rules)│          │ Service      │    │ (Kafka)      │
           └──────────────┘          │ (GPU Cluster)│    └──────┬───────┘
                                     └──────────────┘           │
                                                                ▼
              ┌────────────────┐                        ┌──────────────┐
              │ Policy Engine  │ <────────────────────  │ HITL Dashboard│
              │ (Config Service)│                       │ (Human Mods) │
              └────────────────┘                        └──────────────┘
```

---

## 4. Component Design

### 4.1 Moderation Orchestrator (Decision Engine)

```python
class ModerationOrchestrator:
    """Routes content through moderation layers."""

    def moderate(self, content):
        results = []

        # Layer 1: Fast rules
        rule_result = self.rule_engine.check(content)
        if rule_result.decision == "REJECT":
            return ModerationResult(decision="REJECT", reason=rule_result.reason)

        # Layer 2: Lightweight ML
        ml_result = self.lightweight_classifier.predict(content)
        if ml_result.confidence > 0.95:
            if ml_result.label == "safe":
                return ModerationResult(decision="APPROVE")
            else:
                return ModerationResult(decision="REJECT", reason=ml_result.label)

        # Layer 3: Heavy model (low confidence → escalate)
        if ml_result.confidence < 0.70:
            heavy_result = self.heavy_model.predict(content)
            if heavy_result.severity == "high":
                return ModerationResult(decision="ESCALATE_TO_HUMAN")
            elif heavy_result.confidence > 0.90:
                return ModerationResult(decision=heavy_result.label)

        # Layer 4: Uncertain → human review
        self.review_queue.enqueue(content, results=[rule_result, ml_result])
        return ModerationResult(decision="PENDING_REVIEW")
```

### 4.2 ML Inference Service (GPU Cluster)

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ GPU Server 1  │     │ GPU Server 2  │     │ GPU Server N  │
│ (Text models) │     │ (Image models)│     │ (Video models)│
│               │     │               │     │               │
│ - BERT-base   │     │ - YOLO v8     │     │ - Video CLIP  │
│ - FastText    │     │ - NSFW model  │     │ - Keyframe    │
│ - Lang detect │     │ - OCR (text)  │     │   extraction  │
└───────────────┘     └───────────────┘     └───────────────┘
         ↑                     ↑                     ↑
         └─────────────────────┼─────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Load Balancer        │
                    │ (GPU-aware routing)  │
                    └──────────────────────┘
```

### 4.3 Policy Engine

Different rules for different contexts:

```yaml
# Policy configuration example
policies:
  default:
    - rule: no_hate_speech
      threshold: 0.85
      action: REJECT
    - rule: no_spam
      threshold: 0.90
      action: SHADOWBAN

  children_app:
    - rule: no_profanity
      threshold: 0.50  # much stricter for kids' app
      action: REJECT
    - rule: no_violence
      threshold: 0.30
      action: REJECT

  region_eu:
    - rule: gdpr_pii_detection
      threshold: 0.80
      action: REDACT  # redact PII instead of removing
```

### 4.4 Human Review Queue

```
Content flagged as "uncertain"
    │
    ▼
[Kafka Review Queue]
    │
    ├── Priority 1: CSAM, terror content (immediate, legal team)
    ├── Priority 2: Violence, hate speech (queue within 1 hour)
    ├── Priority 3: Spam, borderline (queue within 24 hours)
    └── Priority 4: Appeals (user says "I was wrongly removed")
    │
    ▼
[HITL Dashboard]
    - Moderator sees content + ML scores + context
    - Decision: Approve / Remove / Escalate
    - Moderator decision feeds back to retrain ML models
```

---

## 5. Data Pipeline & Feedback Loop

```
                     ┌─────────────────────┐
                     │  Moderation Decisions│
                     │  (auto + human)      │
                     └─────────┬───────────┘
                               │
                               ▼
                     ┌─────────────────────┐
                     │  Training Data       │
                     │  Pipeline            │
                     │                     │
                     │  - Human labels      │
                     │  - Model predictions │
                     │  - Appeal outcomes   │
                     │  - False positive/   │
                     │    false negative    │
                     └─────────┬───────────┘
                               │
                               ▼
                     ┌─────────────────────┐
                     │  Model Retraining    │
                     │  (weekly/biweekly)   │
                     │                     │
                     │  - Fine-tune on new  │
                     │    labeled data      │
                     │  - A/B test new model│
                     │    vs current        │
                     │  - Shadow deploy     │
                     └─────────┬───────────┘
                               │
                               ▼
                     ┌─────────────────────┐
                     │  Updated Models      │
                     │  deployed to GPU     │
                     │  inference cluster   │
                     └─────────────────────┘
```

The human review decisions become training data for the next model iteration. This is the **human-in-the-loop feedback loop**.

---

## 6. Scaling AI Inference

### Challenge: 10B items/day at < 100ms latency

```
10B items / 86400 seconds ≈ 115,000 items/second

With cascaded layers:
- Layer 1 (rules): 115K/s on CPU (cheap)
- Layer 2 (lightweight ML): ~46K/s reach here (40% pass layer 1)
- Layer 3 (heavy GPU): ~4.6K/s reach here (10% pass layer 2)
- Layer 4 (human): ~0.92K/s = 920 items/sec → 79K items/day for humans
```

### GPU Optimization

| Technique | Savings |
|-----------|---------|
| **Model quantization** (FP16/INT8) | 2-4× throughput, half VRAM |
| **Batching** (process 32-128 items together) | 10-20× throughput vs single |
| **Model distillation** (small model mimics large) | 5-10× faster, minimal accuracy loss |
| **Dynamic batching** (group by size) | Reduces padding waste |
| **Model cascading** (cheap → expensive) | Only 4% ever hits GPU |

---

## 7. Handling Different Content Types

### Text Moderation
```
Input: "You guys are all [expletive] idiots"
    │
    ├── Rule engine: catches "[expletive]" (exact match) → REJECT
    │
    └── If no exact match:
        ML classifier → toxicity score: 0.92 → REJECT
```

### Image Moderation
```
Input: Uploaded image
    │
    ├── Layer 1: Hash check (perceptual hash against known-bad database)
    │
    ├── Layer 2: NSFW classifier (probability of adult content)
    │
    ├── Layer 3: Object detection (weapons, drugs, violence)
    │
    └── OCR + text moderation (if image contains text)
```

### Video Moderation
```
Input: Video upload
    │
    ├── Extract keyframes (1 frame per second)
    │
    ├── Run image moderation on each keyframe
    │
    ├── Transcribe audio → run text moderation
    │
    └── Flag timestamps with violations
```

---

## 8. Metrics & Monitoring

| Metric | Target | Alert |
|--------|--------|-------|
| Auto-decision rate | > 95% | < 90% (humans overloaded) |
| False positive rate | < 1% | > 3% (users angry, appeals spike) |
| False negative rate (missed) | < 5% | > 8% (brand risk, regulatory) |
| Human review queue depth | < 10K items | > 50K (backlog growing) |
| Model inference latency (text) | < 50ms | > 100ms |
| Model inference latency (image) | < 200ms | > 500ms |
| Appeal overturn rate | < 10% | > 20% (model making bad decisions) |

---

## Interview Q&A

**Q: Why not just use one large LLM for everything?**
A: Cost and latency. A single LLM call costs ~$0.01-0.05 per item and takes 500ms+. At 10B items/day, that's $100M-500M/day just in inference. The cascaded approach means 96% of items never touch a GPU. The LLM is reserved for the hardest 2% of cases.

**Q: How do you handle false positives? (Content wrongly removed)**
A: Three mechanisms: (1) Appeal system — user can request review. (2) Human review for borderline cases before removal. (3) Conservative thresholds — only auto-remove at >95% confidence. Borderline content gets human review.

**Q: How do you handle new types of abuse that the model hasn't seen?**
A: The human review queue catches novel abuse. When moderators see a new pattern, it's labeled and fed into the training pipeline. The model is retrained biweekly. For urgent threats (e.g., a viral dangerous challenge), we add emergency rule-based filters immediately.

**Q: How do you moderate at scale across different languages and cultures?**
A: (1) Multi-lingual models (XLM-RoBERTa, mBERT). (2) Language-specific fine-tuned models for top languages. (3) Cultural context in the policy engine (what's offensive varies by region). (4) Region-specific human moderation teams.

**Q: What about adversarial attacks? (Users trying to bypass filters)**
A: Common tactics: unicode tricks (rеplаcing letters with Cyrillic), embedding text in images, misspellings, coded language. Countermeasures: text normalization (convert unicode → ASCII), OCR for image-embedded text, adversarial training data, and behavioral signals (same IP posting 5000 times → spam).
