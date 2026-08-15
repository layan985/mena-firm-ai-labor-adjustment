# Independent Second-Coder Execution Protocol

## Purpose

This protocol governs the non-author coding step for the frozen 16-passage AI-evidence validation sample. It exists to test the reliability of the project's 0–3 AI substantiveness coding without exposing the second coder to founder labels before coding is complete.

The presence of this protocol does not constitute independent validation.

## Frozen object

Input: `data/validation/blinded_ai_validation_sample.csv`

The sample contains 16 deterministic validation IDs. The second coder must code all 16 rows in the existing order. Rows may not be replaced because they are difficult, ambiguous, or produce disagreement.

## Independence rule

Before completing coder 2 labels, the second coder must not inspect:

- founder labels in `data/interim/ai_evidence_labeled.csv`
- any keyed version of the validation sample
- intercoder agreement output
- adjudicated labels
- private communication revealing how the founder coded a sampled passage

The coder may use the public codebook and labeling protocol because those define the task rather than reveal founder decisions.

## Allowed materials

- `data/validation/blinded_ai_validation_sample.csv`
- `docs/AI_CODING_CODEBOOK_V0_2.md`
- `docs/NLP_LABELING_PROTOCOL.md`
- public source material necessary to understand the passage context, provided the source lookup does not reveal founder labels

## Required output

Complete `data/validation/coder_2.csv` with:

- `validation_id`
- `coder_label` as an integer 0, 1, 2, or 3
- `coder_confidence` using `low`, `medium`, or `high`
- `coder_notes` for ambiguity, context dependence, or any rule interpretation that affected the label

Do not add founder labels to this file.

## Completion record

Complete `audits/SECOND_CODER_RECORD.md` with coder identity, affiliation or independent status, coding date, materials used, conflicts, and a statement confirming whether founder labels were hidden until coding was frozen.

The project may describe this as independent second-human coding only when:

1. all 16 frozen IDs have a valid coder-2 label;
2. the completion record identifies a real non-author coder;
3. the independence statement is completed;
4. `scripts/score_intercoder_agreement.py` successfully produces the paired agreement statistics;
5. disagreements are preserved before adjudication.

## Scoring

After coder 2 freezes the file, run:

```bash
python scripts/score_intercoder_agreement.py
```

Publish:

- number double-coded
- raw agreement
- unweighted Cohen's kappa
- quadratic-weighted kappa
- confusion matrix

Do not select only agreement-favorable rows.

## Disagreement and adjudication

After scoring, build `data/validation/adjudication.csv` from rows where founder and coder-2 labels differ.

For every disagreement record:

- original founder label
- original coder-2 label
- adjudicator
- adjudication date
- final label if one is adopted
- reason
- codebook clarification needed: yes/no

Original labels are immutable evidence. An adjudicated label is a third field; it does not overwrite either original judgment.

## Interpretation rule

Agreement statistics measure coding reproducibility for this frozen passage sample. They do not validate the completeness of the AI-evidence search, the employment panel, causal identification, or the representativeness of the 50-firm frame.
