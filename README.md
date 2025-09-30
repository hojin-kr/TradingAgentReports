## TradingAgents 리포트 생성기

트레이딩 관련 에이전트 파이프라인으로부터 시장/뉴스/심리/기초체력 분석을 수집하고, 날짜/티커/언어별 Markdown 리포트를 생성합니다. 생성된 문서는 최종 의사결정(BUY/HOLD/SELL)에 따라 폴더가 자동 분기되며, **LLM 기반 후처리를 통해 일반 투자자도 이해하기 쉬운 단순화된 보고서**를 자동 생성합니다.

### 🎯 주요 기능
- **📊 전문 분석 리포트 생성**: 다중 에이전트를 통한 종합적 투자 분석
- **🤖 자동 후처리 시스템**: LLM을 활용한 보고서 단순화 및 표준화
- **⚡ GitHub Actions 자동화**: 매일 자동 리포트 생성 및 후처리
- **📈 품질 검증**: 가독성 분석 및 품질 보증 시스템
- **🔄 중복 실행 방지**: 효율적인 처리를 위한 스마트 스킵 기능

### 주요 구성
- `tradingagents/graph/trading_graph.py`: 에이전트 그래프의 진입점
- `gen_reports.py`: 그래프 실행(또는 저장 로그) → Markdown 리포트 생성
- `postprocess_final_reports.py`: **새로운 LLM 기반 후처리 스크립트**
- `report_template.xml`: **표준화된 보고서 구조 정의 템플릿**
- `tradingagents/default_config.py`: 기본 설정(LLM, 디렉토리 경로 등)
- `reports/`: 날짜/의사결정/티커/언어별 결과 저장 루트
- `.github/workflows/`: 자동화된 리포트 생성 및 후처리 워크플로우

## 빠른 시작
```bash
python -V  # Python 3.10+ 권장

python -m venv .venv
source .venv/bin/activate

pip install -U pip
pip install -r requirements.txt
```

### 필수 환경 변수
- `OPENAI_API_KEY`: OpenAI 또는 호환 API 사용 시 필요. 미설정 시 일부 기능(사후 편집/번역, OpenAI 기반 뉴스/펀더멘털)이 비활성화되거나 실패할 수 있습니다.

### 선택 환경 변수
- `TRADINGAGENTS_RESULTS_DIR`: 결과/로그 저장 기본 경로 변경 시 사용. 미지정 시 `./results`.

## 사용법

### 1) 그래프 실행으로 리포트 생성
에이전트를 실제로 실행해서 해당 날짜의 분석을 생성합니다.
```bash
python gen_reports.py \
  --ticker NVDA \
  --date 2025-09-03 \
  --locales EN,KO       # 콤마로 다중 언어 지정 (기본 EN)
```

### 2) 저장된 로그에서 리포트만 재생성
이전에 실행해 저장된 `eval_results/<TICKER>/.../full_states_log_<DATE>.json`을 사용합니다.
```bash
python gen_reports.py \
  --ticker NVDA \
  --date 2025-09-03 \
  --locales EN \
  --from-log
```

### 3) **새로운 LLM 기반 후처리 (권장)**
복잡한 투자 분석을 일반 투자자가 이해하기 쉬운 형태로 자동 변환합니다.
```bash
export OPENAI_API_KEY=...  # 필수
python postprocess_final_reports.py --date 2025-09-03
```

**주요 기능:**
- **난이도 조절**: 고등학교 수준의 읽기 난이도로 단순화
- **표준화**: XML 템플릿 기반 일관된 보고서 구조
- **핵심 추출**: 일반 투자자에게 필요한 정보만 선별
- **중복 방지**: 이미 처리된 파일은 자동으로 건너뛰기

**추가 옵션:**
```bash
# 처리될 파일 미리보기 (실제 처리 안함)
python postprocess_final_reports.py --date 2025-09-03 --dry-run

# 이미 처리된 파일도 강제로 재처리
python postprocess_final_reports.py --date 2025-09-03 --force

# 사용자 정의 템플릿 사용
python postprocess_final_reports.py --date 2025-09-03 --template custom_template.xml
```

## 출력 구조
리포트는 최종 의사결정 텍스트의 말미를 스캔해 BUY/HOLD/SELL 중 하나로 라우팅됩니다.
```
reports/
  2025-09-03/
    BUY|HOLD|SELL/
      NVDA/
        EN/
          market_report.md
          sentiment_report.md
          news_report.md
          fundamentals_report.md
          investment_plan.md
          trader_investment_plan.md
          final_trade_decision.md
          simplified_final_trade_decision.md  # 🆕 단순화된 보고서
          complete.md        # 모든 섹션 합본
        KO/
          ... 동일 파일명 ...
```

### 🆕 단순화된 보고서 구조
후처리를 통해 생성되는 `simplified_final_trade_decision.md`는 다음과 같은 표준 구조를 가집니다:

```markdown
# Investment Report: NVDA

## Executive Summary
간단명료한 2-3문장 요약 (투자 결정, 주요 이유, 핵심 리스크)

## Investment Decision
**Decision: BUY - Confidence: High**
명확한 추천과 신뢰도, 간단한 근거

## Key Reasons Supporting This Decision
1. **시장 리더십**: 기술 우위와 시장 지배력
2. **성장 동력**: 수요 증가와 매출 성장 전망
3. **재무 건전성**: 안정적인 수익성과 현금 흐름

## Risks To Watch
- **밸류에이션**: 높은 주가로 인한 조정 위험
- **시장 변화**: 경쟁 심화 및 규제 리스크
```

## 설정 커스터마이징
- 기본 설정은 `tradingagents/default_config.py`를 참고하세요.
  - `llm_provider`, `deep_think_llm`, `quick_think_llm`, `backend_url` 등 LLM 관련 설정
  - `results_dir`: `TRADINGAGENTS_RESULTS_DIR` 환경 변수로도 변경 가능
  - `data_dir`: 오프라인 데이터(예: SimFin, Finnhub 가공 데이터) 루트. 필요 시 경로를 프로젝트 로컬 경로로 수정하세요.
- 온라인 도구가 기본 활성화되어 있어(`online_tools=True`) OpenAI/Google News/Yahoo Finance 등을 사용합니다. 오프라인 데이터가 없더라도 리포트 생성은 동작하되, 일부 섹션은 비어 있을 수 있습니다.

## 🚀 자동화 (GitHub Actions)

### 매일 자동 실행
이 프로젝트는 GitHub Actions를 통해 완전 자동화된 리포트 생성 파이프라인을 제공합니다:

1. **매일 오전 12:15 UTC**: `generate-reports.yml` 워크플로우가 주요 종목들의 리포트를 자동 생성
2. **자동 후처리**: 리포트 생성 완료 시 `postprocess-reports.yml`이 자동 실행되어 단순화된 보고서 생성
3. **품질 검증**: 가독성 분석 및 구조 검증 자동 실행
4. **자동 커밋**: 생성된 모든 파일들이 자동으로 저장소에 커밋

### 수동 실행
GitHub Actions 탭에서 다음과 같이 수동 실행도 가능합니다:
- **Generate daily TradingAgents reports**: 특정 날짜/종목 리포트 생성
- **Post-process Investment Reports**: 후처리만 별도 실행 (dry-run, force 옵션 지원)

### 현재 처리 현황
- **총 71개의 단순화된 보고서** 생성 완료 (2025-09-10 ~ 2025-09-16)
- 주요 종목: AAPL, AMD, GOOGL, META, NFLX, NVDA, PLTR, QQQ, SPY, TSLA 등
- 모든 보고서가 고등학교 수준의 읽기 난이도로 최적화됨

## 트러블슈팅
- **OpenAI 인증 오류**: `OPENAI_API_KEY`가 설정되어 있는지 확인하세요.
- **후처리 스킵**: 이미 처리된 파일은 자동으로 건너뜁니다. 강제 재처리하려면 `--force` 옵션을 사용하세요.
- **템플릿 오류**: `report_template.xml` 파일이 올바른 XML 형식인지 확인하세요.
- **데이터 경로 오류**: `data_dir`가 로컬 환경에 맞지 않으면 오프라인 도구 결과가 비어 있을 수 있습니다.
- **뉴스/크롤링 제한**: Google News는 비공식 스크래핑으로, 레이트 리밋에 걸릴 수 있습니다.
- **GitHub Actions 권한**: 워크플로우가 저장소에 커밋하려면 `contents: write` 권한이 필요합니다.

## 📊 성과 및 품질 지표

### 가독성 개선 효과
- **원본 보고서**: 대학 수준의 복잡한 금융 분석 (Flesch Score ~30-40)
- **단순화된 보고서**: 고등학교 수준의 읽기 쉬운 내용 (Flesch Score 60+)
- **길이 최적화**: 평균 70% 이상 압축, 최대 800단어 제한

### 표준화 및 일관성
- 모든 보고서가 동일한 4개 섹션 구조 사용 (Executive Summary, Investment Decision, Key Reasons, Risks to Watch)
- 기술 용어 자동 변환 (예: "EBITDA" → "세전 이익", "P/E ratio" → "주가 대비 수익 비율")
- 복잡한 파생상품 및 고급 전략 내용 자동 제거

### 처리 효율성
- **중복 방지**: 이미 처리된 파일 자동 건너뛰기로 80% 이상 시간 절약
- **API 비용 절약**: 불필요한 LLM 호출 방지
- **자동 품질 검증**: Flesch Reading Ease Score 및 Grade Level 자동 분석

## 🔧 고급 사용법

### XML 템플릿 커스터마이징
`report_template.xml`을 수정하여 보고서 구조를 조정할 수 있습니다:
```xml
<section name="custom_section" required="true">
  <description>사용자 정의 섹션 설명</description>
  <max_length>200</max_length>
  <tone>friendly, accessible</tone>
</section>
```

### 환경별 설정
```bash
# 개발 환경에서 드라이런 모드로 테스트
export OPENAI_API_KEY=your_key
python postprocess_final_reports.py --date 2025-09-16 --dry-run

# 프로덕션 환경에서 자동 실행
# GitHub Actions에서 자동으로 처리됨
```

### 품질 모니터링
GitHub Actions는 처리된 모든 파일에 대해 다음을 자동 검증합니다:
- Flesch Reading Ease Score (목표: 60 이상)
- Flesch-Kincaid Grade Level (목표: 12 이하)
- 필수 섹션 구조 존재 여부
- 단어 수 제한 준수

## 📚 관련 문서
- `POST_PROCESSING_README.md`: 후처리 시스템 상세 가이드
- `IMPLEMENTATION_SUMMARY.md`: 구현 세부사항
- `report_template.xml`: 보고서 구조 정의

## 라이선스
프로젝트 루트의 라이선스 파일을 확인하세요(없다면 내부/사내 용도로 간주하십시오).

