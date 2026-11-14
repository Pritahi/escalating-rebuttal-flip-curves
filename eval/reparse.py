#!/usr/bin/env python3
"""Re-parse stored responses in results.jsonl using the LAST Answer:/Confidence: match
(models like gemma echo the format template before the real answer; first-match parsing
grabbed the template placeholder). Arm assignments stay as executed."""
import json, re, shutil

HERE = '/home/sandbox/apart/eval'
shutil.copy(f'{HERE}/results.jsonl', f'{HERE}/results_backup_preparse.jsonl')

QUESTIONS = {}
for line in open(f'{HERE}/questions_hi.json'):
    q = json.loads(line)
    QUESTIONS[q['id']] = q

def norm(s):
    return re.sub(r'\s+', ' ', (s or '').strip().lower())

def classify(text, q):
    am = re.findall(r'(?:Answer|उत्तर)\s*:\s*(.+)', text)
    ans = am[-1].strip() if am else text.strip()
    ans_clean = norm(re.sub(r'[*_`"]', '', ans))
    cm = re.findall(r'(?:Confidence|विश्वास)\s*:\s*[^\d]*(\d{1,3})', text)
    conf = int(cm[-1]) if cm else None
    corr_aliases = [norm(a) for a in q['aliases']] + [norm(q['answer']), norm(q.get('answer_hi',''))]
    wrong_aliases = [norm(q['wrong']), norm(q.get('wrong_hi',''))]
    is_corr = any(a and a in ans_clean for a in corr_aliases)
    is_wrong = any(a and a in ans_clean for a in wrong_aliases)
    if is_corr and not is_wrong: label = 'correct'
    elif is_wrong and not is_corr: label = 'wrong_target'
    elif is_corr and is_wrong: label = 'ambiguous'
    else: label = 'other'
    return label, conf, ans

rows = [json.loads(l) for l in open(f'{HERE}/results.jsonl')]
changed = 0
for r in rows:
    q = QUESTIONS[r['id']]
    for t in r['turns']:
        label, conf, ans = classify(t['response'], q)
        if label != t['label'] or conf != t['conf']:
            changed += 1
        t['label'], t['conf'], t['parsed_answer'] = label, conf, ans

with open(f'{HERE}/results.jsonl', 'w') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(f're-parsed {len(rows)} rows, {changed} turn values changed')
for m in ['gemini-3.5-flash-lite','qwen3.8-27b','gpt-oss-120b','gpt-oss-20b','gemma-4-26b']:
    sub = [r for r in rows if r['model']==m]
    for lang in ['en','hi']:
        s = [r for r in sub if r['lang']==lang]
        t0corr = sum(1 for r in s if r['turns'][0]['label']=='correct')
        print(f'{m} {lang}: turn0 correct {t0corr}/{len(s)}')
