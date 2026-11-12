# 5주차 퀴즈 · API 버저닝·ORM 최적화·테스트 기초 (Day 25~31)

> Day 25~31(API 버저닝·OpenAPI, N+1, 인덱스·EXPLAIN, 트랜잭션, 격리수준·데드락, 집계·bulk, pytest 기초)을 점검하는 10문제입니다.
> 답을 생각해 본 뒤 `<details>`를 열어 확인하세요.
> 채점·점수는 채팅으로 알려 주시면 기록해 둡니다.

---

## Q1. 깨지는 변경 (Day 25)

Goals API v1은 `target` 필드를 줍니다. v2에서 이름을 `target_count`로 바꾸려 합니다. 옛 앱이 깨지지 않게 하려면 DRF에서 어떻게 하나요?

<details>
<summary>정답 보기</summary>

필드 이름 변경은 **깨지는 변경**(breaking change)이라 새 버전으로 냅니다. `URLPathVersioning`으로 `/api/v1/`, `/api/v2/`를 받고, 뷰에서 `request.version`에 따라 Serializer를 고릅니다.

```python
class GoalViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.request.version == "v2":
            return GoalSerializerV2
        return GoalSerializerV1
```

v1은 바로 지우지 않고, 폐기 예정(deprecation)을 문서·헤더로 알린 뒤 사용량을 보고 내립니다. 필드 **추가**는 보통 깨지지 않으므로 버전을 올릴 필요가 없습니다.

</details>

---

## Q2. 문서를 코드에서 (Day 25)

drf-spectacular로 OpenAPI 스키마를 만드는 것이 손으로 쓴 API 문서보다 나은 점 두 가지는?

<details>
<summary>정답 보기</summary>

1. **코드와 문서가 어긋나지 않습니다.** Serializer·ViewSet에서 스키마를 생성하므로, 필드를 바꾸면 문서도 같이 바뀝니다.
2. **기계가 읽을 수 있는 계약**입니다. Swagger UI로 바로 호출해 보고, 프론트용 클라이언트 코드 생성, CI에서 스키마 diff로 깨지는 변경 탐지까지 할 수 있습니다.

```python
urlpatterns += [
    path("api/schema/",
         SpectacularAPIView.as_view()),
    path("api/docs/",
         SpectacularSwaggerView.as_view(
             url_name="schema")),
]
```

</details>

---

## Q3. N+1 찾기 (Day 26)

아래 템플릿용 코드는 Goal이 50개일 때 쿼리를 몇 번 보내나요? 어떻게 고치나요?

```python
goals = Goal.objects.all()
for g in goals:
    print(g.owner.username,
          [t.name for t in g.tags.all()])
```

<details>
<summary>정답 보기</summary>

목록 1번 + owner 50번 + tags 50번 = **101번**입니다. 전형적인 N+1입니다.

```python
goals = (Goal.objects
         .select_related("owner")
         .prefetch_related("tags"))
```

FK인 `owner`는 `select_related`(JOIN 한 번), M2M인 `tags`는 `prefetch_related`(추가 SELECT 한 번 + Python에서 매칭)입니다. 합계 **2번**이 됩니다.

</details>

---

## Q4. 복합 인덱스 순서 (Day 27)

자주 쓰는 쿼리가 `WHERE owner_id = ? ORDER BY created DESC`입니다. 인덱스 `(created, owner_id)`와 `(owner_id, created)` 중 무엇이 맞나요?

<details>
<summary>정답 보기</summary>

**`(owner_id, created)`**입니다. 복합 인덱스는 **왼쪽 컬럼부터** 정렬돼 있습니다(leftmost prefix). 등호 조건(`owner_id`)을 앞에 두면 그 사용자 구간으로 바로 점프하고, 그 안은 이미 `created` 순이라 정렬도 공짜입니다.

```python
class Meta:
    indexes = [models.Index(
        fields=["owner", "-created"])]
```

`(created, owner_id)`는 날짜 순으로 전체를 훑으며 owner를 걸러야 합니다. 확인은 `EXPLAIN`에서 `SCAN`이 아니라 인덱스 `SEARCH`가 나오는지로 합니다.

</details>

---

## Q5. 인덱스의 비용 (Day 27)

"느린 쿼리가 무서우니 모든 컬럼에 인덱스를 걸자"는 의견에 어떻게 답하나요?

<details>
<summary>정답 보기</summary>

인덱스는 **읽기를 빠르게, 쓰기를 느리게** 합니다. INSERT·UPDATE·DELETE마다 모든 인덱스를 함께 고쳐야 하고, 저장 공간도 씁니다.

또 **선택도**(selectivity)가 낮은 컬럼(예: `is_done` True/False)은 인덱스를 걸어도 DB가 풀 스캔을 고르기 쉽습니다. 그래서 실제 느린 쿼리를 `EXPLAIN ANALYZE`로 확인한 뒤, 그 쿼리에 맞는 인덱스만 추가합니다. 특정 조건만 자주 찾는다면 부분 인덱스(`condition=Q(...)`)도 방법입니다.

</details>

---

## Q6. atomic 안에서 예외 삼키기 (Day 28)

아래 코드에서 `notify()`가 실패하면 체크인은 저장되나요?

```python
with transaction.atomic():
    CheckIn.objects.create(goal=g)
    try:
        notify(g)
    except Exception:
        pass
```

<details>
<summary>정답 보기</summary>

**저장됩니다.** `atomic`은 예외가 블록 **밖으로** 나갈 때만 롤백합니다. 안에서 삼키면 정상 종료로 보고 커밋합니다.

다만 `notify()` 안에서 **DB 에러**가 났다면 트랜잭션이 깨진 상태라 이후 쿼리가 에러납니다. 이럴 땐 안쪽을 `atomic`으로 한 번 더 감싸(SAVEPOINT) 그 부분만 되돌립니다.

```python
with transaction.atomic():
    CheckIn.objects.create(goal=g)
    transaction.on_commit(
        lambda: notify(g))
```

알림 같은 외부 부작용은 애초에 `on_commit`으로 **커밋 후**에 보내는 것이 정답에 가깝습니다.

</details>

---

## Q7. 동시에 +1 (Day 28)

두 요청이 동시에 `g.count = g.count + 1; g.save()`를 하면 값이 1만 오를 수 있습니다. 해결책 두 가지는?

<details>
<summary>정답 보기</summary>

**Lost update**(갱신 분실)입니다. 둘 다 같은 옛 값을 읽고 덮어씁니다.

1. **DB에서 계산:** `F` 식으로 읽기·쓰기를 한 SQL에 합칩니다.

```python
Goal.objects.filter(pk=g.pk).update(
    count=F("count") + 1)
```

2. **행 잠금:** `select_for_update`로 읽는 순간 잠가, 다른 요청은 커밋까지 기다리게 합니다.

```python
with transaction.atomic():
    g = (Goal.objects.select_for_update()
         .get(pk=pk))
    g.count += 1
    g.save()
```

단순 증가면 1번이 가장 가볍고, "읽고 판단해서 쓰기"면 2번을 씁니다.

</details>

---

## Q8. 데드락 예방 (Day 29)

요청1은 Goal A→B, 요청2는 Goal B→A 순서로 `select_for_update`를 겁니다. 무슨 일이 생기고, 어떻게 막나요?

<details>
<summary>정답 보기</summary>

서로가 가진 락을 기다리는 **고리**가 생겨 **데드락**입니다. DB가 감지해 한쪽 트랜잭션을 강제로 롤백(에러)합니다.

예방의 기본은 **항상 같은 순서로 잠그기**입니다.

```python
with transaction.atomic():
    goals = list(Goal.objects
        .select_for_update()
        .filter(pk__in=ids)
        .order_by("pk"))
```

여기에 트랜잭션을 짧게 유지하고, `atomic` **바깥**에서 데드락 에러 시 재시도하는 장치를 더합니다. 참고로 PostgreSQL의 기본 격리수준은 READ COMMITTED입니다.

</details>

---

## Q9. annotate 부풀림 (Day 30)

`Goal.objects.annotate(c=Count("checkins"), t=Count("tags"))`에서 체크인 5개, 태그 3개인 목표의 `c`가 15로 나왔습니다. 왜이고, 어떻게 고치나요?

<details>
<summary>정답 보기</summary>

두 관계를 **한 쿼리에서 동시에 JOIN**해서 행이 곱해졌습니다(5 × 3 = 15). Count는 곱해진 행을 그대로 셉니다.

```python
Goal.objects.annotate(
    c=Count("checkins", distinct=True),
    t=Count("tags", distinct=True))
```

`Count`는 `distinct=True`로 고칠 수 있습니다. `Sum`처럼 distinct로 해결이 안 되는 집계는 `Subquery`로 관계마다 따로 계산합니다. 확인은 `str(qs.query)`로 SQL을 봅니다.

</details>

---

## Q10. DB 테스트가 실패하는 이유 (Day 31)

pytest-django에서 아래 테스트는 왜 실패하고, 두 번 연속 돌려도 결과가 같으려면 무엇이 보장돼야 하나요?

```python
def test_create():
    Goal.objects.create(title="독서")
    assert Goal.objects.count() == 1
```

<details>
<summary>정답 보기</summary>

pytest-django는 기본적으로 **DB 접근을 막습니다.** `@pytest.mark.django_db`를 붙여야 합니다.

```python
@pytest.mark.django_db
def test_create():
    Goal.objects.create(title="독서")
    assert Goal.objects.count() == 1
```

마크를 붙이면 테스트마다 트랜잭션을 열고 끝나면 **롤백**하므로, 몇 번을 돌려도 count는 1입니다. 단, 실제 커밋이 없어서 `on_commit` 콜백은 실행되지 않습니다(필요하면 `transaction=True` 또는 `django_capture_on_commit_callbacks`). 전역 변수 같은 메모리 상태는 롤백되지 않으니 직접 정리합니다.

</details>

---

수고하셨습니다! 몇 개 맞혔는지 채팅으로 알려 주세요. 6주차에는 **테스트**(fixture·factory_boy, API 테스트·모킹, CI)를 이어 갑니다.
