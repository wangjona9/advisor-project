# AI Supervision Note

During this project, I used generative AI to help draft the advisor prompt, organize retrieval and evaluation changes, and review outputs. I treated those suggestions as proposals: I checked them against the assignment constraints, source excerpts, calculator behavior, and saved evaluation evidence before accepting or narrowing them.

## 1. Retrieval expansion

**AI-assisted proposal:** Increase retrieval from top-k 4 to top-k 8 so multi-factor questions could receive the CFPB borrowing passage and the synthetic cash-flow framework alongside rate and plan evidence.

**Decision:** Accepted for the development experiment, while retaining the rule that retrieved material is only candidate evidence and the synthetic priority guide must not be presented as authoritative.

**Verification and limitation:** The final development rerun made the substantive CFPB passage available for D03 and the S6 priority passage available for D09. Manual review found these useful for the evaluated cases. A wider retrieval window can also return unrelated chunks, and a citation-ID audit does not prove semantic support, so I kept manual claim-to-source review in the evaluation protocol. This intervention improved retrieval coverage in the tested set; it does not establish that top-k 8 is optimal for future prompts.

## 2. Reserve-coverage arithmetic

**AI-assisted proposal:** Add a deterministic calculator route for comparing stated liquid savings with stated essential monthly expenses, rather than relying on language-model arithmetic.

**Decision:** Accepted with a narrow scope. The tool reports a ratio in months of the user's stated expenses; it does not set a target, recommend an allocation, model debt payoff, or compute employer-match value.

**Verification and limitation:** The development case D09 returned $900 / $3,000 = 0.3 months, and the output identified this as coverage rather than a recommended target. The supplementary fictional scenario of $1,200 / $3,000 likewise represents 0.4 months, but its chat transcript did not include the app's calculator trace, so that instance was not counted as verified tool evidence. The held-out set did not establish performance on changed or contradictory inputs across a long conversation; that remains for the next internal test cycle.

## Supervision practice

I retained the system's source and scope limits even when a fluent answer would have been more decisive. In particular, the authoritative corpus does not set a universal priority order or a fixed emergency-fund target, and the retrieved IRS vesting excerpt does not support claims about how investment gains and losses vest. I recorded the unsatisfactory H05 held-out result without changing the scored run, and the later prompt/interface edits are labeled as post-evaluation remediation candidates in the Part 6 log and run provenance. They require a new development regression cycle before their behavior can be described as improved.
