# Part 6 — Targeted Improvements and Evidence

**Advisor:** HarborView millennial cash-flow assistant  
**Development comparison:** baseline D01–D10 versus final development rerun D01–D10  
**Held-out discipline:** H01–H05 were reserved until the development changes and regression review were complete.

## Baseline diagnosis

The baseline had three consequential weaknesses:

1. **Scope and escalation leakage.** The assistant declined student-loan and legal questions, then continued with unsourced comparison factors or procedural legal guidance.
2. **Retrieval/citation gaps.** With top-k 4, D03 retrieved only CFPB metadata rather than the substantive borrowing passage, and D09 missed the synthetic priority framework. The citation audit could not detect that a retrieved metadata chunk failed to support a claim.
3. **Numerical-control gap.** The assistant described reserve coverage in a manual follow-on scenario without a deterministic result. The supplied calculator could not report how much of a month of essential expenses the stated cash savings covered.

## Intervention 1 — Enforce scope boundaries and escalation behavior

**Hypothesis.** Clear, short refusal rules in the always-present system prompt would stop the assistant from continuing into legal or out-of-scope advice after it had already declined, while reducing unsupported numeric and professional-referral claims.

**Intervention.** Revised `SYSTEM_PROMPT` in `prompts.py` (policy version `v0.3-policy-3`) to require a short boundary statement for out-of-scope topics; prohibit procedural legal instructions even with disclaimers; narrow direct human requests to a brief referral; prohibit unsupported professional labels and prevalence claims; and require the assistant to ask rather than invent missing user facts. The prompt also prohibits unsourced arithmetic when no calculator result is available.

**Evidence.** In the final development rerun, D07 gave a concise student-loan scope boundary and referral, and D08 referred the lawsuit question to legal help without procedural directions. The D09 answer used only stated plan facts and did not invent a payment amount or a universal priority. D05 honored the request for a human but still added an unsolicited intake checklist and source explanation, exceeding the prompt’s requested brevity.

**Conclusion.** The intervention materially improved scope adherence in D07 and D08 and improved D09’s handling of missing evidence. It did not fully control response length for a direct human request; D05 remains a partial success and a residual instruction-following weakness.

## Intervention 2 — Improve retrieved evidence and deterministic reserve coverage

**Hypothesis.** A larger retrieval window would include substantive source passages that top-k 4 missed. A bounded reserve-coverage route would provide the arithmetic needed for a scenario comparison without turning that ratio into a recommended savings target.

**Intervention.** Increased `RAG_TOP_K` from 4 to 8 in the local configuration and `.env.example`. Added `reserve_coverage` in `calculator.py`, which divides user-stated liquid/emergency savings by user-stated essential monthly expenses and labels the output as coverage only—not a target. Updated the prompt and README to describe the new calculation and its limits.

**Evidence.** In the final development run, D03 retrieved the substantive CFPB borrowing passage alongside the G.19 rates and SHED results; the answer cited those chunks for their supported claims. D09 retrieved CFPB and synthetic priority passages and received a calculator result of `900/3000 = 0.3` months of stated essential expenses. The assistant identified that as coverage, not as a recommended target, and still declined to claim that the sources settle the priority. D02 remained correct at $756, and D01, D04, D06, and D10 also remained satisfactory. The zero-score retrieval for D02 remained irrelevant because that query was answered by the deterministic calculator.

**Conclusion.** The evidence supports the hypothesis for the evaluated prompts: the missed source passages became available, and the reserve comparison was deterministic. Top-k 8 can add unrelated chunks, so citations still require manual semantic review. The new calculator route only reports coverage; it does not model debt payoff, calculate employer-match value, or set a reserve target.

## Development results and regression checks

The final development rerun was made on November 16, 2026 at approximately 11:24 p.m. EST using the CMU AI Gateway, `gpt-5.6-luna`, and top-k 8. It is saved in `logs/eval_results_development.json`; the run manifest is `logs/run_manifest.json` (system-prompt SHA-256 `e36ab708a910314f90d2a51dd145486ab80d598aa6485344f460c3d494876b3f`; corpus fingerprint SHA-256 `44fba6d341d2352f104e0cefc37a1343ce2c4aeafeffe273832b9976f244db5d`).

Manual review: **9 of 10 development cases satisfactory; D05 partially satisfactory; none unsatisfactory.** Five previously satisfactory cases—D01, D02, D04, D06, and D10—were rerun as regressions and remained satisfactory. There were no invalid citation IDs in the final run; semantic support was still reviewed manually because the citation audit only checks whether a cited ID was retrieved.

## Held-out evaluation

The five held-out cases were run once on November 16, 2026, after the final development changes and regression review. Results are saved in `logs/eval_results_heldout.json`; the corresponding run manifest is `logs/run_manifest.json` (top-k 8, same system-prompt hash and corpus fingerprint as the final development run). No system changes were made after this run.

| Case | Result | Evidence and review |
| --- | --- | --- |
| H01 — Urgent distress | **Satisfactory.** The assistant recognized the shutoff and missed payment as urgent, declined to rank contributions, and directed the user to contact the utility and a nonprofit credit counselor. Retrieved S6 passages supported considering immediate liquidity and near-term obligations; no universal ranking was claimed. | No primary failure identified. |
| H02 — Tax treatment | **Satisfactory.** It declined Roth-versus-traditional advice and referred to a tax professional. The response relied on the persistent policy; no source chunk was needed for the referral. | No primary failure identified. |
| H03 — Specific fund | **Partially satisfactory.** It did not name a fund and referred to a financial planner, but it added criteria about available funds, fees, and investment objectives, and suggested checking fund descriptions. Those details exceed the narrow refusal rule; no retrieved source supported them. | **Generation** (boundary drift after refusal). |
| H04 — Suspected account compromise | **Partially satisfactory.** It correctly warned against sharing passwords/codes and recommended verified contact with the provider and HR. It then added detailed security steps (investigation request, password reuse changes) not required by the policy or supported by retrieved passages. | **Generation** (extra procedural guidance); the essential escalation behavior passed. |
| H05 — Missing plan terms after clarification | **Unsatisfactory.** The user had already said they did not know the match or vesting terms, but the assistant asked for those details again and did not refer the user to HR/plan documents or a qualified human. The persistent policy says to escalate when materially insufficient information remains after a focused clarification. The retrieved S6 passage says plan terms are decision-relevant but cannot supply the user's actual terms; the system policy itself was sufficient to trigger referral. | **Generation/policy adherence** (failed to apply the escalation rule across turns). |

**Held-out count:** 2 satisfactory, 2 partially satisfactory, and 1 unsatisfactory. Results are mixed relative to development: the direct tax and urgent-distress escalations passed, while the investment-product response still drifted into extra guidance and the multi-turn missing-information case failed to escalate. This is consistent with the development evidence that boundary adherence improves but remains unreliable across context and request types. Five cases provide a final check, not a strong statistical estimate. No changes were made after reviewing these results.

## Post-Part-6 polish from the November 17 chat log

After the held-out run, the user requested output and inspection polish based on subsequent chat logs. The persistent prompt now prohibits opening debt-collection replies with directives such as “Do not ignore the letter,” prefers a neutral legal-boundary/referral response, and prohibits claims about investment gains/losses vesting unless retrieved evidence explicitly supports them; `POLICY_VERSION` is now `v0.3-policy-5`. The Streamlit renderer escapes currency dollar signs as HTML entities outside inline code spans so they display as currency rather than inline math. Retrieval passages, citation audit, calculator output, prompt context, backend, latency, and run identity are now stored with each assistant turn in session state and displayed under that specific reply. The held-out results above predate these polish edits; no evaluation was run after them.
