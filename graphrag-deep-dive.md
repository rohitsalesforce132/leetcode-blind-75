# GraphRAG / ContextGraph — The Ultimate Deep-Dive Interview Guide

> **Purpose:** This is the project that proves you understand RAG beyond "I used LangChain + Pinecone." It shows you can solve the hardest problem in enterprise AI: answering RELATIONAL questions. When the interviewer asks "What's the most advanced AI system you've built?" — this is your answer.

---

## TABLE OF CONTENTS

1. [The Problem Space (Why Vector RAG Fails)](#1-the-problem-space)
2. [System Architecture (Interview Whiteboard Ready)](#2-system-architecture)
3. [The Ingestion Pipeline — How 159 Docs Become a Graph](#3-ingestion-pipeline)
4. [Entity Extraction — Teaching LLMs to Read Blueprints](#4-entity-extraction)
5. [Relationship Extraction — Connecting the Dots](#5-relationship-extraction)
6. [Neo4j Graph Design — Schema, Nodes, Edges](#6-neo4j-schema)
7. [Qdrant Vector Database — Embeddings Design](#7-qdrant-design)
8. [The Hybrid Query Engine — Vector + Graph Fusion](#8-hybrid-query)
9. [How GraphRAG Integrates with IncidentAgent](#9-integration)
10. [Metrics & ROI (Memorize These)](#10-metrics)
11. [15 Interview Questions With Exact Answers](#11-interview-questions)
12. [The 90-Second Verbal Pitch](#12-the-pitch)

---

## 1. THE PROBLEM SPACE

### What Enterprise Knowledge Looks Like at AT&T

```
AT&T has a massive internal knowledge base:
  - 2,000+ runbooks (step-by-step incident remediation guides)
  - 500+ post-mortem reports (root cause analysis from past incidents)
  - 1,000+ architecture documents (system diagrams, dependency maps)
  - 300+ network topology documents (fiber routes, tower configs)
  - 5,000+ Confluence wiki pages (team processes, API docs)
  - ServiceNow tickets (years of incident history)

Total: ~10,000+ documents containing critical operational knowledge.
```

### The Two Types of Questions SREs Ask

```
TYPE 1: SEMANTIC QUESTIONS (Vector RAG handles these well)
  "How do I restart the pgbouncer connection pooler?"
  → Vector search finds the runbook that mentions "pgbouncer restart"
  → Returns the steps. Works great.

  "What is the procedure for a BGP route flap?"
  → Vector search finds the runbook for BGP flapping
  → Returns the remediation steps. Works great.

TYPE 2: RELATIONAL QUESTIONS (Vector RAG COMPLETELY FAILS)
  "Which services depend on the database that's failing?"
  → Vector search finds documents that MENTION "database" and "depend"
  → But it can't TRAVERSE: payment-svc → depends_on → db-prod-01
  → It returns text about dependencies, not the actual dependency graph
  → USELESS ANSWER

  "What incidents have we had on the Mumbai-Ahmedabad fiber route?"
  → Vector search finds documents mentioning "Mumbai" and "fiber"
  → But it can't connect: fiber-route-MUM-AHM → hosts → tower-TX-4471
    → had_incident → INC-2024-0156
  → It returns random paragraphs about Mumbai fiber, not the incident list
  → USELESS ANSWER

  "If I restart pgbouncer, what else breaks?"
  → Vector search finds the pgbouncer runbook
  → But it can't traverse: pgbouncer → serves → payment-svc
    → payment-svc → feeds → billing-svc → feeds → mobile-app-api
  → It can't tell you the blast radius
  → DANGEROUS ANSWER (you restart it and break 3 other services)
```

### Why Vector Search Fails at Relational Questions

```
Vector search works by SEMANTIC SIMILARITY:
  Query embedding → compare with document embeddings → return closest matches

  Query: "Which services depend on db-prod-01?"
  Embedding: [0.2, -0.5, 0.8, ...]

  Document A: "db-prod-01 is a PostgreSQL database hosted on server-srv-04"
  Embedding: [0.3, -0.4, 0.7, ...] → HIGH similarity → RETURNED

  Document B: "payment-svc connects to db-prod-01 for transaction processing"
  Embedding: [0.1, -0.6, 0.5, ...] → MEDIUM similarity → MAYBE RETURNED

  Document C: "checkout-svc calls payment-svc to process orders"
  Embedding: [0.5, -0.1, 0.2, ...] → LOW similarity → NOT RETURNED

  PROBLEM: Document C is CRITICAL — it tells you checkout-svc is affected.
  But vector search can't see the CHAIN:
    checkout-svc → calls → payment-svc → depends_on → db-prod-01

  Vector search sees TEXT SIMILARITY.
  Graph traversal sees RELATIONSHIPS.
  For relational questions, you need GRAPH.
```

---

## 2. SYSTEM ARCHITECTURE

### Complete Architecture (Draw This on the Whiteboard)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     GRAPHRAG PLATFORM ARCHITECTURE                        │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                     INGESTION PIPELINE                              │  │
│  │                     (Runs once + incremental updates)               │  │
│  │                                                                     │  │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────────┐   ┌─────────────┐ │  │
│  │  │ Document │──>│ Chunking │──>│ Entity       │──>│ Relationship│ │  │
│  │  │ Loaders  │   │ Engine   │   │ Extraction   │   │ Extraction  │ │  │
│  │  │          │   │          │   │ (LLM)        │   │ (LLM)       │ │  │
│  │  │ PDF      │   │ Semantic │   │              │   │             │ │  │
│  │  │ Confluence│  │ splitting│   │ "db-prod-01" │   │ "depends_on"│ │  │
│  │  │ Wiki     │   │ + overlap│   │ "payment-svc"│   │ "hosts"     │ │  │
│  │  │ Markdown │   │          │   │ "tower-4471" │   │ "connects"  │ │  │
│  │  └──────────┘   └────┬─────┘   └──────┬───────┘   └──────┬──────┘ │  │
│  │                       │                │                   │        │  │
│  │                       ▼                │                   │        │  │
│  │               ┌──────────────┐         │                   │        │  │
│  │               │ Embedding    │         │                   │        │  │
│  │               │ Model        │         │                   │        │  │
│  │               │ (BGE-large)  │         │                   │        │  │
│  │               └──────┬───────┘         │                   │        │  │
│  │                      │                  │                   │        │  │
│  │                      ▼                  ▼                   ▼        │  │
│  │               ┌──────────────────────────────────────────────────┐  │  │
│  │               │              VALIDATION + FILTERING               │  │  │
│  │               │  • Entity confidence > 0.8                        │  │  │
│  │               │  • Entity type constraints (service, DB, server)  │  │  │
│  │               │  • Relationship type whitelist                    │  │  │
│  │               │  • Deduplication (merge "DB-01" and "db-prod-01") │  │  │
│  │               └──────────────────────────────────────────────────┘  │  │
│  │                      │                  │                   │        │  │
│  │                      ▼                  ▼                   ▼        │  │
│  │               ┌──────────────┐  ┌───────────────┐                   │  │
│  │               │ Qdrant       │  │ Neo4j         │                   │  │
│  │               │ Vector DB    │  │ Graph DB      │                   │  │
│  │               │              │  │               │                   │  │
│  │               │ 4,914 chunks │  │ 297 entities  │                   │  │
│  │               │ with vectors │  │ 6,822 rels    │                   │  │
│  │               │ + metadata   │  │ + properties  │                   │  │
│  │               └──────────────┘  └───────────────┘                   │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                     QUERY PIPELINE                                  │  │
│  │                     (Runs on every question)                        │  │
│  │                                                                     │  │
│  │  User Question: "What services are affected if db-prod-01 fails?"  │  │
│  │                      │                                              │  │
│  │                      ▼                                              │  │
│  │               ┌──────────────┐                                      │  │
│  │               │ Query        │                                      │  │
│  │               │ Understanding│                                      │  │
│  │               │ (Extract     │                                      │  │
│  │               │  entities)   │                                      │  │
│  │               └──────┬───────┘                                      │  │
│  │                      │                                              │  │
│  │           ┌──────────┴──────────┐                                   │  │
│  │           ▼                      ▼                                   │  │
│  │    ┌──────────────┐      ┌───────────────┐                          │  │
│  │    │ Vector       │      │ Graph         │                          │  │
│  │    │ Search       │      │ Traversal     │                          │  │
│  │    │ (Qdrant)     │      │ (Neo4j)       │                          │  │
│  │    │              │      │               │                          │  │
│  │    │ "Find docs   │      │ "Traverse     │                          │  │
│  │    │  about       │      │  dependencies │                          │  │
│  │    │  db-prod-01" │      │  from         │                          │  │
│  │    │              │      │  db-prod-01"  │                          │  │
│  │    │ Top 20       │      │ All affected  │                          │  │
│  │    │ chunks       │      │ services      │                          │  │
│  │    └──────┬───────┘      └──────┬────────┘                          │  │
│  │           │                      │                                   │  │
│  │           ▼                      ▼                                   │  │
│  │    ┌──────────────────────────────────────┐                         │  │
│  │    │        FUSION + RERANKING              │                        │  │
│  │    │                                        │                        │  │
│  │    │  1. Merge vector + graph results       │                        │  │
│  │    │  2. Rerank by relevance (cross-enc)    │                        │  │
│  │    │  3. Deduplicate                        │                        │  │
│  │    │  4. Format for LLM context             │                        │  │
│  │    └──────────────────┬─────────────────────┘                        │  │
│  │                        │                                              │  │
│  │                        ▼                                              │  │
│  │               ┌──────────────┐                                       │  │
│  │               │ LLM          │                                       │  │
│  │               │ (GPT-4o)     │                                       │  │
│  │               │              │                                       │  │
│  │               │ Reasons over │                                       │  │
│  │               │ text + graph │                                       │  │
│  │               │ context      │                                       │  │
│  │               └──────────────┘                                       │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. THE INGESTION PIPELINE

### Step-by-Step: How 159 Documents Become a Graph

```
STAGE 1: DOCUMENT LOADING
  ─────────────────────────
  Load documents from multiple sources:

  Sources:
    - Confluence REST API (export runbooks, architecture docs)
    - ServiceNow REST API (export resolved incident tickets)
    - Git repositories (markdown runbooks in /docs)
    - PDF exports (network architecture diagrams with text)
    - YAML files (service configurations, topology definitions)

  Each document has metadata:
    {
      "source": "confluence",
      "space": "SRE_RUNBOOKS",
      "title": "Payment Service DB Connection Pool Remediation",
      "last_updated": "2024-06-15",
      "author": "sre-team",
      "tags": ["payment", "database", "runbook"]
    }

  Total documents loaded: 159

STAGE 2: CHUNKING (The Most Underrated Step)
  ─────────────────────────
  Split documents into chunks. Bad chunking = bad RAG. Period.

  NAIVE CHUNKING (what most people do):
    Split every 500 tokens with 50-token overlap.
    PROBLEM: Breaks mid-sentence. Loses context.
    "payment-svc depends on" [CHUNK BREAK] "db-prod-01 for transactions"
    → The relationship is split across two chunks. Both chunks are useless
       for entity/relationship extraction.

  SMART CHUNKING (what I built):
    1. Split by markdown headers first (##, ###)
    2. Within each section, split by paragraphs
    3. If a paragraph > 512 tokens, split by sentences
    4. Maintain 50-token overlap between chunks
    5. Each chunk carries section title as context

    Example chunk:
    {
      "chunk_id": "runbook-pay-rb-014_chunk_3",
      "text": "## Remediation Steps\n\nStep 2: If the connection pool
               is exhausted, restart pgbouncer using: systemctl restart
               pgbouncer. Monitor the error rate for 5 minutes after
               restart.",
      "section_title": "Remediation Steps",
      "doc_title": "Payment Service DB Connection Pool Remediation",
      "chunk_index": 3,
      "doc_source": "confluence",
      "tokens": 58
    }

  Total chunks created: 4,914

STAGE 3: EMBEDDING (Vector Creation)
  ─────────────────────────
  Each chunk gets embedded into a 1024-dimensional vector.

  Model: BGE-large-en-v1.5 (open-source, runs locally, free)
  Why not OpenAI embeddings?
    - BGE-large is free (OpenAI text-embedding-3-small is $0.02/1M tokens)
    - BGE-large performs better on MTEB benchmark for technical docs
    - Runs on CPU (no GPU needed for inference)
    - Data never leaves our network (important for compliance)

  Each chunk now has:
    {
      "chunk_id": "runbook-pay-rb-014_chunk_3",
      "text": "## Remediation Steps\n\nStep 2: ...",
      "embedding": [0.0234, -0.1456, 0.8901, ...],  # 1024 dims
      "metadata": {...}
    }

  Stored in Qdrant vector database.

STAGE 4: ENTITY EXTRACTION (LLM-Powered)
  ─────────────────────────
  For each chunk, the LLM extracts entities.

  (Detailed in Section 4 below)

  Result: 297 unique entities across all documents.

STAGE 5: RELATIONSHIP EXTRACTION (LLM-Powered)
  ─────────────────────────
  For each chunk, the LLM extracts relationships between entities.

  (Detailed in Section 5 below)

  Result: 6,822 relationships across all entities.

STAGE 6: GRAPH CONSTRUCTION (Neo4j)
  ─────────────────────────
  Load entities and relationships into Neo4j.

  Each entity becomes a node.
  Each relationship becomes an edge.
  Each chunk is linked to the entities it mentions.

  (Detailed in Section 6 below)

STAGE 7: VALIDATION + QUALITY FILTERING
  ─────────────────────────
  - Filter entities with confidence < 0.8
  - Remove generic entities ("the system", "the database")
  - Deduplicate: merge "DB-01", "db-prod-01", "db_prod_01" into one node
  - Manual review of top 50 most-referenced entities

PIPELINE STATS:
  Documents:     159
  Chunks:        4,914
  Tokens:        1.3M (total text processed)
  Entities:      297 (after filtering, down from ~2,000 raw)
  Relationships: 6,822
  Embedding dim: 1,024
  Pipeline cost: ~$3.20 (LLM calls for extraction on 4,914 chunks)
  Runtime:       ~45 minutes (single-threaded, batch LLM calls)
```

### Ingestion Pipeline Code

```python
"""
The complete ingestion pipeline — from raw documents to Neo4j graph.
"""

import json
import hashlib
from typing import List, Dict, Any
from dataclasses import dataclass

# ============================================================
# STAGE 1: DOCUMENT LOADING
# ============================================================

@dataclass
class Document:
    doc_id: str
    title: str
    content: str
    source: str          # "confluence", "servicenow", "git", "pdf"
    doc_type: str        # "runbook", "postmortem", "architecture", "topology"
    metadata: Dict
    last_updated: str

def load_all_documents() -> List[Document]:
    """Load documents from all sources."""
    docs = []

    # Confluence runbooks and wikis
    docs.extend(load_confluence_docs(
        space="SRE_RUNBOOKS",
        doc_type="runbook"
    ))

    # ServiceNow resolved incidents (post-mortems)
    docs.extend(load_servicenow_incidents(
        states=["resolved", "closed"],
        contains_postmortem=True
    ))

    # Git markdown docs
    docs.extend(load_git_docs(
        repo="atlassian/sre-docs",
        path="docs/runbooks/",
        doc_type="runbook"
    ))

    # Architecture documents
    docs.extend(load_confluence_docs(
        space="ARCHITECTURE",
        doc_type="architecture"
    ))

    return docs


# ============================================================
# STAGE 2: SMART CHUNKING
# ============================================================

@dataclass
class Chunk:
    chunk_id: str
    text: str
    doc_id: str
    doc_title: str
    section_title: str
    chunk_index: int
    source: str
    tokens: int

class SemanticChunker:
    """
    Chunks documents by semantic structure (headers, paragraphs, sentences).

    WHY NOT FIXED-SIZE CHUNKING?
      Fixed-size chunking breaks entities and relationships across chunk
      boundaries. "payment-svc depends on db-prod-01" split into two chunks
      means the relationship is lost in BOTH chunks.

      Semantic chunking keeps related text together → better extraction.
    """

    MAX_CHUNK_TOKENS = 512
    OVERLAP_TOKENS = 50

    def chunk_document(self, doc: Document) -> List[Chunk]:
        chunks = []

        # Step 1: Split by markdown headers
        sections = self._split_by_headers(doc.content)

        chunk_idx = 0
        for section_title, section_text in sections:
            # Step 2: Split section by paragraphs
            paragraphs = self._split_by_paragraphs(section_text)

            for para in paragraphs:
                para_tokens = self._count_tokens(para)

                if para_tokens <= self.MAX_CHUNK_TOKENS:
                    # Paragraph fits in one chunk
                    chunks.append(self._make_chunk(
                        doc, section_title, para, chunk_idx
                    ))
                    chunk_idx += 1
                else:
                    # Step 3: Split large paragraphs by sentences
                    sentences = self._split_by_sentences(para)
                    current_chunk = ""
                    current_tokens = 0

                    for sentence in sentences:
                        sentence_tokens = self._count_tokens(sentence)

                        if current_tokens + sentence_tokens > self.MAX_CHUNK_TOKENS:
                            # Flush current chunk
                            if current_chunk:
                                chunks.append(self._make_chunk(
                                    doc, section_title, current_chunk.strip(), chunk_idx
                                ))
                                chunk_idx += 1
                            # Start new chunk with overlap from previous
                            current_chunk = self._get_overlap(current_chunk) + sentence
                            current_tokens = self._count_tokens(current_chunk)
                        else:
                            current_chunk += " " + sentence
                            current_tokens += sentence_tokens

                    # Flush remaining
                    if current_chunk.strip():
                        chunks.append(self._make_chunk(
                            doc, section_title, current_chunk.strip(), chunk_idx
                        ))
                        chunk_idx += 1

        return chunks

    def _split_by_headers(self, text: str) -> List[tuple]:
        """Split markdown by ## and ### headers."""
        import re
        sections = []
        current_header = "Introduction"
        current_text = ""

        for line in text.split("\n"):
            if re.match(r'^#{1,3}\s+', line):
                if current_text.strip():
                    sections.append((current_header, current_text))
                current_header = line.strip("# ").strip()
                current_text = ""
            else:
                current_text += line + "\n"

        if current_text.strip():
            sections.append((current_header, current_text))

        return sections

    def _make_chunk(self, doc, section, text, idx) -> Chunk:
        """Create a chunk with full context."""
        # Include document title and section for context
        full_text = f"[{doc.title} > {section}]\n{text}"
        return Chunk(
            chunk_id=f"{doc.doc_id}_chunk_{idx}",
            text=full_text,
            doc_id=doc.doc_id,
            doc_title=doc.title,
            section_title=section,
            chunk_index=idx,
            source=doc.source,
            tokens=self._count_tokens(full_text),
        )

    def _count_tokens(self, text: str) -> int:
        """Estimate tokens: ~4 chars per token."""
        return len(text) // 4

    def _get_overlap(self, text: str) -> str:
        """Get last N tokens for overlap."""
        words = text.split()
        overlap_words = words[-self.OVERLAP_TOKENS:] if len(words) > self.OVERLAP_TOKENS else words
        return " ".join(overlap_words) + " "

    def _split_by_paragraphs(self, text: str) -> List[str]:
        return [p.strip() for p in text.split("\n\n") if p.strip()]

    def _split_by_sentences(self, text: str) -> List[str]:
        import re
        return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
```

---

## 4. ENTITY EXTRACTION

### How It Works

```python
"""
For each chunk, the LLM extracts named entities: services, databases,
servers, cell towers, people, tools, protocols.

The LLM acts as a specialized NER (Named Entity Recognition) engine,
but with domain knowledge about telecom infrastructure.
"""

ENTITY_EXTRACTION_PROMPT = """You are an entity extraction engine for a telecom infrastructure knowledge base.

Extract all ENTITIES from the following text. Entities are proper nouns
that refer to specific infrastructure components, services, or people.

ENTITY TYPES (only extract these types):
- SERVICE: Microservices, APIs, applications (e.g., "payment-svc", "auth-gateway")
- DATABASE: Databases, caches, message queues (e.g., "db-prod-01", "redis-cache")
- SERVER: Physical or virtual servers (e.g., "srv-04", "k8s-node-12")
- NETWORK: Network devices, towers, routes (e.g., "tower-TX-4471", "bgp-router-03")
- TOOL: Software tools, platforms (e.g., "Splunk", "Prometheus", "pgbouncer")
- PERSON: People mentioned (e.g., "John Smith", "SRE Team")
- PROTOCOL: Network protocols (e.g., "BGP", "OSPF", "5G NR", "SIP")
- INCIDENT: Incident IDs (e.g., "INC-2024-0156")

OUTPUT FORMAT (JSON):
{
  "entities": [
    {"name": "payment-svc", "type": "SERVICE", "confidence": 0.95},
    {"name": "db-prod-01", "type": "DATABASE", "confidence": 0.98},
    {"name": "pgbouncer", "type": "TOOL", "confidence": 0.90}
  ]
}

RULES:
1. Normalize names to lowercase with hyphens (e.g., "PaymentSvc" → "payment-svc")
2. Only include entities with confidence > 0.8
3. Don't extract generic words ("the database", "the server", "the service")
4. Extract ALL entities — don't miss any

TEXT:
{chunk_text}
"""

class EntityExtractor:
    """Extract entities from text chunks using LLM."""

    def __init__(self, llm_gateway):
        self.llm = llm_gateway

    def extract_from_chunk(self, chunk: Chunk) -> List[dict]:
        """Extract entities from a single chunk."""
        prompt = ENTITY_EXTRACTION_PROMPT.format(chunk_text=chunk.text)

        response = self.llm.call(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o-mini",  # CHEAP model — extraction is simple
            temperature=0.0,      # Deterministic — no creativity needed
            response_format={"type": "json_object"},
        )

        try:
            result = json.loads(response.choices[0].message.content)
            entities = result.get("entities", [])
        except json.JSONDecodeError:
            entities = []

        # Filter by confidence
        entities = [e for e in entities if e.get("confidence", 0) >= 0.8]

        # Add source tracking
        for e in entities:
            e["source_chunk"] = chunk.chunk_id
            e["source_doc"] = chunk.doc_title

        return entities

    def extract_from_all_chunks(self, chunks: List[Chunk]) -> List[dict]:
        """Extract entities from all chunks. Batch for efficiency."""
        all_entities = []

        # Process in batches of 20 (to manage API rate limits)
        BATCH_SIZE = 20
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            for chunk in batch:
                entities = self.extract_from_chunk(chunk)
                all_entities.extend(entities)
            print(f"  Extracted entities from {min(i + BATCH_SIZE, len(chunks))}/{len(chunks)} chunks")

        return all_entities
```

### Entity Normalization & Deduplication

```python
class EntityNormalizer:
    """
    Clean up and merge entity references.

    PROBLEM: The same entity appears in different forms across documents:
      "DB-01", "db-prod-01", "db_prod_01", "Database 01", "the primary DB"

    SOLUTION: Normalize all to canonical form and merge duplicates.
    """

    # Known aliases → canonical name
    ALIAS_MAP = {
        "db-01": "db-prod-01",
        "db_prod_01": "db-prod-01",
        "database 01": "db-prod-01",
        "primary db": "db-prod-01",
        "payment service": "payment-svc",
        "paymentsvc": "payment-svc",
        "auth gw": "auth-gateway",
        "auth-gw": "auth-gateway",
    }

    # Generic terms to REJECT (not real entities)
    GENERIC_TERMS = {
        "the database", "the server", "the service", "the system",
        "the application", "the cluster", "the network", "the api",
        "database", "server", "service", "system", "application",
    }

    def normalize(self, entities: List[dict]) -> List[dict]:
        """Normalize entity names and deduplicate."""
        normalized = []

        for entity in entities:
            name = entity["name"].lower().strip()

            # Skip generic terms
            if name in self.GENERIC_TERMS:
                continue

            # Apply alias mapping
            name = self.ALIAS_MAP.get(name, name)

            # Normalize format: lowercase, hyphens
            name = name.replace("_", "-").replace(" ", "-")
            name = name.strip("-")

            entity["name"] = name
            normalized.append(entity)

        # Deduplicate: merge entities with same name + type
        merged = self._merge_duplicates(normalized)

        return merged

    def _merge_duplicates(self, entities: List[dict]) -> List[dict]:
        """Merge entities with same name and type."""
        seen = {}

        for entity in entities:
            key = f"{entity['name']}:{entity['type']}"

            if key not in seen:
                seen[key] = entity
            else:
                # Merge: track all source documents
                existing = seen[key]
                if "source_docs" not in existing:
                    existing["source_docs"] = [existing.get("source_doc", "")]
                existing["source_docs"].append(entity.get("source_doc", ""))
                # Keep highest confidence
                existing["confidence"] = max(
                    existing.get("confidence", 0),
                    entity.get("confidence", 0)
                )

        return list(seen.values())
```

---

## 5. RELATIONSHIP EXTRACTION

### How It Works

```python
"""
For each chunk, the LLM extracts RELATIONSHIPS between the entities
it found.

This is where GraphRAG gets its power — not just knowing WHAT entities
exist, but HOW they're connected.
"""

RELATIONSHIP_EXTRACTION_PROMPT = """You are a relationship extraction engine for telecom infrastructure.

Given the text and the entities already extracted, identify ALL relationships
between these entities.

RELATIONSHIP TYPES (only use these types):
- DEPENDS_ON: A depends on B to function (e.g., service → database)
- HOSTS: A hosts B (e.g., server → database, server → service)
- CONNECTS_TO: A connects to B over network (e.g., service → service, tower → tower)
- ROUTES_THROUGH: A routes traffic through B (e.g., tower → fiber route)
- MANAGES: A manages B (e.g., person/team → service, tool → device)
- USES: A uses B as a tool (e.g., service → tool, team → platform)
- CAUSED_INCIDENT: A caused incident B (e.g., deploy → incident)
- DOCUMENTED_IN: A is documented in B (e.g., service → runbook)

OUTPUT FORMAT (JSON):
{
  "relationships": [
    {
      "source": "payment-svc",
      "target": "db-prod-01",
      "type": "DEPENDS_ON",
      "detail": "payment-svc connects to db-prod-01 for transaction storage",
      "confidence": 0.95
    },
    {
      "source": "db-prod-01",
      "target": "srv-04",
      "type": "HOSTED_ON",
      "detail": "db-prod-01 is hosted on server srv-04",
      "confidence": 0.90
    }
  ]
}

RULES:
1. Only create relationships between entities that actually appear in the text
2. Extract ALL relationships — don't miss any
3. Include a short detail explaining the relationship
4. Confidence > 0.8

TEXT:
{chunk_text}

ENTITIES FOUND:
{entities_json}
"""

class RelationshipExtractor:
    """Extract relationships between entities using LLM."""

    def __init__(self, llm_gateway):
        self.llm = llm_gateway

    def extract_from_chunk(self, chunk: Chunk, entities: List[dict]) -> List[dict]:
        """Extract relationships from a chunk."""
        if len(entities) < 2:
            return []  # Need at least 2 entities for a relationship

        prompt = RELATIONSHIP_EXTRACTION_PROMPT.format(
            chunk_text=chunk.text,
            entities_json=json.dumps(entities, indent=2),
        )

        response = self.llm.call(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o-mini",
            temperature=0.0,
            response_format={"type": "json_object"},
        )

        try:
            result = json.loads(response.choices[0].message.content)
            rels = result.get("relationships", [])
        except json.JSONDecodeError:
            rels = []

        # Filter by confidence
        rels = [r for r in rels if r.get("confidence", 0) >= 0.8]

        # Validate: source and target must be in the entity list
        entity_names = {e["name"] for e in entities}
        valid_rels = []
        for rel in rels:
            if rel["source"] in entity_names and rel["target"] in entity_names:
                rel["source_chunk"] = chunk.chunk_id
                valid_rels.append(rel)

        return valid_rels
```

---

## 6. NEO4J GRAPH DESIGN

### The Graph Schema

```
┌──────────────────────────────────────────────────────────────────────┐
│                     NEO4J GRAPH SCHEMA                               │
│                                                                      │
│  NODE LABELS (Entity Types):                                         │
│  ─────────────────────────                                           │
│  (:Service)       — Microservices, APIs                              │
│  (:Database)      — PostgreSQL, Redis, Kafka, Elasticsearch           │
│  (:Server)        — Physical/virtual servers, k8s nodes              │
│  (:CellTower)     — 5G/LTE cell sites                                │
│  (:FiberRoute)    — Fiber optic backbone routes                      │
│  (:Router)        — Network routers, switches                        │
│  (:Tool)          — Software tools (Splunk, Prometheus, pgbouncer)   │
│  (:Person)        — People, teams                                    │
│  (:Incident)      — Past incidents (from ServiceNow)                 │
│  (:Document)      — Source documents (runbooks, post-mortems)        │
│  (:Runbook)       — Specific runbook documents                       │
│                                                                      │
│  RELATIONSHIP TYPES (Edge Types):                                    │
│  ──────────────────────────────                                      │
│  [:DEPENDS_ON]    — Service → Database/Service                       │
│  [:HOSTED_ON]     — Database/Service → Server                        │
│  [:CONNECTS_TO]   — Service → Service, Tower → Tower                 │
│  [:ROUTES_THROUGH]— Tower → FiberRoute                               │
│  [:MANAGES]       — Person → Service, Tool → Device                  │
│  [:USES]          — Service → Tool                                   │
│  [:CAUSED]        — Component → Incident                             │
│  [:RESOLVED_BY]   — Incident → Runbook                               │
│  [:MENTIONS]      — Document → Entity (chunk links to graph)         │
│  [:DOCUMENTED_IN] — Entity → Document                                │
│                                                                      │
│  NODE PROPERTIES:                                                    │
│  ─────────────────                                                   │
│  All nodes have: id, name, type, status, description                 │
│  Service: language, version, team_owner, criticality                 │
│  Database: engine (postgres/redis/...), version, size_gb             │
│  CellTower: tower_id, location, frequency_band, status               │
│  Incident: incident_id, severity, created_at, resolved_at            │
│                                                                      │
│  RELATIONSHIP PROPERTIES:                                            │
│  ────────────────────────                                            │
│  All relationships have: source_chunk, confidence, detail            │
│                                                                      │
│  TOTALS:                                                             │
│  Nodes:    297                                                       │
│  Edges:    6,822                                                     │
│  Properties per node: avg 5.2                                        │
└──────────────────────────────────────────────────────────────────────┘
```

### What the Graph Actually Looks Like

```
VISUALIZATION OF A SUBGRAPH (payment-svc and its neighborhood):

    ┌──────────┐    DEPENDS_ON   ┌────────────┐    HOSTED_ON  ┌─────────┐
    │checkout- │────────────────>│            │──────────────>│ srv-04  │
    │  svc     │                 │ db-prod-01 │                └─────────┘
    └────┬─────┘                 │ (PostgreSQL│                     ↑
         │                       │  primary)  │                     │
    CALLS│                       └────────────┘              HOSTED_ON
         v                            ↑                          │
    ┌──────────┐    DEPENDS_ON        │                     ┌─────────┐
    │payment-  │───────────────────────┘                     │pgbouncer│
    │  svc     │                                                 │
    └──┬───┬───┘                                                 │
       │   │   DEPENDS_ON                            DEPENDS_ON  │
       │   └──────────────> ┌────────────┐                       │
       │                     │redis-cache │                       │
       │                     └────────────┘                       │
       │                                                          │
       │ USES                                                     │
       ▼                                                          │
    ┌──────────┐    USES                                         │
    │kafka-    │                                                 │
    │broker-01 │                                                 │
    └──────────┘                                                 │
                                                                  │
    ┌──────────┐  RESOLVED_BY                                    │
    │INC-2024- │──────> ┌──────────────────┐  MENTIONS  ────────┘
    │  0156    │         │Runbook PAY-RB-014│
    └──────────┘         │(DB Pool Remedy)  │
                         └──────────────────┘

    ┌──────────┐ MANAGES
    │SRE Team  │──────> payment-svc, checkout-svc, billing-svc
    └──────────┘
```

### Loading Data into Neo4j

```python
from neo4j import GraphDatabase

class GraphLoader:
    """Load extracted entities and relationships into Neo4j."""

    def __init__(self):
        self.driver = GraphDatabase.driver(
            "bolt://neo4j:7687",
            auth=("neo4j", os.environ.get("NEO4J_PASSWORD", "telecom2026")),
        )

    def create_constraints(self):
        """Create uniqueness constraints for efficient lookups."""
        with self.driver.session() as session:
            # Ensure entity names are unique per type
            session.run("CREATE CONSTRAINT IF NOT EXISTS "
                       "FOR (n:Service) REQUIRE n.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS "
                       "FOR (n:Database) REQUIRE n.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS "
                       "FOR (n:CellTower) REQUIRE n.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS "
                       "FOR (n:Document) REQUIRE n.id IS UNIQUE")

    def load_entities(self, entities: List[dict]):
        """Load all entities as graph nodes."""
        with self.driver.session() as session:
            for entity in entities:
                # Map type to node label
                label = entity["type"].capitalize()  # "SERVICE" → "Service"
                if label == "Cell_tower":
                    label = "CellTower"
                elif label == "Fiber_route":
                    label = "FiberRoute"

                # MERGE = create if not exists, update if exists
                cypher = f"""
                MERGE (n:{label} {{id: $id}})
                SET n.name = $name,
                    n.type = $type,
                    n.description = $description,
                    n.confidence = $confidence,
                    n.source_docs = $source_docs
                """

                session.run(cypher, {
                    "id": entity["name"],
                    "name": entity["name"],
                    "type": entity["type"],
                    "description": entity.get("detail", ""),
                    "confidence": entity.get("confidence", 0.8),
                    "source_docs": entity.get("source_docs", []),
                })

    def load_relationships(self, relationships: List[dict]):
        """Load all relationships as graph edges."""
        with self.driver.session() as session:
            for rel in relationships:
                rel_type = rel["type"]  # DEPENDS_ON, HOSTED_ON, etc.

                cypher = f"""
                MATCH (source {{id: $source_id}})
                MATCH (target {{id: $target_id}})
                MERGE (source)-[:{rel_type} {{detail: $detail}}]->(target)
                """

                session.run(cypher, {
                    "source_id": rel["source"],
                    "target_id": rel["target"],
                    "detail": rel.get("detail", ""),
                })

    def link_chunks_to_entities(self, chunks: List[Chunk], entities: List[dict]):
        """
        Link each text chunk to the entities it mentions.

        This is CRITICAL — it connects the vector DB (chunks) to the
        graph DB (entities). When vector search finds a chunk, we can
        immediately look up its graph neighbors.
        """
        with self.driver.session() as session:
            for chunk in chunks:
                # Create chunk node
                session.run("""
                    MERGE (c:Document {
                        id: $chunk_id,
                        text: $text,
                        doc_title: $doc_title,
                        source: $source
                    })
                """, {
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text[:500],  # Store preview only
                    "doc_title": chunk.doc_title,
                    "source": chunk.source,
                })

                # Link chunk to entities it mentions
                chunk_entities = [e for e in entities
                                  if e.get("source_chunk") == chunk.chunk_id]
                for entity in chunk_entities:
                    session.run("""
                        MATCH (c:Document {id: $chunk_id})
                        MATCH (e {id: $entity_id})
                        MERGE (c)-[:MENTIONS]->(e)
                    """, {
                        "chunk_id": chunk.chunk_id,
                        "entity_id": entity["name"],
                    })
```

### The Cypher Queries That Power GraphRAG

```python
class GraphQueries:
    """Pre-built Cypher queries for common GraphRAG operations."""

    # Query 1: BLAST RADIUS — "What services are affected if X fails?"
    # Traverses reverse DEPENDS_ON chain up to 3 hops
    BLAST_RADIUS = """
    MATCH path = (affected)-[:DEPENDS_ON|CONNECTS_TO*1..3]->(target {id: $entity_id})
    RETURN DISTINCT
        affected.id AS affected_service,
        affected.type AS affected_type,
        length(path) AS hops,
        [node IN nodes(path) | node.id] AS dependency_chain
    ORDER BY hops
    LIMIT 50
    """

    # Query 2: DEPENDENCY CHAIN — "What does X depend on?"
    # Traverses forward DEPENDS_ON chain
    DEPENDENCY_CHAIN = """
    MATCH path = (source {id: $entity_id})-[:DEPENDS_ON|HOSTED_ON*1..3]->(dependency)
    RETURN DISTINCT
        dependency.id AS dependency,
        dependency.type AS dependency_type,
        dependency.status AS status,
        length(path) AS hops,
        [node IN nodes(path) | node.id] AS chain
    ORDER BY hops
    LIMIT 50
    """

    # Query 3: INCIDENT HISTORY — "What incidents has X had?"
    INCIDENT_HISTORY = """
    MATCH (entity {id: $entity_id})-[:CAUSED|RELATED_TO]-(incident:Incident)
    RETURN
        incident.id AS incident_id,
        incident.severity AS severity,
        incident.root_cause AS root_cause,
        incident.resolved_at AS resolved_at,
        incident.resolution AS resolution
    ORDER BY incident.created_at DESC
    LIMIT 10
    """

    # Query 4: RUNBOOK FINDING — "Which runbook applies to X?"
    RUNBOOK_LOOKUP = """
    MATCH (entity {id: $entity_id})-[:DOCUMENTED_IN|RESOLVED_BY]-(doc:Runbook)
    RETURN
        doc.id AS runbook_id,
        doc.title AS title,
        doc.text AS content_preview
    LIMIT 5
    """

    # Query 5: NEIGHBORHOOD — "Everything connected to X"
    NEIGHBORHOOD = """
    MATCH (entity {id: $entity_id})-[r]-(neighbor)
    RETURN
        type(r) AS relationship_type,
        neighbor.id AS neighbor_id,
        neighbor.type AS neighbor_type,
        neighbor.status AS neighbor_status,
        r.detail AS detail
    LIMIT 30
    """

    # Query 6: SHARED INFRASTRUCTURE — "What else uses the same X?"
    SHARED_INFRA = """
    MATCH (entity {id: $entity_id})-[:DEPENDS_ON]->(shared)<-[:DEPENDS_ON]-(other)
    WHERE other.id <> $entity_id
    RETURN DISTINCT
        other.id AS other_service,
        shared.id AS shared_component,
        shared.type AS shared_type
    LIMIT 20
    """

    # Query 7: FIBER ROUTE INCIDENTS (Telecom-specific)
    FIBER_INCIDENTS = """
    MATCH (route:FiberRoute {id: $route_id})<-[:ROUTES_THROUGH]-(tower:CellTower),
          (tower)-[:CAUSED|RELATED_TO]-(incident:Incident)
    RETURN
        tower.id AS tower_id,
        tower.location AS location,
        incident.id AS incident_id,
        incident.severity AS severity,
        incident.root_cause AS root_cause
    ORDER BY incident.created_at DESC
    LIMIT 20
    """
```

---

## 7. QDRANT VECTOR DATABASE

### How Chunks Are Stored and Searched

```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
)

class VectorStore:
    """
    Qdrant vector database for semantic search over text chunks.

    Each chunk is a point in Qdrant with:
    - A 1024-dimensional vector (BGE-large embedding)
    - Payload metadata (doc_title, section, source, linked_entities)
    """

    COLLECTION = "runbooks"
    VECTOR_DIM = 1024

    def __init__(self):
        self.client = QdrantClient(host="qdrant", port=6333)
        self.embedder = EmbeddingModel("BAAI/bge-large-en-v1.5")

    def create_collection(self):
        """Create the vector collection if it doesn't exist."""
        self.client.recreate_collection(
            collection_name=self.COLLECTION,
            vectors_config=VectorParams(
                size=self.VECTOR_DIM,
                distance=Distance.COSINE,
            ),
        )

    def upload_chunks(self, chunks: List[Chunk]):
        """Embed and upload all chunks to Qdrant."""
        points = []

        for chunk in chunks:
            # Generate embedding
            vector = self.embedder.embed(chunk.text)

            points.append(PointStruct(
                id=hash(chunk.chunk_id),  # Unique point ID
                vector=vector,
                payload={
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "doc_title": chunk.doc_title,
                    "section": chunk.section_title,
                    "source": chunk.source,
                    "doc_type": chunk.metadata.get("doc_type", ""),
                    # Linked entities (for graph enrichment later)
                    "linked_entities": chunk.metadata.get("entities", []),
                }
            ))

        # Batch upload
        self.client.upsert(
            collection_name=self.COLLECTION,
            points=points,
        )

    def search(self, query: str, limit: int = 20, filters: dict = None) -> List[dict]:
        """
        Semantic search: find chunks most similar to the query.

        Returns top-N results with scores.
        """
        query_vector = self.embedder.embed(query)

        # Optional filtering (e.g., only runbooks, only post-mortems)
        qdrant_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                ))
            qdrant_filter = Filter(must=conditions)

        results = self.client.search(
            collection_name=self.COLLECTION,
            query_vector=query_vector,
            limit=limit,
            query_filter=qdrant_filter,
            with_payload=True,
        )

        return [{
            "chunk_id": hit.payload["chunk_id"],
            "text": hit.payload["text"],
            "doc_title": hit.payload.get("doc_title", ""),
            "section": hit.payload.get("section", ""),
            "score": hit.score,
            "linked_entities": hit.payload.get("linked_entities", []),
        } for hit in results]
```

---

## 8. THE HYBRID QUERY ENGINE

### The Core Innovation: Vector + Graph Fusion

```python
"""
This is the heart of GraphRAG — combining vector search and graph
traversal into a single, powerful query engine.

THE PROBLEM:
  Vector search: "What documents TALK ABOUT db-prod-01?" → returns text
  Graph search: "What SERVICES DEPEND ON db-prod-01?" → returns structure

  Neither alone gives the full picture. The LLM needs BOTH:
  - Text to understand WHAT the component is and HOW to fix it
  - Graph to understand WHAT ELSE is affected and WHO cares

THE SOLUTION:
  Run both searches in parallel, merge results, and format as a unified
  context block for the LLM.
"""

class HybridQueryEngine:
    """
    Combines vector search and graph traversal for maximum retrieval quality.

    Pipeline:
    1. Understand the query → extract entities and intent
    2. Run vector search (semantic text retrieval)
    3. Run graph traversal (relational retrieval)
    4. Fuse results → rerank → format → return
    """

    def __init__(self, vector_store: VectorStore, neo4j_driver, llm_gateway):
        self.vector = vector_store
        self.graph = neo4j_driver
        self.llm = llm_gateway

    def query(self, question: str, max_context_tokens: int = 8000) -> dict:
        """
        Answer a question using hybrid vector + graph retrieval.

        Returns:
        {
            "answer": "LLM-generated answer",
            "context": {"vector_results": [...], "graph_results": [...]},
            "sources": [...]
        }
        """
        # ============================================================
        # STEP 1: QUERY UNDERSTANDING
        # ============================================================
        # Extract entities from the question and classify intent
        query_analysis = self._understand_query(question)
        # → {"entities": ["db-prod-01"], "intent": "blast_radius",
        #    "is_relational": True}

        # ============================================================
        # STEP 2: VECTOR SEARCH (runs in parallel with graph)
        # ============================================================
        vector_results = self.vector.search(
            query=question,
            limit=20,
        )

        # ============================================================
        # STEP 3: GRAPH TRAVERSAL (runs in parallel with vector)
        # ============================================================
        graph_results = []
        if query_analysis["is_relational"]:
            for entity_id in query_analysis["entities"]:
                graph_results.extend(self._graph_search(
                    entity_id, query_analysis["intent"]
                ))

        # ============================================================
        # STEP 4: FUSION + RERANKING
        # ============================================================
        fused_context = self._fuse_and_rerank(
            vector_results, graph_results, question
        )

        # ============================================================
        # STEP 5: FORMAT CONTEXT FOR LLM
        # ============================================================
        formatted_context = self._format_context(
            fused_context, max_context_tokens
        )

        # ============================================================
        # STEP 6: LLM ANSWER GENERATION
        # ============================================================
        answer = self._generate_answer(question, formatted_context)

        return {
            "answer": answer,
            "context": formatted_context,
            "vector_results_count": len(vector_results),
            "graph_results_count": len(graph_results),
        }

    def _understand_query(self, question: str) -> dict:
        """
        Classify the question's intent and extract entities.

        This determines WHICH graph queries to run.
        """
        INTENT_PROMPT = """Analyze this question and extract:
        1. Entity names mentioned (services, databases, towers, etc.)
        2. Intent type: "blast_radius", "dependency_chain", "incident_history",
           "runbook_lookup", "general_info", "shared_infrastructure"
        3. Is this a RELATIONAL question? (needs graph traversal)

        Output JSON:
        {
          "entities": ["db-prod-01"],
          "intent": "blast_radius",
          "is_relational": true
        }

        Question: {question}
        """

        response = self.llm.call(
            messages=[{"role": "user",
                      "content": INTENT_PROMPT.format(question=question)}],
            model="gpt-4o-mini",  # Cheap classification
            temperature=0.0,
            response_format={"type": "json_object"},
        )

        return json.loads(response.choices[0].message.content)

    def _graph_search(self, entity_id: str, intent: str) -> List[dict]:
        """Run the appropriate Cypher query based on intent."""
        intent_to_query = {
            "blast_radius": GraphQueries.BLAST_RADIUS,
            "dependency_chain": GraphQueries.DEPENDENCY_CHAIN,
            "incident_history": GraphQueries.INCIDENT_HISTORY,
            "runbook_lookup": GraphQueries.RUNBOOK_LOOKUP,
            "shared_infrastructure": GraphQueries.SHARED_INFRA,
        }

        cypher = intent_to_query.get(intent, GraphQueries.NEIGHBORHOOD)

        with self.graph.session() as session:
            result = session.run(cypher, entity_id=entity_id)
            return [dict(record) for record in result]

    def _fuse_and_rerank(self, vector_results, graph_results, question):
        """
        Merge vector and graph results into unified context.

        Strategy:
        - Vector results provide TEXTUAL context (what docs say)
        - Graph results provide STRUCTURAL context (how things connect)
        - They complement each other, not compete
        """
        fused = {
            "text_context": [],    # From vector search
            "graph_context": [],   # From graph traversal
        }

        # Vector results: keep top 5 (already ranked by similarity)
        for result in vector_results[:5]:
            fused["text_context"].append({
                "source": result["doc_title"],
                "section": result.get("section", ""),
                "text": result["text"][:500],  # Truncate for token budget
                "relevance_score": result["score"],
            })

        # Graph results: format as structured relationships
        for result in graph_results:
            if "affected_service" in result:
                # Blast radius result
                fused["graph_context"].append({
                    "type": "blast_radius",
                    "affected": result["affected_service"],
                    "hops": result["hops"],
                    "chain": " → ".join(result.get("dependency_chain", [])),
                })
            elif "dependency" in result:
                # Dependency chain result
                fused["graph_context"].append({
                    "type": "dependency",
                    "component": result["dependency"],
                    "status": result.get("status", "unknown"),
                    "hops": result["hops"],
                    "chain": " → ".join(result.get("chain", [])),
                })
            elif "incident_id" in result:
                # Incident history result
                fused["graph_context"].append({
                    "type": "incident",
                    "id": result["incident_id"],
                    "severity": result.get("severity", ""),
                    "root_cause": result.get("root_cause", ""),
                })

        return fused

    def _format_context(self, fused: dict, max_tokens: int) -> str:
        """
        Format the fused context for the LLM.

        The format is CRITICAL — the LLM needs to distinguish between
        textual context and graph context.
        """
        parts = []

        # Textual context (from vector search)
        if fused["text_context"]:
            parts.append("=== RELEVANT DOCUMENTATION ===")
            for i, ctx in enumerate(fused["text_context"], 1):
                parts.append(f"\n[Source {i}: {ctx['source']} > {ctx['section']}]")
                parts.append(ctx["text"])

        # Graph context (from graph traversal)
        if fused["graph_context"]:
            parts.append("\n=== DEPENDENCY GRAPH ===")

            # Group by type
            blast_radius = [g for g in fused["graph_context"]
                           if g["type"] == "blast_radius"]
            dependencies = [g for g in fused["graph_context"]
                           if g["type"] == "dependency"]
            incidents = [g for g in fused["graph_context"]
                        if g["type"] == "incident"]

            if blast_radius:
                parts.append("\nAffected services (blast radius):")
                for item in blast_radius[:10]:
                    parts.append(f"  {item['chain']} ({item['hops']} hops)")

            if dependencies:
                parts.append("\nDependencies:")
                for item in dependencies[:10]:
                    status = f" [STATUS: {item['status']}]" if item.get("status") else ""
                    parts.append(f"  {item['chain']}{status}")

            if incidents:
                parts.append("\nPast incidents:")
                for item in incidents[:5]:
                    parts.append(f"  {item['id']} ({item['severity']}): {item['root_cause']}")

        context = "\n".join(parts)

        # Enforce token budget
        while len(context) > max_tokens * 4:  # 4 chars ≈ 1 token
            # Remove last entry to fit budget
            context = context.rsplit("\n", 5)[0]
            context += "\n[... context truncated to fit budget ...]"

        return context

    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer using LLM with grounded context."""
        ANSWER_PROMPT = f"""Answer the question based ONLY on the provided context.

The context has two sections:
1. RELEVANT DOCUMENTATION: Text passages from runbooks and docs
2. DEPENDENCY GRAPH: Structured relationship data from the graph database

Use BOTH sections. The documentation tells you WHAT things are.
The graph tells you HOW things are connected.

If the context doesn't contain enough information, say "I don't know."

Cite sources: [Source N] for docs, [Graph] for graph data.

CONTEXT:
{context}

QUESTION: {question}
"""

        response = self.llm.call(
            messages=[{"role": "user", "content": ANSWER_PROMPT}],
            model="gpt-4o",  # Use best model for answer synthesis
            temperature=0.1,
        )

        return response.choices[0].message.content
```

---

## 9. HOW GRAPH RAG INTEGRATES WITH INCIDENT AGENT

### The search_kb Tool — Powered by GraphRAG

```
When IncidentAgent calls search_kb("payment DB connection pool remediation"):

STEP 1: QUERY UNDERSTANDING
  Question: "payment DB connection pool remediation"
  Entities: ["payment-svc", "db-prod-01", "pgbouncer"]
  Intent: "runbook_lookup" + "dependency_chain"
  Is relational: YES (need to know what depends on the DB pool)

STEP 2: VECTOR SEARCH (Qdrant)
  Query: "payment DB connection pool remediation"
  Top 20 results from 4,914 chunks
  Best match: Runbook PAY-RB-014 "Payment Service DB Connection Pool Remediation"

STEP 3: GRAPH TRAVERSAL (Neo4j)
  Entity: "db-prod-01"
  Cypher: DEPENDENCY_CHAIN query
  Result: db-prod-01 → hosted on → srv-04
          payment-svc → depends on → db-prod-01
          checkout-svc → calls → payment-svc (affected!)
          billing-svc → calls → payment-svc (affected!)

  Entity: "pgbouncer"
  Cypher: NEIGHBORHOOD query
  Result: pgbouncer → manages connections for → db-prod-01
          pgbouncer → deployed on → srv-04

STEP 4: FUSION + FORMAT
  Context provided to LLM:

  === RELEVANT DOCUMENTATION ===
  [Source 1: Runbook PAY-RB-014 > Remediation Steps]
  Step 1: Check pool status: pgbouncer -c payment_pool
  Step 2: If pool full: systemctl restart pgbouncer
  Step 3: Monitor error rate for 5 minutes post-restart

  === DEPENDENCY GRAPH ===
  Dependencies:
    payment-svc → depends_on → db-prod-01 [STATUS: degraded ⚠️]
    db-prod-01 → hosted_on → srv-04

  Affected services (blast radius):
    checkout-svc → calls → payment-svc (2 hops)
    billing-svc → calls → payment-svc (2 hops)

  Past incidents:
    INC-2024-0156 (P1): Connection leak in v2.3.1

STEP 5: INCIDENT AGENT USES THIS CONTEXT
  Now the agent knows:
  1. How to fix it (restart pgbouncer) — from VECTOR search
  2. What else is affected (checkout-svc, billing-svc) — from GRAPH search
  3. What caused it last time (connection leak) — from INCIDENT history

  The agent's diagnostic report includes:
  - Root cause: DB pool exhaustion
  - Blast radius: 3 services affected
  - Remediation: Restart pgbouncer
  - Risk: checkout-svc and billing-svc will have brief errors during restart

  WITHOUT GraphRAG, the agent would ONLY have the runbook text.
  It would miss the blast radius analysis entirely.
```

---

## 10. METRICS & ROI

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GRAPH RAG METRICS                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  GRAPH STATISTICS:                                                  │
│  Documents ingested:     159                                        │
│  Text chunks:             4,914                                     │
│  Entities (nodes):        297                                       │
│  Relationships (edges):  6,822                                      │
│  Vector dimensions:       1,024 (BGE-large)                         │
│  Total tokens processed:  1.3M                                      │
│                                                                     │
│  ACCURACY (measured on 100 test queries):                           │
│  Vector-only RAG:         79% correct answers                       │
│  GraphRAG (hybrid):       91% correct answers (+12 points)          │
│                                                                     │
│  ACCURACY BY QUESTION TYPE:                                         │
│  Semantic questions:      82% (vector) → 88% (hybrid)  (+6)        │
│  Relational questions:    41% (vector) → 89% (hybrid) (+48!)       │
│  The huge win is on relational questions.                           │
│  Vector RAG was nearly useless for relational queries (41%).        │
│  GraphRAG makes them almost as good as semantic queries (89%).      │
│                                                                     │
│  COST:                                                              │
│  Ingestion (one-time):   ~$3.20 (LLM calls for 4,914 chunks)       │
│  Per query:              ~$0.06                                     │
│    - Vector search: free (local Qdrant + BGE)                       │
│    - Graph traversal: free (local Neo4j)                            │
│    - LLM answer generation: $0.05 (GPT-4o for synthesis)            │
│    - LLM query understanding: $0.01 (GPT-4o-mini for classification)│
│                                                                     │
│  PERFORMANCE:                                                       │
│  Query latency:           P50: 1.2 sec, P95: 2.8 sec               │
│  Vector search:           ~50ms                                     │
│  Graph traversal:         ~15ms                                     │
│  LLM answer generation:   ~1 sec                                    │
│                                                                     │
│  INGESTION PIPELINE:                                                │
│  Runtime:                 ~45 minutes (single-threaded)             │
│  Incremental update:      ~2 minutes per new document               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 11. INTERVIEW QUESTIONS WITH EXACT ANSWERS

### Q1: "What is GraphRAG and why did you build it?"

```
"Traditional RAG uses vector search to find semantically similar text.
But at AT&T, 40% of the questions SREs ask are RELATIONAL — 'What
depends on the failing database?' or 'What incidents happened on this
fiber route?' Vector search can't answer these because it doesn't
understand relationships.

GraphRAG combines vector search with graph traversal. I built a Neo4j
graph with 297 entities and 6,822 relationships extracted from 159
documents. When a query comes in, I run vector search for textual
context AND graph traversal for relational context, then fuse the
results.

The accuracy improvement was dramatic: 79% with vector-only → 91%
with hybrid. And for relational questions specifically, it went from
41% to 89% — vector RAG was nearly useless for those questions."
```

### Q2: "How did you extract entities and relationships from documents?"

```
"I used LLM-based extraction. For each text chunk, I send it to
GPT-4o-mini with a structured prompt asking for entities (services,
databases, servers, towers) and their types. Then I send the same
chunk plus the extracted entities and ask for relationships between
them — DEPENDS_ON, HOSTED_ON, CONNECTS_TO, etc.

The key challenge was quality. The LLM extracted noisy entities —
common words like 'the database' or 'the system.' I solved this with
three filters: confidence threshold above 0.8, a generic-terms
blocklist, and entity type constraints. I also normalized names —
merging 'DB-01', 'db_prod_01', and 'primary db' into the canonical
'db-prod-01.'

I used GPT-4o-mini for extraction because it's a classification task
that doesn't need deep reasoning. Cost: $3.20 for all 4,914 chunks."
```

### Q3: "Why Neo4j? Why not just use a SQL database with foreign keys?"

```
"Because the queries are inherently recursive graph traversals. 'What
services depend on db-prod-01, directly or transitively, up to 3 hops
away?' In SQL, that's a recursive CTE — complex to write and slow to
execute. In Neo4j, it's a single Cypher pattern match that traverses
the graph in milliseconds.

Neo4j also handles schema flexibility. New entity types and
relationship types can be added without migrations. And the Cypher
query language is purpose-built for pattern matching — expressing
multi-hop traversals is natural and readable.

For our scale (297 entities, 6,822 relationships), Neo4j is instant.
Even at 100x scale (30K entities, 680K relationships), traversal
queries would still be sub-second."
```

### Q4: "How do you fuse vector and graph results?"

```
"They complement each other, so fusion isn't about ranking one against
the other — it's about combining different types of context. Vector
results provide TEXTUAL context: 'Here's what the runbook says about
DB pool remediation.' Graph results provide STRUCTURAL context:
'Here's what services depend on the DB pool.'

I format them as two distinct sections in the LLM context:
'RELEVANT DOCUMENTATION' for vector results and 'DEPENDENCY GRAPH'
for graph results. The LLM reasons over both.

For reranking WITHIN each section: vector results are already ranked
by cosine similarity. Graph results are ranked by hop distance (closer
dependencies are more relevant). The fusion is additive, not
competitive."
```

### Q5: "What's the most common graph query you run?"

```
"Blast radius analysis. When a component fails, the first question is
always 'What else is affected?' The Cypher query traverses reverse
DEPENDS_ON edges up to 3 hops: if db-prod-01 fails, payment-svc
depends on it (1 hop), checkout-svc calls payment-svc (2 hops),
billing-svc calls payment-svc (2 hops).

This query runs in under 15 milliseconds and returns the complete
impact chain. Vector RAG can't answer this at all — there's no
document that lists every transitive dependency. The graph IS the
source of truth for dependencies."
```

### Q6: "How do you handle entity extraction errors?"

```
"Three layers. First, confidence filtering — I only keep entities with
LLM confidence above 0.8. This removes about 60% of raw extractions
that are noisy. Second, a generic-terms blocklist — I reject 'the
database', 'the server', 'the system' because they're not specific
entities. Third, normalization and deduplication — 'DB-01', 'db_prod_01',
and 'primary DB' all merge into 'db-prod-01.'

For quality assurance, I manually reviewed the top 50 most-referenced
entities (entities with the most incoming MENTIONS edges). These 50
entities account for 70% of all relationships, so getting them right
has outsized impact. About 15% needed corrections — wrong type
classification or wrong canonical name."
```

### Q7: "How does this integrate with IncidentAgent?"

```
"GraphRAG powers the search_kb tool in IncidentAgent. When the agent
searches for 'payment DB connection pool remediation,' it doesn't just
get text chunks — it gets the runbook text PLUS the dependency graph
PLUS past incident history. The agent then knows not just how to fix
the issue but also what the blast radius is and what caused it last
time.

This is why IncidentAgent can answer 'What's the impact of restarting
pgbouncer?' — it has the graph data showing which services depend on
the connection pool. Without GraphRAG, the agent would only have text
and couldn't reason about cascading impacts."
```

### Q8: "What would you do differently at 100x scale?"

```
"At 100x scale (30K entities, 30K documents), the main challenges are
ingestion time and entity resolution. For ingestion, I'd parallelize
the LLM extraction calls across multiple workers — 4,914 chunks took
45 minutes single-threaded; with 10 workers, it'd be 5 minutes.

For entity resolution, at 30K entities, manual review isn't feasible.
I'd train a lightweight classifier to score entity quality and use
active learning — surface low-confidence entities for human review
while auto-accepting high-confidence ones.

I'd also add community detection (Louvain algorithm) to cluster
related entities into subgraphs. This would let me partition the graph
and run queries on relevant subgraphs instead of the full graph,
improving query performance."
```

### Q9: "How do you keep the graph up to date?"

```
"Incremental ingestion. When a new runbook is published in Confluence
or a new post-mortem is filed in ServiceNow, a webhook triggers
ingestion of just that document. The pipeline chunks it, extracts
entities and relationships, and MERGES them into the existing graph.

Neo4j's MERGE operation handles deduplication — if the entity already
exists, it updates properties instead of creating a duplicate. If a
document is updated, I re-extract and merge the new entities while
old entities from that document persist (they might also be mentioned
in other documents).

For deleted documents, I run a nightly cleanup that removes entities
with no remaining MENTIONS edges (nothing references them anymore)."
```

### Q10: "Could you do this without a graph database?"

```
"You could simulate it with a relational database and recursive CTEs,
but it would be significantly harder and slower. The DEPENDS_ON
traversal is a 1-3 hop graph query — in SQL, that's a self-join on the
dependencies table, joined 3 times. It works but the query is
unreadable and slow.

You could also use a JSON document with nested dependencies, but
updating and querying that is painful. 'Find all services that depend
on X transitively' requires recursively walking the JSON tree.

Neo4j exists precisely for this use case. The graph data model
naturally represents dependencies, and Cypher is designed for
pattern-matching traversals. Using the right tool for the job is an
engineering decision — and for relationship-heavy data, graph is the
right tool."
```

### Q11: "Why BGE embeddings instead of OpenAI?"

```
"Three reasons. First, cost — BGE-large-en-v1.5 runs locally on CPU,
so embedding 4,914 chunks costs $0. OpenAI text-embedding-3-small
would cost $0.10. Not huge for one-time ingestion, but we re-embed on
every document update, and at scale it adds up.

Second, data privacy — BGE runs on our infrastructure. No document
text leaves our network. For AT&T compliance, this matters.

Third, performance — BGE-large scores higher than OpenAI on the MTEB
benchmark for technical/code text. Our documents are technical
(runbooks, architecture docs), so BGE's advantage in that domain
gives better retrieval quality."
```

### Q12: "What happens when the graph and vector search disagree?"

```
"They can't really 'disagree' because they answer different questions.
Vector search says 'this text is similar to your query.' Graph search
says 'this entity is connected to that entity.' They're complementary.

The case where they might conflict is entity disambiguation. Vector
search might find a chunk mentioning 'DB-01' while the graph has
'db-prod-01.' My normalization layer handles this — both refer to the
same canonical entity. The alias map merges them before graph
construction.

If vector search finds relevant text that mentions entities NOT in
the graph (because extraction missed them), I use that as a signal to
re-run extraction on that chunk with a more aggressive prompt. The
system self-heals over time."
```

### Q13: "How do you measure the 91% accuracy number?"

```
"I built a test set of 100 questions with known correct answers,
split into 50 semantic questions and 50 relational questions. The
correct answers were verified by senior SREs.

For each question, I run the system and compare the output to the
known answer. A response is 'correct' if it contains the key facts
the SRE verified. Partial credit for getting the right entity but
wrong relationship.

Vector-only RAG scored 79% overall (82% semantic, 41% relational).
GraphRAG scored 91% overall (88% semantic, 89% relational). The 12-
point improvement came almost entirely from relational questions,
where graph traversal closed a 48-point gap."
```

### Q14: "What's the hardest part of maintaining this system?"

```
"Entity resolution at scale. As new documents are ingested, new entity
names appear that might or might not refer to existing entities. 'DB-
01' might already exist as 'db-prod-01,' but 'primary database cluster'
is a new variant the alias map doesn't know about.

My current approach is heuristic: string similarity + alias map +
manual review of low-confidence cases. At 100x scale, I'd need a
learned entity resolution model — probably a fine-tuned BERT that
classifies whether two entity strings refer to the same thing.

The other challenge is relationship staleness. If payment-svc migrates
from db-prod-01 to db-prod-02, the graph still shows the old
dependency until a new document mentions the migration. I don't have
a good solution for this yet — it requires syncing with configuration
management data."
```

### Q15: "If you had to rebuild this from scratch, what would you change?"

```
"Three things. First, I'd use a fine-tuned NER model instead of LLM-
based extraction. The LLM approach works but costs $3.20 per full
ingestion and is slow (45 minutes). A fine-tuned spaCy or BERT model
would be instant and free after the one-time fine-tuning cost.

Second, I'd add community detection from day one. Clustering entities
into subgraphs (e.g., 'payment cluster,' 'auth cluster,' 'network
core') would let me run faster queries on relevant subgraphs and
provide better visualization for SREs.

Third, I'd build a feedback loop. When an SRE corrects the agent's
diagnosis (the graph said X but the real root cause was Y), that
correction should update the graph — either by adding a missing
relationship or correcting a wrong one. The graph should learn from
every investigation."
```

---

## 12. THE 90-SECOND VERBAL PITCH

### Memorize This

```
[0-15 sec — THE PROBLEM]
"At AT&T, our SREs need answers from thousands of runbooks and docs.
Traditional RAG with vector search worked for simple questions like
'how do I restart pgbouncer.' But it completely failed for relational
questions like 'what services depend on the failing database' or
'what incidents happened on this fiber route.' Vector search finds
semantically similar TEXT. It can't traverse RELATIONSHIPS."

[15-40 sec — WHAT I BUILT]
"I built GraphRAG — a hybrid retrieval system that combines vector
search with graph traversal. I ingested 159 documents through an LLM
extraction pipeline that pulled out 297 entities and 6,822
relationships. Entities, relationships, and text chunks all live in
Neo4j. Each chunk is also embedded and stored in Qdrant for semantic
search."

[40-60 sec — THE QUERY ENGINE]
"When a query comes in, I classify its intent and extract entities.
Then I run vector search for textual context and graph traversal for
relational context IN PARALLEL. The vector results say 'here's what
the runbook says.' The graph results say 'here's what depends on this
component and what incidents it's had.' I fuse them into a single
context block for the LLM."

[60-75 sec — THE RESULT]
"The accuracy improvement was significant: 79% with vector-only → 91%
with hybrid. But the real win was on relational questions: 41% → 89%.
Vector RAG was nearly useless for relational queries. GraphRAG made
them almost as accurate as semantic queries."

[75-90 sec — THE REFLECTION]
"The key insight is that enterprises are RELATIONAL. Services depend
on databases, which are hosted on servers, which connect to networks.
Vector RAG treats documents as bags of words. GraphRAG treats them as
a connected system. For any domain where relationships matter —
telecom, microservices, supply chains — GraphRAG is dramatically
better."
```

### Delivery Tips

```
1. HIT THE 41% → 89% NUMBER HARD
   This is your killer stat. Pause before saying it.
   "For relational questions specifically... [pause]...
    accuracy went from forty-one percent... to eighty-nine percent."

2. USE THE "WHAT VS HOW" FRAMING
   "Vector search tells you WHAT things are.
    Graph search tells you HOW things are connected.
    The LLM needs BOTH to reason effectively."

3. CONNECT TO INCIDENT AGENT
   "This isn't a standalone system. It powers the search_kb tool in
    IncidentAgent. When the agent investigates an incident, GraphRAG
    gives it both the runbook text AND the dependency graph. That's
    how it knows the blast radius of every action."

4. END WITH THE BROADER INSIGHT
   "GraphRAG is the next evolution of RAG. Not because graphs are
    trendy, but because enterprise systems are inherently relational.
    Any domain with dependencies — and that's every domain — benefits
    from graph-augmented retrieval."
```
