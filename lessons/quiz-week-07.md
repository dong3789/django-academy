# 7주차 퀴즈 · async·배포·ERD 설계 (Day 39~45)

> Day 39~45(async views·Channels, gunicorn 워커, nginx·정적 파일, Docker·compose, 환경변수·보안·로깅, 클라우드 배포, 요구사항·ERD 재설계)를 점검하는 10문제입니다.
> 답을 생각해 본 뒤 `<details>`를 열어 확인하세요.
> 채점·점수는 채팅으로 알려 주시면 기록해 둡니다.

---

## Q1. async 뷰의 두 함정 (Day 39)

아래 async 뷰에는 문제가 두 개 있습니다. 각각 무슨 일이 생기고, 어떻게 고치나요?

```python
async def widget(request, pk):
    goal = Goal.objects.get(pk=pk)
    r = requests.get(WEATHER_URL)
    return JsonResponse({
        "goal": goal.title,
        "w": r.json()})
```

<details>
<summary>정답 보기</summary>

1. `Goal.objects.get`은 **동기 ORM**이라 Django가 `SynchronousOnlyOperation` 에러를 냅니다. 루프를 막지 못하게 하는 안전장치입니다.
2. `requests.get`은 **블로킹** 호출이라, 응답을 기다리는 동안 이벤트 루프 전체가 멈춥니다. 에러가 안 나서 더 위험합니다.

```python
async def widget(request, pk):
    goal = await Goal.objects.aget(pk=pk)
    async with httpx.AsyncClient() as c:
        r = await c.get(WEATHER_URL)
    return JsonResponse({
        "goal": goal.title, "w": r.json()})
```

비동기 API가 없는 라이브러리는 `sync_to_async`로 감쌉니다. 그리고 async의 이득은 **ASGI 서버**(uvicorn 워커)에서 돌 때만 납니다. 기다림이 없는 평범한 CRUD라면 동기 뷰가 더 단순하고 빠릅니다.

</details>

---

## Q2. 서버 두 대와 WebSocket (Day 39)

Goals를 서버 2대로 늘렸습니다. 탭 A는 서버 1, 탭 B는 서버 2의 WebSocket에 붙어 있습니다. 같은 group에 `group_send`했는데 탭 B만 알림을 못 받습니다. 원인과 해결은?

<details>
<summary>정답 보기</summary>

channel layer를 `InMemoryChannelLayer`(프로세스 메모리)로 두었기 때문입니다. 서버 1의 메모리는 서버 2에 붙은 연결을 모릅니다.

```python
CHANNEL_LAYERS = {"default": {
  "BACKEND": "channels_redis.core"
             ".RedisChannelLayer",
  "CONFIG": {"hosts": [REDIS_URL]}}}
```

모든 서버가 같은 **Redis channel layer**를 보면 `group_send`가 서버 경계를 넘어 전달됩니다. Socket.IO의 Redis adapter와 같은 원리입니다. 단, channel layer는 메시지를 저장하지 않아 유실될 수 있으므로 **DB를 진실의 원천**으로 두고 WebSocket은 "바뀌었어" 신호로만 씁니다.

</details>

---

## Q3. sync 워커와 동시 요청 (Day 40)

gunicorn sync 워커 4개입니다. 외부 API를 기다리느라 2초씩 걸리는 요청이 동시에 10개 들어옵니다. 마지막 요청은 약 몇 초 뒤에 응답을 받나요?

<details>
<summary>정답 보기</summary>

**약 6초**입니다. sync 워커는 **워커당 한 번에 요청 하나**만 처리합니다.

```text
0~2초: 요청 1~4
2~4초: 요청 5~8
4~6초: 요청 9~10
```

나머지 요청은 그동안 소켓 대기열(backlog)에서 기다립니다. I/O 대기가 많으면 `gthread` 워커(워커당 스레드 N)나 async 뷰 + uvicorn 워커로 기다림을 겹치게 합니다. 워커 수를 무작정 늘리면 프로세스마다 메모리를 먹으니, 시작은 `2×코어+1`로 하고 부하 테스트로 조정합니다.

</details>

---

## Q4. 40초짜리 뷰와 502 (Day 40)

sync 워커, `timeout=30`입니다. "1년치 CSV 내보내기"가 40초 걸리면 사용자는 무엇을 보고, 올바른 해결은 무엇인가요?

<details>
<summary>정답 보기</summary>

30초에 gunicorn 마스터가 `WORKER TIMEOUT`을 남기고 워커를 **강제 종료**합니다. 응답이 끊기니 앞단 nginx가 **502 Bad Gateway**를 돌려줍니다.

`timeout`을 늘리는 건 미봉책입니다. 그동안 워커 하나가 묶여 다른 요청을 못 받습니다. 올바른 해결은 오래 걸리는 일을 **Celery 작업**으로 넘기는 것입니다.

```python
def export(request):
    t = export_csv.delay(request.user.id)
    return JsonResponse(
        {"task": t.id}, status=202)
```

뷰는 즉시 202(접수됨)를 주고, 완료되면 다운로드 링크를 알림·메일로 보내거나 클라이언트가 상태를 조회합니다.

</details>

---

## Q5. nginx 뒤의 https (Day 41)

nginx가 HTTPS를 받고 gunicorn에는 HTTP로 넘깁니다. `SECURE_SSL_REDIRECT = True`를 켰더니 무한 리다이렉트가 납니다. 왜이고, 무엇을 설정하나요?

<details>
<summary>정답 보기</summary>

nginx에서 TLS를 끝내니(TLS 종료) Django가 받는 요청은 **항상 http**입니다. Django는 "https가 아니네"라며 https로 보내고, 다시 http로 들어오고… 를 반복합니다.

nginx가 원래 프로토콜을 헤더로 알려 주고, Django가 그 헤더를 믿게 합니다.

```nginx
proxy_set_header X-Forwarded-Proto
                 $scheme;
```

```python
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO", "https")
```

이제 `request.is_secure()`가 `True`가 됩니다. Express의 `app.set("trust proxy", 1)`과 같은 역할입니다. 주의: 이 설정은 **프록시가 이 헤더를 항상 덮어쓸 때만** 안전합니다. 클라이언트가 직접 보낸 헤더를 그대로 믿으면 위조됩니다.

</details>

---

## Q6. Dockerfile 줄 순서 (Day 42)

`views.py` 한 줄만 고쳤는데 빌드할 때마다 `pip install`이 처음부터 다시 돕니다. 무엇이 문제인가요?

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
```

<details>
<summary>정답 보기</summary>

Docker는 **줄 단위로 레이어를 캐시**하고, 한 줄이 바뀌면 그 **아래는 전부 다시** 빌드합니다. `COPY . .`는 코드가 바뀔 때마다 달라지므로, 그 아래 `pip install`도 매번 다시 돕니다.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

**잘 안 바뀌는 것 → 자주 바뀌는 것** 순서로 둡니다. 이제 `requirements.txt`가 그대로면 설치 레이어는 캐시를 씁니다. Node에서 `package*.json`만 먼저 복사하고 `npm ci`한 뒤 코드를 복사하는 것과 같습니다. `.dockerignore`로 `.git`, `.venv`를 빼는 것도 함께 합니다.

</details>

---

## Q7. depends_on만으로는 부족하다 (Day 42)

compose에서 `web`에 `depends_on: [db]`를 넣었는데도 첫 실행 때 가끔 `connection refused`로 web이 죽습니다. 왜이고, 어떻게 고치나요?

<details>
<summary>정답 보기</summary>

`depends_on`은 **시작 순서**만 보장합니다. db 컨테이너가 "시작"된 것과 Postgres가 연결을 받을 **준비가 된 것**은 다릅니다. 초기화 중에 web이 붙으면 거절됩니다.

```yaml
db:
  healthcheck:
    test: ["CMD", "pg_isready"]
    interval: 2s
web:
  depends_on:
    db: {condition: service_healthy}
```

healthcheck가 통과해야 web을 띄웁니다. 그래도 운영에선 DB가 잠깐 끊길 수 있으니, 앱도 연결 재시도(`CONN_HEALTH_CHECKS` 등)를 갖추는 게 좋습니다. web 안에서는 `localhost`가 아니라 **서비스 이름 `db`**가 호스트 이름입니다.

</details>

---

## Q8. liveness와 readiness (Day 43)

`/healthz`에서 DB 연결까지 확인하도록 만들고, 이걸 liveness(살아 있나?) 검사로 등록했습니다. DB가 30초 장애를 겪으면 무슨 일이 생기나요?

<details>
<summary>정답 보기</summary>

모든 웹 컨테이너의 liveness가 실패하고, 플랫폼이 멀쩡한 웹 컨테이너를 **전부 재시작**합니다. 재시작 중엔 DB가 살아나도 서비스를 못 하고, 동시에 다시 붙으며 DB에 부하가 몰리는 **연쇄 장애**가 됩니다.

나눠서 둡니다.

```python
def livez(request):
    return HttpResponse("ok")

def readyz(request):
    connection.ensure_connection()
    return HttpResponse("ready")
```

- **liveness** = 프로세스만 확인. 실패하면 재시작.
- **readiness** = DB 등 의존성 확인. 실패하면 **트래픽만 빼고** 재시작은 안 함.

헬스체크 경로는 로그인·`ALLOWED_HOSTS` 검사에 막히지 않는지도 확인합니다.

</details>

---

## Q9. 컬럼 삭제를 무중단으로 (Day 44)

Goal의 `memo` 컬럼을 없애려고 모델에서 필드를 지우고 `makemigrations` → 배포했습니다. 롤링 배포 중 일부 요청이 500을 냅니다. 왜이고, 어떻게 배포해야 하나요?

<details>
<summary>정답 보기</summary>

release 단계에서 migrate가 **먼저** 돌아 컬럼이 사라졌는데, 아직 교체되지 않은 **v1 머신**은 모델에 `memo`가 있어 `SELECT ... memo`를 보냅니다. 없는 컬럼이라 500입니다. 롤링 중엔 두 버전이 같은 DB에서 함께 돕니다.

**expand → contract**로 배포를 나눕니다.

1. **배포 1**: 코드에서 `memo`를 안 쓰고 모델에서도 지웁니다. 마이그레이션은 Django **상태에서만** 필드를 지우고, DB 컬럼은 남기되 `NOT NULL`만 풉니다. 새 코드가 INSERT할 때 memo를 안 넣어도 되게요.

```python
migrations.SeparateDatabaseAndState(
  database_operations=[migrations.RunSQL(
    "ALTER TABLE goals_goal ALTER COLUMN"
    " memo DROP NOT NULL")],
  state_operations=[migrations
    .RemoveField("goal", "memo")])
```

2. **배포 2**: 모든 머신이 새 코드가 된 뒤 실제 컬럼을 지웁니다. 이제 `memo`를 SELECT하는 코드가 어디에도 없습니다.

```python
migrations.RunSQL(
    "ALTER TABLE goals_goal"
    " DROP COLUMN memo")
```

이렇게 하면 어느 순간에도 바로 앞 버전 코드가 같은 DB에서 동작합니다. 배포 1까지는 컬럼과 데이터가 남아 있어 롤백도 안전합니다.

</details>

---

## Q10. 관계에 정보가 붙을 때 (Day 45)

"친구와 함께하는 목표"를 만듭니다. 요구사항: 멤버마다 **역할**(방장/멤버)과 **참여일**이 있고, 같은 사람은 같은 목표에 **한 번만** 들어갈 수 있다. 어떻게 모델링하나요? `ManyToManyField(User)`만 쓰면 왜 부족한가요?

<details>
<summary>정답 보기</summary>

기본 M2M의 중간 테이블은 `goal_id`, `user_id`만 가져서 역할·참여일을 저장할 곳이 없습니다. 관계 자체가 속성을 가지면 **관계를 엔티티로 승격**합니다.

```python
class GoalMember(models.Model):
    goal = models.ForeignKey(Goal,
        on_delete=models.CASCADE,
        related_name="memberships")
    user = models.ForeignKey(User,
        on_delete=models.CASCADE)
```

```python
    role = models.CharField(max_length=10)
    joined_at = models.DateTimeField(
        auto_now_add=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["goal", "user"],
                name="one_membership")]
```

`Goal`에는 `members = ManyToManyField(User, through="GoalMember")`를 달아 둡니다. "한 번만"은 앱 코드의 "있는지 확인 후 추가"로는 동시 요청을 못 막으니 **DB 유일 제약**으로 지킵니다. 함께 체크인하므로 `CheckIn`에도 `user` FK가 생기고, 유일 조건이 `(goal, day)`에서 `(goal, user, day)`로 바뀝니다. 요구사항 한 줄이 FK와 제약을 함께 바꾼다는 점이 핵심입니다.

</details>

---

수고하셨습니다! 몇 개 맞혔는지 채팅으로 알려 주세요. 다음 주에는 오늘 그린 ERD로 **핵심 API를 다듬고**, **부하 테스트·보안 점검(OWASP)**을 거쳐 Goals를 **포트폴리오**로 마무리합니다.
