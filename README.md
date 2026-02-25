# Reactive Presentation

> 인터랙티브 HTML 슬라이드쇼 허브 | Canvas 애니메이션, 라이브 시뮬레이터, 퀴즈

브라우저에서 바로 실행되는 동적 프레젠테이션 플랫폼입니다.
PPT 대신 HTML/CSS/JS로 16:9 슬라이드를 구성하며, Canvas 애니메이션, 버튼 인터랙션, 실시간 시뮬레이터, 자동 채점 퀴즈를 지원합니다.

---

## Presentations

| 슬라이드 | 주제 | 시간 | 슬라이드 수 | 인터랙티브 |
|---------|------|------|-----------|-----------|
| [EKS Auto Mode & Observability](eks-observability-ops/) | EKS Auto Mode 아키텍처, 노드 모니터링, Grafana 상관분석, VPA 최적화 | 2h | 48장 | 10 Canvas, 12 퀴즈 |

> 새로운 프레젠테이션이 추가되면 위 표와 `index.html` 허브 페이지에 카드를 추가합니다.

---

## Project Structure

```
reactive_presentation/
├── README.md                              # This file
├── index.html                             # Hub — 모든 프레젠테이션 목록
├── common/                                # Shared framework (모든 슬라이드가 공유)
│   ├── theme.css                          #   Dark theme, 16:9 layout, CSS variables
│   ├── slide-framework.js                 #   키보드/터치 내비게이션, 프레젠터 뷰
│   ├── presenter-view.js                  #   듀얼 윈도우 프레젠터 모드 (P 키)
│   ├── animation-utils.js                 #   Canvas 드로잉 프리미티브
│   └── quiz-component.js                  #   퀴즈 자동 채점
│
└── eks-observability-ops/                 # 프레젠테이션: EKS Auto Mode & Observability
    ├── index.html                         #   목차 페이지 (블록별 타임라인)
    ├── 01-architecture.html               #   Block 1: 내부 아키텍처 (35분, 15 slides)
    ├── 02-node-lifecycle.html             #   Block 2: 노드 라이프사이클 (25분, 10 slides)
    ├── 03-observability-correlation.html   #   Block 3: 관측성 상관분석 (35분, 14 slides)
    └── 04-resource-optimization.html      #   Block 4: VPA & 최적화 (20분, 9 slides)
```

### 새 프레젠테이션 추가 방법

```
1. 폴더 생성:  {slug}/
2. 목차 작성:  {slug}/index.html
3. 블록 작성:  {slug}/01-block-name.html, 02-...
4. 허브 등록:  index.html에 카드 추가
5. README 표에 행 추가
```

공통 프레임워크(`common/`)를 그대로 참조하므로 별도 빌드 없이 HTML만 작성하면 됩니다.

---

## How It Works

각 슬라이드는 `<div class="slide">` 단위로 구성되며, `SlideFramework`가 키보드/터치 내비게이션, 진행률 표시, URL 해시 동기화를 처리합니다.

```html
<!-- 슬라이드 구조 -->
<div class="slide-deck">
  <div class="slide title-slide">
    <h1>제목</h1>
    <p class="subtitle">부제목</p>
  </div>

  <div class="slide">
    <div class="slide-header"><h2>슬라이드 제목</h2></div>
    <div class="slide-body">
      <!-- Canvas 애니메이션, 버튼, 시뮬레이터 등 -->
    </div>
  </div>
</div>

<script src="../common/slide-framework.js"></script>
<script>
  const deck = new SlideFramework({
    footer: 'Company Name',
    logoSrc: '../common/pptx-theme/images/logo_1.png',
    presenterNotes: { 1: '첫 슬라이드 노트', 2: '...' }
  });
</script>
```

### 동적 슬라이드 예시

일반 PPT와 달리, 각 슬라이드 안에서 **JavaScript로 동작하는 인터랙션**을 구현합니다:

- **Canvas 애니메이션:** `requestAnimationFrame` 기반 실시간 렌더링 (아키텍처 흐름, 노드 시뮬레이터)
- **버튼 인터랙션:** Scale-Out/Scale-In 버튼으로 상태 변화 체험
- **시뮬레이터:** 슬라이더로 파라미터 조정 → 실시간 결과 시각화
- **비교 토글:** A vs B 옵션을 버튼으로 전환
- **자동 채점 퀴즈:** 정답/오답 즉시 피드백

---

## Keyboard Shortcuts

| 키 | 동작 |
|-----|--------|
| ← → | 이전 / 다음 슬라이드 |
| Space | 다음 슬라이드 |
| F | 전체 화면 토글 |
| P | 프레젠터 뷰 (별도 창: 타이머, 노트, 다음 슬라이드 미리보기) |
| Esc | 전체 화면 해제 |
| Home / End | 처음 / 마지막 슬라이드 |

---

## PPTX Theme Support

기업 PPTX 템플릿에서 색상, 폰트, 로고를 추출하여 슬라이드에 적용할 수 있습니다:

```bash
# PPTX 테마 추출
python3 scripts/extract_pptx_theme.py template.pptx -o common/pptx-theme/

# 결과물
# common/pptx-theme/
# ├── theme-manifest.json     # 색상, 폰트, 로고 메타데이터
# ├── theme-override.css      # CSS 변수 오버라이드
# └── images/logo_1.png       # 추출된 로고
```

---

## Getting Started

```bash
# 로컬 서버 실행
python3 -m http.server 8080

# 브라우저에서 열기
open http://localhost:8080
```

## Deploy

```bash
git add .
git commit -m "feat: add new presentation"
git push origin main
# GitHub Settings → Pages → main branch / root
```
