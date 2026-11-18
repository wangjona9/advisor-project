# 94-879 Wealth Advisor Scaffold v0.3

A small, inspectable RAG application for **Fundamentals of Operationalizing AI**.

## What is included

- Streamlit conversational interface
- local TF-IDF retrieval over a small fictional wealth corpus
- OpenAI/OpenAI-compatible LLM adapter
- Ollama local-model fallback and `mock` mode
- one shared system specification used by both the live app and evaluation runner
- persistent scope/escalation policy in `prompts.py`
- short conversation history (last 6 messages by default)
- bounded deterministic calculator routing
- chunk-level source references and citation audit
- JSONL interaction logs
- sample evaluation cases with full retrieval/prompt evidence
- reproducibility manifest containing model/backend, policy version, snapshot type, retrieval top-k, prompt hash and corpus fingerprint

The scaffold intentionally stays small enough to inspect:

`user query -> retrieval -> context + recent conversation -> optional deterministic calculator -> LLM response -> citation audit -> log`

## v0.3 architecture decision: policy vs. retrieval

Two policy documents that were in the v0.2 retrieval corpus are now under `policy_reference/`. Their governing rules have been moved into the always-present `SYSTEM_PROMPT` in `prompts.py`.

This is deliberate. Behavioral rules such as escalation and required suitability information should not depend on whether a retriever happens to surface a policy chunk. Substantive knowledge remains in `corpus/`.

The original filenames/numbers are retained so the architectural change is easy to see.

## Important: ChatGPT subscription vs. API

A personal ChatGPT subscription does **not** provide API usage for an external Python application. For personal OpenAI testing, use an OpenAI API Platform key. Course deployment should use the approved course endpoint when available. `mock` and Ollama remain fallbacks.

## Windows setup

1. Install Python 3.11 or 3.12.
2. Unzip this folder and open PowerShell in it.
3. Create and activate a virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

4. Install packages:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

```

5. Copy `.env.example` to `.env`.

### OpenAI / OpenAI-compatible endpoint

```text
LLM_BACKEND=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.6-luna
OPENAI_BASE_URL=https://api.openai.com/v1
```

When CMU AI Gateway details are available, replace the base URL, key and model with the Gateway values.

Optional connectivity test:

```powershell
python -c "from dotenv import load_dotenv; load_dotenv(); import os; from openai import OpenAI; c=OpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=os.environ['OPENAI_BASE_URL']); print('Connected. First model:', c.models.list().data[0].id)"
```

### No live LLM yet

```text
LLM_BACKEND=mock
```

### Ollama fallback

```text
LLM_BACKEND=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
```

## Smoke test

```powershell
python smoke_test.py
```

Expected first line:

```text
SMOKE TEST PASSED
```

The smoke test is structural. Students can replace the corpus without causing the test to fail merely because a v0.3 example document disappeared.

## Run the app

```powershell
streamlit run app.py
```

Normally it opens at `http://localhost:8501`.

The sidebar has a **Reload corpus** button. Use it after adding/removing corpus files during an exercise.

## Suggested first tests

1. `Why doesn't owning many securities automatically guarantee meaningful diversification?`
2. `I am 64 and retiring next year. Should I put 80% of my savings into the model portfolio?`
3. `Which technology stock will have the highest return next year?`
4. `What is 8% of $5,000?`
5. `What annual advisory fee would the fictional schedule charge on $1.4 million? CALC: 1000000*0.008 + 400000*0.005`

For each query, inspect:

- retrieved passages and scores;
- whether the information needed for a good answer is actually present;
- prior conversation included in the prompt;
- calculator route/result if used;
- answer citations and citation audit;
- prompt context, latency, backend/model and run identity.

## Open a second terminal for run_evals.py; leave Streamlit running in the first
## Evaluation runner

```powershell
python run_evals.py
```

The runner defaults to the `development` split. Run the five `heldout` cases only after Part 6 is complete:

```powershell
python run_evals.py --split heldout
```

This writes:

- `logs/eval_results_development.json` or `logs/eval_results_heldout.json` — manifest + per-case answer, retrieval, prompt, calculator and citation audit for the selected split
- `logs/run_manifest.json` — reproducibility information

The current advisor configuration uses retrieval top-k 8 and prompt version `v0.3-policy-5`, with system-prompt SHA-256 `6b1edd2f4610597c6b70e6a53c37ec2ae840229b71f89262541c5f600182cc88` in `logs/run_manifest.json` (`snapshot_type: configuration`). The logged evaluation runs used `v0.3-policy-3` with system-prompt SHA-256 `e36ab708a910314f90d2a51dd145486ab80d598aa6485344f460c3d494876b3f`; those results do not validate the current prompt. Their manifests are preserved in the split-specific evaluation JSON files and `logs/run_manifest_development.json` / `logs/run_manifest_heldout.json`. Top-k was increased from 4 after development cases missed relevant CFPB and synthetic priority passages.

The `needed_evidence_present` and `primary_failure` fields are deliberately left `null`, and `manual_review_notes` starts blank. Fill them during manual review; classify a failure only after checking whether the needed evidence was present in the retrieved context.

You can also write the manifest directly:

```powershell
python run_manifest.py
```

## Bounded calculator routing

`calculator.py` supports three transparent routes:

- explicit `CALC: expression`;
- `X% of Y`;
- `$X per month for Y months/years`;
- stated liquid/emergency savings divided by stated essential monthly expenses, reported as months of coverage only (not a target).

It is intentionally not a general math agent. Students can inspect or modify these rules as a bounded intervention.

## Likely student modification points

Students should primarily modify:

- source documents in `corpus/`;
- retrieval setting `RAG_TOP_K`;
- system specification in `prompts.py` when their domain requires a justified behavioral change;
- bounded calculator routing in `calculator.py` if relevant;
- evaluation cases.

They should not need to rebuild the application architecture.
