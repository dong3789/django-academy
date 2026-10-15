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

for f in (day1, day2_list, day2_hash, day3, day4, day5, day6):
    f()
