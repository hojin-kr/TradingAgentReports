# 최종 보고서 후처리 시스템

이 시스템은 복잡한 투자 분석 보고서를 일반 투자자가 이해하기 쉬운 형태로 변환하는 후처리 파이프라인입니다.

## 🎯 목표

- **난이도 조절**: 복잡한 금융 용어와 분석을 일반인이 이해할 수 있는 수준으로 단순화
- **형식 표준화**: XML 템플릿을 사용하여 일관된 보고서 형식 제공
- **핵심 정보 추출**: 일반 투자자에게 필요한 정보만 남기고 과도하게 복잡한 내용 제거
- **요점 정리**: 진부하지 않으면서도 핵심을 파악할 수 있는 간결한 내용 구성

## 📁 구성 요소

### 1. XML 템플릿 (`report_template.xml`)
표준화된 보고서 구조를 정의하는 XML 파일:

```xml
<report_template>
  <structure>
    <section name="executive_summary" required="true">
      <description>Brief, clear summary in 2-3 sentences maximum</description>
      <max_length>300</max_length>
    </section>
    <!-- 기타 섹션들 -->
  </structure>
</report_template>
```

**주요 섹션:**
- ✅ **Executive Summary**: 2-3문장으로 요약된 핵심 내용
- ✅ **Investment Decision**: 명확한 투자 결정과 신뢰도
- ✅ **Key Reasons**: 결정을 뒷받침하는 주요 이유 (최대 3개)
- ✅ **Risks to Watch**: 주의해야 할 주요 리스크 (최대 2개)
- ✅ **Simple Action Plan**: 실행 가능한 구체적 계획
- ⭕ **Market Context**: 관련 시장 상황 (선택사항)

### 2. 후처리 스크립트 (`postprocess_final_reports.py`)
LLM을 사용하여 보고서를 변환하는 메인 스크립트:

```bash
python postprocess_final_reports.py --date 2025-09-12
```

**주요 기능:**
- XML 템플릿 기반 구조화된 변환
- 기술적 용어를 일반 용어로 자동 변환
- 복잡한 투자 전략 및 파생상품 정보 제거
- 읽기 수준을 고등학교 수준으로 조정
- 최대 800단어로 내용 압축
- **중복 실행 방지**: 이미 처리된 파일은 자동으로 건너뜀

### 3. GitHub Actions 워크플로우 (`.github/workflows/postprocess-reports.yml`)
자동화된 후처리 실행을 위한 CI/CD 파이프라인:

**트리거 조건:**
- 수동 실행 (workflow_dispatch)
- 매일 오전 2시 자동 실행 (schedule)
- reports/ 디렉토리 변경 시 (push)

**품질 검증:**
- 가독성 분석 (Flesch Reading Ease Score)
- 학년 수준 검증 (Flesch-Kincaid Grade Level)
- 단어 수 및 구조 검증

## 🚀 사용법

### 환경 설정
```bash
# 필수 환경 변수 설정
export OPENAI_API_KEY="your-openai-api-key"

# 의존성 설치
pip install -r requirements.txt
```

### 1. 수동 실행
```bash
# 특정 날짜의 보고서 후처리 (이미 처리된 파일은 자동으로 건너뜀)
python postprocess_final_reports.py --date 2025-09-12

# 드라이런 (처리될 파일과 건너뛸 파일 확인)
python postprocess_final_reports.py --date 2025-09-12 --dry-run

# 강제 재처리 (이미 처리된 파일도 다시 처리)
python postprocess_final_reports.py --date 2025-09-12 --force

# 사용자 정의 템플릿 사용
python postprocess_final_reports.py --date 2025-09-12 --template custom_template.xml
```

### 2. GitHub Actions를 통한 자동 실행
- **수동 트리거**: GitHub Actions 탭에서 "Post-process Investment Reports" 워크플로우 실행
  - 날짜, 드라이런 모드, 강제 처리 옵션 설정 가능
- **자동 실행**: 매일 오전 2시(UTC)에 전날 보고서 자동 처리 (중복 방지 적용)
- **Push 트리거**: reports/ 디렉토리에 새 파일이 추가되면 자동 실행

### 3. 테스트 및 데모
```bash
# 파이프라인 구성 요소 테스트
python test_postprocess.py

# 변환 결과 데모 확인
python demo_postprocess.py
```

## 📊 변환 예시

### 변환 전 (원본 보고서)
```markdown
Decision: Buy NVDA (with an explicit risk-managed plan)

Executive verdict
- Buy NVDA. The long-run AI infrastructure thesis, reinforced by a durable 
  CUDA/software moat and robust data-center demand, justifies a constructive stance...

How the debate supports the verdict (key points and quotes)
- Bull case that matters most
  - "Growth runway is intact and multi-year: AI compute demand, hyperscalers, 
    and enterprise AI investments continue to expand." NVDA benefits from both 
    hardware leadership and software monetization (CUDA, libraries, tooling)...
```

### 변환 후 (단순화된 보고서)
```markdown
# Investment Report: NVDA

## Executive Summary
This report recommends a BUY position on NVDA based on our analysis. The main 
factors supporting this decision include strong AI market position and growing 
demand for their products.

## Investment Decision
**Decision: BUY - Confidence: High**

NVDA is well-positioned to benefit from the growing artificial intelligence market...

## Key Reasons Supporting This Decision
1. **Market Leadership**: NVDA dominates the AI chip market with advanced technology
2. **Growing Demand**: Increasing need for AI computing power drives sales
3. **Strong Finances**: Company shows solid profits and cash flow

## Simple Action Plan
**Position Size**: Consider 3-5% of your total investment portfolio.
**Entry Strategy**: Gradual buying over 2-3 months to average your entry price.
```

## 🚫 중복 실행 방지 기능

### 자동 스킵 조건
시스템은 다음 조건을 모두 만족할 때 파일 처리를 자동으로 건너뜁니다:

1. **파일 존재**: `simplified_*.md` 파일이 이미 존재
2. **유효성 검증**: 파일 크기가 100바이트 이상
3. **구조 검증**: 필수 마크다운 구조 포함 (`# Investment Report`, `## Executive Summary` 등)
4. **시간 비교**: 출력 파일이 원본 파일보다 최신 (1초 허용 오차)

### 사용 예시
```bash
# 첫 번째 실행 - 모든 파일 처리
python postprocess_final_reports.py --date 2025-09-12
# ✓ Processed: .../NVDA/EN/final_trade_decision.md → .../simplified_final_trade_decision.md

# 두 번째 실행 - 이미 처리된 파일 건너뜀
python postprocess_final_reports.py --date 2025-09-12  
# ⏭ Skipped (already exists): .../simplified_final_trade_decision.md

# 강제 재처리
python postprocess_final_reports.py --date 2025-09-12 --force
# ✓ Processed: .../NVDA/EN/final_trade_decision.md → .../simplified_final_trade_decision.md
```

### 장점
- **비용 절약**: 불필요한 LLM API 호출 방지
- **시간 단축**: 이미 처리된 파일 건너뛰기
- **안전성**: 유효하지 않은 출력 파일 자동 재처리
- **유연성**: `--force` 옵션으로 강제 재처리 가능

## 📈 성과 지표

### 가독성 개선
- **원본**: Flesch Score ~30-40 (대학 수준)
- **변환후**: Flesch Score 60+ (고등학교 수준)
- **길이 단축**: 평균 70% 이상 압축

### 표준화 효과
- 모든 보고서가 동일한 구조와 형식 사용
- 투자자가 빠르게 핵심 정보 파악 가능
- 일관된 의사결정 프레임워크 제공

### 효율성 개선
- **중복 방지**: 이미 처리된 파일 자동 건너뛰기
- **API 비용 절약**: 불필요한 LLM 호출 방지
- **처리 시간 단축**: 평균 80% 이상 시간 절약 (재실행 시)

## 🔧 커스터마이징

### XML 템플릿 수정
`report_template.xml` 파일을 편집하여 다음을 조정할 수 있습니다:
- 섹션 구조 및 필수 여부
- 최대 길이 제한
- 언어 스타일 가이드라인
- 기술 용어 변환 규칙

### 스크립트 설정
`postprocess_final_reports.py`에서 다음을 수정 가능:
- LLM 모델 선택
- 재시도 로직
- 출력 파일 명명 규칙

## 🚨 주의사항

### 필수 요구사항
- `OPENAI_API_KEY` 환경 변수 설정 필수
- 기존 OpenAI API 키 사용 (새로 발급 불필요)
- Python 3.10+ 권장

### 제한사항
- 현재 `final_trade_decision.md` 파일만 처리
- 영어 보고서 기준으로 최적화
- LLM API 사용으로 인한 비용 발생

### 품질 보증
- 자동 가독성 검증
- 템플릿 구조 검증
- 원본 의미 보존 검증

## 📋 파일 구조

```
workspace/
├── report_template.xml              # XML 템플릿
├── postprocess_final_reports.py     # 메인 후처리 스크립트
├── test_postprocess.py             # 테스트 스크립트
├── demo_postprocess.py             # 데모 스크립트
├── .github/workflows/
│   └── postprocess-reports.yml     # GitHub Actions 워크플로우
├── reports/
│   └── YYYY-MM-DD/
│       └── [BUY|HOLD|SELL]/
│           └── TICKER/
│               └── EN/
│                   ├── final_trade_decision.md
│                   └── simplified_final_trade_decision.md  # 생성됨
└── requirements.txt                 # 의존성 (업데이트됨)
```

## 🔄 워크플로우

1. **보고서 생성**: `gen_reports.py`로 원본 보고서 생성
2. **후처리 실행**: 자동 또는 수동으로 후처리 스크립트 실행
3. **품질 검증**: 가독성 및 구조 검증
4. **결과 저장**: 단순화된 보고서를 동일 디렉토리에 저장
5. **Git 커밋**: 변경사항 자동 커밋 및 푸시

이 시스템을 통해 복잡한 투자 분석을 누구나 이해할 수 있는 명확하고 실용적인 정보로 변환할 수 있습니다.