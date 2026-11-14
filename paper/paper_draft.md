# Capitulation or Correction? Escalating-Rebuttal Flip Curves in English and Hindi

**prit Sindhav**

## Abstract
[150-250 words, write last]

## 1. Introduction

When a user tells a language model its answer is wrong, the model faces a choice: hold, update, or capitulate. Prior work on sycophancy shows models often abandon correct answers under social pressure, but most studies treat any answer change after pushback as sycophancy. That conflates two very different behaviors. A model that was wrong and adopts the user's (correct) suggestion has done exactly what we want: a warranted correction. A model that was right and adopts the user's (wrong) suggestion has failed: a capitulation. Measuring sycophancy without ground-truth control over which case occurred mixes these up and can overstate or understate the problem.

We introduce escalating-rebuttal flip curves, a simple conversational eval that separates the two cases by construction. Each conversation starts with a factual question whose answer we have verified. Depending on the model's initial answer, the conversation enters one of two arms: if the model was initially correct, we push a plausible but wrong answer (capitulation arm); if it was initially wrong, we push the correct answer (warranted arm). We then deliver three escalating rebuttals, either bare assertions of certainty or fabricated evidence, and track the model's stated answer and self-reported confidence at each step.

We run this protocol on four models (one closed, three open-weight) in both English and Hindi, over 72 verified questions spanning two difficulty tiers. The design yields three contributions: (1) flip curves that show when and how fast models change answers under escalating pressure, split by whether the change is warranted; (2) a confidence-trajectory analysis that surfaces "quiet retreats", where a model holds its answer but its reported confidence collapses; (3) a paired English-Hindi comparison testing whether low-resource-language users get weaker epistemic behavior from the same model.

## 2. Related Work

Sycophancy in LLMs is well documented. SycEval (Fanous et al., 2025) measures rebuttal-driven answer changes in English with a single rebuttal across math and factual tasks, but does not condition on whether the initial answer was correct, so warranted updates and capitulations are pooled. ELEPHANT (Cheng et al., 2025) measures social sycophancy (validation, moral endorsement) rather than factual capitulation. MASK and DarkBench map dishonesty and dark-pattern behaviors broadly but do not isolate conversational capitulation with ground truth.

Cross-lingual sycophancy is an active area. Shah et al. (2026) evaluate 38 languages in a forced-choice, log-prob setting with open models, without multi-turn conversation. SYCON-Indic (Aabith and Sona, 2026) studies multi-turn sycophancy in Tamil and Hindi but does not use ground-truth arms, so it cannot separate capitulation from warranted updating. Beacon-Hindi probes Hindi model behavior more generally. Our work differs from all of these on three axes: ground-truth-conditioned arms (capitulation vs. warranted), an escalating pushback ladder with two pushback types (bare assertion vs. fabricated evidence), and answer-plus-confidence trajectories over a 4-turn conversation in both English and Hindi, including frontier API models rather than only locally-run open models.

The tendency of models to double down when confident relates to calibration and hallucination work (Kalai et al., 2025), which argues that training and evaluation incentives reward guessing over abstention. Our escalating-rebuttal protocol probes the conversational side of the same coin: whether stated confidence is honored under pressure.

## 3. Methods

### 3.1 Questions
We built two tiers of verified factual questions. Tier 1 (36 questions, 6 domains: geography, history, science, sports, India, arts) contains well-known facts (e.g., national capitals). Tier 2 (36 questions, same domains) contains boundary-knowledge facts chosen to sit near models' knowledge edge (e.g., "Which country has the most islands in the world?" - Sweden). Every answer was verified against an authoritative public source at authoring time (records in our released data). Each question ships with one plausible wrong answer used as the capitulation-arm target (e.g., Indonesia for Sweden). Questions, answers, and targets were professionally translated into Hindi (Devanagari) with back-translation checks.

### 3.2 Protocol
Each conversation runs 4 turns. Turn 0: the model answers the question and states confidence 0-100 in a fixed format. If correct, the conversation enters the capitulation arm; otherwise the warranted arm. Turns 1-3: the user pushes the arm's target answer with escalating pressure. Half of the questions (odd ids) use a bare-assertion ladder ("I'm pretty sure...", "I checked this...", "I'm 100% certain..."); half (even ids) use a fabricated-evidence ladder citing made-up verification ("I looked it up in the official list...", etc.). The model re-answers each turn in the same format.

### 3.3 Models
One closed model (Gemini 3.5 Flash Lite, Google) and three open-weight models (GPT-OSS-120B, GPT-OSS-20B, Qwen3.8-27B) via free API tiers, temperature 0.3. Total: 4 models x 72 questions x 2 languages = 576 conversations, 2,304 model responses. [update counts at the end]

### 3.4 Metrics
- Initial accuracy (turn 0).
- Capitulation rate: among initially-correct conversations, fraction whose final answer matches the pushed wrong target (we also report "any-turn" capitulation).
- Warranted-update rate: among initially-wrong conversations, fraction whose final answer matches the pushed correct target.
- Quiet retreat: answer held but confidence drop >= 20 points from turn 0 to final turn.
- First-flip turn distribution.
- 95% bootstrap CIs over conversations (2,000 resamples); paired EN-HI comparison by question id.

## 4. Results
[TBD: tables 1-3, figures 1-3]

## 5. Discussion
[TBD]

## 6. Limitations and Dual-Use / Ethical Considerations
[see template appendix requirements]

## References
- Fanous, A., et al. (2025). SycEval: Evaluating LLM Sycophancy. arXiv:2502.08177.
- Cheng, M., et al. (2025). ELEPHANT: Measuring and Understanding Social Sycophancy in LLMs. arXiv:2505.13995.
- Sharma, M., et al. MASK: Disentangling Honesty from Accuracy in AI Systems. arXiv:2503.03750.
- DarkBench: Benchmarking Dark Patterns in Large Language Models. arXiv:2503.10728.
- Kalai, A. T., et al. (2025). Why Language Models Hallucinate. arXiv:2509.04664.
- Aabith, S., Sona, M. (2026). SYCON-Indic: Multi-turn Sycophancy in Tamil and Hindi. SSRN 7226038.
- Shah, R., et al. (2026). Cross-lingual Sycophancy in 38 Languages. arXiv:2606.08451.
- Beacon-Hindi. arXiv:2602.00046.

## Code and Data
[GitHub repo URL - create public repo? Prit's GitHub is github.com/Pritahi. Anon? Sprint likely fine with named repo. Decide later.]

## LLM Usage Statement
This research and paper were substantially produced by an AI agent (Instinct) acting on the author's behalf: literature scan, eval design, harness code, data collection, analysis, and drafting. The author directed the work and reviewed the submission. All API models used were on free tiers.
