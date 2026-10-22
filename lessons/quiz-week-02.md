# 2주차 퀴즈 · Goals 앱 만들기

> Day 7~12(모델·ModelForm·PRG, 템플릿 상속, 로그인·owner, 배포 맛보기, 요청 생명주기·settings, 모델 관계)를 점검하는 10문제입니다.
> 답을 생각해 본 뒤 `<details>`를 열어 확인하세요.
> 채점·점수는 채팅으로 알려 주시면 기록해 둡니다.

---

## Q1. 마이그레이션 두 단계 (Day 7)

`Goal` 모델에 필드를 하나 추가했습니다. DB에 반영하려면 어떤 명령 두 개를 어떤 순서로 실행하고, 각각 무슨 일을 하나요?

<details>
<summary>정답 보기</summary>

**답:** `python manage.py makemigrations` → `python manage.py migrate`.

- `makemigrations`: 모델과 지난 마이그레이션을 비교해 **변경 설계도 파일**(`0002_....py`)을 만듭니다. DB는 아직 그대로입니다.
- `migrate`: 그 파일을 읽어 실제 **SQL(`ALTER TABLE` 등)을 DB에 실행**합니다.

마이그레이션 파일은 git에 커밋해서 팀원·운영 서버가 같은 순서로 DB를 바꾸게 합니다.

</details>

---

## Q2. 폼 검증은 어디에? (Day 7)

"달성량(`done`)이 목표(`target`)보다 크면 안 된다"는 규칙을 ModelForm에 넣으려 합니다. 필드 하나만 보는 검사로는 왜 안 되고, 어디에 써야 하나요?

<details>
<summary>정답 보기</summary>

**답:** 두 필드를 **함께** 비교해야 하므로 폼의 `clean()`에 씁니다.

```python
def clean(self):
    data = super().clean()
    done = data.get("done") or 0
    target = data.get("target") or 0
    if done > target:
        raise forms.ValidationError(
            "달성량이 목표보다 큽니다")
    return data
```

`clean_done()` 같은 필드별 메서드는 그 필드 값만 확실히 볼 수 있습니다. `super().clean()`을 먼저 불러 필드별 검사 결과를 받고, 값이 없을 수 있으니 `.get()`으로 꺼냅니다.

</details>

---

## Q3. 저장 후 redirect (Day 7)

POST로 Goal을 저장한 뒤 `redirect` 대신 바로 `render`로 목록을 보여 줬습니다. 사용자가 새로고침하면 무슨 일이 생기고, 이 패턴의 이름은?

<details>
<summary>정답 보기</summary>

**답:** 브라우저가 **같은 POST를 다시 보내** Goal이 하나 더 생깁니다 ("양식을 다시 제출할까요?" 경고).

해결책은 **PRG**(Post → Redirect → Get) 패턴입니다. 저장 후 `redirect("goal_list")`로 302 응답을 보내면, 브라우저의 마지막 요청이 GET이 되어 새로고침해도 조회만 반복됩니다. Express의 `res.redirect("/")`와 같은 이유입니다.

</details>

---

## Q4. 템플릿 상속 (Day 8)

`list.html` 맨 위에 `{% extends "base.html" %}`가 있고, 그 아래 `{% block content %}` **밖에** `<p>안녕</p>`을 썼습니다. 화면에 "안녕"이 보일까요?

<details>
<summary>정답 보기</summary>

**답:** **보이지 않습니다.**

자식 템플릿은 부모(`base.html`)의 뼈대를 그대로 쓰고, **block 안의 내용만** 부모의 같은 이름 block을 갈아 끼웁니다. block 밖의 내용은 끼울 자리가 없어 버려집니다. 그래서 `extends`는 맨 위에, 나머지는 전부 block 안에 씁니다.

</details>

---

## Q5. 내 것만 보기와 IDOR (Day 9)

수정 뷰에서 `Goal.objects.get(pk=pk)`로 Goal을 가져왔습니다. 로그인한 사용자가 주소창의 숫자를 바꿔 `/7/edit/`에 들어가면 어떤 문제가 생기고, 어떻게 고치나요?

<details>
<summary>정답 보기</summary>

**답:** **남의 Goal을 수정할 수 있습니다.** ID만 바꿔 남의 데이터에 접근하는 취약점을 **IDOR**(Insecure Direct Object Reference)라고 합니다.

```python
goal = get_object_or_404(
    Goal, pk=pk, owner=request.user)
```

조회 조건에 `owner=request.user`를 **항상** 함께 걸면, 남의 번호로는 "없음"이 되어 404가 납니다. 403 대신 404를 주면 그 번호의 Goal이 존재하는지도 숨길 수 있습니다.

</details>

---

## Q6. 환경변수 함정 (Day 10)

```python
import os
os.environ["DEBUG"] = "False"
DEBUG = bool(os.environ.get("DEBUG"))
print(DEBUG)
```

출력은? 어떻게 고쳐야 하나요?

<details>
<summary>정답 보기</summary>

**답:** `True`.

환경변수는 언제나 **문자열**이고, `"False"`도 빈 문자열이 아니므로 `bool("False")`는 `True`입니다. 값을 비교해야 합니다.

```python
DEBUG = os.environ.get("DEBUG") == "1"
```

기본값(환경변수가 없을 때)이 `False`가 되는 점도 중요합니다. 실수로 설정을 빠뜨려도 운영에서 DEBUG가 켜지지 않습니다.

</details>

---

## Q7. 운영 서버와 정적 파일 (Day 10)

운영에서 `runserver` 대신 `gunicorn`을 쓰는 이유 하나, 그리고 `DEBUG=False`에서 CSS가 사라졌을 때 필요한 두 가지는?

<details>
<summary>정답 보기</summary>

**답:**

- `runserver`는 개발용입니다. 여러 워커 프로세스 관리, 죽은 워커 재시작, 성능·보안 검증이 없습니다. `gunicorn`은 워커 여러 개로 요청을 나눠 처리하는 **WSGI 서버**입니다.
- CSS: ① `python manage.py collectstatic`으로 정적 파일을 `STATIC_ROOT`에 모으고, ② `whitenoise` 미들웨어(또는 nginx)가 그 폴더에서 파일을 내주게 합니다. `DEBUG=False`이면 Django는 정적 파일을 직접 서빙하지 않기 때문입니다.

</details>

---

## Q8. 미들웨어 순서 (Day 11)

```python-run
def mw(name, nxt):
    def h(req):
        print(name, "전")
        res = nxt(req)
        print(name, "후")
        return res
    return h

app = mw("A", mw("B", lambda r: "뷰"))
app("GET /")
```

출력 네 줄의 순서는? Django의 `MIDDLEWARE` 목록과 어떻게 연결되나요?

<details>
<summary>정답 보기</summary>

**답:** `A 전` → `B 전` → `B 후` → `A 후`.

바깥 껍질 A가 먼저 들어가고 가장 나중에 나옵니다. Django도 `MIDDLEWARE` 목록 **위→아래**로 요청을 통과시키고, 응답은 **아래→위**로 돌아 나갑니다. 그래서 `SessionMiddleware`가 `AuthenticationMiddleware`보다 위에 있어야 세션에서 user를 찾을 수 있습니다.

</details>

---

## Q9. settings 나누기 (Day 11)

`config/settings/base.py`, `dev.py`, `prod.py`로 나눴습니다. 운영 서버가 `prod.py`를 쓰게 하려면 무엇을 설정하나요? 그리고 `SECRET_KEY`는 어느 파일에 쓰나요?

<details>
<summary>정답 보기</summary>

**답:**

- 환경변수 `DJANGO_SETTINGS_MODULE=config.settings.prod`를 설정합니다 (`wsgi.py`의 기본값을 prod로 둘 수도 있음).
- `SECRET_KEY`는 **어느 파일에도 쓰지 않습니다.** `prod.py`에서 `os.environ["SECRET_KEY"]`로 읽고, 실제 값은 배포 플랫폼의 환경변수(비밀 저장소)에 둡니다. 코드가 git에 올라가도 비밀이 새지 않습니다.

</details>

---

## Q10. FK와 M2M (Day 12)

체크인(날짜별 기록)과 태그를 Goal에 붙였습니다. 각각 FK와 M2M 중 무엇이고, DB에는 어떻게 저장되나요? 태그 `#건강`을 지우면 그 태그가 붙은 Goal은?

<details>
<summary>정답 보기</summary>

**답:**

- **체크인 = FK (1:N)**. `CheckIn` 테이블에 `goal_id` 열이 생깁니다. Goal 하나에 체크인 여러 개.
- **태그 = M2M (N:M)**. Goal·Tag 테이블은 그대로이고, `(goal_id, tag_id)` 짝을 담는 **중간 테이블**이 생깁니다.
- 태그를 지우면 **중간 테이블의 짝만** 지워지고 Goal은 남습니다.

```python
Goal.objects.filter(
    owner=request.user,
    tags__name="건강")
```

`__`로 관계를 건너면 Django가 JOIN을 만들어 줍니다.

</details>

---

수고하셨어요! 맞힌 개수를 채팅으로 알려 주세요. 틀린 문항의 Day를 다시 보면 다음 주 복습 문제에 반영됩니다.
