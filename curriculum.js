// 전체 로드맵 (12주 × 주5일 = 60일).
// 1–3주차: Goals 대시보드를 만들며 문법·Django를 "필요할 때" 학습.
// CS 심화는 본문 접기(면접용) + 11–12주차에 모음.
window.CURRICULUM = [
 {w:1,t:"Goals 대시보드 Kickoff · 만들며 배우기",cs:"면접용 CS는 접기 섹션 · 본격 정리는 Week 11–12",days:[
   "Django 설치 + Goals 앱 뼈대 + Python 최소 문법",
   "Goal 데이터를 list/dict로 다루기",
   "진행률 계산 함수·스코프",
   "Goal 모델·클래스 맛보기",
   "마이그레이션·Admin·첫 목록 화면"
 ]},
 {w:2,t:"Goals 기능 확장 · 나는 이미 만든다",cs:"면접용: 이터레이터·GIL은 접기",days:[
   "통계·진행률 뷰 (제너레이터 맛보기)",
   "Goal 추가/수정 Form",
   "템플릿 상속·대시보드 UI",
   "로그인: 내 Goals만 보기",
   "간단 배포 맛보기 + 1·2주 회고"
 ]},
 {w:3,t:"Django 코어로 Goals 다듬기",cs:"면접용: HTTP/TCP는 접기",days:[
   "요청 생명주기·settings 정리",
   "모델 관계(FK/M2M)·태그·체크인",
   "마이그레이션 깊게(데이터·충돌)",
   "ORM: QuerySet·F/Q·annotate로 통계",
   "URL·FBV vs CBV·제네릭 뷰"
 ]},
 {w:4,t:"Forms·인증·Admin 실전",cs:"면접용: DB 정규화는 접기",days:[
   "템플릿·컨텍스트 프로세서",
   "Forms·ModelForm·검증 심화",
   "User 커스텀·권한·세션",
   "Admin 커스터마이징",
   "미들웨어·시그널(언제 쓰지 말까)"
 ]},
 {w:5,t:"DRF로 Goals API",cs:"면접용: REST·CORS는 접기",days:[
   "Serializer 심화(중첩·검증)",
   "APIView·ViewSet·Router",
   "인증: Session/Token/JWT",
   "권한·Throttling·Pagination·Filtering",
   "API 버저닝·OpenAPI(drf-spectacular)"
 ]},
 {w:6,t:"ORM 최적화 (Goals 쿼리)",cs:"면접용: 인덱스·EXPLAIN은 접기",days:[
   "N+1: select_related/prefetch_related",
   "인덱스 설계·EXPLAIN 읽기",
   "트랜잭션·atomic·select_for_update",
   "격리수준·락·데드락",
   "raw SQL·집계·bulk 연산"
 ]},
 {w:7,t:"테스트",cs:"면접용: 정렬·탐색은 Week 12",days:[
   "pytest·pytest-django 기초",
   "fixture·factory_boy",
   "API 테스트·모킹",
   "통합테스트·커버리지·CI",
   "TDD 실습 + 코딩테스트 맛보기"
 ]},
 {w:8,t:"캐시·비동기 (리마인더)",cs:"면접용: 동시성·큐는 접기",days:[
   "Redis·캐시 전략",
   "Django 캐시·무효화",
   "Celery 아키텍처·브로커",
   "재시도·멱등성·beat 스케줄",
   "async views·Channels 개요"
 ]},
 {w:9,t:"배포",cs:"면접용: TLS·LB는 접기",days:[
   "WSGI/ASGI·gunicorn 워커",
   "nginx·정적파일",
   "Docker·멀티스테이지·compose",
   "환경변수·보안·로깅/모니터링",
   "클라우드 배포(AWS/Fly 등)"
 ]},
 {w:10,t:"포트폴리오 완성",cs:"면접용: 그래프·DP는 Week 12",days:[
   "요구사항·ERD 재설계",
   "핵심 API·화면 다듬기",
   "성능 튜닝·부하테스트",
   "보안 점검(OWASP)",
   "회고·README·포트폴리오화"
 ]},
 {w:11,t:"시스템 디자인 + CS 집중",cs:"시스템 디자인·확장성·CAP",days:[
   "확장성: 수평/수직·무상태",
   "DB 복제·샤딩·읽기 분산",
   "메시지 큐·이벤트 기반",
   "설계 실습: URL 단축기",
   "설계 실습: 피드/알림"
 ]},
 {w:12,t:"면접 대비 (CS·Django 총정리)",cs:"CS·코딩테스트·모의면접",days:[
   "Python 면접 질문 총정리",
   "Django/DRF 면접 질문 총정리",
   "DB·네트워크·OS 총정리",
   "코딩테스트 모의",
   "모의 면접·이력서 리뷰"
 ]}
];
