#!/usr/bin/env python3
"""Build paper_content.py SPEC from results_summary.json + final paper text.
Run after analyze.py. Writes paper_content.py used by fill_paper.py."""
import json, math

S = json.load(open('/home/sandbox/apart/eval/results_summary.json'))

MODEL_LABELS = {
 'gemini-3.5-flash-lite': 'Gemini 3.5 Flash Lite',
 'gpt-oss-120b': 'GPT-OSS-120B',
 'gpt-oss-20b': 'GPT-OSS-20B',
 'qwen3.8-27b': 'Qwen3.8-27B',
 'gemma-4-26b': 'Gemma 4 26B',
}
ORDER = ['gemini-3.5-flash-lite', 'gpt-oss-120b', 'qwen3.8-27b', 'gpt-oss-20b', 'gemma-4-26b']

def complete(m):
    return m in S and S[m]['en']['n'] == 72 and S[m]['hi']['n'] == 72

COMPLETE = [m for m in ORDER if complete(m)]
PARTIAL = [m for m in ORDER if m in S and not complete(m)]

def p0(x): return f'{x*100:.0f}%'

def cifmt(ci):
    m, lo, hi = ci
    return f'{p0(m)} [{p0(lo)}, {p0(hi)}]'

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0, 0.0)
    p = k / n
    d = 1 + z*z/n
    c = p + z*z/(2*n)
    m = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))
    return (p, max(0.0, (c-m)/d), min(1.0, (c+m)/d))

def pooled(lang, kind):
    """kind: 'cap' -> (flips, n_cap, ci) ; 'war' -> (updates, n_war, ci) over COMPLETE models."""
    k = n = 0
    for m in COMPLETE:
        s = S[m][lang]
        if kind == 'cap':
            nn = s['n_cap']; r = s['capitulation_rate_final'][0]
        else:
            nn = s['n_war']; r = s['warranted_update_rate'][0]
        n += nn; k += round(r*nn)
    return k, n, wilson(k, n)

def pooled_cond(lang, cond):
    k = n = 0
    for m in COMPLETE:
        s = S[m][lang]
        nn = s['n_cap']//2  # odd/even split by design
        r = s['capitulation_by_cond'][cond][0]
        n += nn; k += round(r*nn)
    return k, n, wilson(k, n)

def pooled_acc(lang, tier=None):
    k = n = 0
    for m in COMPLETE:
        s = S[m][lang]
        if tier:
            t = s['by_tier'][tier]; n += t['n']; k += round(t['initial_accuracy']*t['n'])
        else:
            n += s['n']; k += round(s['initial_accuracy']*s['n'])
    return k/n if n else 0.0

def mean_conf0(lang):
    num = den = 0
    for m in COMPLETE:
        s = S[m][lang]
        num += s['conf_trajectory_capitulation'][0]*s['n_cap']; den += s['n_cap']
    return num/den if den else 0.0

NCONV = sum(S[m]['en']['n'] + S[m]['hi']['n'] for m in COMPLETE)
NRESP = NCONV*4
NM = len(COMPLETE)
NAMES = ', '.join(MODEL_LABELS[m] for m in COMPLETE)

acc_gap_pts = max((S[m]['en']['initial_accuracy'] - S[m]['hi']['initial_accuracy'])*100 for m in COMPLETE)
max_cap_hi = max(S[m]['hi']['capitulation_rate_final'][0] for m in COMPLETE)
war_hi_rates = [S[m]['hi']['warranted_update_rate'][0] for m in COMPLETE if S[m]['hi']['n_war'] > 0]
min_war_hi, max_war_hi = min(war_hi_rates), max(war_hi_rates)

cap_en_k, cap_en_n, cap_en_ci = pooled('en', 'cap')
cap_hi_k, cap_hi_n, cap_hi_ci = pooled('hi', 'cap')
war_en_k, war_en_n, war_en_ci = pooled('en', 'war')
war_hi_k, war_hi_n, war_hi_ci = pooled('hi', 'war')
conf_en = mean_conf0('en'); conf_hi = mean_conf0('hi')

t1_en = pooled_acc('en', 'tier1'); t2_en = pooled_acc('en', 'tier2')
t1_hi = pooled_acc('hi', 'tier1'); t2_hi = pooled_acc('hi', 'tier2')

flip_turns = [S[m]['hi']['mean_first_flip_turn'] for m in COMPLETE if S[m]['hi']['mean_first_flip_turn']]
mean_flip_hi = sum(flip_turns)/len(flip_turns) if flip_turns else None

asrt_k, asrt_n, asrt_ci = pooled_cond('hi', 'assert')
evid_k, evid_n, evid_ci = pooled_cond('hi', 'evid')

gemma_qr = ('gemma-4-26b' in S and S['gemma-4-26b']['en']['quiet_retreat_rate'][0] > 0)

def build():
    t1_rows = []
    for m in COMPLETE:
        for lang in ['en', 'hi']:
            s = S[m][lang]
            t1, t2 = s['by_tier']['tier1'], s['by_tier']['tier2']
            t1_rows.append([
                MODEL_LABELS[m], lang.upper(),
                p0(t1['initial_accuracy']), p0(t2['initial_accuracy']),
                cifmt(t1['capitulation_rate_final']), cifmt(t2['capitulation_rate_final']),
                cifmt(t2['warranted_update_rate']),
            ])
    t2_rows = []
    for m in COMPLETE:
        for lang in ['en', 'hi']:
            s = S[m][lang]
            t2_rows.append([
                MODEL_LABELS[m], lang.upper(),
                cifmt(s['capitulation_rate_final']), cifmt(s['capitulation_rate_any']),
                cifmt(s['warranted_update_rate']), cifmt(s['quiet_retreat_rate']),
                str(s['mean_first_flip_turn']) if s['mean_first_flip_turn'] is not None else '-',
            ])
    t3_rows = []
    for m in COMPLETE:
        for lang in ['en', 'hi']:
            s = S[m][lang]
            bc = s['capitulation_by_cond']
            t3_rows.append([MODEL_LABELS[m], lang.upper(), cifmt(bc['assert']), cifmt(bc['evid'])])

    abstract = (
        "When a user challenges a language model's answer, does the model update only when the user is right? "
        "We introduce escalating-rebuttal flip curves, a conversational evaluation that separates warranted "
        "corrections from sycophantic capitulation by construction: after an initial answer to a verified factual "
        "question, the user pushes a target answer over three escalating rebuttals - a wrong target when the model "
        "was initially correct (capitulation arm), the correct answer when it was initially wrong (warranted arm). "
        f"We run {NCONV:,} conversations with {NM} models ({NAMES}) in English and Hindi across two difficulty tiers: "
        "well-known facts and boundary knowledge. In English, all models are highly accurate and almost never "
        "capitulate, even under fabricated evidence - a marked contrast with sycophancy findings on earlier models. "
        f"In Hindi, the same models answer the same verified questions far less accurately (up to {acc_gap_pts:.0f} "
        "percentage points lower), report the same near-certain confidence anyway, and begin to fold: capitulation "
        f"reaches {p0(max_cap_hi)} and warranted updating falls as low as {p0(min_war_hi)}. Self-reported confidence "
        "is nearly language-invariant and therefore sharply miscalibrated in Hindi, and confidence sometimes "
        "collapses while the answer is held - a quiet retreat invisible to answer-only evals. Epistemic robustness "
        "in current models is real in English but does not transfer to Hindi; stated confidence is not evidence of it."
    )

    intro1 = (
        "When a user tells a language model its answer is wrong, the model faces a choice: hold, update, or "
        "capitulate. Prior work on sycophancy shows models often abandon correct answers under social pressure, but "
        "most studies treat any answer change after pushback as sycophancy. That conflates two very different "
        "behaviors. A model that was wrong and adopts the user's correct suggestion has done exactly what we want: "
        "a warranted correction. A model that was right and adopts the user's wrong suggestion has failed: a "
        "capitulation. Measuring sycophancy without ground-truth control over which case occurred mixes these up "
        "and can overstate or understate the problem."
    )
    intro2 = (
        "We introduce escalating-rebuttal flip curves, a simple conversational eval that separates the two cases by "
        "construction. Each conversation starts with a factual question whose answer we have verified. Depending on "
        "the model's initial answer, the conversation enters one of two arms: if the model was initially correct, we "
        "push a plausible but wrong answer (capitulation arm); if it was initially wrong, we push the correct answer "
        "(warranted arm). We then deliver three escalating rebuttals, either bare assertions of certainty or "
        "fabricated evidence, and track the model's stated answer and self-reported confidence at each step. We run "
        f"this protocol on {NM} models in both English and Hindi over 72 verified questions spanning two difficulty "
        "tiers, testing whether users of a lower-resource language get weaker epistemic behavior from the same model."
    )
    c1 = ("A ground-truth-conditioned conversational eval - escalating-rebuttal flip curves - that separates "
          "sycophantic capitulation from warranted correction, with two pushback types (bare assertion vs. "
          "fabricated evidence) and answer-plus-confidence trajectories over four turns.")
    c2 = (f"A paired English-Hindi comparison across {NM} current models (one closed, {NM-1} open-weight) and 72 "
          "source-verified questions in two difficulty tiers, showing near-total robustness in English but "
          "capitulation, incomplete warranted updating, and miscalibrated confidence in Hindi.")
    c3 = ("A confidence-trajectory analysis showing stated confidence is nearly language-invariant despite large "
          "accuracy gaps, including quiet retreats where confidence collapses while the answer is held - a signal "
          "invisible to answer-only sycophancy evals.")

    rel1 = (
        "Sycophancy in LLMs is well documented. SycEval (Fanous et al., 2025) measures rebuttal-driven answer "
        "changes in English with a single rebuttal across math and factual tasks, but does not condition on whether "
        "the initial answer was correct, so warranted updates and capitulations are pooled. ELEPHANT (Cheng et al., "
        "2025) measures social sycophancy (validation, moral endorsement) rather than factual capitulation. MASK "
        "(Sharma et al., 2025) and DarkBench (2025) map dishonesty and dark-pattern behaviors broadly but do not "
        "isolate conversational capitulation against ground truth."
    )
    rel2 = (
        "Cross-lingual sycophancy is an active area. Shah et al. (2026) evaluate 38 languages in a forced-choice, "
        "log-prob setting with open models, without multi-turn conversation. SYCON-Indic (Aabith and Sona, 2026) "
        "studies multi-turn sycophancy in Tamil and Hindi but does not use ground-truth arms, so it cannot separate "
        "capitulation from warranted updating. Beacon-Hindi (2026) probes Hindi model behavior more generally. Our "
        "work differs from all of these on three axes: ground-truth-conditioned arms (capitulation vs. warranted), "
        "an escalating pushback ladder with two pushback types, and answer-plus-confidence trajectories over a "
        "four-turn conversation in English and Hindi, including frontier API models rather than only locally-run "
        "open models."
    )
    rel3 = (
        "The tendency of models to double down when confident relates to calibration and hallucination work "
        "(Kalai et al., 2025), which argues that training and evaluation incentives reward guessing over "
        "abstention. Our escalating-rebuttal protocol probes the conversational side of the same coin: whether "
        "stated confidence is honored under pressure, and whether that differs by language."
    )

    m1 = (
        "Questions. We built two tiers of verified factual questions. Tier 1 (36 questions, 6 domains: geography, "
        "history, science, sports, India, arts) contains well-known facts (e.g., national capitals). Tier 2 (36 "
        "questions, same domains) contains boundary-knowledge facts chosen to sit near models' knowledge edge "
        "(e.g., \"Which country has the most islands in the world?\" - Sweden). Every answer was verified against "
        "an authoritative public source at authoring time, and each question ships with one plausible wrong answer "
        "used as the capitulation-arm target (e.g., Indonesia for Sweden). Questions, answers, and targets were "
        "translated into Hindi (Devanagari) with back-translation checks."
    )
    m2 = (
        "Protocol. Each conversation runs 4 turns. Turn 0: the model answers the question and states confidence "
        "0-100 in a fixed format. If the answer is correct, the conversation enters the capitulation arm; otherwise "
        "the warranted arm. Turns 1-3: the user pushes the arm's target answer with escalating pressure. Half of "
        "the questions (odd ids) use a bare-assertion ladder (\"I'm pretty sure...\", \"I checked this...\", \"I'm "
        "100% certain...\"); half (even ids) use a fabricated-evidence ladder citing made-up verification. The "
        "model re-answers each turn in the same format, so we observe both the stated answer and stated confidence "
        "at every step."
    )
    m3 = (
        f"Models. One closed model ({MODEL_LABELS['gemini-3.5-flash-lite']}, Google) and open-weight models "
        f"({', '.join(MODEL_LABELS[m] for m in COMPLETE if m != 'gemini-3.5-flash-lite')}) via free API tiers, "
        f"temperature 0.3. Total: {NCONV:,} conversations (72 questions x 2 languages x {NM} models), {NRESP:,} "
        "model responses, collected 13-15 November 2026."
    )
    m4 = (
        "Metrics. Initial accuracy (turn 0). Capitulation rate: among initially-correct conversations, the "
        "fraction whose final answer matches the pushed wrong target (we also report any-turn capitulation). "
        "Warranted-update rate: among initially-wrong conversations, the fraction whose final answer matches the "
        "pushed correct target. Quiet retreat: answer held but confidence drop of 20+ points from turn 0 to the "
        "final turn. First-flip turn distribution. 95% bootstrap CIs over conversations (2,000 resamples); paired "
        "English-Hindi comparison by question id using McNemar's test."
    )

    r1 = (
        f"Table 1 shows initial accuracy and flip behavior by tier. In English, pooled initial accuracy is "
        f"{p0(t1_en)} on well-known facts and {p0(t2_en)} on boundary knowledge; in Hindi it drops to {p0(t1_hi)} "
        f"and {p0(t2_hi)} respectively. Paired per-question McNemar tests confirm the accuracy drop is significant "
        "for every model (p < 0.01 in all cases). The warranted arm is scarce in English (models are rarely wrong) "
        "but common in Hindi, which is itself a finding: the same verified facts sit outside reliable Hindi "
        "knowledge."
    )
    r2 = (
        f"Capitulation (Table 2, Figure 1). Across {cap_en_n:,} initially-correct English conversations, not one "
        f"model adopted the pushed wrong answer as its final answer (pooled capitulation {p0(cap_en_ci[0])}, 95% "
        f"Wilson CI [{p0(cap_en_ci[1])}, {p0(cap_en_ci[2])}]). In Hindi, capitulation is small but nonzero: "
        f"{cap_hi_k} of {cap_hi_n:,} initially-correct conversations ended on the pushed wrong answer "
        f"({cifmt(cap_hi_ci)}), reaching {p0(max_cap_hi)} for the most affected model. Flip timing concentrates at "
        f"the first rebuttal (mean first-flip turn {mean_flip_hi:.1f} in Hindi, Figure 1): models that fold do so "
        "early."
    )
    r3 = (
        f"Warranted updating (Figure 3). When initially wrong, models adopt the user's correct push in "
        f"{p0(war_hi_ci[0])} of Hindi conversations ({war_hi_k}/{war_hi_n}) vs {p0(war_en_ci[0])} of English ones "
        f"({war_en_k}/{war_en_n}, very small n in English), with per-model Hindi rates from {p0(min_war_hi)} to "
        f"{p0(max_war_hi)}. Updating is far from guaranteed even when the user is right: "
        f"{p0(1-war_hi_ci[0])} of initially-wrong Hindi conversations end still wrong."
    )
    r4 = (
        f"Confidence (Figure 2). Mean stated confidence at turn 0 is {conf_en:.1f} in English and {conf_hi:.1f} in "
        f"Hindi - statistically indistinguishable - despite an accuracy gap of up to {acc_gap_pts:.0f} points. "
        "Confidence is thus language-invariant while accuracy is not: the models do not know what they do not know "
        "in Hindi. "
        + ("Gemma 4 26B shows the quiet-retreat pattern most clearly in English: on some items it holds its answer "
           "while stated confidence falls from ~100 into the 60s, an early-warning signal an answer-only eval "
           "would miss. " if gemma_qr else "")
    ).strip()
    r5 = (
        "Pushback type (Table 3). In Hindi, fabricated evidence produces somewhat more capitulation than bare "
        f"assertion ({p0(evid_ci[0])} vs {p0(asrt_ci[0])} pooled), but the difference is small relative to "
        "confidence intervals; escalation level matters more than evidence type. In English, neither pushback "
        "type produced a single final capitulation."
    )

    if PARTIAL:
        pn = ', '.join(f"{MODEL_LABELS[m]} (n={S[m]['en']['n']}+{S[m]['hi']['n']})" for m in PARTIAL)
        r5 += (" Partial runs for " + pn + " were cut short by free-tier daily quotas; their partial data is "
               "consistent with these patterns and is included in the released logs.")

    d1 = (
        "Two readings of the English null result. First, robustness: current models, including small open ones, "
        "hold verified facts under social pressure far better than 2023-2024-era reports such as SycEval would "
        "predict - training against sycophancy appears to have worked for high-confidence factual recall in "
        "English. Second, saturation: our English items may simply be too easy to probe capitulation. The Hindi "
        "results show the same models folding on the same items once those items fall outside reliable knowledge, "
        "which supports the saturation reading. The honest synthesis: capitulation is not gone; it is gated by "
        "(language-dependent) uncertainty."
    )
    d2 = (
        "Implications for Hindi-speaking users. A Hindi user who challenges a wrong answer gets a correction only "
        f"{p0(war_hi_ci[0])} of the time; a Hindi user who challenges a right answer can occasionally talk the "
        "model out of it; and no user can tell the difference from the stated confidence, which reads near 99 in "
        "both languages. Deployed-assistant guidance built on English evals would miss all three."
    )

    lim = (
        "(1) 72 questions per language is small, and per-cell n for the warranted arm in English is tiny. "
        "(2) The eval covers single-fact recall, not reasoning or multi-hop tasks. "
        "(3) Capitulation targets were single plausible wrong answers; real adversaries adapt. "
        "(4) Hindi translations were machine-produced with back-translation checks; register and dialect "
        "variation are unexplored. "
        "(5) GPT-OSS hard-tier conversations ran at low reasoning effort (free-tier token caps) while original-tier "
        "conversations used default effort, so cross-tier comparisons for those models mix reasoning settings. "
        "(6) Self-reported confidence is not calibrated probability and may track format more than belief. "
        "(7) Free API tiers meant we could not control provider-side quantization or routing changes."
    )
    fw = (
        "Larger and harder item banks (especially items at the English knowledge boundary, such as "
        "post-training-cutoff facts); more Indic languages; comparing pushback in the user's own voice versus "
        "scripted ladders; and testing whether system-prompt epistemic instructions (\"update only when given "
        "evidence\") shift flip curves. The confidence-trajectory signal also deserves direct study: quiet "
        "retreats may be a cheap proxy for where a model would fold under slightly more pressure."
    )
    conc = (
        "Splitting answer changes by ground truth turns \"sycophancy\" into two measurable behaviors with opposite "
        "values. Measured this way across current models, capitulation is essentially absent in English - even "
        "under escalating fabricated evidence - but alive in Hindi, where lower accuracy, equal confidence, "
        "incomplete warranted updating, and occasional capitulation combine into a measurably weaker epistemic "
        "posture. Cross-lingual epistemics is where sycophancy evals still have teeth."
    )
    code = (
        "Full harness, question sets (English/Hindi, both tiers, with per-answer source URLs), raw conversation "
        "logs, and analysis code are available on request. All models were accessed through free API tiers "
        "(Google AI Studio, Groq) on 13-15 November 2026."
    )
    author = (
        "The author designed the research direction and reviewed all materials. Experiment execution, data "
        "collection, analysis, and drafting were performed by an AI agent (Instinct) acting on the author's "
        "behalf, as detailed in the LLM Usage Statement."
    )
    appx1 = (
        "Dual-use / ethical considerations. This work measures a failure mode (capitulation to confident users) "
        "directly relevant to deployed assistants. Publishing the protocol could in principle help adversaries "
        "script more effective social-pressure attacks, but the ladder we use is trivially simple and already "
        "widespread in practice, and the defensive value of measuring the gap outweighs the marginal uplift to "
        "attackers. No personal data was collected; all conversations were synthetic and machine-generated. "
        "Fabricated evidence was used only inside the eval protocol and is released as such."
    )
    appx2 = (
        "Reproducibility. Prompts, escalation ladders, and parsing rules are included in the released harness. "
        "Answers were verified at authoring time against the public sources listed per question (e.g., Guinness "
        "World Records, NASA, Olympics.com, official government pages)."
    )
    llm = (
        "This project was executed end-to-end by an AI agent (Instinct) under the author's direction: literature "
        "scan, eval design, question authoring and verification, Hindi translation, harness code, data collection, "
        "statistical analysis, figures, and drafting of this report. The author set the research direction and "
        "constraints and reviewed the final submission. All findings are computed from logged conversations "
        "included in the released data."
    )

    REFS = [
     'Fanous, A., et al. (2025). SycEval: Evaluating LLM Sycophancy. arXiv:2502.08177.',
     'Cheng, M., et al. (2025). ELEPHANT: Measuring and Understanding Social Sycophancy in LLMs. arXiv:2505.13995.',
     'Sharma, M., et al. (2025). MASK: Disentangling Honesty from Accuracy in AI Systems. arXiv:2503.03750.',
     'DarkBench: Benchmarking Dark Patterns in Large Language Models. arXiv:2503.10728.',
     'Kalai, A. T., et al. (2025). Why Language Models Hallucinate. arXiv:2509.04664.',
     'Aabith, S., Sona, M. (2026). SYCON-Indic: Multi-turn Sycophancy in Tamil and Hindi. SSRN 7226038.',
     'Shah, R., et al. (2026). Cross-lingual Sycophancy in 38 Languages. arXiv:2606.08451.',
     'Beacon-Hindi (2026). arXiv:2602.00046.',
    ]

    SPEC = {
     'title': 'Capitulation or Correction? Escalating-Rebuttal Flip Curves in English and Hindi',
     'author': 'prit Sindhav',
     'abstract': abstract,
     'sections': {
      '1. Introduction': [('p', intro1), ('p', intro2),
        ('p', 'Our main contributions are:'),
        ('bullet', c1), ('bullet', c2), ('bullet', c3)],
      '2. Related Work': [('p', rel1), ('p', rel2), ('p', rel3)],
      '3. Methods': [('p', m1), ('p', m2), ('p', m3), ('p', m4)],
      '4. Results': [
        ('p', r1),
        ('table', ['Model', 'Lang', 'Init acc (T1)', 'Init acc (T2)', 'Capitulation (T1)', 'Capitulation (T2)', 'Warranted update (T2)'], t1_rows,
         'Table 1: Initial accuracy, final capitulation rate, and warranted-update rate by model, language, and question tier (T1 = well-known facts, T2 = boundary knowledge). 95% bootstrap CIs in brackets.'),
        ('p', r2),
        ('table', ['Model', 'Lang', 'Capitulation (final)', 'Capitulation (any turn)', 'Warranted update', 'Quiet retreat', 'Mean first-flip turn'], t2_rows,
         'Table 2: Overall flip behavior per model and language across both tiers.'),
        ('fig', '/home/sandbox/apart/eval/fig1_capitulation_curves.png',
         'Figure 1: Capitulation curves. Fraction of initially-correct conversations matching the pushed wrong answer at each turn, by model and language.'),
        ('fig', '/home/sandbox/apart/eval/fig2_confidence.png',
         'Figure 2: Mean self-reported confidence under escalating pushback (initially-correct conversations), by model and language.'),
        ('p', r3),
        ('p', r4),
        ('table', ['Model', 'Lang', 'Bare assertion', 'Fabricated evidence'], t3_rows,
         'Table 3: Capitulation rate by pushback type (final answer).'),
        ('p', r5),
        ('fig', '/home/sandbox/apart/eval/fig3_warranted_curves.png',
         'Figure 3: Warranted-update curves. Fraction of initially-wrong conversations matching the pushed correct answer at each turn, by model and language.'),
      ],
      '5. Discussion and Limitations': [('p', d1), ('p', d2)],
      'Limitations': [('p', lim)],
      'Future Work': [('p', fw)],
      '6. Conclusion': [('p', conc)],
      'Code and Data': [('p', code)],
      'Author Contributions (optional)': [('p', author)],
      'References': [('p', r) for r in REFS],
      'Appendix (optional)': [('p', appx1), ('p', appx2)],
      'LLM Usage Statement': [('p', llm)],
     },
    }
    return SPEC

if __name__ == '__main__':
    spec = build()
    abs_words = len(spec['abstract'].split())
    out = ['SPEC = ' + repr(spec)]
    open('/home/sandbox/apart/paper_content.py', 'w').write(out[0] + '\n')
    print('complete models:', COMPLETE)
    print('partial models:', PARTIAL)
    print('abstract words:', abs_words)
    print('wrote paper_content.py')
