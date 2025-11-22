# Workflow 실행 순서 구성

## 🔄 업데이트된 실행 순서

뉴스 리포트 처리 워크플로우가 **투자 리포트 처리 완료 후**에 실행되도록 구성했습니다.  
주식/지수 리포트를 생성하는 `Generate daily TradingAgents reports` 뿐 아니라, 코인 리포트를 생성하는 `Generate daily CoinTradingAgents reports`도 동일한 후속 파이프라인을 트리거하도록 연결되어 있습니다.

### 자동 실행 흐름

```
1. Generate daily TradingAgents reports 또는 Generate daily CoinTradingAgents reports
   ↓ (완료 시 자동 트리거)
2. Post-process Investment Reports  
   ↓ (완료 시 자동 트리거)
3. Post-process News Reports
   ↓
4. 모든 처리 완료
```

## 📋 워크플로우 옵션

### Option 1: 순차 실행 워크플로우 (권장)
**파일**: `postprocess-sequential.yml`

**특징**:
- 단일 워크플로우에서 순차적으로 처리
- 투자 리포트 → 뉴스 리포트 순서 보장
- 각 단계별 상태 추적
- 실패 시에도 다음 단계 진행 가능

**실행 순서**:
```
Job 1: process-investment-reports
  ├── 투자 결정 리포트 처리
  ├── simplified_*.md 생성
  └── 커밋 & 푸시

Job 2: process-news-reports (depends on Job 1)
  ├── 뉴스 리포트 처리  
  ├── structured_*.md 생성
  └── 커밋 & 푸시

Job 3: create-summary
  └── 종합 결과 요약
```

### Option 2: 분리된 워크플로우
**파일**: `postprocess-reports.yml` → `postprocess-news-reports.yml`

**특징**:
- 각각 독립적인 워크플로우
- 투자 리포트 워크플로우 완료 후 뉴스 리포트 워크플로우 자동 트리거
- 개별 모니터링 가능

**실행 순서**:
```
Workflow 1: Post-process Investment Reports
  └── 투자 리포트 처리 완료
      ↓ (workflow_run 트리거)
Workflow 2: Post-process News Reports  
  └── 뉴스 리포트 처리 완료
```

### Option 3: 통합 워크플로우
**파일**: `postprocess-all-reports.yml`

**특징**:
- 투자 리포트 워크플로우 완료 후 트리거
- 단일 워크플로우에서 두 종류 모두 처리
- 선택적 처리 옵션 제공

## 🚀 권장 사용법

### 자동 실행 (권장)
**순차 실행 워크플로우** 사용:
- 가장 안정적이고 예측 가능한 실행 순서
- 단일 워크플로우에서 모든 처리 완료
- 각 단계별 성공/실패 상태 명확히 추적

### 수동 실행
```bash
# 순차 실행 워크플로우 (권장)
gh workflow run postprocess-sequential.yml -f date=2025-09-22

# 개별 실행 (테스트용)
gh workflow run postprocess-reports.yml -f date=2025-09-22
# 위 완료 후 자동으로 뉴스 리포트 처리됨
```

## 📊 트리거 설정 변경사항

### 변경 전
```yaml
workflow_run:
  workflows: ["Generate daily TradingAgents reports", "Generate daily CoinTradingAgents reports"]
  types: [completed]
```

### 변경 후
```yaml
workflow_run:
  workflows: ["Post-process Investment Reports"]
  types: [completed]
```

## 🔧 설정된 워크플로우들

### 1. `postprocess-sequential.yml` ⭐ (신규, 권장)
- **트리거**: `Generate daily TradingAgents reports` 완료 후
- **실행**: 투자 리포트 → 뉴스 리포트 순차 처리
- **장점**: 가장 안정적이고 명확한 실행 순서

### 2. `postprocess-news-reports.yml`
- **트리거**: `Post-process Investment Reports` 완료 후
- **실행**: 뉴스 리포트만 처리

### 3. `postprocess-all-reports.yml`
- **트리거**: `Post-process Investment Reports` 완료 후  
- **실행**: 투자 + 뉴스 리포트 통합 처리

### 4. `postprocess-reports.yml` (기존)
- **트리거**: `Generate daily TradingAgents reports` 완료 후
- **실행**: 투자 리포트만 처리

## 🎯 최종 실행 흐름

### 완전 자동화 흐름
```
매일 자동:
Generate (Stocks or Coins) Reports → Process Investment Reports → Process News Reports → 완료
```

### 수동 실행 흐름  
```
수동 트리거:
postprocess-sequential.yml → 투자 + 뉴스 리포트 순차 처리 → 완료
```

이제 **투자 리포트 처리가 완료된 후에 뉴스 리포트 처리가 시작**되어 올바른 순서로 실행됩니다! 🎉