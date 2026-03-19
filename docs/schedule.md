# (가) 프로젝트: Discord Summary 개발 일정

## 📅 Phase 1 - 기반 작업
Task 1: 프로젝트 세팅
  - 폴더 구조 생성
  - Poetry/venv 세팅
  - PostgreSQL 로컬 설치
  - DB 스키마 작성 (Alembic 마이그레이션)

Task 2: Domain 레이어
  - 엔티티 작성
    (Message, AILog, Alert, Feedback)
  - Repository 인터페이스 작성

Task 3: Infrastructure - DB
  - PostgreSQL 연결 (SQLAlchemy async)
  - Repository 구현체 작성
  - 단위 테스트

Task 4: Infrastructure - Ollama
  - Ollama 클라이언트 작성
  - 프롬프트 템플릿 관리
  - 단위 테스트

Task 5: Application 레이어
  - JudgeMessageUseCase
  - SendAlertUseCase
  - ManageConfigUseCase
  - GetStatsUseCase
---
## 📅 Phase 2 - 인터페이스 작업
Task 6: discord.py 봇
  - on_message 이벤트
  - 메시지 버퍼
  - 쿨다운 매니저
  - DM 발송

Task 7: FastAPI 백엔드
  - /api/config
  - /api/logs
  - /api/stats
  - /api/feedback

Task 8~9: React 대시보드
  - 대시보드 홈 (통계)
  - 감시 설정 페이지
  - AI 로그 페이지
  - 품질 검증 페이지

Task 10: 통합 테스트
  - 봇 → Ollama → DB → API → React
  - 엣지 케이스 테스트
  - 버그 수정
---
## 📅 Phase 3 - 마무리
Task 11: Docker 세팅
  - 각 서비스 Dockerfile
  - docker-compose.yml
  - 로컬에서 docker-compose up 테스트

Task 12: Oracle 배포
  - VM 인스턴스 생성 (자원 생기면)
  - Ubuntu 세팅
  - docker-compose 배포

Task 13: 마무리
  - 최종 문서화