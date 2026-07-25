# Designing ML Systems — Infrastructure, Tooling & Human Side (Ch 10-11)

> **Source:** "Designing Machine Learning Systems" by Chip Huyen
> **Coverage:** Ch 10 (Infrastructure and Tooling for MLOps), Ch 11 (The Human Side of ML)

---

## Chapter 10: Infrastructure and Tooling for MLOps

### The MLOps Stack

```
┌──────────────────────────────────────────────────────────────────┐
│                 THE MLOPS STACK                                   │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐          │
│  │ MONITORING                                          │          │
│  │ Grafana, Prometheus, Evidently, Arize               │          │
│  └───────────────────────┬────────────────────────────┘          │
│                          │                                        │
│  ┌───────────────────────▼────────────────────────────┐          │
│  │ CONTINUOUS DELIVERY (CD)                            │          │
│  │ Champion/Challenger, Canary, A/B Testing           │          │
│  └───────────────────────┬────────────────────────────┘          │
│                          │                                        │
│  ┌───────────────────────▼────────────────────────────┐          │
│  │ MODEL REGISTRY & FEATURE STORE                     │          │
│  │ MLflow Model Registry, Feast, Tecton               │          │
│  └───────────────────────┬────────────────────────────┘          │
│                          │                                        │
│  ┌───────────────────────▼────────────────────────────┐          │
│  │ CONTINUOUS INTEGRATION (CI)                         │          │
│  │ GitHub Actions, Jenkins, GitLab CI                 │          │
│  └───────────────────────┬────────────────────────────┘          │
│                          │                                        │
│  ┌───────────────────────▼────────────────────────────┐          │
│  │ WORKFLOW ORCHESTRATION                              │          │
│  │ Airflow, Kubeflow, Dagster, Prefect               │          │
│  └───────────────────────┬────────────────────────────┘          │
│                          │                                        │
│  ┌───────────────────────▼────────────────────────────┐          │
│  │ COMPUTE & STORAGE                                   │          │
│  │ Kubernetes, AWS EC2/GPU, S3, EFS                    │          │
│  └────────────────────────────────────────────────────┘          │
└──────────────────────────────────────────────────────────────────┘
```

### Workflow Orchestration

```
ORCHESTRATORS MANAGE ML PIPELINES:

  Airflow (Apache):
    DAG-based scheduling. Mature, widely used.
    Good for: Batch ETL, scheduled model training.
    Weakness: Not ML-specific (no native model versioning).

  Kubeflow (CNCF):
    Kubernetes-native ML toolkit.
    Good for: Distributed training, pipeline orchestration.
    Weakness: Steep learning curve, Kubernetes expertise required.

  Dagster:
    Asset-oriented (data + code as first-class entities).
    Good for: Data lineage tracking, testing.
    Modern, growing adoption.

  Prefect:
    Python-native, dynamic DAGs.
    Good for: Rapid prototyping, dynamic workflows.
    Simpler than Airflow.

  Metaflow (Netflix):
    Data science-focused.
    Good for: Data scientists (minimal DevOps knowledge needed).
    Built-in versioning and artifact storage.
```

### Model Store and Feature Store

```
MODEL STORE:
  Purpose: Version, track, and serve ML models.
  Capabilities:
    • Version models (model v1.2.3)
    • Track model lineage (which data, code, params → which model)
    • Serve models via API
    • Stage models (dev → staging → production)
  Tools: MLflow Model Registry, Vertex AI Model Registry

FEATURE STORE:
  Purpose: Central repository for features, shared across teams.
  Capabilities:
    • Define features once, reuse everywhere
    • Serve features at training time AND inference time
    • Ensure consistency (same features in training and production)
    • Track feature lineage and freshness
  Tools: Feast (open source), Tecton, Hopsworks, Vertex AI Feature Store

WHY FEATURE STORES MATTER:
  "Training-serving skew" is a top ML failure mode.
  If training computes features differently than production,
  the model sees different data and performs worse.
  Feature store ensures SAME computation in both environments.
```

### Build vs Buy

```
┌──────────────────┬────────────────────┬───────────────────────┐
│ Component        │ Build              │ Buy                   │
├──────────────────┼────────────────────┼───────────────────────┤
│ Model training   │ Custom pipeline    │ Vertex AI, SageMaker  │
│ Model serving    │ FastAPI + K8s      │ Vertex AI, BentoML    │
│ Feature store    │ Feast + Redis      │ Tecton, Hopsworks     │
│ Experiment track │ Custom + MLflow    │ W&B, Neptune          │
│ Monitoring       │ Prometheus + custom│ Arize, Fiddler        │
│ Data labeling    │ Custom UI          │ Labelbox, Scale AI    │
│ Pipelines        │ Airflow + custom   │ Kubeflow, Vertex      │
└──────────────────┴────────────────────┴───────────────────────┘

HUYEN'S ADVICE:
  "Build what differentiates your business.
   Buy what doesn't. For most teams, model training and serving
   infrastructure don't differentiate — buy those. Feature stores,
   custom metrics, and monitoring might differentiate — consider building."
```

---

## Chapter 11: The Human Side of ML

### User Experience for ML

```
Huyen's UX principles for ML-powered products:

1. CONSISTENCY
   Model predictions should be consistent within a session.
   If user refreshes and gets totally different results → trust breaks.
   Solution: Cache predictions within a session.

2. COMBATTING "MOSTLY CORRECT" PREDICTIONS
   "A model that's 95% accurate produces wrong predictions 5% of the time.
    Those 5% are not random — they're concentrated on edge cases,
    which are the most memorable for users."
   Solution: Confidence thresholds (don't show low-confidence predictions),
    graceful fallbacks (show a default when model is unsure).

3. SMOOTH FAILING
   ML systems WILL fail. Design for graceful degradation.
   "If the recommendation engine is down, show popular items."
   "If the model times out, show last cached result."
   Never show an error page because the ML model failed.
```

### Team Structure

```
CROSS-FUNCTIONAL ML TEAM:

  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │ Data         │  │ ML           │  │ ML           │
  │ Scientist    │  │ Engineer     │  │ Researcher   │
  │              │  │              │  │              │
  │ Experiments  │  │ Production   │  │ New model    │
  │ Analysis     │  │ Deployment   │  │ architectures│
  │ Prototypes   │  │ Monitoring   │  │ Research     │
  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Data        │
                    │ Engineer    │
                    │             │
                    │ Pipelines   │
                    │ ETL         │
                    │ Data quality│
                    └─────────────┘

  CHALLENGE: Hand-off between teams.
  Data scientist builds a prototype → ML engineer must productionize.
  Often, the production pipeline differs from the prototype,
  causing training-serving skew.

  HUYEN'S SOLUTION: "End-to-end data scientists" —
  One person owns the model from prototype to production.
  Reduces hand-off friction. Requires broader skill set.
```

### Responsible AI

```
CASE STUDIES OF IRRESPONSIBLE AI:
  1. Amazon resume screening (gender bias) — shut down
  2. COMPAS recidivism prediction (racial bias)
  3. Facebook ad delivery (discriminatory targeting)
  4. Deepfakes (misinformation)

FRAMEWORK FOR RESPONSIBLE AI:
  1. FAIRNESS: Test for bias across demographics
  2. ACCOUNTABILITY: Clear ownership of model decisions
  3. TRANSPARENCY: Explainable predictions where possible
  4. PRIVACY: Protect user data, minimize collection
  5. ROBUSTNESS: Handle edge cases, adversarial inputs
  6. SAFETY: Prevent harmful outputs

HUYEN'S KEY QUOTE:
  "Responsible AI isn't a feature you add at the end.
   It's a principle that guides every decision."
```

---

## Interview Q&As

### Q1: "What is a feature store and why is it important?"

"A feature store is a centralized repository for ML features that ensures consistency between training and serving. Without it, data scientists compute features one way in their notebook (e.g., using pandas), and ML engineers re-implement them differently in production (e.g., using SQL). This causes training-serving skew — the model sees different features in production than in training, degrading performance. Tools like Feast, Tecton, or Vertex AI Feature Store solve this by providing a single source of truth for feature definitions and computations."

### Q2: "How would you set up MLOps for a team of 10 data scientists?"

"I'd start with: (1) A shared experiment tracking tool (MLflow or W&B) so every experiment is logged. (2) A model registry for versioning and staging models. (3) A CI/CD pipeline that runs on every code commit — linting, tests, and model validation. (4) A feature store to prevent training-serving skew. (5) A workflow orchestrator (Airflow or Prefect) for scheduled pipelines. (6) Monitoring (Prometheus + Grafana for ops, Evidently for ML drift). I'd buy infrastructure (Vertex AI or SageMaker) and build custom monitoring if needed."

### Q3: "How do you handle the hand-off between data science and ML engineering?"

"Huyen identifies this as a major friction point. I'd address it by: (1) Having data scientists write production-quality code (not just notebooks), (2) Using containers (Docker) so the prototype environment IS the production environment, (3) Implementing a feature store so feature definitions are shared, (4) Doing code reviews across teams before deployment. The ideal state is 'end-to-end data scientists' — one person owns the model from prototype to production, eliminating the hand-off entirely."

### Q4: "What is training-serving skew?"

"Training-serving skew occurs when the model sees different data distributions in training versus production. Causes: (1) Feature computation differs (pandas vs SQL), (2) Preprocessing differs (scaler fit on different data), (3) Data sources differ (sampled training data vs full production data). Detection: monitor feature distributions in production and compare to training. Prevention: use a feature store for consistent computation, use the same preprocessing pipeline for training and serving, and validate feature parity during CI."

### Q5: "How do you design ML systems for graceful failure?"

"ML systems will fail — the question is how gracefully. I implement: (1) Fallbacks — if the model times out, return last cached prediction or a sensible default. (2) Confidence thresholds — if model confidence is below X%, don't show the prediction. (3) Circuit breakers — if the model service fails 5 times in a row, stop calling it for 60 seconds and use fallback. (4) Rate limiting — prevent overload during traffic spikes. The user should never see an error page because the ML model failed."
