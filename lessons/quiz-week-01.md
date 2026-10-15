# 1주차 퀴즈 · Python 기초

> Day 1~5(환경·타입, 컬렉션, 함수/클로저, 클래스/MRO, 모듈/예외/해시 테이블)를 점검하는 10문제입니다.
> 답을 생각해 본 뒤 `<details>`를 열어 확인하세요.
> 채점·점수는 채팅으로 알려 주셔도 됩니다.

---

## Q1. 가상환경 (Day 1)

프로젝트마다 venv(또는 uv)를 쓰는 **가장 중요한 이유**는 무엇인가요?
전역에 패키지를 설치하는 것과 비교해 한 가지만 골라 설명하세요.

<details>
<summary>정답 보기</summary>

**답:** 프로젝트마다 **의존성 버전을 격리**하기 위해서입니다.

전역 `site-packages`에 설치하면 A 프로젝트의 Django 4와
B 프로젝트의 Django 5가 서로 덮어씁니다.
venv는 전용 `python`·`pip`·패키지 디렉터리를 만들어
PATH만 바꿔 그 환경을 씁니다.

**부가:** 재현 가능한 배포(`requirements.txt` / `uv.lock`)의 전제 조건이기도 합니다.

</details>

---

## Q2. == vs is (Day 1)

아래 출력은 무엇일까요? 이유를 `==`와 `is`의 차이로 설명하세요.

```python
a = [1, 2]
b = [1, 2]
c = a
print(a == b, a is b, a is c)
```

<details>
<summary>정답 보기</summary>

```text
True False True
```

**설명:**

- `a == b` → 내용(값)이 같아 `True`
- `a is b` → 서로 **다른 객체**(다른 id)라 `False`
- `a is c` → `c`는 `a`와 **같은 객체**를 가리켜 `True`

`is`는 식별성(identity), `==`는 동등성(equality)입니다.
`None` 비교만 `is None`을 쓰고, 값 비교는 `==`를 씁니다.

</details>

---

## Q3. 가변 기본 인자 (Day 1)

다음 함수를 두 번 호출하면 무엇이 출력되나요? 왜 그런가요?

```python
def add(item, bucket=[]):
    bucket.append(item)
    return bucket

print(add(1))
print(add(2))
```

<details>
<summary>정답 보기</summary>

```text
[1]
[1, 2]
```

**이유:** 기본 인자 `[]`는 **함수 정의 시 한 번만** 만들어집니다.
호출마다 새 리스트가 생기지 않아, 두 번째 호출이 같은 리스트에 append합니다.

**수정:**

```python
def add(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

</details>

---

## Q4. list vs dict 멤버십 (Day 2)

길이 N인 리스트와 같은 원소를 담은 set에서
`x in container`의 평균 시간 복잡도는 각각 무엇인가요?
실무에서 중복 검사·존재 확인에 set/dict를 쓰는 이유도 한 줄로 쓰세요.

<details>
<summary>정답 보기</summary>

**답:**

- list: 평균 **O(N)** (앞에서부터 선형 탐색)
- set / dict 키: 평균 **O(1)** (해시 테이블 조회)

**실무:** 반복문 안에서 `x in list`를 돌리면 O(N²)가 되기 쉽습니다.
존재·중복 체크는 set(또는 dict)으로 바꿉니다.

</details>

---

## Q5. 컴프리헨션 (Day 2)

아래와 **같은 결과**를 만드는 리스트 컴프리헨션을 한 줄로 쓰세요.
(실행 결과: `[0, 1, 4, 9, 16]`)

```python
out = []
for i in range(5):
    out.append(i * i)
```

<details>
<summary>정답 보기</summary>

```python
out = [i * i for i in range(5)]
print(out)
# 출력: [0, 1, 4, 9, 16]
```

**참고:** 조건 필터는 `for` 뒤에 `if`를 붙입니다.
예: `[i for i in range(10) if i % 2 == 0]`

dict/set도 `{k: v for ...}`, `{x for ...}` 형태입니다.

</details>

---

## Q6. 클로저 (Day 3)

아래 코드의 출력은 무엇인가요? 클로저가 **어떤 변수를** 붙잡는지 설명하세요.

```python
def make_fns():
    fns = []
    for i in range(3):
        fns.append(lambda: i)
    return fns

for f in make_fns():
    print(f())
```

<details>
<summary>정답 보기</summary>

```text
2
2
2
```

**설명:** 람다는 `i`의 **값이 아니라 변수 `i` 자체**를 닫습니다(late binding).
루프가 끝난 뒤 `i`는 2이므로, 세 함수 모두 호출 시점의 `i`(2)를 읽습니다.

**수정 예:** 기본 인자로 그때의 값을 박제합니다.

```python
fns.append(lambda i=i: i)
```

</details>

---

## Q7. *args / **kwargs (Day 3)

`def f(a, *args, **kwargs):`로 정의된 함수를
`f(1, 2, 3, x=4, y=5)`로 호출하면
`a`, `args`, `kwargs`에 무엇이 들어가나요?

<details>
<summary>정답 보기</summary>

```python
a == 1
args == (2, 3)
kwargs == {"x": 4, "y": 5}
```

**설명:**

- 위치 인자 첫 칸 → `a`
- 남는 위치 인자 → 튜플 `args`
- 키워드 인자 → dict `kwargs`

Django 뷰·데코레이터·`settings` 래퍼에서 같은 패턴이 반복됩니다.

</details>

---

## Q8. MRO / super (Day 4)

다음이 출력하는 MRO 순서를 쓰고,
`C().ping()`이 왜 `"C B A"`인지 한두 문장으로 설명하세요.

```python
class A:
    def ping(self):
        return "A"

class B(A):
    def ping(self):
        return "B " + super().ping()
```

```python
class C(B):
    def ping(self):
        return "C " + super().ping()

print(C.__mro__)
print(C().ping())
```

<details>
<summary>정답 보기</summary>

```text
(C, B, A, object)
C B A
```

**설명:** `super()`는 "부모 클래스"가 아니라
**인스턴스 타입의 MRO에서 다음 클래스**에 위임합니다.
`C` → `B` → `A` 순으로 `ping`이 이어져 `"C B A"`가 됩니다.

Django CBV 믹스인도 같은 MRO/`super()` 협력에 의존합니다.

</details>

---

## Q9. 예외 처리 (Day 5)

다음 중 **더 파이썬다운(EAFP)** 쪽은 어느 것인가요? 이유를 말하세요.

```python
# A (LBYL)
if key in data:
    return data[key]
return default
```

```python
# B (EAFP)
try:
    return data[key]
except KeyError:
    return default
```

(또는 `data.get(key, default)`와의 관계도 언급해도 됩니다.)

<details>
<summary>정답 보기</summary>

**답:** 흐름상 **B(EAFP)** 가 파이썬 관용에 가깝습니다.
"일단 시도하고, 실패를 예외로 처리"합니다.

A는 LBYL(Look Before You Leap)입니다.
키가 있는 경우를 두 번 조회하고,
멀티스레드/공유 dict에서는 확인과 사용 사이에 키가 사라질 수 있습니다(TOCTOU).

**실무:** 단순 조회는 `data.get(key, default)`가 가장 짧고 안전합니다.
EAFP는 파일 열기·파싱처럼 "실패가 예외로 정의된" 연산에 특히 잘 맞습니다.

</details>

---

## Q10. 해시 테이블 (Day 5)

Python `dict` 평균 조회가 O(1)에 가까운 이유를
"해시 → 버킷 → 충돌" 흐름으로 짧게 설명하세요.
부하율(load factor)이 커지면 CPython이 하는 일도 한 줄로 쓰세요.

<details>
<summary>정답 보기</summary>

**흐름:**

1. 키의 `hash()`로 정수를 얻습니다.
2. 테이블 크기로 마스크해 **버킷 인덱스**를 고릅니다.
3. 그 칸이 비었거나 같은 키면 끝나고,
   충돌이면 **탐침(probe)** 으로 다음 칸을 봅니다.

평균적으로 몇 칸만 보면 되므로 **상각 O(1)** 에 가깝습니다.
키가 해시 가능(`__hash__`)하고, `a == b`이면 `hash(a) == hash(b)`여야 합니다.

**부하율:** 항목이 많아져 테이블이 너무 꽉 차면
CPython은 **더 큰 테이블로 재해시(리사이즈)** 합니다.
삽입이 가끔 O(n)이지만, 전체에 나누면 여전히 상각 O(1)입니다.

</details>

---

**채점 가이드 (참고):** 10문항 만점. 개념+이유까지 맞으면 1점,
결과만 맞추고 이유가 비면 0.5점으로 보아도 됩니다.
점수나 틀린 번호를 채팅에 보내 주시면 복습 포인트를 짚어 드립니다.
