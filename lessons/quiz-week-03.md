# 3주차 퀴즈 · Django 코어·Forms·인증·Admin

> Day 13~19(마이그레이션 심화, ORM 통계, URL·CBV, 템플릿 태그, Forms 검증, 커스텀 User·세션, Admin)를 점검하는 10문제입니다.
> 답을 생각해 본 뒤 `<details>`를 열어 확인하세요.
> 채점·점수는 채팅으로 알려 주시면 기록해 둡니다.

---

## Q1. 데이터 마이그레이션의 모델 (Day 13)

`RunPython` 함수 안에서 `from goals.models import Goal` 대신 `apps.get_model("goals", "Goal")`을 써야 하는 이유는?

<details>
<summary>정답 보기</summary>

**마이그레이션이 실행되는 "그 시점"의 모델 모양**이 필요하기 때문입니다.

- `goals.models`의 Goal은 **오늘의** 코드입니다. 나중에 필드를 지우거나 이름을 바꾸면 옛 마이그레이션이 깨집니다.
- `apps.get_model`은 앞선 마이그레이션들로 재구성한 **과거 버전 모델**을 줍니다.

```python
def forward(apps, schema_editor):
    Goal = apps.get_model("goals", "Goal")
    for g in Goal.objects.all():
        ...
```

새 DB에서 처음부터 `migrate`해도 항상 같은 결과가 나오게 하는 장치입니다.

</details>

---

## Q2. 잎이 두 개 (Day 13)

두 사람이 각자 `0004` 뒤에 `0005_a`, `0005_b`를 만들었습니다. git 충돌은 없었는데 `migrate`하면 어떻게 되고, 어떻게 해결하나요?

<details>
<summary>정답 보기</summary>

**"Conflicting migrations detected"로 멈춥니다.** 마이그레이션 그래프에 마지막 노드(잎)가 두 개라 순서를 정할 수 없기 때문입니다.

```bash
python manage.py makemigrations --merge
```

두 파일을 부모로 갖는 **병합 마이그레이션**(`0006_merge_...`)이 생깁니다. 두 변경이 같은 열을 건드리지 않는지 사람이 확인한 뒤 커밋합니다.

</details>

---

## Q3. 쿼리는 몇 번? (Day 14)

```python
qs = Goal.objects.filter(owner=me)
qs = qs.filter(target__gte=10)
qs = qs.order_by("-id")
first = qs[0]
```

DB 쿼리는 몇 번 나가나요?

<details>
<summary>정답 보기</summary>

**1번**입니다. QuerySet은 **게으르게**(lazy) 동작해서 1~3줄은 조건만 쌓습니다. 4줄에서 값을 꺼낼 때 `WHERE ... ORDER BY id DESC LIMIT 1` 한 번이 실행됩니다.

Node의 Knex 빌더도 `await` 전까지 쿼리가 안 나가는 것과 비슷합니다.

</details>

---

## Q4. aggregate vs annotate (Day 14)

"내 체크인 총합 하나"와 "목표마다 체크인 합계"는 각각 무엇으로 구하고, 반환 타입은 무엇인가요?

<details>
<summary>정답 보기</summary>

```python
from django.db.models import Sum

CheckIn.objects.filter(
    goal__owner=me).aggregate(
    total=Sum("amount"))
# {'total': 42}  ← dict

Goal.objects.annotate(
    s=Sum("checkins__amount"))
# QuerySet, 각 Goal에 .s 칸
```

- `aggregate`: 전체를 **값 하나**로 접고 dict를 돌려줍니다. 체이닝이 끝납니다.
- `annotate`: 행마다 계산 칸을 붙인 **QuerySet**을 돌려줍니다 (SQL `GROUP BY`). 이어서 `filter`·`order_by`가 가능하고, 그 칸으로 거르면 `HAVING`이 됩니다.

</details>

---

## Q5. Mixin 순서 (Day 15)

```python
class GoalCreate(CreateView,
                 LoginRequiredMixin):
    model = Goal
```

이 뷰에는 어떤 문제가 있나요?

<details>
<summary>정답 보기</summary>

**로그인 검사가 동작하지 않습니다.** 파이썬은 MRO(메서드 찾는 순서)에서 **왼쪽부터** 찾습니다. `CreateView` 쪽 `View.dispatch`가 먼저 잡히고, 이 메서드는 `super().dispatch()`를 부르지 않아 `LoginRequiredMixin.dispatch`가 실행되지 않습니다.

```python
class GoalCreate(LoginRequiredMixin,
                 CreateView):
    model = Goal
```

Mixin은 항상 **왼쪽**, 기반 뷰는 맨 오른쪽에 둡니다.

</details>

---

## Q6. 템플릿 필터와 XSS (Day 16)

커스텀 필터가 `f"<b>{name}</b>"`을 돌려주는데 화면에 `<b>` 글자가 그대로 보입니다. `mark_safe(f"<b>{name}</b>")`로 고치면 무엇이 위험하고, 올바른 방법은?

<details>
<summary>정답 보기</summary>

템플릿은 자동 이스케이프로 XSS(남의 스크립트 주입)를 막습니다. `mark_safe`는 "이 문자열 전체를 믿어라"는 뜻이라, `name`에 사용자가 쓴 `<script>`가 들어 있으면 **그대로 실행**됩니다.

```python
from django.utils.html import format_html

@register.filter
def bold(name):
    return format_html("<b>{}</b>", name)
```

`format_html`은 틀(`<b>{}</b>`)만 믿고, 끼워 넣는 값은 **이스케이프**합니다.

</details>

---

## Q7. clean 순서 (Day 17)

폼에 `target="abc"`가 들어왔습니다. `clean()`에서 `data["target"]`을 읽으면 무슨 일이 생기고, 어떻게 써야 하나요?

<details>
<summary>정답 보기</summary>

**`KeyError`가 납니다.** `"abc"`는 정수 변환(`to_python`) 단계에서 실패했고, 실패한 필드는 `cleaned_data`에서 **빠집니다.** 그 뒤에도 `clean()`은 호출됩니다.

```python
def clean(self):
    data = super().clean()
    t = data.get("target")
    if t is None:
        return data
    ...
```

`.get()`으로 읽고, 값이 없으면 "이미 에러가 붙은 칸"이니 건너뜁니다. 특정 칸에 에러를 붙이려면 `self.add_error("target", "...")`를 씁니다.

</details>

---

## Q8. 3겹 방어 (Day 17)

"한 사용자는 같은 제목의 목표를 두 개 가질 수 없다"를 폼 검증으로만 막으면 왜 부족하고, 무엇을 더해야 하나요?

<details>
<summary>정답 보기</summary>

폼 검사는 **"확인한 순간"과 "저장하는 순간" 사이에 틈**이 있습니다 (TOCTOU). 두 요청이 동시에 오면 둘 다 "중복 없음"을 보고 둘 다 저장할 수 있습니다.

```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=["owner", "title"],
            name="uniq_owner_title")]
```

- 폼: 친절한 에러 메시지.
- 모델 제약(DB): 동시 요청에도 **최종적으로 막아 줌**.
- 뷰: 그래도 나는 `IntegrityError`를 잡아 사용자에게 다시 안내.

</details>

---

## Q9. 커스텀 User (Day 18)

`AUTH_USER_MODEL = "accounts.User"`로 바꾼 프로젝트에서 Goal의 FK와 뷰 코드는 User를 각각 어떻게 참조해야 하나요? 그리고 왜 **프로젝트 시작 때** 바꿔야 하나요?

<details>
<summary>정답 보기</summary>

```python
# models.py
owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE)

# views.py 등
User = get_user_model()
```

- 모델 FK는 문자열 설정(`settings.AUTH_USER_MODEL`), 실행 코드에서는 `get_user_model()`.
- 첫 `migrate` 뒤에는 모든 FK, 권한·그룹 M2M, contenttypes가 `auth_user`에 묶여 교체가 매우 어렵습니다. 그래서 처음에 `AbstractUser` 상속 User를 만들어 두는 것이 비용 없는 보험입니다.

</details>

---

## Q10. Admin 목록 N+1 (Day 19)

CheckIn Admin의 `list_display`에 `obj.goal.owner.username`을 보여 주는 메서드 칸이 있습니다. 한 페이지 30행일 때 쿼리 수를 줄이려면?

<details>
<summary>정답 보기</summary>

설정이 없으면 목록 쿼리 1번 + 행마다 Goal·User 조회가 붙어 **최대 61번**까지 나갈 수 있습니다.

```python
class CheckInAdmin(admin.ModelAdmin):
    list_display = ["goal", "owner_name"]
    list_select_related = ["goal__owner"]
```

`list_select_related`로 두 단계를 **JOIN 한 번**에 가져오면 목록이 쿼리 1번(+ 페이지 개수 세기 1번)으로 줄어듭니다. M2M(예: tags)이라면 `get_queryset`에서 `prefetch_related`를 씁니다.

</details>

---

수고하셨어요! 점수(예: 8/10)를 채팅으로 알려 주시면 진행 기록에 남겨 둘게요.
