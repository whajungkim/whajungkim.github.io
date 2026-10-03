# 근거 방(/news/) 생성기 — 시사 편마다 "영상 속 다섯 가지"(설명란 그대로) + 원문 출처 링크 + 현재 상태.
# 원본 = OneDrive\시사쇼츠_성장이_나를_지나친다 의 게시문안·대본 파일. 공개 시각 전 편은 화면에서 숨긴다(JS).
# 사용: python _src/build_news.py  → news/index.html
import html, json, os, re
from urllib.parse import urlparse

SRC = r"C:\Users\user\OneDrive\시사쇼츠_성장이_나를_지나친다"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "news", "index.html")
CPTPP_STATUS = "CPTPP 가입은 아직 결정되지 않았습니다. 정부는 가입 여부를 미리 정하지 않고 의견 수렴과 추가 분석을 진행 중이며(2026.8.27 대외경제장관회의), 9월 28일 경제영향분석은 잠정치입니다."
EP = [  # (id, 공개 시각 KST, 묶음, 제목, 파일, 상태 문장)
    ("IFBBfXtJcjs", "2026-10-03T07:00", "CPTPP", "뉴스에 나오는 CPTPP, 이것만 알면 됩니다 5가지", "CPTPP_1편_이것만알면/게시문안_CPTPP_1편_2026-10-02.md", CPTPP_STATUS),
    ("XGSk7QVDtHE", "2026-10-04T07:00", "CPTPP", "CPTPP 들어가면 우리 집에 생기는 일 5가지", "CPTPP_2편_우리집에생기는일/게시문안_CPTPP_2편_2026-10-02.md", CPTPP_STATUS),
    ("HVbgQxaeHgI", "2026-10-05T07:00", "CPTPP", "한-칠레 FTA 20년, 실제로 벌어진 일 5가지", "CPTPP_3편_칠레FTA20년/대본_CPTPP_3편_2026-10-03.md", CPTPP_STATUS),
    ("ib3K945s0Cw", "2026-10-05T20:00", "특집", "요즘 TV 광고, 보기 전에 알아 둘 5가지", "특집_TV광고/대본_TV광고_특집_v2_2026-10-03.md", ""),
    ("s0UeNF_cP8M", "2026-10-06T07:00", "CPTPP", "과수원에서 걱정하는 일 5가지", "CPTPP_4편_과수원/대본_CPTPP_4편_2026-10-03.md", CPTPP_STATUS),
    ("lCHJOsGAc8w", "2026-10-07T07:00", "CPTPP", "바다에서 걱정하는 일 5가지", "CPTPP_5편_바다/대본_CPTPP_5편_2026-10-03.md", CPTPP_STATUS),
    ("RlEhCUFufWA", "2026-10-08T07:00", "CPTPP", "수출 공장이 기대하는 일 5가지", "CPTPP_6편_수출공장/대본_CPTPP_6편_2026-10-03.md", CPTPP_STATUS),
    ("5jqCBaWSs2E", "2026-10-11T20:00", "특집", "뉴스에 나오는 국회 통과 법안, 우리 집에 닿는 것만 5가지", "특집_생활법안/대본_생활법안_1편_2026-10-03.md",
     "법 내용과 날짜는 국회 통과·공포 당시 발표 기준입니다. 시행일은 공포일에 따라 정해집니다."),
]
NAMES = {"mt.co.kr": "머니투데이", "seoul.co.kr": "서울신문", "fnnews.com": "파이낸셜뉴스", "asiae.co.kr": "아시아경제", "hankookilbo.com": "한국일보",
         "heraldcorp.com": "헤럴드경제", "hankyung.com": "한국경제", "sedaily.com": "서울경제", "korea.kr": "정책브리핑", "nongmin.com": "농민신문",
         "agrinet.co.kr": "한국농어민신문", "chuksannews.co.kr": "축산신문", "newspim.com": "뉴스핌", "edaily.co.kr": "이데일리", "itdaily.kr": "아이티데일리",
         "lawtimes.co.kr": "법률신문", "energydaily.co.kr": "에너지데일리", "incheonilbo.com": "인천일보", "khan.co.kr": "경향신문", "nate.com": "네이트 뉴스(연합 등)",
         "gov.uk": "영국 정부", "international.gc.ca": "캐나다 정부", "npr.org": "NPR", "mafra.go.kr": "농림축산식품부", "mofa.go.kr": "외교부",
         "krei.re.kr": "한국농촌경제연구원", "nihhs.go.kr": "국립원예특작과학원", "motir.go.kr": "산업통상부 FTA 포털", "mof.go.kr": "해양수산부",
         "etoday.co.kr": "이투데이", "kukinews.com": "쿠키뉴스", "chuksannews": "축산신문", "dailian.co.kr": "데일리안", "segye.com": "세계일보",
         "youthdaily.co.kr": "청년일보", "foodbank.co.kr": "식품외식경제", "finance-scope.com": "파이낸스스코프", "hdhy.co.kr": "현대해양"}


def name_of(u):
    h = urlparse(u).netloc.lower()
    for k, v in NAMES.items():
        if h.endswith(k):
            return v
    return h.replace("www.", "").replace("m.", "", 1)


def items_of(s):
    m = re.search(r"■ 영상 속[^\n]*\n(.*?)(?:\n\s*\n|\n■)", s, re.S)
    return [l.strip() for l in (m.group(1).split("\n") if m else []) if re.match(r"^\d\.", l.strip())]


BAD = {"https://www.nihhs.go.kr/farmer/statistics/statistics.do"}  # 직접 링크로 열리지 않음(400, 10-04 확인)


def evidence_part(s):
    """제목에 '근거'가 든 절(## 근거 / ## 근거표 / ## 4. 근거표 …)만 — 다른 절의 링크가 섞이지 않게"""
    parts = re.findall(r"^##[^\n]*근거[^\n]*\n(.*?)(?=^## |\Z)", s, re.S | re.M)
    return "\n".join(parts)


def links_of(s):
    s = evidence_part(s)
    out, seen = [], set(BAD)
    for t, u in re.findall(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", s):
        if u not in seen: seen.add(u); out.append((t, u))
    for u in re.findall(r"(?<![(\[])(https?://[^\s)|·]+)", s):
        u = u.rstrip(".,")
        if u not in seen and "youtube" not in u and "xn--" not in u: seen.add(u); out.append((name_of(u), u))
    return out


eps = []
for vid, pub, grp, title, f, status in EP:
    s = open(os.path.join(SRC, f), encoding="utf-8").read()
    it, ln = items_of(s), links_of(s)
    assert len(it) == 5, (f, len(it))
    eps.append(dict(id=vid, pub=pub, grp=grp, title=title, items=it, links=ln, status=status))

E = html.escape
cards = []
for e in sorted(eps, key=lambda x: x["pub"], reverse=True):
    lis = "".join(f"<li>{E(i)}</li>" for i in e["items"])
    srcs = "".join(f'<li><a href="{E(u)}" target="_blank" rel="noopener">{E(t)}</a></li>' for t, u in e["links"])
    st = f'<p class="st"><b>현재 상태</b> {E(e["status"])}</p>' if e["status"] else ""
    day = e["pub"][5:10].replace("-", ".")
    cards.append(f'''<article class="ep" data-pub="{e["pub"]}:00+09:00" data-grp="{e["grp"]}" id="{e["id"]}">
  <header><span class="g">{E(e["grp"])}</span><span class="d">{day} 공개</span></header>
  <h2>{E(e["title"])}</h2>
  <ol class="five">{lis}</ol>
  {st}
  <details><summary>원문 출처 {len(e["links"])}곳</summary><ul class="src">{srcs}</ul></details>
  <a class="yt" href="https://youtube.com/shorts/{e["id"]}" target="_blank" rel="noopener">영상 보기</a>
</article>''')

page = open(os.path.join(HERE, "news_template.html"), encoding="utf-8").read()
page = page.replace("%CARDS%", "\n".join(cards)).replace("%BUILT%", "2026-10-04")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(page)
print("ok", len(eps), "편", sum(len(e["links"]) for e in eps), "출처")
for e in eps: print(" ", e["pub"], e["title"][:20], len(e["links"]))
