# 6주차 퀴즈 · 테스트·캐시·Celery (Day 32~38)

> Day 32~38(fixture·factory_boy, API 테스트·모킹, 통합테스트·CI, TDD, Redis 캐시, Celery, 재시도·멱등성·beat)을 점검하는 10문제입니다.
> 답을 생각해 본 뒤 `<details>`를 열어 확인하세요.
> 채점·점수는 채팅으로 알려 주시면 기록해 둡니다.

---

## Q1. fixture 정리 순서 (Day 32)

아래 테스트가 끝나면 무엇이 어떤 순서로 출력될까요?

```python
@pytest.fixture
def db_conn():
    yield "conn"
    print("conn 닫기")
```

```python
@pytest.fixture
def user(db_conn):
    yield "user"
    print("user 삭제")
def test_a(user): ...
```

<details>
<summary>정답 보기</summary>

```text
user 삭제
conn 닫기
```

fixture는 **의존하는 순서대로 준비**(db_conn → user)되고, 정리는 **반대 순서**(LIFO, 나중에 만든 것부터)로 합니다. user가 conn을 쓰고 있을 수 있으니, user를 먼저 치우고 conn을 닫아야 안전합니다. `yield` 뒤가 정리 코드입니다.

</details>

---

## Q2. build vs create (Day 32)

factory_boy에서 `GoalFactory.build()`와 `GoalFactory.create()`의 차이와, 각각 언제 쓰나요?

<details>
<summary>정답 보기</summary>

- `build()`: 객체를 **메모리에만** 만듭니다. DB 저장 없음, `pk`는 `None`. 순수 계산(진행률 함수, Serializer 검증 등)을 테스트할 때 빠릅니다. `django_db` 마크도 필요 없습니다.
- `create()`: **DB에 저장**까지 합니다. 쿼리·API·권한처럼 DB에서 읽어 오는 흐름을 테스트할 때 씁니다.

```python
g = GoalFactory.build(target=10)
assert g.pk is None
```

DB가 필요 없는 테스트는 `build()`로 써야 테스트 전체가 빨라집니다.

</details>

---

## Q3. 어디를 patch하나 (Day 33)

`goals/views.py`가 `from goals.mailer import send_cheer`로 가져와 씁니다. 테스트에서 어떤 경로를 patch해야 하나요?

<details>
<summary>정답 보기</summary>

**`goals.views.send_cheer`**입니다.

```python
@patch("goals.views.send_cheer")
def test_checkin(m, client): ...
```

`from … import`는 `views` 모듈 안에 **같은 함수를 가리키는 새 이름표**를 만듭니다. `goals.mailer.send_cheer`를 바꿔도 `views`의 이름표는 여전히 진짜 함수를 가리킵니다. 규칙: **정의된 곳이 아니라 쓰는 곳**을 patch합니다.

</details>

---

## Q4. 401 vs 403 (Day 33)

Goals API에서 ① 로그인 안 한 사용자가 목록을 요청할 때, ② 로그인한 사용자가 **남의** Goal을 수정할 때 각각 어떤 상태 코드가 맞나요?

<details>
<summary>정답 보기</summary>

- ① **401 Unauthorized**: "누구인지 모름". 인증 정보가 없거나 틀림.
- ② **403 Forbidden**: "누구인지는 알지만 권한이 없음".

```python
r = api.get("/api/goals/")
assert r.status_code == 401
api.force_authenticate(user=other)
r = api.patch(f"/api/goals/{g.id}/", {})
assert r.status_code == 403
```

참고: DRF는 `SessionAuthentication`만 쓰면 `WWW-Authenticate` 헤더가 없어 ①도 403을 돌려줍니다. 또 `get_queryset`으로 내 것만 거르면 ②는 **404**가 되는데, 남의 Goal 존재 자체를 숨기는 장점이 있습니다.

</details>

---

## Q5. 커버리지 100%의 함정 (Day 34)

아래 함수와 테스트로 줄 커버리지는 100%입니다. 그런데도 놓친 것은?

```python
def pct(done, target):
    if target:
        return done * 100 // target
    return 0
def test_pct():
    assert pct(5, 10) == 50
    assert pct(1, 0) == 0
```

<details>
<summary>정답 보기</summary>

모든 줄은 지나갔지만, **값이 맞는지**는 일부만 확인했습니다. 예를 들어 `done > target`(초과 달성 시 120%를 줄지 100%로 자를지), 음수 입력 같은 **규칙**은 테스트가 없습니다. 커버리지는 "안 지나간 곳"을 찾는 도구일 뿐, "맞게 동작한다"는 증거가 아닙니다.

```python
def test_over():
    assert pct(12, 10) == 100
```

이 테스트를 추가하면 지금 코드는 120을 돌려줘 **실패**합니다. 줄 100%인데도 버그가 숨어 있던 겁니다. 그래서 `--cov-branch`(분기 커버리지)와, 일부러 코드를 바꿔 테스트가 잡는지 보는 **뮤테이션 테스트**를 함께 봅니다.

</details>

---

## Q6. CI에서 잡는 마이그레이션 실수 (Day 34)

모델 필드를 추가하고 `makemigrations`를 깜빡한 채 push했습니다. CI에서 이를 잡으려면 어떤 명령을 넣나요?

<details>
<summary>정답 보기</summary>

```bash
python manage.py makemigrations \
  --check --dry-run
```

모델과 마이그레이션 파일이 어긋나 있으면 **0이 아닌 종료 코드**를 내서 CI가 빨간불이 됩니다. `--dry-run`이라 파일은 만들지 않습니다. 브랜치 보호 규칙에서 이 CI를 **필수 체크**로 걸어야 "빨간불이면 머지 금지"가 됩니다.

</details>

---

## Q7. TDD와 시간 (Day 35)

TDD로 "오늘까지 연속 체크인 일수(streak)"를 만들 때, 테스트가 **자정 근처에만 실패**합니다. 원인과 해결은?

<details>
<summary>정답 보기</summary>

원인은 함수 안에서 **현재 시각을 직접** 읽기 때문입니다(`date.today()`). 테스트가 만든 데이터와 함수가 읽는 "오늘"이 자정을 사이에 두고 달라지면 실패하는 flaky test가 됩니다. 서버가 UTC라면 한국 시간과 날짜가 어긋나는 문제도 겹칩니다.

해결은 두 가지입니다.

```python
def streak(days, today):
    ...
assert streak(days, date(2026, 11, 20)) == 3
```

① **의존성 주입**: "오늘"을 인자로 받아 순수 함수로 만듭니다. ② 꼭 시각을 읽어야 하면 `freezegun`의 `@freeze_time("2026-11-20")`으로 고정합니다. Django에선 `timezone.localdate()`로 설정한 시간대 기준 날짜를 씁니다.

</details>

---

## Q8. 캐시 스탬피드 (Day 36)

인기 대시보드의 캐시가 TTL로 만료되는 순간, 동시에 요청 500개가 들어왔습니다. 무슨 일이 생기고, 어떻게 막나요?

<details>
<summary>정답 보기</summary>

500개 요청이 모두 miss를 보고 **동시에 DB 집계**를 실행합니다. DB가 순간 과부하로 느려지거나 죽습니다. 이것이 **캐시 스탬피드**(cache stampede)입니다.

막는 방법:

- **락**: 첫 요청만 `cache.add("lock:stats", 1, 10)`에 성공해 계산하고, 나머지는 잠시 기다리거나 옛 값을 씁니다.
- **TTL 지터**: 키마다 만료 시각을 흩뜨려 한꺼번에 만료되지 않게 합니다.
- **미리 갱신**: 만료 전에 백그라운드(Celery)로 다시 채웁니다.

```python
ttl = 300 + random.randint(0, 60)
cache.set(key, data, ttl)
```

</details>

---

## Q9. Celery와 on_commit (Day 37)

아래 코드는 가끔 워커에서 `CheckIn.DoesNotExist`를 냅니다. 고쳐 보세요.

```python
with transaction.atomic():
    ci = CheckIn.objects.create(...)
    send_cheer.delay(ci.id)
```

<details>
<summary>정답 보기</summary>

```python
with transaction.atomic():
    ci = CheckIn.objects.create(...)
    transaction.on_commit(
        lambda: send_cheer.delay(ci.id))
```

`delay()`는 **커밋 전에** 메시지를 브로커에 넣습니다. 빠른 워커가 그 사이 작업을 꺼내면 아직 커밋되지 않은 행은 안 보입니다. "가끔"인 이유는 워커와 커밋의 **경쟁 상태**이기 때문입니다. `on_commit`으로 커밋이 확정된 뒤에만 보내고, 롤백되면 아예 안 보냅니다. Celery 5.4+는 `send_cheer.delay_on_commit(ci.id)`도 있습니다.

</details>

---

## Q10. 재시도와 멱등성 (Day 38)

축하 메일 작업에 `acks_late=True`와 자동 재시도를 켰더니, 가끔 메일이 **두 통** 갑니다. 왜 그렇고, 어떻게 한 통만 가게 하나요?

<details>
<summary>정답 보기</summary>

`acks_late`와 재시도는 **at-least-once**(최소 한 번)를 보장합니다. 메일은 보냈는데 응답 직전 실패하거나 워커가 죽으면, 같은 작업이 **다시 실행**됩니다. 중복 실행은 버그가 아니라 **설계상 일어나는 일**입니다.

해결은 작업을 **멱등**하게 만드는 것입니다. 확인과 기록을 **원자적으로** 합니다.

```python
n = (CheckIn.objects
     .filter(id=cid, cheer_sent=False)
     .update(cheer_sent=True))
if n == 0:
    return
send_mail(...)
```

여러 워커가 동시에 실행해도 `UPDATE … WHERE`는 한 쪽만 1행을 받습니다. Redis `cache.add(f"cheer:{cid}", 1, 86400)`(SET NX)도 같은 원리입니다. "확인 → 보내기"를 따로 하면 그 사이에 경쟁 상태가 생기니 안 됩니다.

</details>

---

수고하셨습니다! 몇 개 맞혔는지 채팅으로 알려 주세요. 7주차에는 **async views·Channels**로 8주차를 마무리하고 **배포**(gunicorn·nginx·Docker)로 넘어갑니다.
