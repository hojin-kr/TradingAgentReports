# News Report Template Development Plan & Implementation

## 🎯 목표 (Objective)

`report_template.xml`을 참고하여 `news_report.md`를 정형화된 데일리 뉴스 정리 형태로 변환할 XML 템플릿을 만들고, postprocess에서 변환을 진행하는 시스템을 개발했습니다.

## 📁 구현된 파일들 (Implemented Files)

### 1. `news_report_template.xml`
- **목적**: 뉴스 리포트의 표준화된 구조를 정의하는 XML 템플릿
- **기반**: 기존 `report_template.xml`의 구조와 원칙을 따름
- **특징**:
  - 트레이더와 투자자를 위한 실행 가능한 정보 중심
  - 구체적인 가격 수준과 거래 시나리오 포함
  - 리스크 관리와 포지션 사이징 가이드라인 제공

### 2. `postprocess_news_reports.py`
- **목적**: 뉴스 리포트를 구조화된 형태로 변환하는 후처리 스크립트
- **기능**:
  - XML 템플릿 기반 구조화된 변환
  - LLM을 사용한 지능형 콘텐츠 재구성
  - 배치 처리 및 중복 실행 방지
  - 상세한 진행 상황 리포팅

## 🏗 템플릿 구조 (Template Structure)

### 필수 섹션 (Required Sections)

1. **Executive Snapshot**
   - 핵심 시장 동향과 거래 함의를 간결하게 요약
   - 최대 500자, 권위 있고 트레이더 중심의 톤

2. **Key Catalysts & Market Drivers**
   - 주요 뉴스 이벤트와 시장 움직임의 동력
   - 최대 5개 항목, 각각 100-200자
   - 이벤트 설명, 시장 영향, 거래 함의 포함

3. **Technical Analysis & Key Levels**
   - 지지선, 저항선, 가격 목표 등 핵심 기술적 수준
   - 현재 가격 컨텍스트와 돌파/하락 시나리오

4. **Risk Factors to Monitor**
   - 현재 내러티브를 방해할 수 있는 주요 리스크
   - 최대 3개 항목, 즉각적인 위협에 집중

5. **Trading Scenarios & Targets**
   - 강세, 약세, 기본 시나리오별 구체적 가격 목표
   - 트리거 조건과 타겟 수준 명시

6. **Market Context & Macro Backdrop**
   - 광범위한 시장 조건과 거시경제 요인
   - 최대 300자, 섹터 성과와 상대적 퍼포먼스 포함

### 선택 섹션 (Optional Sections)

7. **Data Signals & Indicators**
   - 볼륨 패턴, 옵션 플로우, 센티먼트 지표
   - 최대 4개 항목

8. **Upcoming Events Calendar**
   - 모니터링할 예정된 이벤트와 발표
   - 최대 3개 항목, 날짜-이벤트-예상 영향 형식

## 🔧 사용법 (Usage)

### 기본 실행
```bash
# 특정 날짜의 모든 news_report.md 파일 처리
export OPENAI_API_KEY=your_api_key
python3 postprocess_news_reports.py --date 2025-09-22
```

### 옵션들
```bash
# 드라이 런 (실제 처리 없이 분석만)
python3 postprocess_news_reports.py --date 2025-09-22 --dry-run

# 강제 재처리 (기존 파일 덮어쓰기)
python3 postprocess_news_reports.py --date 2025-09-22 --force

# 사용자 정의 템플릿 사용
python3 postprocess_news_reports.py --date 2025-09-22 --template custom_template.xml

# 출력 파일 접두사 변경
python3 postprocess_news_reports.py --date 2025-09-22 --output-suffix "daily_intel_"
```

## 📊 출력 형식 (Output Format)

변환된 파일은 다음 구조를 가집니다:

```markdown
# Daily Market Intelligence: [TICKER] - [DATE]

## Executive Snapshot
[핵심 요약...]

## Key Catalysts and Market Drivers
[주요 촉매...]

## Technical Analysis and Key Levels
[기술적 분석...]

## Risk Factors to Monitor
[리스크 요인...]

## Trading Scenarios and Targets
[거래 시나리오...]

## Market Context and Macro Backdrop
[시장 컨텍스트...]

## Data Signals and Indicators (if applicable)
[데이터 신호...]

## Upcoming Events Calendar (if applicable)
[예정된 이벤트...]

| Scenario | Price Target | Key Trigger | Risk Level |
|----------|-------------|-------------|------------|
[요약 테이블...]
```

## 🎯 품질 기준 (Quality Standards)

### 정확성 (Accuracy)
- 모든 가격 수준과 기술적 분석 검증
- 주요 뉴스 항목 교차 참조
- 이벤트 날짜와 타이밍 정확성 보장

### 실행 가능성 (Actionability)
- 범위가 아닌 정확한 가격 수준 제공
- 시나리오 활성화를 위한 구체적 조건 정의
- 스톱 레벨과 포지션 사이징 가이드라인 포함

### 시의성 (Timeliness)
- 현재 시장 세션과 타이밍 고려
- 최근 이벤트에 더 높은 가중치 부여
- 분석이 언제 만료될지 인지

## 🔄 기존 시스템과의 통합 (Integration)

### 기존 postprocess_final_reports.py와의 관계
- `postprocess_final_reports.py`: final_trade_decision.md 파일을 일반 투자자용으로 단순화
- `postprocess_news_reports.py`: news_report.md 파일을 구조화된 거래 정보로 변환
- 두 시스템은 독립적으로 작동하며 서로 다른 목적을 가짐

### 파일 구조
```
workspace/
├── report_template.xml              # 기존 투자 리포트 템플릿
├── news_report_template.xml         # 새로운 뉴스 리포트 템플릿
├── postprocess_final_reports.py     # 기존 투자 결정 후처리
├── postprocess_news_reports.py      # 새로운 뉴스 리포트 후처리
└── reports/
    └── YYYY-MM-DD/
        └── BUY|HOLD|SELL/
            └── TICKER/
                └── EN/
                    ├── news_report.md                    # 원본
                    ├── structured_news_report.md         # 변환된 파일
                    ├── final_trade_decision.md           # 원본
                    └── simplified_final_trade_decision.md # 기존 시스템 출력
```

## 🚀 개발 완료 사항 (Completed Development)

✅ **XML 템플릿 설계**: `news_report_template.xml` 생성
✅ **후처리 스크립트 구현**: `postprocess_news_reports.py` 개발
✅ **템플릿 파싱 로직**: XML 구조를 파이썬 객체로 변환
✅ **LLM 통합**: OpenAI API를 사용한 지능형 변환
✅ **배치 처리**: 여러 파일 동시 처리 지원
✅ **중복 방지**: 이미 처리된 파일 자동 스킵
✅ **오류 처리**: 재시도 로직과 상세한 오류 리포팅
✅ **드라이 런 모드**: 실제 처리 전 분석 기능
✅ **테스트 완료**: 2025-09-22 데이터로 검증

## 🎉 사용 준비 완료 (Ready for Use)

이 시스템은 완전히 구현되어 사용할 준비가 되었습니다. 유효한 `OPENAI_API_KEY`만 설정하면 즉시 뉴스 리포트를 구조화된 데일리 마켓 인텔리전스 형태로 변환할 수 있습니다.

## 📝 향후 개선 사항 (Future Enhancements)

- 다양한 LLM 제공업체 지원 (Anthropic, Google 등)
- 템플릿 검증 및 스키마 체크
- 성능 최적화 및 병렬 처리
- 웹 인터페이스 또는 API 엔드포인트
- 자동화된 품질 점검 및 메트릭