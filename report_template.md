# 최종 투자 결정 보고서 템플릿 (Final Trade Decision Report Template)

<!--
이 템플릿은 LLM이 일관된 형식의 최종 의사결정 보고서를 생성하도록 설계되었습니다.
- 커스텀 변수는 {{VARIABLE_NAME}} 형태로 채워 넣으세요.
- BUY/HOLD/SELL 3종의 결론을 모두 포괄합니다.
- 간결하고 실행 가능한 문장, 숫자 우선, 불필요한 수식/수사를 피하세요.
- 각 섹션은 존재 이유가 명확해야 하며, 중복 서술을 금지합니다.
-->

## 1) 메타데이터 (Metadata)
- **리포트 날짜**: {{REPORT_DATE}}
- **종목**: {{TICKER}} ({{COMPANY_NAME}})
- **거래소/국가**: {{EXCHANGE}} / {{COUNTRY}}
- **섹터/산업**: {{SECTOR}} / {{INDUSTRY}}
- **의사결정 시점(UTC)**: {{DECISION_TIMESTAMP_UTC}}
- **투자 시간축**: {{TIME_HORIZON}}  (예: 3–6개월, 6–12개월, 12–24개월)
- **리스크 예산(포지션 기준)**: {{RISK_BUDGET_DESC}}
- **포지션 컨텍스트**: {{POSITION_CONTEXT}}  (예: 신규 진입 / 보유 중 / 축소 중)
- **분석 소스**: 최종결정 문서 + {감성, 펀더멘털, 뉴스, 마켓} 리포트 요약

---

## 2) 최종 요약 (Executive Summary – 3줄)
1. **결정**: {{FINAL_DECISION}}  (BUY | HOLD | SELL)
2. **권고 한줄**: {{ONE_SENTENCE_RECOMMENDATION}}
3. **핵심 근거**: {{PRIMARY_RATIONALE}}

> 신뢰도(Confidence): {{CONFIDENCE_LEVEL}} (Low/Medium/High) | 근거 신호: {{KEY_SIGNALS}}

---

## 3) 한줄 논지 (One-line Thesis)
- {{ONE_LINE_THESIS}}  (25단어 이내, 모호어 금지)

---

## 4) 권고 (Recommendation)
- **Recommendation**: {{FINAL_DECISION}}  (예: “Hold with hedges” / “Sell or materially trim with hedges” / “Buy with staged entries”)
- **대안 시나리오 선택지(있다면)**: {{ALTERNATIVES}}
- **요구 전제/가정**: {{ASSUMPTIONS_BRIEF}}

---

## 5) 논쟁 종합 (Synthesis of Debate)
- **Bull(공격적) 강점 요지**:
  - {{BULL_KEY_POINT_1}}
  - {{BULL_KEY_POINT_2}}
  - 인용: “{{BULL_QUOTE}}”
- **Bear(보수적) 강점 요지**:
  - {{BEAR_KEY_POINT_1}}
  - {{BEAR_KEY_POINT_2}}
  - 인용: “{{BEAR_QUOTE}}”
- **Neutral(중립) 요지**:
  - {{NEUTRAL_KEY_POINT_1}}
  - 인용: “{{NEUTRAL_QUOTE}}”
- **왜 이 결정인가 (Why this decision follows)**:
  - {{WHY_DECISION_POINT_1}}
  - {{WHY_DECISION_POINT_2}}
  - {{WHY_DECISION_POINT_3}}

---

## 6) 트레이더 실행 계획 (Trader-focused Plan)
### 6.1 포지셔닝과 사이징 (Positioning & Sizing)
- **코어 포지션**: {{CORE_POSITION_DESC}}
- **추가/축소 트랜치 규칙**: {{TRANCHE_RULES}}
- **최대 익스포저/드로다운 가드레일**: {{EXPOSURE_DRAWNDOWN_GUARDRAILS}}

### 6.2 리스크 관리 및 헤지 (Risk Controls & Hedges)
- **기본 구조**: {{PRIMARY_HEDGE_STRUCTURE}}  (예: 콜라, 보호풋, 풋스프레드)
- **예시 파라미터**: {{HEDGE_PARAMETERS}}  (만기, 행사가, 목표 비용/커버리지)
- **동적 조정 규칙**: {{HEDGE_ADJUST_RULES}}

### 6.3 촉매 캘린더 (Catalyst Calendar)
- {{CATALYST_1}} – {{DATE_1}} – 기대/리스크: {{CATALYST_NOTE_1}}
- {{CATALYST_2}} – {{DATE_2}} – 기대/리스크: {{CATALYST_NOTE_2}}
- {{CATALYST_3}} – {{DATE_3}} – 기대/리스크: {{CATALYST_NOTE_3}}

### 6.4 업그레이드/다운그레이드 트리거 (Upgrade/Downgrade Triggers)
- **업그레이드(예: HOLD → BUY)**: {{UPGRADE_TRIGGER_RULES}}
- **다운그레이드(예: HOLD → SELL)**: {{DOWNGRADE_TRIGGER_RULES}}

### 6.5 모니터링 주기 (Monitoring Cadence)
- **주기/이벤트 기반 재평가 규칙**: {{REVIEW_CADENCE_AND_RULES}}

### 6.6 실행 체크리스트 (Execution Checklist)
- [ ] 포지션 사이즈와 리스크 예산 확인 ({{CHECK_SIZE_RISK}})
- [ ] 헤지 체결/롤링 계획 수립 ({{CHECK_HEDGE}})
- [ ] 촉매 캘린더 등록 및 사전/사후 프로토콜 ({{CHECK_CATALYST}})
- [ ] 트리거 룰 엔코딩 (가격/지표/뉴스) ({{CHECK_TRIGGERS}})

### 6.7 시나리오 매트릭스 (Scenario Matrix)
| 시나리오 | 핵심 동인 | 가격/지표 시그널 | 액션 |
|---|---|---|---|
| Bull | {{SC_BULL_DRIVERS}} | {{SC_BULL_SIGNALS}} | {{SC_BULL_ACTIONS}} |
| Base | {{SC_BASE_DRIVERS}} | {{SC_BASE_SIGNALS}} | {{SC_BASE_ACTIONS}} |
| Bear | {{SC_BEAR_DRIVERS}} | {{SC_BEAR_SIGNALS}} | {{SC_BEAR_ACTIONS}} |

---

## 7) 밸류에이션/기초체력 스냅샷 (Valuation & Fundamentals)
- **밸류에이션**: {{VALUATION_METRICS}}  (예: EV/S, P/E, FCF Yield)
- **성장/수익성**: {{GROWTH_PROFITABILITY}}  (예: 매출/이익 성장률, GPM/OPM/FCF)
- **재무구조**: {{BALANCE_SHEET}}  (현금/부채, 유동성)
- 출처/시점: {{DATA_SOURCE_AND_AS_OF}}

---

## 8) 기술적/마켓 컨텍스트 (Technical & Market Context)
- **추세/변동성**: {{TREND_VOL}}  (예: 50/200SMA, MACD, RSI, ATR)
- **수급/베타**: {{FLOW_BETA}}
- **상대강도/상대가치**: {{RELATIVE_STRENGTH_VALUE}}

---

## 9) 핵심 리스크와 완화책 (Top Risks & Mitigations)
- 리스크 1: {{RISK_1}} → 완화: {{MITIGATION_1}}
- 리스크 2: {{RISK_2}} → 완화: {{MITIGATION_2}}
- 리스크 3: {{RISK_3}} → 완화: {{MITIGATION_3}}

---

## 10) 데이터 공백 및 가정 (Data Gaps & Assumptions)
- 공백/제약: {{DATA_GAPS}}
- 운영 가정: {{OPERATING_ASSUMPTIONS}}

---

## 11) 산출물 재요약 (Deliverables Recap)
- **Decision**: {{FINAL_DECISION}}
- **Rationale**: {{RATIONALE_SUMMARY}}
- **Trader Plan**: {{TRADER_PLAN_SUMMARY}}

---

## 12) 부록 A: 핵심 인용구 (Key Quotes)
- Bull: “{{BULL_QUOTE_FULL}}”
- Bear: “{{BEAR_QUOTE_FULL}}”
- Neutral: “{{NEUTRAL_QUOTE_FULL}}”

## 13) 부록 B: 8-지표 스냅샷 (Optional)
- close_50_sma: {{INDICATOR_CLOSE_50_SMA}}
- close_200_sma: {{INDICATOR_CLOSE_200_SMA}}
- close_10_ema: {{INDICATOR_CLOSE_10_EMA}}
- MACD / Signal / Hist: {{INDICATOR_MACD}} / {{INDICATOR_MACDS}} / {{INDICATOR_MACDH}}
- RSI: {{INDICATOR_RSI}}
- ATR: {{INDICATOR_ATR}}

---

## 14) 스타일 가이드 (Style Guide for LLM)
- **톤**: 단호하고 실행 중심. 모호어 금지(“아마도, 가능성” 등).
- **길이**: 각 하위 섹션 3–6개 불릿, 문장 짧게.
- **수치**: 퍼센트/구간/만기 등 구체 수치 제시. 단위 표준화.
- **형식**: 본 템플릿의 헤딩/테이블/체크박스 구조 유지.
- **규칙**:
  - 불필요한 반복 금지, 상위 요약과 상세의 내용 일관성 유지.
  - 트리거는 “조건 → 액션”의 if/then 규칙으로.
  - 헤지 구조는 목적/파라미터/조정 규칙을 반드시 포함.
  - 표/리스트는 3개 이상 항목을 권장하되, 불필요시 생략 가능.

<!-- End of template -->