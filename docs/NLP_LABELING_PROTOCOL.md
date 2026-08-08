# NLP and manual labeling protocol

## Unit of observation

A candidate passage is a sentence plus up to two neighboring sentences from an annual report or WBES innovation response.

## Labels

- `0_no_ai`: unrelated technology, generic automation, or ambiguous “smart” language.
- `1_rhetoric`: AI discussed as trend, ambition, risk, investment theme, or future plan without an implemented use.
- `2_deployed`: concrete AI/ML/NLP/computer-vision system used in a named business function.
- `3_core`: deployment materially embedded in core production, service delivery, underwriting, risk, logistics, pricing, or a commercial AI product.

## Functional tags

`customer_service`, `hr`, `finance`, `risk_compliance`, `marketing`, `pricing`, `operations`, `production`, `logistics`, `cybersecurity`, `analytics`, `product_service`, `other`.

## Rules

1. “smart” alone is not AI.
2. “automation” alone is not AI.
3. buying an AI company is not operational adoption unless integration/use is described.
4. a board discussion of AI risk is rhetoric, not adoption.
5. named ML, NLP, computer vision, generative AI, LLM, chatbot or predictive model counts only when use is concrete.
6. retain the exact evidence passage and page number.
7. manual adjudication overrides the rules engine, but every override is logged.

## Validation sample

Before freezing treatment:

- manually inspect 100% of rule-engine positives
- manually inspect a stratified random sample of negatives by country/language/year
- double-code at least 20% of the labeled set
- report inter-rater agreement
- report precision, recall and F1 for the frozen classifier
