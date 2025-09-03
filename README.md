## TradingAgents 리포트 생성기

트레이딩 관련 에이전트 파이프라인으로부터 시장/뉴스/심리/기초체력 분석을 수집하고, 날짜/티커/언어별 Markdown 리포트를 생성합니다. 생성된 문서는 최종 의사결정(BUY/HOLD/SELL)에 따라 폴더가 자동 분기되며, 선택적으로 사후 편집/번역을 수행할 수 있습니다.

### 주요 구성
- `tradingagents/graph/trading_graph.py`: 에이전트 그래프의 진입점
- `gen_reports.py`: 그래프 실행(또는 저장 로그) → Markdown 리포트 생성
- `postprocess_reports.py`: 생성된 리포트 문서 품질 개선 및 EN → KO 번역
- `tradingagents/default_config.py`: 기본 설정(LLM, 디렉토리 경로 등)
- `reports/`: 날짜/의사결정/티커/언어별 결과 저장 루트

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

### 3) 사후 편집 및 번역(선택)
생성된 Markdown을 문장 품질 위주로 다듬고, EN 문서를 기준으로 KO 번역본을 추가 생성합니다.
```bash
export OPENAI_API_KEY=...  # 필수
python postprocess_reports.py --date 2025-09-03
```
사후 편집은 모든 언어 문서를 개선하고, EN 문서가 있을 경우 동일 경로의 `KO/`에 번역 문서를 생성합니다.

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
          complete.md        # 모든 섹션 합본
        KO/
          ... 동일 파일명 ...
```

## 설정 커스터마이징
- 기본 설정은 `tradingagents/default_config.py`를 참고하세요.
  - `llm_provider`, `deep_think_llm`, `quick_think_llm`, `backend_url` 등 LLM 관련 설정
  - `results_dir`: `TRADINGAGENTS_RESULTS_DIR` 환경 변수로도 변경 가능
  - `data_dir`: 오프라인 데이터(예: SimFin, Finnhub 가공 데이터) 루트. 필요 시 경로를 프로젝트 로컬 경로로 수정하세요.
- 온라인 도구가 기본 활성화되어 있어(`online_tools=True`) OpenAI/Google News/Yahoo Finance 등을 사용합니다. 오프라인 데이터가 없더라도 리포트 생성은 동작하되, 일부 섹션은 비어 있을 수 있습니다.

## 트러블슈팅
- OpenAI 인증 오류: `OPENAI_API_KEY`가 설정되어 있는지 확인하세요.
- 번역이 생성되지 않음: `--translate` 옵션은 `gen_reports.py`에서만 사용됩니다. `postprocess_reports.py`는 EN 문서를 기준으로 자동 KO 번역을 시도합니다.
- 데이터 경로 오류: `data_dir`가 로컬 환경에 맞지 않으면 오프라인 도구 결과가 비어 있을 수 있습니다. 필요한 경우 `tradingagents/default_config.py`에서 수정하세요.
- 뉴스/크롤링 제한: Google News는 비공식 스크래핑으로, 레이트 리밋에 걸릴 수 있습니다. 재시도 시 지연이 포함됩니다.

## 라이선스
프로젝트 루트의 라이선스 파일을 확인하세요(없다면 내부/사내 용도로 간주하십시오).

