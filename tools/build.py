"""크레인 벨 코리아 사이트 빌드.

index.src.html(한국어 원본)에서
  1) 모델 · 마감 표를 채워 index.html(한국어)을 만들고
  2) i18n/en.json, i18n/ja.json 번역으로 en/index.html, ja/index.html을 만들고
  3) sitemap.xml을 다시 씁니다.

사용법: python3 tools/build.py
문구를 고친 뒤에는 python3 i18n/extract.py 로 ko.json을 갱신하고,
새로 생긴 문장을 i18n/tr_source.py에 (한국어, 영어, 일본어)로 추가하고
python3 i18n/tr_source.py 로 en.json / ja.json을 만든 다음 빌드합니다.
"""
import json, re, sys, pathlib, datetime
from bs4 import BeautifulSoup, NavigableString, Comment

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'i18n'))
from extract import HANGUL  # noqa: E402

SITE = 'https://cranebell.rubiworkshop.com/'

# ---------------------------------------------------------------- tables
# 크레인 벨 공식 스펙(cranebellco.com 모델별 Specs, 2026-11 확인)과 루비워크샵 · 루비서플라이 취급 마감 기준.
MODELS = [
  # 모델, 돔, 마운트, 핸들바, 소재, 무게, 마감 수, 취급
  ('이네 벨', '37mm', '클램프 밴드', '22.2 ~ 31.8mm', '황동 · 알루미늄', '53g · 38g', '11', '루비워크샵 · 루비서플라이'),
  ('미니 스즈 벨', '45mm', '다이캐스트', '22.2 · 25.4mm', '황동 · 알루미늄', '80g · 57g', '8', '루비워크샵 · 루비서플라이'),
  ('미니 카렌 벨', '45mm', '다이캐스트', '22.2 · 25.4mm', '황동 · 알루미늄', '72g · 42g', '8', '루비워크샵 · 루비서플라이'),
  ('리튼 벨', '57mm', '스틸 밴드', '22.2 · 25.4mm', '황동', '117g', '4', '루비서플라이'),
]

B, A, Y = '황동', '알루미늄', '취급'
FINISHES = [
  # 마감, 스와치, 이네, 미니 스즈, 미니 카렌, 리튼
  ('크롬 플레이트', 'linear-gradient(135deg,#f5f6f7,#9da2a8 55%,#e4e6e8)', f'{B} · 53g', f'{B} · 80g', f'{B} · 72g', f'{B} · 117g'),
  ('올 크롬 플레이트', 'linear-gradient(135deg,#f5f6f7,#9da2a8 55%,#e4e6e8)', f'{B} · 53g', '', '', ''),
  ('폴리시드 실버', 'linear-gradient(135deg,#f2f2f2,#b9bcc0 55%,#e9eaeb)', f'{A} · 38g (실버)', f'{A} · 57g', f'{A} · 42g', ''),
  ('매트 실버', '#c4c6c8', '', f'{A} · 57g', f'{A} · 42g', ''),
  ('골드', 'linear-gradient(135deg,#f3dc95,#b8923f 55%,#e9cf7d)', f'{B} · 53g (폴리시드 골드)', f'{B} · 80g', f'{B} · 72g', f'{B} · 117g'),
  ('매트 골드', '#b89b5e', f'{B} · 53g', '', '', ''),
  ('코퍼', 'linear-gradient(135deg,#f0b38f,#b0603a 55%,#e3a07a)', f'{B} · 53g', f'{B} · 80g', f'{B} · 72g', f'{B} · 117g'),
  ('브러시드 코퍼', '#a66a45', f'{B} · 53g', f'{B} · 80g', f'{B} · 72g', ''),
  ('브라운', '#6b4a32', f'{B} · 53g', '', '', ''),
  ('네오 블랙', 'linear-gradient(135deg,#4a4b4f,#0d0d0f 55%,#3a3b3f)', f'{B} · 53g', f'{B} · 80g', f'{B} · 72g', f'{B} · 117g'),
  ('스텔스 블랙', '#2a2a2c', f'{A} · 38g', '', '', ''),
  ('올 스텔스 블랙', '#1a1a1b', f'{B} · 53g', Y, Y, ''),
]

def model_table():
    head = ['모델', '돔 지름', '마운트', '핸들바', '소재', '무게 (황동 · 알루미늄)', '마감', '취급']
    h = '<table class="size fit"><thead><tr>' + ''.join(f'<th>{c}</th>' for c in head) + '</tr></thead><tbody>'
    for r in MODELS:
        h += f'<tr><th>{r[0]}</th>' + ''.join(f'<td>{v}</td>' for v in r[1:]) + '</tr>'
    return h + '</tbody></table>'

def finish_table():
    head = ['마감', '이네 벨', '미니 스즈 벨', '미니 카렌 벨', '리튼 벨']
    h = '<table class="size fit"><thead><tr>' + ''.join(f'<th>{c}</th>' for c in head) + '</tr></thead><tbody>'
    for name, sw, *cells in FINISHES:
        h += f'<tr><th><i style="background:{sw}"></i>{name}</th>' + ''.join(f'<td>{v}</td>' if v else '<td class="na">-</td>' for v in cells) + '</tr>'
    return h + '</tbody></table>'

def build_ko():
    s = (ROOT / 'index.src.html').read_text()
    s = s.replace('{{MODEL_TABLE}}', model_table()).replace('{{FINISH_TABLE}}', finish_table())
    assert '{{' not in s
    assert '\u2014' not in re.sub(r'<!--.*?-->', '', s, flags=re.S), 'em dash in Korean page'
    (ROOT / 'index.html').write_text(s)
    return s

# ---------------------------------------------------------------- translate
LANG = {
 'en': {'locale': 'en_US', 'path': 'en/'},
 'ja': {'locale': 'ja_JP', 'path': 'ja/'},
}

def translate(ko_html, lang):
    tr = json.loads((ROOT / f'i18n/{lang}.json').read_text())
    missing = set()
    def t(s):
        k = s.strip()
        if not HANGUL.search(k):
            return s
        if k in tr:
            return s.replace(k, tr[k])
        missing.add(k)
        return s

    soup = BeautifulSoup(ko_html, 'html.parser')
    soup.html['lang'] = lang
    if soup.title:
        soup.title.string = t(soup.title.string)
    for m in soup.find_all('meta'):
        if m.has_attr('content'):
            m['content'] = t(m['content'])
    for sc in soup.find_all('script', type='application/ld+json'):
        data = json.loads(sc.string)
        def walk(o):
            if isinstance(o, dict):
                return {k: walk(v) for k, v in o.items()}
            if isinstance(o, list):
                return [walk(v) for v in o]
            if isinstance(o, str):
                return t(o)
            return o
        data = walk(data)
        for node in data.get('@graph', []):
            if node.get('@type') == 'WebSite':
                node['url'] = SITE + LANG[lang]['path']
                node['inLanguage'] = lang
        sc.string = '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    for el in soup.body.find_all(True):
        for a in ('alt', 'aria-label', 'title'):
            if el.has_attr(a):
                el[a] = t(el[a])

    def visit(el):
        if el.name in ('script', 'style'):
            return
        direct = any(isinstance(c, NavigableString) and not isinstance(c, Comment) and HANGUL.search(c) for c in el.children)
        if direct:
            k = el.decode_contents().strip()
            if k in tr:
                el.clear()
                frag = BeautifulSoup(tr[k], 'html.parser')
                for c in list(frag.contents):
                    el.append(c)
            else:
                missing.add(k)
            return
        for c in list(el.children):
            if getattr(c, 'name', None):
                visit(c)
    visit(soup.body)

    # canonical, og, hreflang self, language switcher
    soup.find('link', rel='canonical')['href'] = SITE + LANG[lang]['path']
    soup.find('meta', property='og:url')['content'] = SITE + LANG[lang]['path']
    soup.find('meta', property='og:locale')['content'] = LANG[lang]['locale']
    for a in soup.select('nav.lang a'):
        code = a['hreflang']
        a['href'] = '../' if code == 'ko' else ('./' if code == lang else f'../{code}/')
        if code == lang:
            a['class'] = ['on']; a['aria-current'] = 'page'
        else:
            a.attrs.pop('class', None); a.attrs.pop('aria-current', None)
    if lang == 'ja':
        # 일본어는 한글 서체(에스코어 드림) 대신 Noto Sans JP로 통일 (영문·숫자는 Pretendard 유지)
        style = soup.find('style')
        for tag in BeautifulSoup('<link rel="preconnect" href="https://fonts.googleapis.com">'
                                 '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                                 '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400&display=swap" rel="stylesheet">'
                                 '<style>:root{--font:"RubiLatin","Noto Sans JP","Hiragino Sans","Yu Gothic",system-ui,sans-serif}</style>',
                                 'html.parser').contents[:]:
            style.insert_after(tag) if tag.name == 'style' else style.insert_before(tag)

    out = str(soup)
    # 하위 폴더에서 이미지 경로 보정
    out = out.replace('src="images/', 'src="../images/').replace('url(images/', 'url(../images/').replace('href="images/', 'href="../images/')
    left = [k for k in missing]
    return out, left

def sitemap(html):
    imgs = sorted(set(re.findall(r'images/[\w/.-]+\.(?:jpg|png|webp)', html)))
    imgs = [i for i in imgs if not re.search(r'logo|favicon|apple-touch', i)]
    today = datetime.date.today().isoformat()
    alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{h}" href="{SITE}{p}"/>' for h, p in [('ko', ''), ('en', 'en/'), ('ja', 'ja/'), ('x-default', '')])
    urls = []
    for p in ['', 'en/', 'ja/']:
        u = f'  <url>\n    <loc>{SITE}{p}</loc>{alts}\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>{"1.0" if not p else "0.8"}</priority>'
        if not p:
            u += ''.join(f'\n    <image:image><image:loc>{SITE}{i}</image:loc></image:image>' for i in imgs)
        urls.append(u + '\n  </url>')
    x = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
         'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
         + '\n'.join(urls) + '\n</urlset>\n')
    (ROOT / 'sitemap.xml').write_text(x)

if __name__ == '__main__':
    ko = build_ko()
    print('ko  index.html', len(ko))
    for lang in LANG:
        if not (ROOT / f'i18n/{lang}.json').exists():
            print(lang, 'skipped (no translation file)'); continue
        out, left = translate(ko, lang)
        d = ROOT / LANG[lang]['path']; d.mkdir(exist_ok=True)
        (d / 'index.html').write_text(out)
        hangul = len(HANGUL.findall(re.sub(r'<script(?![^>]*ld\+json).*?</script>', '', out, flags=re.S)))
        print(lang, f'{d.name}/index.html', len(out), 'untranslated units:', len(left), 'hangul chars left:', hangul)
        for k in left[:20]:
            print('   -', k[:90])
    sitemap(ko)
