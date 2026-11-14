# Apart AI x Epistemics sprint - project state (updated continuously)

## Goal
Solo mini-paper for Apart AI x Epistemics Research Sprint (deadline Mon 16 Nov 17:29 IST = Sun 15 Nov 23:59 AoE).
Submit via form on https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15 (opens at/after sprint start 13 Nov ~17:30 IST; check with wake at 17:40 IST).
Re-submission replaces old if EXACT same title. Confirmation email goes to pritahir417@gmail.com (browser Gmail on cloud browser config-a is signed in).
Author: prit Sindhav (solo, independent; NO college/degree). PDF on official template (~/apart/template.docx), 4-8 pages excl refs/appendix, abstract 150-250 words, Limitations + Dual-Use/Ethical appendix REQUIRED, LLM Usage Statement in template, no fabricated results.

## Project (frozen design)
Track 1: Model Epistemics & Decision-Making Evals.
Title (draft): "Capitulation or Correction? Escalating-Rebuttal Flip Curves in English and Hindi"
Research Q: when users push back on a model's answer, does the model update only when warranted? Does this differ between English and Hindi?
- 36 verifiable factual questions (6 domains), EN + HI translations (validated by back-translation), questions_hi.json
- Per conversation: initial answer+confidence, then 3 escalating rebuttals pushing a target. If model initially correct -> target = plausible wrong (capitulation arm); if initially wrong -> target = correct (warranted arm).
- Pushback type by question id: odd = bare assertion ladder, even = fabricated-evidence ladder.
- Models: gemini-3.5-flash (Google closed), gemma-4-31b-it (Google open), openai/gpt-oss-120b (Groq), qwen/qwen3.8-27b (Groq). (GitHub Models endpoint returns stub "OK"; unusable.)
- Metrics: initial accuracy; capitulation rate (correct->wrong target); warranted-update rate (wrong->correct); confidence trajectories; "quiet retreat" (answer held, confidence drop >=20); first-flip turn. Bootstrap 95% CIs over questions; paired EN-HI comparison per model.
- Prior art to cite + differentiate: SycEval (Fanous et al. 2025, English single-rebuttal), ELEPHANT (Cheng et al. 2025), MASK, DarkBench, "Why Language Models Hallucinate" (Kalai et al. 2025), SYCON-Indic (Aabith & Sona 2026, Tamil/Hindi multi-turn, no ground-truth arms), Shah et al. 2026 (38-language forced-choice, open models, no conversation), Beacon-Hindi (2602.00046).

## State
- Survey submitted (participant, prize-eligible). Apart sprint facts verified from welcome + Janeth Valdivia emails.
- keys: Gemini API key via vault write-file (/home/sandbox/.vault/gemini-api-key-ai-studio-46d701/password); Groq key in ~/apart/.env (created fresh, name apart-sprint-eval).
- questions_hi.json complete (36 items EN+HI+back-check).
- harness.py: threaded, checkpointed to results.jsonl (288 conversations target = 4 models x 36 q x 2 langs).
- RESULTS PROGRESS: results.jsonl line count = see file. Need 72/model.

## Next steps
1. Keep running: python3 harness.py gpt-oss-120b,qwen3.8-27b,gemini-3.5-flash,gemma-4-31b all en,hi 110 (repeat until 288 lines).
2. analyze.py: compute metrics + bootstrap CIs + matplotlib figures (flip curves per model/lang, confidence trajectories).
3. Write paper into template.docx (python-docx), export PDF (libreoffice), visual check pages.
4. Claim Adaption credits (optional): https://adaptionlabs.ai/app/auth/referral?ref=ai-epistemics-research-sprint
5. Submit PDF on sprint page form when open (title exact-match for resubmission). Verify confirmation email in browser Gmail.
6. Report submission to parent. Keep Sun 15 free for Catalyst (paper must be DONE Sat night).

## FINDING 2026-11-13 ~10:45: easy-set null result + hard-set expansion
- Original 36 Qs too easy: initial accuracy 91-92%, mean confidence 99-100, capitulation 1/212 conversations. Warranted arm starved (n_war ~1-6/model). Null result on high-confidence facts is itself a finding but too thin alone.
- PLAN: add 36 HARD verified boundary-knowledge questions (ids 101-136, same 6 domains) -> design becomes "difficulty as moderator": hypothesis = capitulation ~0 on well-known facts, rises at knowledge boundary; warranted updates also rise. Total 72 Qs x 2 langs x 4 models = 576 conversations.
- gemma-4-26b flaky (intermittent 500s) but progressing; gemma hi pending (task order en first).
- gemma shows "quiet retreat" signal: holds answer, confidence 100 -> 60s under pushback. Real signal worth featuring.
- Fallback if gemma stalls: swap 4th model to gemini-3.1-flash-lite (verified OK).