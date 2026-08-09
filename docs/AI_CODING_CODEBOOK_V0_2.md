# AI coding codebook v0.2

This codebook freezes the pilot's ordered AI-evidence labels before outcome estimation.

## Unit

One evidence passage: the focal sentence plus up to two adjacent sentences from an annual report, exchange filing, sustainability report, investor report or other approved corporate source.

## Ordered labels

### 0 — no_ai

No concrete AI evidence. Includes generic digitization, automation, analytics, "smart" technology, data science or innovation language when AI/ML/NLP/computer vision/LLM use is not established.

### 1 — rhetoric_or_plan

AI is discussed as a trend, risk, ambition, research activity, roadmap, planned investment or future deployment, but no implemented business use is established.

### 2 — operational_deployment

A named or clearly described AI/ML/NLP/computer-vision/generative-AI system is in use in a specific business function. Examples include deployed fraud detection, predictive maintenance, AI customer service, workforce tools or operational decision support.

### 3 — core_integration

AI is materially embedded in core production, service delivery, underwriting, logistics, pricing, industrial operations, product delivery or workflow redesign; or the firm documents material scaling of a core AI capability.

## Primary adoption rule

The candidate first substantive adoption year is the earliest firm-year with a manually verified label >= 2. It is not automatically accepted as causal treatment timing. Left-censoring, anticipation, persistence and reporting gaps must be audited before treatment freeze.

## Functional tags

`customer_service`, `hr`, `finance`, `risk_compliance`, `marketing`, `pricing`, `operations`, `production`, `logistics`, `cybersecurity`, `analytics`, `product_service`, `other`.

## Ambiguity rules

- "smart" alone is not AI;
- "automation" alone is not AI;
- generic predictive analytics does not count unless the passage establishes ML/AI or an approved model class;
- acquisition/investment in an AI company is not operational adoption without evidence of internal integration;
- an AI research chair, conference or partnership is label 1 unless firm deployment is separately documented;
- generative-AI roadmaps are label 1 until implemented use is documented;
- a chatbot counts as label 2 only if the firm states it is deployed and AI/NLP/generative-AI functionality is established;
- manual adjudication may override a rules-engine candidate label, but every override must be logged.

## Blinded second coding

Second coders receive only `validation_id`, evidence text, evidence year and codebook instructions. They must not receive firm identity, country, labor outcomes, first-coder label or adoption year.

For each passage they record:

- `coder_label` in {0,1,2,3};
- `coder_confidence` in {low,medium,high};
- optional `coder_notes`.

Agreement must be computed before disagreements are adjudicated.
