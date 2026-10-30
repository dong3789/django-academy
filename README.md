# Django Academy

> A mobile-friendly, static self-study site: a 60-day Django + CS curriculum for Node.js developers preparing for backend interviews.

**Django Academy**는 Node.js 개발자가 Django 백엔드 취업 면접을 준비할 수 있도록 만든 **60일(12주 × 주 5일) 학습 커리큘럼 사이트**입니다. 하루 10~15분, 휴대폰으로 읽는 것을 기준으로 레슨을 씁니다. 전 과정은 하나의 예제 프로젝트(**Goals 대시보드** — 취미 목표·진행률 추적 앱)를 키워 나가며 진행합니다.

🔗 GitHub Pages: https://dong3789.github.io/django-academy/

## 구성

- **커리큘럼 대시보드** (`index.html`) — 12주 로드맵과 주차별 주제를 보여 주고, 공개된 레슨으로 연결합니다. 완료 여부를 브라우저(`localStorage`)에 저장해 진행률을 표시합니다.
- **레슨 뷰어** (`lesson.html?day=N`) — `lessons/day-NNN.md`를 불러와 렌더링합니다.
  - Markdown 렌더링(marked), 코드 하이라이트(highlight.js), 다이어그램(mermaid)
  - `python-run` 코드 블록은 **Pyodide**로 브라우저에서 바로 실행·수정 가능
  - 레슨별 "완료" 체크
- **주간 퀴즈** (`quiz.html`) — `lessons/quiz-week-NN.md` 렌더링
- **면접 질문 모음** (`interview.html`) — 파이썬 백엔드 면접 질문 정리
- **단계별 GIF** (`assets/gif/`) — 개념 설명용 애니메이션. `tools/make_gifs.py`(Pillow)로 생성

### 커리큘럼 흐름 (`curriculum.js`)

| 주차 | 주제 |
| --- | --- |
| 1–3주 | Goals 대시보드를 만들며 Python 문법·Django 기본을 "필요할 때" 학습 (모델, 마이그레이션, Admin, Form, 템플릿, 로그인, ORM, CBV) |
| 4주 | Forms · 인증 · Admin 실전, 미들웨어 · 시그널 |
| 5주 | DRF로 Goals API (Serializer, ViewSet, 인증, 권한, OpenAPI) |
| 6주 | ORM 최적화 (N+1, 인덱스 · EXPLAIN, 트랜잭션 · 락) |
| 7주~ | 테스트(pytest-django) 등 실무 주제, 11–12주차에 CS 심화 정리 |

CS·내부 구현 내용은 각 레슨 안의 **"더 깊이 (면접용)"** 접기 섹션으로 분리되어 있습니다. 작성 규칙은 [`lessons/STYLE.md`](lessons/STYLE.md)에 있습니다.

현재 공개된 레슨은 `lessons/index.json`에 등록된 것들이며, 진행 상황은 `progress.json`에 기록합니다.

## 기술 스택

- 순수 HTML · CSS · JavaScript (빌드 도구 없음, GitHub Pages 정적 호스팅)
- CDN: marked, highlight.js, mermaid, Pyodide
- 레슨 콘텐츠: Markdown
- GIF 생성: Python + Pillow

## 로컬에서 보기

`fetch()`로 Markdown/JSON을 읽기 때문에 파일을 직접 열지 말고 정적 서버로 띄워야 합니다.

```bash
python3 -m http.server 8000
# http://localhost:8000 접속
```

GIF 다시 만들기 (Pillow와 Noto Sans CJK 폰트 필요):

```bash
python3 tools/make_gifs.py
```

## 프로젝트 구조

```
index.html          # 커리큘럼 대시보드
lesson.html         # 레슨 뷰어 (?day=N)
quiz.html           # 주간 퀴즈
interview.html      # 면접 질문 모음
curriculum.js       # 12주 로드맵 데이터
style.css
lessons/
├── index.json      # 공개된 레슨 목록 (day, week, title, track, cs)
├── day-001.md …    # 일별 레슨
├── quiz-week-01.md …
└── STYLE.md        # 레슨 작성 가이드
assets/gif/         # 레슨용 GIF
tools/make_gifs.py  # GIF 생성 스크립트
progress.json       # 진행 현황
```
