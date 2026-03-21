# Testing Guide

## 목차
- [테스트 철학](#테스트-철학)
- [환경 설정](#환경-설정)
- [디렉터리 구조](#디렉터리-구조)
- [공통 설정 — conftest.py](#공통-설정--conftestpy)
- [테스트 실행](#테스트-실행)
- [Task별 테스트 현황](#task별-테스트-현황)
- [새 테스트 추가 가이드](#새-테스트-추가-가이드)

---

## 테스트 철학

### 레이어별 테스트 종류

| 레이어 | 테스트 종류 | DB 필요 여부 | 비고 |
|---|---|---|---|
| `domain/entities/` | — | 불필요 | 순수 데이터 구조, 로직 없음 |
| `infrastructure/db/mapper.py` | 단위 테스트 | 불필요 | 순수 Python 변환 함수 |
| `infrastructure/db/repositories/` | DB 통합 테스트 | 필요 | PostgreSQL 전용 기능 포함 |
| `infrastructure/ollama/` | 단위 테스트 | 불필요 | HTTP 클라이언트 mock |
| `application/` (Use Case) | 단위 테스트 | 불필요 | Repository mock 주입 |
| `interfaces/` | E2E 테스트 | 필요 | Task 10에서 진행 |

### SQLite를 쓰지 않는 이유

Repository 구현체는 PostgreSQL 전용 문법을 사용합니다.

```python
# PostgreSQL 전용 — SQLite에서는 동작하지 않음
insert(Model).on_conflict_do_update(...)   # upsert
exists().where(...)                         # EXISTS 절
ARRAY(Integer)                              # 배열 타입
```

따라서 Repository 테스트는 실제 PostgreSQL 컨테이너를 대상으로 실행합니다.

---

## 환경 설정

### 1. 테스트 DB 생성

```bash
# Docker 컨테이너 기동 (없으면 먼저 실행)
docker start discord_summary_db

# 테스트 전용 DB 생성
docker exec -it discord_summary_db \
  psql -U discord_summary -c "CREATE DATABASE discord_summary_test;"
```

### 2. dev 의존성 설치

```bash
uv sync
```

`pyproject.toml`의 dev 그룹에 `pytest`, `pytest-asyncio`가 포함되어 있습니다.

### 3. pytest 설정 (`pyproject.toml`)

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "session"
asyncio_default_test_loop_scope = "session"
```

**`asyncio_mode = "auto"`** — 모든 async 테스트 함수를 자동으로 async 테스트로 인식합니다. `@pytest.mark.asyncio` 데코레이터를 매번 붙이지 않아도 됩니다.

**루프 스코프를 `session`으로 통일하는 이유** — `setup_tables` fixture(session-scoped)에서 생성한 asyncpg DB 커넥션은 해당 이벤트 루프에 귀속됩니다. 테스트 함수가 다른 루프(function-scoped)에서 실행되면 `Future attached to a different loop` 에러가 발생합니다. fixture와 테스트 루프 스코프를 모두 `session`으로 맞춰 하나의 이벤트 루프를 공유합니다. ([pytest-asyncio 공식 문서 참고](https://pytest-asyncio.readthedocs.io/en/stable/reference/configuration.html))

---

## 디렉터리 구조

```
tests/
├── conftest.py                          # 공통 fixture (DB 세션, 테이블 초기화)
│
├── infrastructure/
│   └── db/
│       ├── test_mapper.py               # Task 3: mapper 단위 테스트
│       └── repositories/
│           ├── test_config_repository.py    # Task 3
│           ├── test_server_repository.py    # Task 3
│           └── test_alert_repository.py     # Task 3
│
├── application/                         # Task 5: Use Case 테스트 (예정)
│   ├── test_judge_message_use_case.py
│   ├── test_send_alert_use_case.py
│   └── ...
│
└── infrastructure/
    └── ollama/                          # Task 4: Ollama 클라이언트 테스트 (예정)
        └── test_ollama_client.py
```

> 테스트 파일은 `tests/` 하위에 실제 소스 디렉터리 구조를 그대로 미러링합니다.
> `domain/entities/` → `tests/domain/entities/`, `application/` → `tests/application/` 등.

---

## 공통 설정 — conftest.py

`tests/conftest.py`는 DB 연동 테스트 전체에서 공유하는 fixture를 제공합니다.

```
setup_tables (scope="session", autouse=True)
  └── 테스트 세션 시작 시 테이블 전체 CREATE
  └── 테스트 세션 종료 시 테이블 전체 DROP

session (scope="function")
  └── 각 테스트에 독립된 AsyncSession 제공

clean_tables (scope="function", autouse=True)
  └── 각 테스트 종료 후 별도 커넥션으로 TRUNCATE 실행
  └── RESTART IDENTITY CASCADE — auto-increment ID도 초기화
```

**`clean_tables`가 `session` fixture를 재사용하지 않는 이유**

Repository 내부에서 `session.commit()`이 호출되면 asyncpg 커넥션 상태가 변합니다. 같은 커넥션으로 즉시 TRUNCATE를 시도하면 `another operation is in progress` 에러가 발생합니다. `_engine.begin()`으로 완전히 새로운 커넥션을 열어 클린업합니다.

---

## 테스트 실행

```bash
# 전체 실행
python -m pytest tests/

# 특정 파일만
python -m pytest tests/infrastructure/db/test_mapper.py

# 특정 테스트만
python -m pytest tests/infrastructure/db/repositories/test_config_repository.py::test_set_upsert_overwrites_value

# 상세 출력
python -m pytest tests/ -v
```

---

## Task별 테스트 현황

### Task 3 — Infrastructure DB (완료, 32개)

#### `test_mapper.py` (13개) — 단위 테스트, DB 불필요

mapper.py의 entity ↔ SQLAlchemy model 변환 함수를 검증합니다.

| 테스트 | 검증 내용 |
|---|---|
| `test_*_to_model_excludes_id` | entity → model 시 id 필드가 제외되는지 (DB auto-assign 보장) |
| `test_*_roundtrip` | model → entity 변환 시 모든 필드 값이 보존되는지 |
| `test_feedback_roundtrip_none_note` | Optional 필드(note)가 None인 채로 변환되는지 |

#### `test_config_repository.py` (5개) — DB 통합 테스트

FK 관계 없는 단순 테이블. upsert 동작 검증.

| 테스트 | 검증 내용 |
|---|---|
| `test_get_missing_key_returns_none` | 없는 key 조회 → None 반환 |
| `test_set_and_get` | set() 후 get()으로 값 정확히 반환 |
| `test_set_upsert_overwrites_value` | 같은 key 두 번 set() → 최신 값으로 덮어씀 |
| `test_get_all_empty` | 데이터 없을 때 빈 dict 반환 |
| `test_get_all_returns_all_pairs` | 전체 key-value 쌍 반환 |

#### `test_server_repository.py` (10개) — DB 통합 테스트

discord_id를 PK로 쓰는 Server, Channel의 upsert 및 필터 조회 검증.

| 테스트 | 검증 내용 |
|---|---|
| `test_server_upsert_updates_name` | 같은 discord_id로 재저장 시 name 업데이트 |
| `test_server_upsert_updates_is_active` | 같은 discord_id로 재저장 시 is_active 업데이트 |
| `test_server_get_all_active_excludes_inactive` | is_active=False 서버 필터링 |
| `test_channel_get_watched_excludes_unwatched` | is_watched=False 채널 필터링 |
| `test_channel_update_watched` | update_watched() 후 DB에 상태 반영 확인 |

#### `test_alert_repository.py` (4개) — DB 통합 테스트

쿨다운 로직의 핵심인 `exists_recent_by_channel()` 검증.
Alert → AILog → MessageBatch → Message 4단계 JOIN 경로를 포함합니다.

| 테스트 | 검증 내용 |
|---|---|
| `test_alert_save_assigns_id` | save() 후 DB가 id를 할당하는지 |
| `test_exists_recent_returns_true` | 30분 이내 Alert 존재 → True |
| `test_exists_recent_returns_false_when_alert_is_old` | since 이전 Alert만 존재 → False (쿨다운 만료) |
| `test_exists_recent_returns_false_for_different_channel` | 다른 채널의 Alert → False (채널 필터 동작 확인) |

---

### Task 4 — Infrastructure Ollama (예정)

#### `test_prompt.py` — 단위 테스트, DB/HTTP 불필요

| 테스트 | 검증 내용 |
|---|---|
| `test_prompt_contains_context` | 컨텍스트 메시지가 프롬프트에 포함되는지 |
| `test_prompt_contains_trigger_message` | 트리거 메시지가 프롬프트에 포함되는지 |

#### `test_ollama_client.py` — 단위 테스트, httpx mock

| 테스트 | 검증 내용 |
|---|---|
| `test_parse_answer_true` | 응답에서 answer=True 파싱 |
| `test_parse_answer_false` | 응답에서 answer=False 파싱 |
| `test_parse_reason` | 응답에서 reason 문자열 추출 |
| `test_timeout_raises` | 타임아웃 시 적절한 예외 발생 |
| `test_connection_error_raises` | 연결 실패 시 적절한 예외 발생 |

---

### Task 5 — Application Use Case (예정)

Repository를 `AsyncMock`으로 주입. DB 불필요.

#### `test_judge_message_use_case.py`

| 테스트 | 검증 내용 |
|---|---|
| `test_answer_true_calls_save_alert` | answer=True → AlertRepository.save() 호출 |
| `test_answer_false_skips_alert` | answer=False → AlertRepository.save() 미호출 |
| `test_cooldown_active_skips_ollama` | 쿨다운 중 → Ollama 클라이언트 호출 건너뜀 |

#### `test_send_alert_use_case.py`

| 테스트 | 검증 내용 |
|---|---|
| `test_dm_sent_with_correct_content` | DM 발송 시 올바른 내용 포함 여부 |

#### `test_manage_config_use_case.py`

| 테스트 | 검증 내용 |
|---|---|
| `test_set_and_get_config` | config 저장 후 조회 시 정확한 값 반환 |

#### `test_get_stats_use_case.py`

| 테스트 | 검증 내용 |
|---|---|
| `test_stats_correct_counts` | AILog 수, Alert 수 등 통계 집계 결과 검증 |

---

### Task 6 — discord.py 봇 (예정)

순수 Python 로직만 테스트. discord.py mock 불필요.

#### `test_message_buffer.py`

| 테스트 | 검증 내용 |
|---|---|
| `test_flush_on_max_messages` | 최대 메시지 수 초과 시 flush 트리거 |
| `test_flush_on_max_minutes` | 최대 시간 초과 시 flush 트리거 |
| `test_channels_are_independent` | 채널A의 flush가 채널B에 영향 없는지 |

#### `test_cooldown_manager.py`

| 테스트 | 검증 내용 |
|---|---|
| `test_blocks_during_cooldown` | 쿨다운 중 동일 채널 중복 차단 |
| `test_allows_after_cooldown_expires` | 쿨다운 만료 후 재허용 |

---

### Task 7 — FastAPI 백엔드 (예정)

FastAPI `TestClient` 사용.

| 테스트 | 검증 내용 |
|---|---|
| `test_get_config_200` | GET /api/config → 200 OK |
| `test_set_config_invalid_422` | 잘못된 요청 → 422 |
| `test_get_logs_200` | GET /api/logs → 200 OK |
| `test_get_nonexistent_log_404` | 존재하지 않는 log_id → 404 |
| `test_post_feedback_200` | POST /api/feedback → 200 OK |

---

## 새 테스트 추가 가이드

### DB 불필요한 단위 테스트 (mapper, Use Case 등)

`conftest.py`의 `session`, `clean_tables` fixture에 의존하지 않으므로 별도 설정 없이 작성합니다.

```python
# tests/application/test_judge_message_use_case.py
from unittest.mock import AsyncMock
from application.use_cases.judge_message import JudgeMessageUseCase

async def test_judge_returns_alert_when_answer_is_true():
    mock_message_repo = AsyncMock()
    mock_ai_log_repo = AsyncMock()
    # ...Repository를 mock으로 주입
    use_case = JudgeMessageUseCase(
        message_repo=mock_message_repo,
        ai_log_repo=mock_ai_log_repo,
    )
    result = await use_case.execute(...)
    assert result.should_alert is True
```

### DB 필요한 통합 테스트 (새 Repository 추가 시)

1. `tests/infrastructure/db/repositories/test_<name>_repository.py` 파일 생성
2. `session` fixture를 인자로 받아 Repository 인스턴스 생성
3. FK 선행 데이터가 필요하면 별도 fixture로 분리 (`chain` 패턴 참고)

```python
# 기본 패턴
import pytest
from infrastructure.db.repositories.foo_repository import PostgresFooRepository

@pytest.fixture
def repo(session):
    return PostgresFooRepository(session)

async def test_save(repo):
    result = await repo.save(...)
    assert result.id is not None
```

### 복잡한 선행 데이터가 필요한 경우

`test_alert_repository.py`의 `chain` fixture 패턴을 사용합니다.
필요한 모든 선행 데이터를 하나의 fixture로 묶고, 테스트에 필요한 ID만 반환합니다.

```python
@pytest.fixture
async def chain(session):
    # 선행 데이터 전체 생성
    server = await PostgresServerRepository(session).save(...)
    channel = await PostgresChannelRepository(session).save(...)
    # ...
    return {"channel_id": channel.discord_id, "ai_log_id": ai_log.id}

async def test_something(repo, chain):
    result = await repo.some_method(chain["channel_id"])
    assert result is True
```
