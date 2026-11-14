# Capitulation or Correction? Escalating-Rebuttal Flip Curves in English and Hindi

Code, data, and paper for our entry to the [Apart AI x Epistemics Research Sprint](https://apartresearch.com/sprints/ai-x-epistemics-research-sprint-2026-11-13-to-2026-11-15) (Nov 13-15, 2026), Track 1: Model Epistemics & Decision-Making Evals.

**Team:** prit Sindhav (solo)

## What we found

When a user challenges a language model's answer, does the model update only when the user is right? We built **escalating-rebuttal flip curves**: a conversational eval that separates warranted corrections from sycophantic capitulation by construction. After an initial answer to a verified factual question, the user pushes a target answer over three escalating rebuttals - a wrong target when the model was initially correct (capitulation arm), the correct answer when it was initially wrong (warranted arm). We ran 720 conversations with 5 models (Gemini 3.5 Flash Lite, GPT-OSS-120B, Qwen3.8-27B, GPT-OSS-20B, Gemma 4 26B) in English and Hindi across two difficulty tiers: well-known facts and boundary knowledge.

- **English:** all models are highly accurate and almost never capitulate - zero final flips across 325 valid initially-correct conversations, even under fabricated evidence.
- **Hindi:** the same questions are answered up to 26 percentage points less accurately, capitulation reaches 14% on boundary knowledge (Gemini 3.5 Flash Lite), and warranted updating falls as low as 29% - while stated confidence stays near-certain (~99) in both languages. Confidence is language-invariant and therefore sharply miscalibrated exactly where accuracy drops.
- **Gemma 4 26B** is the exception: 83% accuracy in both languages and no measurable Hindi capitulation (its Hindi capitulation rate is unestimable due to a parse artifact we disclose in the paper's Limitations).

Full numbers, method, related work, and limitations: see [`paper/submission.pdf`](paper/submission.pdf).

## Repository layout

```
eval/
  design.md                  experiment design notes and decisions
  questions_en.json          36 original verified questions (English)
  hard_questions_draft.json  36 boundary-knowledge questions (English), sources noted per item
  questions_hi.json          full 72-question bilingual set (EN + Hindi translations, back-translation checks)
  translate.py               EN -> HI translation + back-translation pipeline (Gemini API)
  harness.py                 escalating-rebuttal conversation harness (Gemini / Groq / GitHub Models APIs)
  reparse.py                 offline re-parser for stored responses (fixes template-echo models)
  analyze.py                 metrics, bootstrap CIs, McNemar paired tests, figures
paper/
  submission.pdf             the submitted paper (7 pages + references, official sprint template)
  paper_prose.md             paper prose with computed placeholders
  build_content.py           fills prose placeholders from results_summary.json -> paper_content.py
  fill_paper.py              renders paper_content.py into the sprint template -> submission.docx/pdf
```

## Reproducing the eval

Requirements: Python 3.10+, `pip install -r requirements.txt`, and API keys as environment variables (`GEMINI_API_KEY` for Gemini/Gemma models, `GROQ_API_KEY` for GPT-OSS and Qwen, `GH_MODELS_TOKEN` for GitHub Models). All models used here have free API tiers.

```bash
cd eval
python3 translate.py 1 36        # translate question set to Hindi (with back-translation check)
python3 harness.py gemini-3.5-flash-lite,gpt-oss-120b,qwen3.8-27b,gpt-oss-20b all en,hi 100
python3 reparse.py               # only if a model echoes the answer template (see paper Limitations)
python3 analyze.py               # writes results_summary.json + figures
cd ../paper && python3 build_content.py && python3 fill_paper.py
```

Note: the raw conversation logs (`results.jsonl`, 720 conversations) were produced in an ephemeral run environment and are not included here; every number in the paper is computed from them by `analyze.py`. The full question sets and the complete pipeline are included, so the eval can be re-run end to end.

## License

MIT (see LICENSE). The paper PDF is shared for review under the sprint's terms.
