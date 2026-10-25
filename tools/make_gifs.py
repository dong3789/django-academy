"""레슨용 단계별 GIF 생성기. 실행: python3 tools/make_gifs.py"""
from PIL import Image, ImageDraw, ImageFont
import os
W, H = 480, 300
BG, FG, DIM = (13, 17, 23), (230, 237, 243), (110, 118, 129)
ACC, OK, WARN, BOX = (88, 166, 255), (63, 185, 80), (240, 136, 62), (33, 38, 45)
KO = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
F = ImageFont.truetype(KO, 17); FS = ImageFont.truetype(KO, 14)
FT = ImageFont.truetype(KO, 19)
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "gif")

def canvas(title, caption):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.text((14, 10), title, font=FT, fill=ACC)
    d.text((14, H - 34), caption, font=F, fill=FG)
    return im, d

def box(d, x, y, w, h, txt, col=BOX, out=DIM, tc=FG, f=F):
    d.rounded_rectangle((x, y, x + w, y + h), 6, fill=col, outline=out, width=2)
    tw = d.textlength(txt, font=f)
    d.text((x + (w - tw) / 2, y + h / 2 - 11), txt, font=f, fill=tc)

def arrow(d, x1, y1, x2, y2, col=ACC):
    d.line((x1, y1, x2, y2), fill=col, width=3)
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    for s in (2.6, -2.6):
        d.line((x2, y2, x2 - 10 * math.cos(a + s / 6), y2 - 10 * math.sin(a + s / 6)), fill=col, width=3)

def save(name, frames, ms=1300):
    frames = [f.convert("P", palette=Image.ADAPTIVE, colors=32) for f in frames]
    p = os.path.join(OUT, name)
    frames[0].save(p, save_all=True, append_images=frames[1:], duration=ms, loop=0, optimize=True)
    print(name, os.path.getsize(p) // 1024, "KB")

def code(d, lines, hi=None, x=14, y=48, done=()):
    for i, l in enumerate(lines):
        yy = y + i * 26
        if i == hi:
            d.rectangle((x - 4, yy - 2, x + 250, yy + 22), fill=(31, 58, 95))
        d.text((x, yy), l, font=FS, fill=FG if (i == hi or i in done) else DIM)

# 1) Day1: 이름표(별칭)
def day1():
    fr = []
    steps = [("a = [1, 2]", ["1", "2"], False, "리스트 객체에 이름표 a를 붙임"),
             ("b = a", ["1", "2"], True, "복사 아님! 같은 객체에 b도 붙음"),
             ("b.append(3)", ["1", "2", "3"], True, "b로 바꿨는데…"),
             ("print(a)", ["1", "2", "3"], True, "a도 [1, 2, 3] — 같은 객체니까")]
    for c, vals, hasb, cap in steps:
        im, d = canvas("변수는 이름표 : " + c, cap)
        for i, v in enumerate(vals):
            box(d, 220 + i * 56, 120, 50, 50, v, out=ACC)
        box(d, 40, 90, 60, 40, "a", (20, 50, 30), OK)
        arrow(d, 100, 110, 215, 140)
        if hasb:
            box(d, 40, 170, 60, 40, "b", (60, 40, 20), WARN)
            arrow(d, 100, 190, 215, 155, WARN)
        fr.append(im)
    save("day1-alias.gif", fr, 1600)

# 2) Day2: list 재할당
def day2_list():
    fr = []; cap = 4; items = []
    seq = [("append(1)", 1), ("append(2)", 2), ("append(3)", 3), ("append(4)", 4),
           ("append(5): 자리 없음!", None), ("새 배열(8칸) 할당 + 복사", "copy"),
           ("append(5)", 5), ("append(6)", 6)]
    for cap_txt, v in seq:
        im, d = canvas("list.append — 동적 배열", cap_txt)
        if v == "copy":
            cap = 8
        elif v is not None:
            items.append(v)
        full = v is None
        for i in range(cap):
            val = str(items[i]) if i < len(items) else ""
            out = WARN if full else (OK if v == "copy" and i < len(items) else DIM)
            box(d, 20 + i * 55, 110, 50, 50, val, out=out)
        d.text((20, 175), f"len={len(items)}  capacity={cap}", font=F, fill=DIM)
        if full:
            d.text((20, 205), "→ 더 큰 배열을 새로 잡는다 (가끔 O(n))", font=FS, fill=WARN)
        if v == "copy":
            d.text((20, 205), "→ 여유분 덕분에 다음 append는 O(1)", font=FS, fill=OK)
        fr.append(im)
    save("day2-list-grow.gif", fr)

# 3) Day2: 해시 삽입
def day2_hash():
    fr = []; slots = [""] * 8
    seq = [("name", 5, None), ("age", 2, None), ("city", 5, 6)]
    def draw(t, cap, hi=None, bad=None):
        im, d = canvas("dict 삽입 — 해시 테이블", cap)
        d.text((20, 50), t, font=F, fill=FG)
        for i in range(8):
            out = OK if i == hi else (WARN if i == bad else DIM)
            box(d, 20 + i * 56, 130, 50, 50, slots[i][:4], out=out, f=FS)
            d.text((38 + i * 56, 185), str(i), font=FS, fill=DIM)
        fr.append(im)
    draw("빈 테이블 (8칸)", "키 → hash() → 칸 번호")
    for k, idx, alt in seq:
        draw(f'd["{k}"]  hash % 8 = {idx}', f"{idx}번 칸을 확인", None, None)
        if alt is None:
            slots[idx] = k; draw(f'd["{k}"]  hash % 8 = {idx}', "비어 있음 → 저장 (O(1))", idx)
        else:
            draw(f'd["{k}"]  hash % 8 = {idx}', "충돌! 이미 차 있음", None, idx)
            slots[alt] = k; draw(f'd["{k}"] → 다른 칸 탐사', f"{alt}번 칸에 저장 (오픈 어드레싱)", alt)
    save("day2-hash-insert.gif", fr)

# 4) Day3: 콜 스택
def day3():
    fr = []
    ev = [("push", "fact(3)"), ("push", "fact(2)"), ("push", "fact(1)"),
          ("pop", "fact(1) → 1"), ("pop", "fact(2) → 2"), ("pop", "fact(3) → 6")]
    st = []
    lines = ["def fact(n):", "    if n <= 1:", "        return 1", "    return n * fact(n-1)"]
    for kind, lab in ev:
        if kind == "push":
            st.append(lab); cap = f"{lab} 호출 → 프레임 쌓기"
        else:
            st.pop(); cap = f"{lab} 반환 → 프레임 제거"
        im, d = canvas("콜 스택 (call stack)", cap)
        code(d, lines, hi=3 if kind == "push" and len(st) < 3 else 2)
        for i, s in enumerate(st):
            box(d, 300, 220 - i * 50, 160, 44, s.split(" ")[0], out=ACC if i == len(st) - 1 else DIM)
        d.text((330, 50), "스택 ↑ 위가 실행 중", font=FS, fill=DIM)
        fr.append(im)
    save("day3-call-stack.gif", fr)

# 5) Day4: MRO
def day4():
    fr = []; mro = ["C", "A", "B", "Base", "object"]
    have = {"B": True}
    for i in range(len(mro)):
        found = have.get(mro[i])
        im, d = canvas("c.hello() — MRO 순서로 찾기",
                       f"{mro[i]}에 hello가 " + ("있다! → 실행" if found else "없다 → 다음"))
        d.text((20, 50), "class C(A, B)   C.__mro__:", font=F, fill=FG)
        for j, n in enumerate(mro):
            col = (OK if found else WARN) if j == i else (DIM if j > i else (60, 60, 60))
            box(d, 14 + j * 92, 130, 80, 50, n, out=col)
            if j < 4:
                arrow(d, 96 + j * 92, 155, 104 + j * 92, 155, DIM)
        fr.append(im)
        if found:
            break
    save("day4-mro.gif", fr, 1500)

# 6) Day5: try 흐름
def day5():
    lines = ["try:", "    data = load()", "except ValueError:", "    data = {}",
             "else:", "    log('성공')", "finally:", "    close()"]
    fr = []
    for path, cap in [((0, 1, 4, 5, 6, 7), "예외 없음: try → else → finally"),
                      ((0, 1, 2, 3, 6, 7), "예외 발생: try → except → finally")]:
        done = []
        for h in path:
            im, d = canvas("try / except / else / finally", cap)
            code(d, lines, hi=h, done=done, y=46)
            fr.append(im); done.append(h)
    save("day5-try-flow.gif", fr, 800)

# 7) Day6: 제너레이터
def day6():
    lines = ["def gen():", "    print('시작')", "    yield 1", "    yield 2", "",
             "g = gen()", "next(g)", "next(g)"]
    steps = [(5, None, [], "gen() 호출: 아직 아무것도 실행 안 됨"),
             (6, 1, ["시작"], "next → '시작' 출력"),
             (6, 2, ["시작", "→ 1"], "yield 1: 값 주고 여기서 멈춤"),
             (7, 3, ["시작", "→ 1", "→ 2"], "다음 next: 멈춘 곳부터 재개"),
             (7, None, ["시작", "→ 1", "→ 2", "next → StopIteration"], "더 없으면 StopIteration")]
    fr = []
    for caller, inner, out, cap in steps:
        im, d = canvas("제너레이터: yield에서 멈췄다 재개", cap)
        code(d, lines, hi=caller, y=46)
        if inner is not None:
            yy = 46 + inner * 26
            d.rectangle((10, yy - 2, 264, yy + 22), outline=OK, width=2)
        d.text((290, 50), "출력", font=FS, fill=DIM)
        for i, o in enumerate(out):
            d.text((290, 76 + i * 26), o, font=FS, fill=FG)
        fr.append(im)
    save("day6-generator.gif", fr, 1700)

# 8) Day7: PRG (Post → Redirect → Get)
def day7():
    steps = [("GET /new/", "빈 폼", ACC, "1. GET: 빈 폼을 받는다"),
             ("POST (abc)", "폼 + 에러", WARN, "2. 잘못된 값: is_valid False → 폼 다시"),
             ("POST (20)", "save() → 302", OK, "3. 올바른 값: 저장 후 redirect"),
             ("GET /", "목록 화면", ACC, "4. 목록은 GET → 새로고침해도 안전")]
    fr = []
    for k, (req, res, col, cap) in enumerate(steps):
        im, d = canvas("PRG: 저장 후 redirect", cap)
        box(d, 20, 70, 130, 150, "브라우저")
        box(d, 330, 70, 130, 150, "goal_create")
        arrow(d, 155, 110, 325, 110, col)
        d.text((165, 82), req, font=FS, fill=col)
        arrow(d, 325, 180, 155, 180, col)
        d.text((175, 186), res, font=FS, fill=col)
        for i in range(4):
            c = col if i == k else (DIM if i > k else FG)
            d.ellipse((190 + i * 28, 236, 204 + i * 28, 250), fill=c)
        fr.append(im)
    save("day7-prg.gif", fr, 1800)


# 9) Day8: template extends → dashboard bar
def day8():
    fr = []
    # frame 1: base only
    im, d = canvas("템플릿 상속 extends", "1. base.html — 헤더 + 빈 block")
    box(d, 40, 60, 400, 50, "header: Goals 대시보드", out=ACC)
    box(d, 40, 120, 400, 90, "{% block content %}  (비어 있음)", out=DIM)
    box(d, 40, 220, 400, 40, "footer", out=DIM)
    fr.append(im)
    # frame 2: child fills block
    im, d = canvas("템플릿 상속 extends", "2. list.html — block에 목록 채움")
    box(d, 40, 60, 400, 50, "header: Goals 대시보드", out=ACC)
    box(d, 40, 120, 400, 90, "독서 20권 · 25%", out=OK, col=(20, 50, 30))
    box(d, 40, 220, 400, 40, "footer", out=DIM)
    fr.append(im)
    # frame 3: progress bar empty-ish
    im, d = canvas("pct → 진행률 바", "3. width: {{ g.pct }}%  (25%)")
    box(d, 40, 70, 400, 44, "독서 20권  5/20 (25%)", out=ACC)
    d.rounded_rectangle((40, 140, 440, 160), 5, fill=BOX, outline=DIM, width=2)
    d.rounded_rectangle((40, 140, 40 + int(400 * 0.25), 160), 5, fill=ACC)
    d.text((40, 180), "track 400px 중 100px 채움", font=FS, fill=DIM)
    fr.append(im)
    # frame 4: nearly full
    im, d = canvas("pct → 진행률 바", "4. 같은 목표 · pct=90")
    box(d, 40, 70, 400, 44, "독서 20권  18/20 (90%)", out=ACC)
    d.rounded_rectangle((40, 140, 440, 160), 5, fill=BOX, outline=DIM, width=2)
    d.rounded_rectangle((40, 140, 40 + int(400 * 0.90), 160), 5, fill=OK)
    d.text((40, 180), "거의 완료 → 막대가 길게", font=FS, fill=OK)
    fr.append(im)
    save("day8-extends.gif", fr, 1700)


# 10) Day9: session cookie -> request.user -> owner filter
def day9():
    fr = []
    im, d = canvas("로그인 · 세션", "1. 로그인 성공 → sessionid 쿠키")
    box(d, 30, 90, 150, 50, "브라우저", out=ACC)
    box(d, 300, 90, 150, 50, "Django", out=ACC)
    arrow(d, 300, 125, 185, 125, OK)
    box(d, 150, 170, 180, 40, "sessionid=abc", (20, 50, 30), OK)
    fr.append(im)
    im, d = canvas("로그인 · 세션", "2. 다음 요청: 쿠키 abc → User 찾기")
    box(d, 30, 90, 150, 50, "GET /", out=ACC)
    arrow(d, 185, 115, 295, 115)
    box(d, 300, 90, 150, 50, "abc → dong", (20, 50, 30), OK)
    d.text((300, 160), "request.user = dong", font=FS, fill=OK)
    fr.append(im)
    rows = [("1 독서", "dong"), ("7 걷기", "mom"), ("9 코딩", "dong")]
    for step in (0, 1):
        cap = ("3. Goal 전체 (owner 칸 있음)" if step == 0
               else "4. filter(owner=dong) → 내 것만")
        im, d = canvas("내 Goals만", cap)
        for i, (t, o) in enumerate(rows):
            mine = o == "dong"
            if step == 1 and not mine:
                box(d, 60, 60 + i * 56, 360, 44, t + "  · " + o + "  (숨김)", out=DIM, tc=DIM)
            else:
                col = (20, 50, 30) if step == 1 else BOX
                box(d, 60, 60 + i * 56, 360, 44, t + "  · owner=" + o, col, OK if step else ACC)
        fr.append(im)
    im, d = canvas("남의 번호로 접근", "5. /7/edit/ → pk=7 AND owner=dong 없음")
    box(d, 60, 80, 360, 50, "get(pk=7, owner=dong)", out=WARN)
    arrow(d, 240, 135, 240, 175, WARN)
    box(d, 160, 180, 160, 50, "404", (60, 30, 20), WARN, WARN)
    fr.append(im)
    save("day9-owner.gif", fr, 1800)


# 11) Day10: runserver (1 lane) vs gunicorn (workers)
def day10():
    fr = []
    reqs = ["요청1", "요청2", "요청3"]
    for k in range(4):
        cap = ["1. runserver: 코드 바뀌면 자동 재시작 (개발용)",
               "2. 워커 관리·장애 복구 없음 → 운영엔 X",
               "3. gunicorn: 워커 여러 개가 나눠 처리",
               "4. 앞에 HTTPS 프록시 → gunicorn → Django"][k]
        im, d = canvas("개발 서버 vs 운영 서버", cap)
        if k < 2:
            box(d, 300, 110, 150, 60, "runserver", out=WARN)
            n = 1 if k == 0 else 3
            for i in range(n):
                box(d, 30 + i * 85, 115, 75, 50, reqs[i], out=ACC)
            arrow(d, 30 + n * 85 - 5, 140, 295, 140, WARN)
        elif k == 2:
            for i in range(3):
                box(d, 30, 60 + i * 62, 90, 46, reqs[i], out=ACC)
                arrow(d, 125, 83 + i * 62, 285, 83 + i * 62, OK)
                box(d, 290, 60 + i * 62, 160, 46, "워커 %d" % (i + 1),
                    (20, 50, 30), OK)
        else:
            box(d, 14, 110, 100, 56, "브라우저", out=ACC)
            arrow(d, 116, 138, 150, 138)
            box(d, 152, 110, 110, 56, "HTTPS", out=ACC, f=FS)
            arrow(d, 264, 138, 298, 138)
            box(d, 300, 80, 166, 46, "gunicorn", (20, 50, 30), OK)
            box(d, 300, 150, 166, 46, "Django 앱", out=ACC)
            arrow(d, 383, 128, 383, 148, OK)
        fr.append(im)
    save("day10-deploy.gif", fr, 1800)

# 12) Day11: 요청 생명주기 (양파 미들웨어)
def day11():
    fr = []
    steps = [
        ("1. gunicorn이 HTTP를 받아 WSGI로 넘김", 0),
        ("2. 미들웨어를 위에서 아래로 통과 (요청)", 1),
        ("3. URLconf가 경로 → 뷰를 고름", 2),
        ("4. 뷰가 ORM·템플릿으로 응답을 만듦", 3),
        ("5. 응답은 미들웨어를 거꾸로 통과", 4),
    ]
    names = ["gunicorn (WSGI)", "Security · Session",
             "Csrf · Auth", "urls.py", "views.goal_list"]
    for cap, k in steps:
        im, d = canvas("요청 하나의 여행", cap)
        for i, n in enumerate(names):
            y = 46 + i * 42
            on = (i <= k) if k < 4 else (i < 3)
            col = (20, 50, 30) if on else BOX
            out = OK if on else DIM
            if k == 4 and i >= 3:
                col, out = (31, 58, 95), ACC
            box(d, 90, y, 300, 34, n, col, out, f=FS)
        if k < 4:
            arrow(d, 60, 50, 60, 60 + k * 42 + 20, ACC)
        else:
            arrow(d, 420, 60 + 4 * 42, 420, 56, WARN)
            d.text((396, 30), "응답", font=FS, fill=WARN)
        fr.append(im)
    save("day11-lifecycle.gif", fr, 1800)

# 13) Day12: FK(체크인) vs M2M(태그 + 중간 테이블)
def day12():
    fr = []
    cap = ["1. Goal 하나 = 행 하나", "2. FK: 체크인 여러 개가 goal_id로 가리킴",
           "3. M2M: 태그는 여러 Goal에 붙을 수 있음",
           "4. Django가 중간 테이블(goal_tags)을 만듦"]
    for k in range(4):
        im, d = canvas("모델 관계", cap[k])
        box(d, 170, 50, 140, 40, "Goal 1 · 독서", (20, 50, 30), OK, f=FS)
        if k == 1:
            for i, t in enumerate(["10/21 +2", "10/22 +1", "10/23 +3"]):
                y = 120 + i * 42
                box(d, 20, y, 170, 34, "CheckIn " + t, out=ACC, f=FS)
                arrow(d, 190, y + 17, 240, 92, ACC)
            d.text((260, 160), "goal_id = 1", font=FS, fill=ACC)
        if k >= 2:
            box(d, 330, 50, 140, 40, "Goal 2 · 걷기", (20, 50, 30), OK, f=FS)
            tags = ["#건강", "#습관"]
            for i, t in enumerate(tags):
                box(d, 120 + i * 160, 190, 120, 36, t, out=WARN, f=FS)
            if k == 2:
                arrow(d, 220, 92, 180, 188, WARN)
                arrow(d, 240, 92, 330, 188, WARN)
                arrow(d, 400, 92, 350, 188, WARN)
            else:
                box(d, 120, 110, 280, 64,
                    "goal_tags: (1,#습관) (2,#건강) (2,#습관)",
                    (31, 58, 95), ACC, f=FS)
                arrow(d, 260, 176, 260, 188, ACC)
        fr.append(im)
    save("day12-relations.gif", fr, 1900)

# 14) Day13: 마이그레이션 그래프 · 충돌 · merge
def day13():
    fr = []
    cap = ["1. 마이그레이션은 앞 파일을 가리키는 사슬",
           "2. 나: 0005_checkin_note 추가",
           "3. 동료도 0004 뒤에 0005_goal_color 추가",
           "4. 잎이 2개 → migrate가 멈춤 (충돌)",
           "5. makemigrations --merge 로 합침"]
    for k in range(5):
        im, d = canvas("마이그레이션 그래프", cap[k])
        box(d, 20, 120, 90, 40, "0003", f=FS)
        box(d, 130, 120, 90, 40, "0004", (20, 50, 30), OK, f=FS)
        arrow(d, 110, 140, 128, 140, ACC)
        if k >= 1:
            box(d, 236, 60, 146, 40, "0005_checkin_note", out=ACC, f=FS)
            arrow(d, 220, 132, 234, 82, ACC)
        if k >= 2:
            box(d, 236, 180, 146, 40, "0005_goal_color", out=WARN, f=FS)
            arrow(d, 220, 148, 234, 198, WARN)
        if k == 3:
            d.text((392, 128), "잎 2개!", font=FS, fill=WARN)
        if k == 4:
            box(d, 388, 120, 86, 40, "0006_merge", (31, 58, 95), ACC, f=FS)
            arrow(d, 382, 82, 420, 118, ACC)
            arrow(d, 382, 198, 420, 162, ACC)
        fr.append(im)
    save("day13-merge.gif", fr, 1800)

# 15) Day14: aggregate vs annotate
def day14():
    fr = []
    cap = ["1. 체크인 행들 (goal_id, amount)",
           "2. annotate: Goal별로 묶어 행마다 합계 칸",
           "3. aggregate: 전체를 dict 한 개로",
           "4. 쿼리는 둘 다 1번 (N+1 없음)"]
    rows = [("1", "+2"), ("1", "+3"), ("2", "+5")]
    for k in range(4):
        im, d = canvas("aggregate vs annotate", cap[k])
        for i, (g, a) in enumerate(rows):
            col = OK if g == "1" else WARN
            box(d, 20, 60 + i * 44, 130, 36, "goal " + g + "  " + a,
                out=col, f=FS)
        if k in (1, 3):
            box(d, 210, 70, 120, 36, "Goal 1 · 5", (20, 50, 30), OK, f=FS)
            box(d, 210, 140, 120, 36, "Goal 2 · 5", (60, 40, 20), WARN, f=FS)
            arrow(d, 150, 90, 206, 88, OK)
            arrow(d, 150, 168, 206, 158, WARN)
        if k in (2, 3):
            box(d, 350, 105, 116, 40, "{s: 10}", (31, 58, 95), ACC, f=FS)
            arrow(d, 150, 130, 346, 125, ACC)
        if k == 3:
            d.text((210, 200), "SQL 1번 · GROUP BY", font=FS, fill=ACC)
        fr.append(im)
    save("day14-annotate.gif", fr, 1800)

# 16) Day15: CBV 요청 흐름
def day15():
    fr = []
    steps = [("GET /", "1. URL이 as_view()가 만든 함수를 부름"),
             ("dispatch()", "2. dispatch: 메서드 보고 갈 곳 결정"),
             ("get()", "3. GET이면 get() 실행"),
             ("get_queryset()", "4. 내 것만: 여기를 오버라이드"),
             ("get_context_data()", "5. 템플릿 변수 채우기"),
             ("render", "6. goal_list.html 렌더 → 응답")]
    for k in range(len(steps)):
        im, d = canvas("ListView 안에서 일어나는 일", steps[k][1])
        for i, (t, _) in enumerate(steps):
            col = (31, 58, 95) if i == k else BOX
            out = ACC if i == k else (OK if i < k else DIM)
            x = 30 + (i % 2) * 220
            y = 52 + (i // 2) * 66
            box(d, x, y, 200, 44, t, col, out, f=FS)
        fr.append(im)
    save("day15-cbv-flow.gif", fr, 1600)

import sys
FNS = {f.__name__: f for f in
       (day1, day2_list, day2_hash, day3, day4, day5, day6, day7, day8, day9, day10, day11, day12, day13, day14, day15)}
for name in (sys.argv[1:] or FNS):
    FNS[name]()
