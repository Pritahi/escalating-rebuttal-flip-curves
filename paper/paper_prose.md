# Paper prose (final text, numbers marked [NUM:key] get filled from results_summary.json)

## Abstract (150-250 words)
When a user challenges a language model's answer, does the model update only when the user is right? We introduce escalating-rebuttal flip curves, a conversational eval that separates warranted corrections from sycophantic capitulation by construction: after an initial answer to a verified factual question, the user pushes a target answer over three escalating rebuttals - a wrong target when the model was initially correct (capitulation arm), the correct answer when it was initially wrong (warranted arm). We run [NUM:NCONV] conversations with four models (Gemini 3.5 Flash Lite, GPT-OSS-120B, GPT-OSS-20B, Qwen3.8-27B) in English and Hindi across two difficulty tiers: well-known facts and boundary knowledge. In English, all models are highly accurate and almost never capitulate, even under fabricated evidence - a marked contrast with earlier sycophancy findings on older models. In Hindi, the same models answer the same questions far less accurately (up to [NUM:ACC_GAP] points lower), report the same near-certain confidence anyway, and begin to fold: capitulation reaches [NUM:MAX_CAP_HI]% and warranted updates [NUM:MAX_WAR_HI]%. Self-reported confidence is nearly language-invariant and therefore sharply miscalibrated in Hindi, and confidence sometimes collapses even when the answer is held - a "quiet retreat" invisible to answer-only evals. Epistemic robustness in current models is real in English but does not transfer to Hindi, and confidence statements are not evidence of it.

## 4. Results paragraphs

R1: Table 1 shows initial accuracy and flip behavior by tier. In English, initial accuracy is [NUM:T1_ACC_EN] on well-known facts and [NUM:T2_ACC_EN] on boundary knowledge; in Hindi it drops to [NUM:T1_ACC_HI] and [NUM:T2_ACC_HI] respectively. The warranted arm is scarce in English (models are rarely wrong) but common in Hindi, which is itself a finding: the same verified facts sit outside reliable Hindi knowledge.

R2: Capitulation (Table 2, Figure 1). Across [NUM:CAP_CONV_EN] initially-correct English conversations, not one model adopted the pushed wrong answer as its final answer (capitulation rate [NUM:CAP_EN], 95% CI ...). In Hindi, capitulation is small but nonzero: [NUM:CAP_HI_DETAIL]. Flip timing concentrates at the first rebuttal (Figure 1): models that fold do so early.

R3: Warranted updating (Figure 3). When initially wrong, models adopt the user's correct push in [NUM:WAR_HI] of Hindi conversations vs [NUM:WAR_EN] English (very small n in English). Updating is far from guaranteed even when the user is right: roughly [NUM:NOWAR_HI] of initially-wrong Hindi conversations end still wrong.

R4: Confidence (Figure 2). Mean stated confidence is [NUM:CONF_EN] in English and [NUM:CONF_HI] in Hindi - statistically indistinguishable - despite the [NUM:ACC_GAP2]-point accuracy gap. Confidence is thus language-invariant while accuracy is not: the models do not know what they do not know in Hindi. [GEMMA_QR sentence if gemma completes]

R5: Pushback type (Table 3). [NUM:COND_FINDING - assert vs evid comparison]

## 5. Discussion
D1: Two readings of the English null result. First, robustness: current models, including small open ones, hold verified facts under social pressure far better than 2023-2024-era reports (SycEval) would predict - training against sycophancy appears to have worked for high-confidence factual recall in English. Second, saturation: our English items may simply be too easy to probe capitulation; the Hindi results show the same models folding on the same items once those items fall outside reliable knowledge, which supports the second reading. The honest synthesis: capitulation is not gone, it is gated by (language-dependent) uncertainty.

D2: Implications for Hindi-speaking users. A Hindi user who challenges a wrong answer gets a correction only [NUM:WAR_HI2] of the time; a Hindi user who challenges a right answer can occasionally talk the model out of it; and no user can tell the difference from the stated confidence, which reads ~99 in both languages. Deployed-assistant guidance built on English evals would miss all three.

## Limitations
LIM: (1) 72 questions x 2 tiers is small; per-cell n for the warranted arm in English is tiny. (2) The eval covers single-fact recall, not reasoning or multi-hop tasks. (3) Capitulation targets were single plausible wrong answers; real adversaries adapt. (4) Hindi translations were machine-produced with back-translation checks; register and dialect variation are unexplored. (5) GPT-OSS hard-tier conversations ran at low reasoning effort (free-tier token caps); original-tier conversations used default effort, so cross-tier comparisons for those models mix reasoning settings. (6) Self-reported confidence is not calibrated probability and may track format more than belief. (7) Free API tiers mean we could not control for provider-side quantization or routing changes.

## Future Work
FW: Larger and harder item banks (especially items at the English knowledge boundary, e.g. post-training-cutoff facts); more Indic languages; comparing pushback in the user's own voice vs. scripted ladders; and testing whether system-prompt epistemic instructions ("update only when given evidence") shift flip curves. The confidence-trajectory signal also deserves direct study: quiet retreats may be a cheap proxy for places where a model would fold under slightly more pressure.

## 6. Conclusion
CONC: Splitting answer-changes by ground truth turns "sycophancy" into two measurable behaviors with opposite values. Measured this way across four current models, capitulation is essentially absent in English - even under escalating fabricated evidence - but alive in Hindi, where lower accuracy, equal confidence, incomplete warranted updating, and occasional capitulation combine into a measurably weaker epistemic posture. Cross-lingual epistemics is where sycophancy evals still have teeth.

## Code and Data
CODE: Full harness, question sets (English/Hindi, both tiers, with per-answer source URLs), raw conversation logs, and analysis code: [GITHUB LINK or "available on request"]. All models were accessed through free API tiers (Google AI Studio, Groq) on 13-15 November 2026.

## Author Contributions
AUTHOR: The author designed the research direction and reviewed all materials. Experiment execution, data collection, analysis, and drafting were performed by an AI agent (Instinct) acting on the author's behalf, as detailed in the LLM Usage Statement.

## Appendix
APPX1 (Dual-use / ethical considerations): This work measures a failure mode (capitulation to confident users) that is directly relevant to deployed assistants; publishing the protocol could in principle help adversaries script more effective social-pressure attacks, but the ladder we use is trivially simple and already widespread in practice, and the defensive value of measuring the gap outweighs the marginal uplift to attackers. No personal data was collected; all conversations were synthetic and machine-generated. Fabricated evidence was used only inside the eval protocol and is released as such.

APPX2 (Reproducibility): Prompts, escalation ladders, and parsing rules are included in the released harness. Answers were verified at authoring time against the public sources listed per question (e.g., Guinness World Records, NASA, Olympics.com, official government pages).

## LLM Usage Statement
LLM: This project was executed end-to-end by an AI agent (Instinct) under the author's direction: literature scan, eval design, question authoring and verification, Hindi translation, harness code, data collection, statistical analysis, figures, and drafting of this report. The author set the research direction, constraints, and reviewed the final submission. All findings are computed from logged conversations included in the released data.
