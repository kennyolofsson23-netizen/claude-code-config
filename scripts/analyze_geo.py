import re

with open("C:/Users/Kenny/.claude/scripts/hub_html.txt", encoding="utf-8") as f:
    html = f.read()

content = re.sub(r'<script[\s\S]*?</script>', '', html, flags=re.I)
content = re.sub(r'<style[\s\S]*?</style>', '', content, flags=re.I)
content = re.sub(r'<nav[\s\S]*?</nav>', '', content, flags=re.I)
content = re.sub(r'<footer[\s\S]*?</footer>', '', content, flags=re.I)
content = re.sub(r'<header[\s\S]*?</header>', '', content, flags=re.I)

paras = re.findall(r'<p[^>]*>([\s\S]*?)</p>', content, re.I)
paras = [re.sub(r'<[^>]+>', '', p).strip() for p in paras]
paras = [re.sub(r'\s+', ' ', p) for p in paras if len(p.strip()) > 20]

headings = re.findall(r'<h[2-3][^>]*>([\s\S]*?)</h[2-3]>', content, re.I)
headings = [re.sub(r'<[^>]+>', '', h).strip() for h in headings]

bold_count = len(re.findall(r'<(?:strong|b)>', content, re.I))
has_table = bool(re.search(r'<table', content, re.I))
has_list = bool(re.search(r'<[ou]l', content, re.I))

all_text = ' '.join(paras)
word_count = len(all_text.split())

def_pats = [
    r'^[A-Z][^.]+\s+(?:is|are|refers?\s+to|means?|provides?|enables?|allows?)\s+',
    r'^(?:The|A|An)\s+[^.]+\s+(?:is|are|refers?\s+to|was|were)\s+'
]

first_para = paras[0] if paras else ''
first_words = len(first_para.split())
has_def = any(re.match(p, first_para) for p in def_pats)
has_spec = bool(re.search(r'\d|tool|app|platform|service|solution|system|software|generator|analyzer|builder', first_para, re.I))
first_ok = first_words >= 20 and (has_def or has_spec)

q_headings = [h for h in headings if re.match(r'^(?:What|How|Why|When|Where|Who|Which|Can|Should|Is|Are|Do|Does)\b', h, re.I)]
answer_blocks = [p for p in paras if any(re.match(pat, p) for pat in def_pats)]

not_self = re.compile(r'^(?:It|This|That|They|These|Those|He|She|We|But|However|And|Also|Furthermore|Moreover|Additionally|Therefore|Thus|Hence)\b')
self_contained = [p for p in paras if not not_self.match(p) and 15 <= len(p.split()) <= 200]

has_privacy = bool(re.search(r'privacy[- ]?policy', html, re.I))
has_terms = bool(re.search(r'terms[- ]?of[- ]?service|terms[- ]?and[- ]?conditions', html, re.I))
has_contact = bool(re.search(r'contact|kontakt|email|mailto:', html, re.I))
has_author = bool(re.search(r'name\s*=\s*["\']author["\']', html, re.I))
total_words = len(re.sub(r'<[^>]+>', '', html).split())

stats_pat = r'\d+(?:\.\d+)?%|\d{4}|\d+\s*(?:million|billion|thousand|x|times|percent)|according to|study|research|survey|report'
stats = re.findall(stats_pat, all_text, re.I)

# Compute scores exactly as geo-checker
target_ab = max(3, len(paras) * 3 // 10)
answer_score = min(1.0, len(answer_blocks) / target_ab) * 100 if target_ab > 0 else 0
sc_score = (len(self_contained) / max(1, len(paras))) * 100

struct_score = 0
if len(q_headings) >= 3: struct_score += 35
elif len(q_headings) >= 1: struct_score += 15
short_paras = [p for p in paras if 1 <= len(re.split(r'[.!?]+', p)) <= 6]
struct_score += (len(short_paras) / max(1, len(paras))) * 30
if has_table: struct_score += 15
if has_list: struct_score += 10
if bold_count >= 3: struct_score += 10

stats_per_500 = (len(stats) / word_count * 500) if word_count > 0 else 0
if stats_per_500 >= 5: stats_score = 100
elif stats_per_500 >= 3: stats_score = 80
elif stats_per_500 >= 1: stats_score = 50
elif stats_per_500 >= 0.5: stats_score = 30
else: stats_score = 0

citability = round(answer_score * 0.30 + sc_score * 0.25 + struct_score * 0.20 + stats_score * 0.15 + (10 if first_ok else 0))
citability = min(100, citability)

eeat = 0
if has_privacy: eeat += 15
if has_terms: eeat += 10
if has_contact: eeat += 15
if has_author: eeat += 20
if total_words >= 1500: eeat += 20
elif total_words >= 500: eeat += 10
eeat = min(100, eeat)

content_bonus = 15 if len(html) > 10000 else (10 if len(html) > 5000 else (5 if len(html) > 2000 else 0))

# Assume crawler=10, jsonld=~12, llmstxt=~7, sitemap=~4 (all good)
# We'll estimate these; the key is citability + eeat + content_bonus
print("=== CITABILITY BREAKDOWN ===")
print(f"Paragraphs: {len(paras)}")
print(f"First para ({first_words}w): {first_para[:150]}")
print(f"  has_definition: {has_def}, has_specifics: {has_spec}")
print(f"  firstParagraphOk: {first_ok} (+10 if true)")
print(f"Answer blocks: {len(answer_blocks)}/{target_ab} target -> score: {answer_score:.0f} (x0.30 = {answer_score*0.30:.1f})")
print(f"Self-contained: {len(self_contained)}/{len(paras)} -> score: {sc_score:.0f} (x0.25 = {sc_score*0.25:.1f})")
print(f"Structure: {struct_score:.0f} (x0.20 = {struct_score*0.20:.1f})")
print(f"  Q-headings: {len(q_headings)}, Bold: {bold_count}, Table: {has_table}, List: {has_list}")
print(f"Stats: {len(stats)} in {word_count}w = {stats_per_500:.1f}/500w -> score: {stats_score} (x0.15 = {stats_score*0.15:.1f})")
print(f"CITABILITY TOTAL: {citability}")
print()
print("=== E-E-A-T ===")
print(f"Privacy: {has_privacy}(+15), Terms: {has_terms}(+10), Contact: {has_contact}(+15), Author: {has_author}(+20)")
print(f"Total words: {total_words} -> {'20' if total_words>=1500 else '10' if total_words>=500 else '0'}")
print(f"E-E-A-T TOTAL: {eeat}")
print()
print(f"Content bonus: {content_bonus} (html={len(html)})")
print()
print("=== ALL PARAGRAPHS ===")
for i, p in enumerate(paras):
    is_def = any(re.match(pat, p) for pat in def_pats)
    is_sc = not not_self.match(p) and 15 <= len(p.split()) <= 200
    print(f"  [{i}] ({len(p.split())}w) DEF={'Y' if is_def else 'N'} SC={'Y' if is_sc else 'N'} | {p[:160]}")
print()
print("=== QUESTION HEADINGS ===")
for h in q_headings: print(f"  {h}")
print("=== ALL HEADINGS ===")
for h in headings: print(f"  {h}")
