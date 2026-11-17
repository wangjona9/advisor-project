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

## v0.2

- fixed empty OpenAI base-URL handling
- added TA recitation guide and OpenAI connectivity test
