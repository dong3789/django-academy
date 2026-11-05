# 4주차 퀴즈 · 미들웨어·DRF API (Day 20~24)

> Day 20~24(미들웨어·시그널, Serializer 심화, ViewSet·Router, 인증, 권한·Throttling·Pagination)를 점검하는 10문제입니다.
> 답을 생각해 본 뒤 `<details>`를 열어 확인하세요.
> 채점·점수는 채팅으로 알려 주시면 기록해 둡니다.

---

## Q1. 미들웨어 순서 (Day 20)

`MIDDLEWARE`에 A, B, C 순서로 적었습니다. 요청과 응답은 각각 어떤 순서로 통과하나요?

<details>
<summary>정답 보기</summary>

요청은 **A → B → C → 뷰**, 응답은 **C → B → A**입니다. 양파 껍질처럼 바깥(A)에서 들어가 안에서 나옵니다.

```python
def simple_mw(get_response):
    def mw(request):
        # 요청: 뷰 전에 실행
        resp = get_response(request)
        # 응답: 뷰 후에 실행
        return resp
    return mw
```

그래서 `SessionMiddleware`가 `AuthenticationMiddleware`보다 **앞**에 있어야 합니다. 세션이 먼저 준비돼야 `request.user`를 채울 수 있습니다.

</details>

---

## Q2. 시그널과 트랜잭션 (Day 20)

`post_save` 시그널에서 환영 메일을 보냈더니, 가끔 DB가 롤백됐는데도 메일이 나갔습니다. 어떻게 고치나요?

<details>
<summary>정답 보기</summary>

`post_save`는 **커밋 전**, 트랜잭션 안에서 실행됩니다. 이후 롤백돼도 이미 보낸 메일은 못 되돌립니다. `transaction.on_commit`으로 **커밋이 확정된 뒤**에 보냅니다.

```python
from django.db import transaction

@receiver(post_save, sender=User)
def welcome(sender, instance, created,
            **kw):
    if created:
        transaction.on_commit(
            lambda: send_mail_to(instance))
```

더 나아가, 숨은 제어 흐름을 피하려고 시그널 대신 서비스 함수에서 명시적으로 부르는 편이 낫다는 것도 Day 20의 포인트였습니다.

</details>

---

## Q3. DRF는 `clean()`을 부르지 않는다 (Day 21)

모델의 `clean()`에 "목표 수치는 1 이상" 검사를 넣었는데, API로는 0이 저장됩니다. 왜이고, 어디로 옮겨야 하나요?

<details>
<summary>정답 보기</summary>

ModelForm은 `full_clean()`으로 모델 `clean()`을 부르지만, **DRF Serializer는 부르지 않습니다**. 검증을 Serializer로 옮기거나(또는 DB 제약을 둡니다).

```python
class GoalSerializer(
        serializers.ModelSerializer):
    def validate_target(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "1 이상이어야 합니다.")
        return value
```

최후 방어선으로 `CheckConstraint`를 모델 `Meta.constraints`에 두면 어떤 경로로 저장하든 DB가 막습니다.

</details>

---

## Q4. 중첩 응답과 N+1 (Day 21)

목표마다 체크인 목록을 중첩 Serializer로 넣었더니, 목표 50개 목록에 쿼리가 51번 나갑니다. 해결책은?

<details>
<summary>정답 보기</summary>

목표 1번 + 목표마다 체크인 1번씩 = **N+1 문제**입니다. 뷰의 쿼리셋에서 미리 가져옵니다.

```python
def get_queryset(self):
    return (Goal.objects
        .filter(owner=self.request.user)
        .prefetch_related("checkins"))
```

역방향 FK·M2M은 `prefetch_related`(쿼리 2번), 정방향 FK(`owner` 등)는 `select_related`(JOIN 1번)입니다.

</details>

---

## Q5. Router가 만드는 URL (Day 22)

`router.register("goals", GoalViewSet)`일 때, `PATCH /goals/3/`은 어떤 메서드로 연결되나요?

<details>
<summary>정답 보기</summary>

`partial_update`입니다. Router는 HTTP 메서드와 URL 모양(목록/상세)을 ViewSet 동작으로 바꿉니다.

| 요청 | 동작 |
|---|---|
| GET /goals/ | list |
| POST /goals/ | create |
| GET /goals/3/ | retrieve |
| PUT /goals/3/ | update |
| PATCH /goals/3/ | partial_update |
| DELETE /goals/3/ | destroy |

</details>

---

## Q6. `@action`의 함정 (Day 22)

아래 코드의 보안 문제는?

```python
@action(detail=True, methods=["post"])
def checkin(self, request, pk=None):
    goal = Goal.objects.get(pk=pk)
    goal.checkins.create()
    return Response(status=201)
```

<details>
<summary>정답 보기</summary>

`Goal.objects.get(pk=pk)`는 `get_queryset()`의 소유자 필터와 객체 권한 검사를 **모두 우회**합니다. 남의 목표 id로 체크인을 만들 수 있습니다(IDOR). 또 없는 id면 404가 아니라 500이 납니다.

```python
def checkin(self, request, pk=None):
    goal = self.get_object()
    goal.checkins.create()
    return Response(status=201)
```

`get_object()`는 범위 필터 + 404 처리 + `check_object_permissions`를 한 번에 해 줍니다.

</details>

---

## Q7. 세션 인증과 CSRF (Day 23)

세션으로 로그인한 브라우저의 `fetch` POST는 403인데, 같은 요청을 JWT `Authorization` 헤더로 보내면 통과합니다. 왜 JWT는 CSRF 검사를 안 하나요?

<details>
<summary>정답 보기</summary>

CSRF는 **브라우저가 쿠키를 자동으로 붙이는** 점을 노린 공격입니다. 세션 인증은 쿠키 기반이라 다른 사이트의 요청에도 쿠키가 따라가므로 CSRF 토큰으로 확인해야 합니다.

`Authorization` 헤더는 브라우저가 **자동으로 붙이지 않습니다**. 우리 JS 코드가 직접 넣어야 하므로, 남의 사이트가 대신 만들 수 없습니다. 단, JWT를 **쿠키**에 저장하면 다시 CSRF 대비가 필요합니다.

</details>

---

## Q8. JWT 위조 (Day 23)

공격자가 JWT 페이로드를 `{"user_id": 1}`로 바꿨습니다. 서버가 거부할 수 있는 이유를 한 문장으로, 그리고 서버 쪽에서 반드시 고정해야 하는 것 하나는?

<details>
<summary>정답 보기</summary>

서명은 **비밀키로 헤더·페이로드를 HMAC한 값**이라, 내용이 바뀌면 서버가 다시 계산한 서명과 맞지 않고, 공격자는 키가 없어 새 서명을 못 만듭니다.

서버는 **허용 알고리즘을 고정**해야 합니다. 헤더의 `alg: none`을 믿는 옛 라이브러리 버그처럼, 토큰이 알고리즘을 정하게 두면 서명 없이 통과될 수 있습니다.

</details>

---

## Q9. 객체 권한이 안 도는 곳 (Day 24)

`IsOwnerOrReadOnly`(객체 권한)만 두고 `get_queryset()`은 `Goal.objects.all()`입니다. 어떤 엔드포인트에서 남의 데이터가 새나요?

<details>
<summary>정답 보기</summary>

**목록(`GET /goals/`)**입니다. `has_object_permission`은 `get_object()`가 불리는 상세·수정·삭제에서만 실행되고, 목록은 객체를 하나씩 검사하지 않습니다.

```python
def get_queryset(self):
    return Goal.objects.filter(
        owner=self.request.user)
```

목록 보안은 `get_queryset()`, 객체 권한은 두 번째 잠금입니다.

</details>

---

## Q10. 깊은 페이지가 느린 이유 (Day 24)

`?page=5000`(PAGE_SIZE 20)이 1페이지보다 훨씬 느립니다. 이유와 대안은?

<details>
<summary>정답 보기</summary>

PageNumber는 `LIMIT 20 OFFSET 99980`이 됩니다. DB는 앞의 99,980행을 **읽고 버린 뒤** 20개를 줍니다. 매번 `COUNT(*)`도 합니다.

대안은 **CursorPagination**입니다. "마지막으로 본 값 다음부터" 가져옵니다.

```sql
SELECT * FROM goals
WHERE created < '2026-11-01'
ORDER BY created DESC
LIMIT 20;
```

정렬 키에 인덱스가 있으면 깊이와 무관하게 빠르고, 중간에 새 행이 들어와도 중복·누락이 없습니다. 대신 임의 페이지로 점프는 못 합니다.

</details>

---

수고하셨습니다! 몇 개 맞혔는지 채팅으로 알려 주세요. 5주차에는 API 버저닝·문서화, 그리고 ORM 최적화로 넘어갑니다.
