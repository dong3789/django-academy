// 전체 로드맵 (12주 × 주5일 = 60일). CS 트랙은 각 주에 끼워 넣음.
window.CURRICULUM = [
 {w:1,t:"Python 기초 (JS 비교)",cs:"자료구조: 배열/해시/복잡도",days:["환경 구축(uv/venv) + 핵심 문법 JS 비교","컬렉션: list/dict/set/tuple, 컴프리헨션","함수·스코프·클로저, *args/**kwargs","클래스·던더 메서드·데이터클래스","모듈/패키지·예외·파일 I/O + CS: 해시테이블 내부"]},
 {w:2,t:"Python 심화",cs:"OS: 프로세스·스레드·GIL",days:["이터레이터·제너레이터·yield from","데코레이터(인자·functools.wraps)","컨텍스트 매니저·contextlib","메모리 모델: 참조카운트·GC·가변성 + GIL","타입 힌트·mypy·Protocol·asyncio 맛보기"]},
 {w:3,t:"Django 코어 I",cs:"네트워킹: HTTP/TCP/DNS",days:["프로젝트 구조·settings·요청 생명주기","모델·필드·관계(FK/M2M)","마이그레이션 깊게(데이터 마이그레이션·충돌)","ORM 쿼리: QuerySet 지연평가·F/Q·annotate","URL·FBV vs CBV·제네릭 뷰"]},
 {w:4,t:"Django 코어 II",cs:"DB: 정규화·키·제약조건",days:["템플릿·상속·컨텍스트 프로세서","Forms·ModelForm·검증","인증/인가: User 커스텀·권한·세션","Admin 커스터마이징","미들웨어·시그널(언제 쓰지 말아야 하나)"]},
 {w:5,t:"Django REST Framework",cs:"네트워킹: REST·HTTP 캐싱·CORS",days:["Serializer 심화(중첩·검증)","APIView·ViewSet·Router","인증: Session/Token/JWT","권한·Throttling·Pagination·Filtering","API 버저닝·OpenAPI 문서화(drf-spectacular)"]},
 {w:6,t:"ORM 최적화",cs:"DB: 인덱스(B-Tree)·실행계획",days:["N+1: select_related/prefetch_related","인덱스 설계·EXPLAIN 읽기","트랜잭션·atomic·select_for_update","격리수준·락·데드락","raw SQL·집계 최적화·bulk 연산"]},
 {w:7,t:"테스트",cs:"알고리즘: 정렬·탐색·이분탐색",days:["pytest·pytest-django 기초","fixture·factory_boy","API 테스트·모킹","통합테스트·커버리지·CI(GitHub Actions)","TDD 실습 + 코딩테스트 풀이"]},
 {w:8,t:"비동기·캐싱",cs:"OS: 동시성·락·큐",days:["Redis 자료구조·캐시 전략","Django 캐시 프레임워크·무효화","Celery 아키텍처·브로커","재시도·멱등성·beat 스케줄","Django async views·Channels 개요"]},
 {w:9,t:"배포",cs:"네트워킹: TLS·로드밸런싱·리버스 프록시",days:["WSGI/ASGI·gunicorn 워커 모델","nginx 설정·정적파일","Docker·멀티스테이지·compose","환경변수·보안 설정·로깅/모니터링","클라우드 배포 실습(AWS/Fly 등)"]},
 {w:10,t:"실전 프로젝트",cs:"알고리즘: 그래프·DP",days:["요구사항·ERD 설계","핵심 API 구현","성능 튜닝·부하테스트(locust)","보안 점검(OWASP)","회고·README·포트폴리오화"]},
 {w:11,t:"시스템 디자인",cs:"시스템 디자인: 확장성·샤딩·CAP",days:["확장성 기본: 수평/수직·무상태","DB 복제·샤딩·읽기 분산","메시지 큐·이벤트 기반","설계 실습: URL 단축기","설계 실습: 피드/알림 시스템"]},
 {w:12,t:"면접 대비",cs:"CS 총정리",days:["Python 면접 질문 총정리","Django/DRF 면접 질문 총정리","DB·네트워크·OS 총정리","코딩테스트 모의","모의 면접·이력서 리뷰"]}
];
