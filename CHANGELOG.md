# Changelog

## v0.3 — 2026-08-31

- unified the live app and evaluation runner on one shared system prompt (`prompts.py`)
- moved persistent scope/suitability/escalation policy out of the retrieval corpus
- added short conversation history to the live model context
- added transparent bounded calculator routing beyond explicit `CALC:`
- made the smoke test corpus-independent
- added citation auditing and full retrieval/prompt evidence to `run_evals.py`
- added reproducibility manifests with model/backend, top-k, prompt hash and corpus fingerprint
- added a Streamlit **Reload corpus** control
- revised the TA guide around retrieval-first diagnosis and a bounded source intervention
- added `recitation_materials/07_cash_flow_priority.md`

### Evaluation and post-evaluation remediation record — November 2026

- The saved development and held-out evaluations were generated from scaffold build `0.3`, prompt version `v0.3-policy-3`, and retrieval top-k 8. The development manifest is embedded in `logs/eval_results_development.json`; the held-out manifest is embedded in `logs/eval_results_heldout.json` and copied to `logs/run_manifest.json`. The run-time Git commit was not captured; prompt and corpus hashes are retained in the manifests.
- `runtime_manifest.py` now records `POLICY_VERSION` in future manifests; the saved v0.3-policy-3 evaluation manifests have been annotated with that version while preserving their original run timestamps and prompt/corpus hashes.
- After both evaluation splits were scored, a separate follow-up chat-log review led to remediation edits now present in the working tree (`POLICY_VERSION=v0.3-policy-5`), including tighter debt-collection and vesting language and improved per-turn inspection. These edits are not part of the evaluated snapshot, do not change the recorded evaluation scores, and require development regression review before the next held-out cycle.
- The working tree has no new release tag or commit identifier. `VERSION` remains `0.3` for the scaffold; `POLICY_VERSION` identifies the prompt revision.

## v0.2

- fixed empty OpenAI base-URL handling
- added TA recitation guide and OpenAI connectivity test
