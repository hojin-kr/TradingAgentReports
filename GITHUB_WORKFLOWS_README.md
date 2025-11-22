# GitHub Actions Workflows for Report Processing

## 🚀 Available Workflows

### 0. `generate-coin-reports.yml` - 일일 코인 리포트 생성
Binance 24h USDT 거래대금 기준 상위 코인(기본 10개)에 대해 `gen_coin_reports.py`를 실행하여 `coin_reports/`와 `coin_eval_results/`를 갱신합니다.

**트리거:**
- 매일 00:30 UTC (schedule)
- 수동 실행 (`workflow_dispatch`) – `date`, `tickers`, `top_count` 입력 가능

**출력:**
- `coin_reports/YYYY-MM-DD/BUY|HOLD|SELL/SYMBOL/LOCALE/*.md`
- `coin_eval_results/SYMBOL/CoinTradingAgents_logs/full_states_log_<DATE>.json`

### 1. `postprocess-news-reports.yml` - 뉴스 리포트 구조화
뉴스 리포트를 구조화된 일일 거래 인텔리전스 형태로 변환합니다.

**트리거:**
- 수동 실행 (workflow_dispatch)
- 자동 실행 (generate-reports workflow 완료 후)

**입력 매개변수:**
- `date`: 처리할 날짜 (YYYY-MM-DD)
- `dry_run`: 드라이 런 실행 (기본값: false)
- `force`: 강제 재처리 (기본값: false)

**처리 내용:**
- `news_report.md` → `structured_news_report.md`
- 6개 구조화된 섹션으로 변환
- Executive Snapshot, Macro Backdrop, Catalysts, Technical Levels, Trading Scenarios

### 2. `postprocess-reports.yml` - 투자 결정 리포트 간소화
복잡한 투자 결정 리포트를 일반 투자자용으로 간소화합니다.

**트리거:**
- 수동 실행 (workflow_dispatch)  
- 자동 실행 (generate-reports workflow 완료 후)

**처리 내용:**
- `final_trade_decision.md` → `simplified_final_trade_decision.md`
- 기술적 용어 간소화
- 일반 투자자 접근성 향상

### 3. `postprocess-all-reports.yml` - 모든 리포트 통합 처리
투자 결정과 뉴스 리포트를 모두 처리하는 통합 워크플로우입니다.

**트리거:**
- 수동 실행 (workflow_dispatch)
- 자동 실행 (generate-reports workflow 완료 후)

**입력 매개변수:**
- `date`: 처리할 날짜 (YYYY-MM-DD)
- `dry_run`: 드라이 런 실행 (기본값: false)
- `force`: 강제 재처리 (기본값: false)
- `process_investment`: 투자 리포트 처리 여부 (기본값: true)
- `process_news`: 뉴스 리포트 처리 여부 (기본값: true)

## 🔧 사용법

### 수동 실행

1. **GitHub 웹사이트에서:**
   - Actions 탭으로 이동
   - 원하는 워크플로우 선택
   - "Run workflow" 버튼 클릭
   - 매개변수 입력 후 실행

2. **GitHub CLI 사용:**
```bash
# 뉴스 리포트만 처리
gh workflow run postprocess-news-reports.yml -f date=2025-09-22

# 모든 리포트 처리 (드라이 런)
gh workflow run postprocess-all-reports.yml -f date=2025-09-22 -f dry_run=true

# 강제 재처리
gh workflow run postprocess-all-reports.yml -f date=2025-09-22 -f force=true
```

### 자동 실행

`generate-reports.yml` 혹은 `generate-coin-reports.yml` 워크플로우가 성공적으로 완료되면 후속 처리 워크플로우가 자동으로 실행됩니다.

## 📊 품질 검사

각 워크플로우는 처리된 리포트의 품질을 자동으로 검사합니다:

### 뉴스 리포트 품질 기준:
- ✅ 필수 섹션 4/5개 이상 포함
- ✅ 불릿 포인트 5개 이상
- ✅ 구체적 가격 언급 2회 이상
- ✅ 거래 시나리오 포함
- ✅ 적절한 길이 (500-3000 단어)

### 투자 리포트 품질 기준:
- ✅ Flesch 가독성 점수 ≥60
- ✅ 학년 수준 ≤12
- ✅ 적절한 길이와 구조

## 🔐 필수 설정

### GitHub Secrets
다음 시크릿이 설정되어야 합니다:

```
OPENAI_API_KEY: OpenAI API 키 (필수)
```

### 파일 요구사항
워크플로우 실행 전 다음 파일들이 존재해야 합니다:

```
├── news_report_template_simple.xml     # 뉴스 리포트 템플릿
├── report_template.xml                 # 투자 리포트 템플릿  
├── postprocess_news_reports.py         # 뉴스 리포트 처리 스크립트
└── postprocess_final_reports.py        # 투자 리포트 처리 스크립트
```

## 📁 출력 구조

처리된 파일들은 다음과 같은 구조로 저장됩니다:

```
reports/
  YYYY-MM-DD/
    BUY|HOLD|SELL/
      TICKER/
        EN/
          ├── news_report.md                    # 원본 뉴스 리포트
          ├── structured_news_report.md         # 구조화된 뉴스 리포트
          ├── final_trade_decision.md           # 원본 투자 결정
          └── simplified_final_trade_decision.md # 간소화된 투자 결정
```

코인 리포트는 다음과 같이 저장됩니다:

```
coin_reports/
  YYYY-MM-DD/
    BUY|HOLD|SELL/
      SYMBOL/
        EN/
          market_report.md
          sentiment_report.md
          news_report.md
          trader_investment_plan.md
          final_trade_decision.md
coin_eval_results/
  SYMBOL/
    CoinTradingAgents_logs/
      full_states_log_YYYY-MM-DD.json
```

## 🎯 워크플로우 선택 가이드

- **뉴스 리포트만 처리**: `postprocess-news-reports.yml`
- **투자 결정만 처리**: `postprocess-reports.yml`  
- **모든 리포트 처리**: `postprocess-all-reports.yml` (권장)
- **테스트/검토**: 모든 워크플로우에서 `dry_run=true` 사용

## 🔄 자동화 흐름

```
1. generate-reports.yml 또는 generate-coin-reports.yml 실행
   ↓
2. 리포트 생성 완료
   ↓  
3. postprocess-all-reports.yml 자동 트리거
   ↓
4. 투자 결정 + 뉴스 리포트 동시 처리
   ↓
5. 품질 검사 실행
   ↓
6. 처리된 파일 커밋 & 푸시
```

이 자동화된 흐름을 통해 매일 일관된 품질의 구조화된 리포트를 생성할 수 있습니다.