"""Rebuild the portable demo from the selected CSV files and copy WAV assets."""
import csv
import hashlib
import html
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
SOURCES = [('selected_demo_cases_char_vs_mt5_film.csv', 'Character vs mT5 + FiLM', 'CHAR', 'MT5_FILM', 'Character baseline', 'mT5 + FiLM'),
           ('selected_demo_cases_us_vs_dhvaani.csv', 'Ours vs Dhvaani', 'ours', 'dhv', 'Ours', 'Dhvaani')]

def esc(s):
    return html.escape(str(s), quote=True)

assets = {}
def audio(path, label):
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    name = hashlib.sha256(str(source).encode()).hexdigest()[:20] + '.wav'
    assets[name] = source
    return f'<div class="player"><span>{esc(label)}</span><button type="button" class="play" data-src="audio/{name}" aria-label="Play {esc(label)}">▶ Play</button><audio controls preload="none" hidden aria-label="{esc(label)}"></audio><small class="error" role="status"></small></div>'

sections = []
rows_total = 0
languages = set()
for filename, title, left, right, left_label, right_label in SOURCES:
    rows = list(csv.DictReader((REPO / 'src/f5_tts/scripts' / filename).open(encoding='utf-8')))
    rows_total += len(rows)
    grouped = {}
    for row in rows:
        language = row[f'language_{left}'].strip().lower()
        languages.add(language)
        grouped.setdefault(language, []).append(row)
    groups = []
    for language, cases in sorted(grouped.items()):
        samples = []
        for number, row in enumerate(cases, 1):
            samples.append(f'''<tr><td class="text-cell"><div class="sample-id">Sample {number:02d} · {esc(row['id'])}</div><p class="transcript" dir="auto">{esc(row[f'reference_transcript_{left}'])}</p></td>
            <td>{audio(row[f'reference_audio_{left}'], 'Voice prompt')}<details class="reference"><summary>Prompt transcript</summary><p dir="auto">{esc(row[f'prompt_text_{left}'])}</p></details></td>
            <td>{audio(row[f'audio_{left}'], left_label)}</td><td>{audio(row[f'audio_{right}'], right_label)}</td></tr>''')
        groups.append(f'<details class="language"><summary><span>{esc(language.title())}</span><span class="count">{len(cases)} samples</span></summary><div class="table-scroll" role="region" aria-label="{esc(language.title())} comparison" tabindex="0"><table><thead><tr><th scope="col">Text to synthesize</th><th scope="col">Voice prompt</th><th scope="col">{esc(left_label)}</th><th scope="col">{esc(right_label)}</th></tr></thead><tbody>{"".join(samples)}</tbody></table></div></details>')
    section_id = 'character-comparison' if left == 'CHAR' else 'dhvaani-comparison'
    sections.append(f'<section id="{section_id}"><div class="section-heading"><h2>{esc(title)}</h2><button class="collapse" type="button">Collapse all</button></div>{"".join(groups)}</section>')

style = '''
:root{color-scheme:light;--ink:#242424;--muted:#666;--line:#ddd;--accent:#1769aa}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#fff;color:var(--ink);font:16px/1.65 Arial,"Helvetica Neue",sans-serif}main{max-width:1320px;margin:auto;padding:55px 30px 35px}header{text-align:center;max-width:1000px;margin:0 auto 42px}h1{font-size:clamp(30px,4vw,44px);line-height:1.25;margin:0 0 18px;font-weight:650}header .subtitle{color:var(--muted);font-size:18px}.abstract{max-width:1000px;margin:0 auto 35px;text-align:justify}.abstract h2{text-align:center}.abstract p{margin-top:12px}.stats{display:flex;justify-content:center;gap:22px;flex-wrap:wrap;font-size:14px;color:var(--muted)}h2{font-size:25px;font-weight:600;margin:0 0 12px;line-height:1.4}.contents{border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:22px 0;margin:30px 0 40px}.contents h2{font-size:20px}.contents ul{margin:0;padding-left:24px}a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}section{margin:40px 0;scroll-margin-top:24px}.section-heading{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:18px}.section-heading h2{margin:0}button{font:inherit;cursor:pointer;color:var(--accent);background:#fff;border:1px solid #ccc;border-radius:4px;padding:8px 16px}button:hover{background:#f0f6fc}button:focus-visible,summary:focus-visible,.table-scroll:focus-visible,a:focus-visible{outline:3px solid #4993cc;outline-offset:3px}.collapse{font-size:12px;white-space:nowrap}.language{border:1px solid var(--line);margin:12px 0;border-radius:4px;overflow:hidden}.language>summary{display:flex;align-items:center;gap:12px;cursor:pointer;background:#f7f7f7;padding:14px 18px;font-weight:600;list-style:none}.language>summary::-webkit-details-marker{display:none}.language>summary:before{content:'▸';color:var(--muted)}.language[open]>summary:before{content:'▾'}.language[open]>summary{border-bottom:1px solid var(--line)}.count{margin-left:auto;font-size:12px;color:var(--muted);font-weight:400}.table-scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;table-layout:fixed;min-width:1000px}th,td{padding:17px 14px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line);border-right:1px solid #eee}th{background:#f1f1f1;font-weight:600;font-size:14px}th:first-child{width:34%}th:nth-child(2){width:22%}th:nth-child(3),th:nth-child(4){width:22%}td:last-child,th:last-child{border-right:0}tbody tr:last-child td{border-bottom:0}tbody tr:nth-child(even){background:#fcfcfc}.sample-id{font-size:10px;color:var(--muted);overflow-wrap:anywhere}.transcript{font-size:16px;line-height:1.85;margin:9px 0;unicode-bidi:plaintext}.player>span{display:none}.play{width:100%;text-align:center;font-size:13px;min-height:38px}audio{width:100%;height:38px}.reference{font-size:12px;color:var(--muted);margin-top:12px}.reference summary{cursor:pointer}.reference p{font-size:14px;line-height:1.7;unicode-bidi:plaintext}.error{display:block;color:#a52b2b;font-size:12px}footer{border-top:1px solid var(--line);padding-top:24px;font-size:12px;color:var(--muted)}.hint{font-size:14px;color:var(--muted)}noscript{display:block;padding:20px;background:#fff1cf}@media(max-width:650px){main{padding:32px 16px}header{margin-bottom:30px}.abstract{text-align:left}.section-heading h2{font-size:21px}.stats{gap:8px 16px}.hint{font-size:13px}}
'''

script = '''
const players = [...document.querySelectorAll('audio')];
document.querySelectorAll('.play').forEach(button => {
 button.addEventListener('click', async () => {
  const audio = button.nextElementSibling;
  const error = audio.nextElementSibling;
  players.forEach(other => { if (other !== audio) other.pause(); });
  error.textContent = '';
  if (!audio.hasAttribute('src')) audio.src = button.dataset.src;
  audio.hidden = false;
  button.hidden = true;
  try { await audio.play(); }
  catch (_) { error.textContent = 'Could not start playback. Try Play again.'; button.hidden = false; }
 });
});
players.forEach(audio => {
 audio.addEventListener('play', () => players.forEach(other => { if (other !== audio) other.pause(); }));
 audio.addEventListener('error', () => {audio.nextElementSibling.textContent = 'Audio could not be loaded. Please retry.'; audio.previousElementSibling.hidden = false;});
});
document.querySelectorAll('.collapse').forEach(button => button.addEventListener('click', () => {
 button.closest('section').querySelectorAll('details').forEach(details => details.open = false);
 players.forEach(audio => audio.pause());
}));
'''
page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Speech samples for What Matters in Multilingual F5-TTS? Compare multilingual speech synthesis across languages."><title>What Matters in Multilingual F5-TTS? · Speech samples</title><style>{style}</style></head><body><main>
<header><h1>What Matters in Multilingual F5-TTS?</h1><p class="subtitle">Speech samples · Multilingual zero-shot text-to-speech</p><div class="stats"><span>{len(languages)} demo languages</span><span>{rows_total} selected comparisons</span></div></header>
<div class="abstract"><h2>Abstract</h2><p>How far can a widely used non-autoregressive TTS backbone go with better conditioning and alignment? We examine this question through controlled experiments with F5-TTS across 11 Indian languages and Indian English. Our results show that shared phonetic representations and explicit language identity do not independently improve intelligibility over characters; their benefits emerge through complementary alignment supervision and contextual conditioning. The resulting recipe, using mixed character–IPA training with character inference, reduces validation CER by 16% relative to the character baseline. Scaled to 22 Indian languages plus English, it outperforms all three evaluated open-source systems on WER and CER across the 12 primary test languages, improving over SPRING-F5 (WER: 12.71 → 10.54; CER: 3.30 → 2.07). Code-switched evaluation further shows that word-level language modulation improves embedded English-word recovery, while inserted language tokens reduce it. These findings establish an effective multilingual conditioning recipe and show why individual design choices must be evaluated together.</p></div>
<nav class="contents" aria-label="Contents"><h2>Contents</h2><ul><li><a href="#character-comparison">Character vs mT5 + FiLM</a></li><li><a href="#dhvaani-comparison">Ours vs Dhvaani</a></li></ul></nav>
<noscript>Enable JavaScript to play the audio samples. The text and language sections remain available below.</noscript>
<p class="hint">Expand a language to listen. The synthesis text is on the left; voice prompts and model outputs appear in adjacent columns. Audio loads only when you press Play. On smaller screens, scroll the table horizontally.</p>
{''.join(sections)}<footer>Companion audio demo for “What Matters in Multilingual F5-TTS?” · Selected examples, not aggregate evaluation results.</footer></main><script>{script}</script></body></html>'''
(ROOT / 'audio').mkdir(exist_ok=True)
for name, source in assets.items():
    shutil.copyfile(source, ROOT / 'audio' / name)
(ROOT / 'index.html').write_text(page, encoding='utf-8')
(ROOT / '.nojekyll').touch()
print(f'Built {rows_total} comparisons across {len(languages)} languages; copied {len(assets)} WAVs ({sum((ROOT / "audio" / n).stat().st_size for n in assets) / 1024**2:.1f} MiB).')
