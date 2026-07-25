# Designing ML Systems — Training Data, Features & Model Dev (Ch 4-6)

> **Source:** "Designing Machine Learning Systems" by Chip Huyen
> **Coverage:** Ch 4 (Training Data), Ch 5 (Feature Engineering), Ch 6 (Model Development & Offline Eval)

---

## Chapter 4: Training Data

### Sampling Methods

```
┌──────────────────────────────────────────────────────────────────┐
│              SAMPLING METHODS                                      │
│                                                                  │
│  NONPROBABILITY SAMPLING:                                        │
│    Convenience sample (whatever data you can get).               │
│    Common but biased. "The first N rows from the database."     │
│                                                                  │
│  SIMPLE RANDOM SAMPLING:                                         │
│    Every sample has equal probability of selection.              │
│    Unbiased but may miss rare classes.                           │
│                                                                  │
│  STRATIFIED SAMPLING:                                            │
│    Divide population into strata, sample from each.             │
│    Ensures representation of all classes.                        │
│    Example: 50% spam, 50% ham (even if 10% spam in reality)    │
│                                                                  │
│  WEIGHTED SAMPLING:                                              │
│    Samples with higher importance are picked more often.        │
│    Example: Recent data weighted higher than old data.          │
│                                                                  │
│  RESERVOIR SAMPLING:                                             │
│    Sample from a stream of unknown length.                       │
│    Maintains a fixed-size reservoir as stream flows.            │
│    Each item has equal probability of being in reservoir.       │
│    Use case: Sample from a real-time event stream.              │
│                                                                  │
│  IMPORTANCE SAMPLING:                                            │
│    Sample more from high-loss regions to focus learning.        │
│    Use case: Active learning, RL training.                      │
└──────────────────────────────────────────────────────────────────┘
```

### Labeling Strategies

```
HAND LABELS:
  Humans annotate each example.
  Cost: $0.05-$5 per label (depends on complexity)
  Problem: Slow, expensive, noisy (annotator disagreement)

NATURAL LABELS:
  Ground truth emerges naturally from the system.
  Example: "Did the user click?" → implicit relevance label.
  Example: "Did the package arrive on time?" → delivery label.
  Advantage: Free, accurate, large volume.
  Challenge: Feedback delay (labels arrive days/weeks later).

HANDLING LACK OF LABELS:
  1. WEAK SUPERVISION (Snorkel):
     Heuristic rules generate noisy labels.
     Rule 1: Contains "free" → likely spam (70% confidence)
     Rule 2: From known sender → likely ham
     System combines rules into probabilistic labels.

  2. SEMI-SUPERVISED LEARNING:
     Train on small labeled set, use model to label unlabeled data.
     Self-training: Model predicts labels → adds high-confidence
     predictions to training set → retrains.
     Challenge: Confirmation bias (model reinforces its own mistakes).

  3. ACTIVE LEARNING:
     Model identifies WHICH examples to label next.
     "I'm most uncertain about these 100 examples — please label them."
     Maximizes information per labeled example.
     Reduces labeling cost by 10-100x.
```

### Class Imbalance

```
THE PROBLEM:
  99% normal traffic, 1% fraud.
  Model predicts "normal" for everything → 99% accuracy, 0% fraud caught.

SOLUTIONS:

1. RESAMPLING:
   Oversample minority: Duplicate fraud examples
   Undersample majority: Remove some normal examples
   SMOTE: Synthesize new minority examples (interpolation)

2. LOSS WEIGHTING:
   Penalize mistakes on minority class MORE.
   loss = weight_fraud × loss_fraud + weight_normal × loss_normal
   Set weight_fraud = 99, weight_normal = 1

3. THRESHOLD ADJUSTMENT:
   Instead of 0.5 decision threshold, use 0.1.
   Lower threshold → catch more fraud (more false positives).
   Trade-off: recall vs precision.

4. ENSEMBLE METHODS:
   Train multiple models on balanced subsets (bagging).
   Combine predictions → more robust to imbalance.

HUYEN'S KEY INSIGHT:
  "Don't just fix the class imbalance. Understand WHY it exists.
   Maybe your fraud detection is catching only one type of fraud.
   Collect more diverse fraud examples instead of just duplicating."
```

---

## Chapter 5: Feature Engineering

### Learned vs Engineered Features

```
ENGINEERED (traditional ML — XGBoost, Random Forest):
  Human expert designs features: "age × income × zip_code"
  Pros: Interpretable, works with small data
  Cons: Requires domain expertise, time-consuming

LEARNED (deep learning, foundation models):
  Model learns features from raw data automatically.
  Pros: No manual feature engineering, works with large data
  Cons: Black box, requires large data and compute

REALITY: Most production systems use a MIX.
  Tabular data → engineered features (XGBoost)
  Text/images → learned features (deep learning)
  Hybrid → engineered features + learned embeddings
```

### Common Feature Engineering Operations

```
1. MISSING VALUES:
   Delete rows with missing data (if <5%)
   Fill with mean/median/mode (simple)
   Fill with model prediction (KNN imputation)
   Add "is_missing" binary flag (model learns missingness pattern)

2. SCALING:
   Min-max: (x - min) / (max - min) → [0, 1]
   Standard: (x - mean) / std → mean=0, std=1
   Log: log(x) → handles skewness
   CRITICAL: Fit scaler on TRAINING data only. Apply to test/production.

3. ENCODING CATEGORICALS:
   One-hot: [red, green, blue] → [1,0,0] (problematic for high cardinality)
   Label: [red=1, green=2, blue=3] (introduces false ordering)
   Target: Replace category with mean of target (risk of overfitting)
   Embedding: Learn dense vector for each category (deep learning)

4. DATA LEAKAGE:
   THE #1 MISTAKE in ML projects.
   Using information during training that wouldn't be available at inference.

   Common leaks:
   - Normalizing using test data statistics
   - Including future information as a feature
   - Duplicating rows across train/test split
   - Including the target variable as a feature (directly or indirectly)

   DETECTION: "If the model performs suspiciously well, check for leakage."
```

---

## Chapter 6: Model Development and Offline Evaluation

### Ensemble Methods

```
1. BAGGING (Bootstrap Aggregating):
   Train N independent models on different random subsets.
   Combine by averaging (regression) or voting (classification).
   Example: Random Forest = bagged decision trees.
   Reduces variance (overfitting).

2. BOOSTING:
   Train models sequentially. Each model corrects the previous.
   Example: XGBoost, LightGBM, CatBoost.
   Reduces bias (underfitting).
   State-of-the-art for tabular data.

3. STACKING:
   Train diverse base models (e.g., XGBoost + Neural Net + RF).
   Train a meta-model on their predictions.
   Example: Netflix Prize winning solution used stacking.
   Pros: Captures different patterns from different models.
   Cons: Complex, harder to deploy, harder to debug.
```

### Experiment Tracking

```
Huyen emphasizes: Track EVERYTHING.

  WHAT TO TRACK:
    • Model architecture and hyperparameters
    • Training/validation metrics per epoch
    • Dataset version used
    • Feature engineering pipeline version
    • Code commit hash
    • Environment (library versions, GPU type)
    • Training time, cost

  TOOLS:
    MLflow: Open-source experiment tracking + model registry
    Weights & Biases: Rich visualization, team collaboration
    Neptune.ai: Lightweight experiment tracking
    Comet.ml: Experiment management + optimization

  GOLDEN RULE: "If it's not tracked, it didn't happen."
  Every model should be reproducible from its tracking record.
```

### Evaluation Methods

```
BASELINES:
  Always compare against baselines:
  1. Random baseline (predict randomly)
  2. Majority class baseline (predict most common class)
  3. Simple heuristic (rules-based)
  4. Previous production model

  If your fancy ML model barely beats the heuristic,
  the complexity isn't worth it.

EVALUATION APPROACHES:
  1. HOLDOUT: Train on 80%, test on 20% (simple, fast)
  2. K-FOLD CROSS-VALIDATION: Rotate test set. More reliable.
  3. TIME-BASED SPLIT: Train on Jan-Jun, test on Jul-Dec.
     CRITICAL for time-series (never randomly split temporal data)
  4. BOOTSTRAP: Resample with replacement to estimate confidence intervals

HUYEN'S RULE:
  "Offline evaluation tells you if the model COULD work.
   Only production evaluation tells you if it DOES work."
```

---

## Interview Q&As

### Q1: "How do you handle class imbalance?"

"Four approaches. Resampling: oversample minority (SMOTE) or undersample majority. Loss weighting: penalize minority class errors more. Threshold adjustment: lower the decision threshold to catch more minority cases. Ensemble methods: train multiple models on balanced subsets. The key is to understand WHY the imbalance exists — if fraud is 1% because you're only catching one type, collect more diverse fraud examples rather than just duplicating."

### Q2: "What is data leakage and how do you detect it?"

"Data leakage is using information during training that wouldn't be available at inference time. Common causes: normalizing with test data statistics, including future information, duplicating rows across splits, or accidentally including the target as a feature. Detection: if the model performs suspiciously well (99%+ accuracy), check for leakage. Prevention: always fit preprocessing on training data only, use time-based splits for temporal data, and carefully audit every feature."

### Q3: "What's the difference between bagging and boosting?"

"Bagging trains N independent models in parallel on different random subsets, combining by averaging or voting. It reduces variance (overfitting). Random Forest is the classic example. Boosting trains models sequentially — each model corrects the errors of the previous one. It reduces bias (underfitting). XGBoost and LightGBM are the state-of-the-art. Bagging models are parallelizable; boosting models are sequential."

### Q4: "How would you set up experiment tracking for ML?"

"I'd use MLflow or Weights & Biases to track: model architecture, hyperparameters, training/validation metrics per epoch, dataset version, feature pipeline version, code commit hash, environment (library versions, GPU type), training time, and cost. The golden rule is: if it's not tracked, it didn't happen. Every experiment must be reproducible from its tracking record. I'd also set up a model registry to track which models are in staging vs production."

### Q5: "What is weak supervision?"

"Weak supervision uses heuristic rules to generate noisy labels instead of hand-labeling. For example, a rule like 'contains the word free → likely spam' generates a probabilistic label with 70% confidence. Tools like Snorkel combine multiple rules into a single probabilistic label using a generative model. This lets you label millions of examples in minutes instead of months, at a fraction of the cost of hand-labeling."
