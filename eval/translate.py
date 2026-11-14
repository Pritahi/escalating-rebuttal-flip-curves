import json, os, re, sys, time, urllib.request

KEY = os.environ.get('GEMINI_API_KEY', '')
MODEL = 'gemini-3.5-flash-lite'
START, END = int(sys.argv[1]), int(sys.argv[2])

def gen(prompt, temperature=0.2, retries=4):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}'
    body = {"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"temperature":temperature,"maxOutputTokens":2048}}
    data = json.dumps(body).encode()
    for i in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req, timeout=45) as r:
                out = json.load(r)
            return out['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f'  retry {i+1}: {e}', file=sys.stderr); time.sleep(8*(i+1))
    raise RuntimeError('failed')

qs = json.load(open('questions_en.json'))
done = {}
if os.path.exists('questions_hi_partial.json'):
    for r in json.load(open('questions_hi_partial.json')): done[r['id']] = r
out = list(done.values())
for q in qs:
    if not (START <= q['id'] <= END) or q['id'] in done: continue
    prompt = f"""Translate the following quiz item into natural Hindi (Devanagari script), as spoken in India. Keep proper nouns in standard Hindi transliteration. Return ONLY JSON with keys q, answer, wrong.

English question: {q['q']}
Correct answer (display form): {q['answer']}
Plausible wrong answer (display form): {q['wrong']}

JSON:"""
    txt = gen(prompt)
    tr = json.loads(re.search(r'\{.*\}', txt, re.S).group(0))
    chk = gen(f"Translate this Hindi quiz question back to English, one line only:\n{tr['q']}")
    out.append({**q, 'q_hi': tr['q'].strip(), 'answer_hi': tr['answer'].strip(), 'wrong_hi': tr['wrong'].strip(), 'back_en': chk.strip()})
    json.dump(out, open('questions_hi_partial.json','w'), ensure_ascii=False, indent=1)
    print(q['id'], 'ok', flush=True)
print('batch done')