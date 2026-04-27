---
remarp: true
block: talk
---

<!-- Slide 1: Cover -->
@type: cover
@background: ../common/pptx-theme/images/Picture_13.png
@badge: ../common/pptx-theme/images/Picture_8.png

# Claude Code 플러그인 마켓플레이스를 만들어보자
Lightning Tech Talk — 15 min

---
<!-- Slide 2: Agenda -->
@type: agenda

## 오늘의 여정

1. 왜 만들었나 — oh-my-cloud-skills (2min)
2. 플러그인 구조 & 하네스 엔지니어링 (3min)
3. Remarp 프레임워크 — 프레젠테이션 혁신 (3min)
4. VSCode Extension 개발기 (3min)
5. 또박(Ttobak) — 동료와 함께 일하기 (2min)
6. 마무리 & 배운 점 (2min)
:::notes
{timing: 0.5min}
안녕하세요, 오준석입니다. 오늘은 제가 Claude Code 위에서 플러그인 마켓플레이스를 만들어본 경험을 공유하려고 합니다. 참고로 지금 보고 계신 이 슬라이드도 제가 만든 Remarp라는 도구로 생성했습니다. 15분 동안 빠르게 진행하겠습니다.
{cue: transition}
먼저 왜 이걸 만들게 됐는지부터 말씀드리겠습니다.
:::

---
<!-- Slide 3: Why — 동기 -->
@type: content

## 왜 만들었나?

:::html
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
  <div class="fragment fade-up" data-fragment-index="1" style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:12px;padding:18px;">
    <div style="font-size:1.5rem;margin-bottom:8px;">😤</div>
    <div style="color:#ef4444;font-weight:bold;font-size:1.2rem;margin-bottom:10px;">반복되는 고통</div>
    <div style="color:#8b95a5;font-size:0.95rem;line-height:1.65;">
      AI로 PPT 만들면 레이아웃이 깨짐<br>
      HTML 직접 작성하면 수정이 너무 어려움<br>
      아키텍처 다이어그램은 한땀한땀<br>
      고객 세션 준비는 항상 시간 부족
    </div>
  </div>
  <div class="fragment fade-up" data-fragment-index="2" style="background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:12px;padding:18px;">
    <div style="font-size:1.5rem;margin-bottom:8px;">💡</div>
    <div style="color:#00ff88;font-weight:bold;font-size:1.2rem;margin-bottom:10px;">플러그인으로 해결</div>
    <div style="color:#8b95a5;font-size:0.95rem;line-height:1.65;">
      SA 노하우를 Agent + Skill로 캡슐화<br>
      누구나 설치해서 바로 사용<br>
      팀 전체의 생산성 향상<br>
      지식이 코드로 축적<br>
      Hook + Quality Gate로 실수 자동 차단<br>
      /명령어 하나로 SA 워크플로우 실행
    </div>
  </div>
</div>
:::
:::notes
{timing: 1.5min}
SA로 일하다 보면 고객 세션 준비가 정말 큰 비중을 차지합니다. AI한테 PPT를 만들어달라고 하면 레이아웃이 깨지고, 그렇다고 HTML을 직접 짜면 한 번 수정할 때마다 시간이 너무 오래 걸리고요. 아키텍처 다이어그램도 한땀한땀이고, 항상 시간이 부족합니다. 이런 고통들을 플러그인으로 해결하면 팀 전체가 쓸 수 있겠다는 생각이 들었습니다.
{cue: transition}
그래서 만든 게 oh-my-cloud-skills 입니다.
:::

---
<!-- Slide 4: oh-my-cloud-skills 개요 -->
@type: content

## oh-my-cloud-skills

:::html
<div style="text-align:center;margin-bottom:16px;">
  <span style="background:rgba(108,92,231,0.2);border:1px solid rgba(108,92,231,0.4);border-radius:20px;padding:6px 16px;font-size:0.95rem;color:#a29bfe;">Claude Code Plugin Marketplace</span>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
  <div class="fragment fade-up" data-fragment-index="1" style="background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.3);border-radius:12px;padding:18px;text-align:center;">
    <div style="color:#00d4ff;font-weight:bold;font-size:1.15rem;margin-bottom:8px;">aws-content-plugin</div>
    <div style="color:#8b95a5;font-size:0.9rem;">8 Agents · 5 Skills</div>
    <div style="color:#999;font-size:0.85rem;margin-top:8px;">프레젠테이션, 다이어그램<br>문서, 워크숍</div>
  </div>
  <div class="fragment fade-up" data-fragment-index="2" style="background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:12px;padding:18px;text-align:center;">
    <div style="color:#00ff88;font-weight:bold;font-size:1.15rem;margin-bottom:8px;">aws-ops-plugin</div>
    <div style="color:#8b95a5;font-size:0.9rem;">10 Agents · 6 Skills</div>
    <div style="color:#999;font-size:0.85rem;margin-top:8px;">EKS, 네트워크, IAM<br>모니터링, 스토리지</div>
  </div>
  <div class="fragment fade-up" data-fragment-index="3" style="background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.3);border-radius:12px;padding:18px;text-align:center;">
    <div style="color:#a855f7;font-weight:bold;font-size:1.15rem;margin-bottom:8px;">kiro-power-converter</div>
    <div style="color:#8b95a5;font-size:0.9rem;">1 Agent · 1 Skill</div>
    <div style="color:#999;font-size:0.85rem;margin-top:8px;">Claude → Kiro<br>플러그인 변환</div>
  </div>
  <div class="fragment fade-up" data-fragment-index="4" style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:12px;padding:18px;text-align:center;">
    <div style="color:#f59e0b;font-weight:bold;font-size:1.15rem;margin-bottom:8px;">kiro-review</div>
    <div style="color:#8b95a5;font-size:0.9rem;">1 Agent · 1 Skill</div>
    <div style="color:#999;font-size:0.85rem;margin-top:8px;">코드 리뷰, 보안 감사<br>Well-Architected 평가</div>
  </div>
</div>
<div class="fragment fade-up" data-fragment-index="5" style="text-align:center;margin-top:16px;">
  <code style="color:#a29bfe;font-size:0.88rem;">/plugin marketplace add https://github.com/Atom-oh/oh-my-cloud-skills</code>
</div>
:::
:::notes
{timing: 1.5min}
oh-my-cloud-skills는 네 개의 플러그인으로 구성되어 있습니다. content 플러그인은 프레젠테이션, 다이어그램, 워크숍 같은 콘텐츠를 만들고, ops 플러그인은 EKS 트러블슈팅이나 Well-Architected 리뷰 같은 운영 업무를 지원합니다. kiro-power-converter는 이 플러그인들을 Kiro IDE 포맷으로 변환하고, kiro-review는 코드 리뷰, 보안 감사, Well-Architected 평가를 자동화합니다. GitHub URL 하나로 전체 설치가 됩니다.
{cue: transition}
그러면 이 플러그인이 어떻게 PPT 제작을 자동화하는지 살펴보겠습니다.
:::

---
<!-- Slide 5: Plugin Structure Title -->
@type: title
@transition: zoom

# 플러그인 구조 &
# 하네스 엔지니어링

---
<!-- Slide 6: Plugin Anatomy -->
@type: content

## aws-content-plugin 하네스: PPT 제작 파이프라인

:::html
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:14px;">
  <div class="fragment fade-up" data-fragment-index="1" style="background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.3);border-radius:12px;padding:16px;">
    <div style="color:#00d4ff;font-weight:bold;font-size:1.4rem;margin-bottom:8px;">① PPTX 테마 추출</div>
    <div style="background:rgba(15,22,41,0.6);border-radius:6px;padding:8px;font-family:monospace;font-size:1.05rem;color:#a29bfe;margin-bottom:8px;">extract_pptx_theme.py</div>
    <div style="color:#8b95a5;font-size:1.2rem;line-height:1.6;">
      색상 · 폰트 · 로고 자동 추출<br>
      theme-override.css 생성<br>
      <span style="color:#00d4ff;">→ 회사 브랜드 자동 적용</span>
    </div>
  </div>
  <div class="fragment fade-up" data-fragment-index="2" style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:12px;padding:16px;">
    <div style="color:#f59e0b;font-weight:bold;font-size:1.4rem;margin-bottom:8px;">② Rejection Loop</div>
    <div style="background:rgba(15,22,41,0.6);border-radius:6px;padding:8px;font-family:monospace;font-size:1.05rem;color:#f59e0b;margin-bottom:8px;">remarp_to_slides.py validate</div>
    <div style="color:#8b95a5;font-size:1.2rem;line-height:1.6;">
      7가지 규칙 자동 검증<br>
      CRITICAL → 빌드 차단<br>
      <span style="color:#f59e0b;">→ 레이아웃 깨짐 방지</span>
    </div>
  </div>
  <div class="fragment fade-up" data-fragment-index="3" style="background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.3);border-radius:12px;padding:16px;">
    <div style="color:#a855f7;font-weight:bold;font-size:1.4rem;margin-bottom:8px;">③ Quality Gate</div>
    <div style="background:rgba(15,22,41,0.6);border-radius:6px;padding:8px;font-family:monospace;font-size:1.05rem;color:#a855f7;margin-bottom:8px;">content-review-agent</div>
    <div style="color:#8b95a5;font-size:1.2rem;line-height:1.6;">
      100점 만점 자동 평가<br>
      85점 미만 → 배포 차단<br>
      <span style="color:#a855f7;">→ 품질 기계적 보장</span>
    </div>
  </div>
</div>
<div class="fragment fade-up" data-fragment-index="4" style="display:flex;align-items:center;justify-content:center;gap:8px;background:rgba(15,22,41,0.7);border-radius:8px;padding:10px 16px;">
  <span style="color:#00d4ff;font-size:1.25rem;">PPTX 제공</span>
  <span style="color:#666;">→</span>
  <span style="color:#f59e0b;font-size:1.25rem;">Remarp 작성</span>
  <span style="color:#666;">→</span>
  <span style="color:#f59e0b;font-size:1.25rem;">validate</span>
  <span style="color:#666;">→</span>
  <span style="color:#a855f7;font-size:1.25rem;">review (≥85)</span>
  <span style="color:#666;">→</span>
  <span style="color:#00ff88;font-size:1.25rem;">build ✓</span>
</div>
:::
:::notes
{timing: 1.5min}
aws-content-plugin은 PPT 제작에 세 겹의 안전장치를 두고 있습니다. 첫째, PPTX 테마 추출입니다. 회사 템플릿 PPTX를 넣으면 extract_pptx_theme.py가 색상, 폰트, 로고를 자동으로 추출해서 CSS 변수로 만들어줍니다. 브랜드가 자동 적용되는 거죠. 둘째, Rejection Loop입니다. remarp_to_slides.py validate 명령이 7가지 규칙으로 마크다운을 검증하고, 콘텐츠 오버플로우나 요소 겹침 같은 CRITICAL 이슈가 있으면 빌드 자체가 차단됩니다. 셋째, Quality Gate입니다. content-review-agent가 100점 만점으로 결과물을 평가하고, 85점 미만이면 배포를 차단합니다.
{cue: transition}
핵심은 하네스 엔지니어링인데요.
:::

---
<!-- Slide 7: Harness Engineering -->
@type: content

## 하네스 엔지니어링이란?

:::css
.harness-card {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.45s ease, transform 0.45s ease;
}
.harness-card.visible {
  opacity: 1;
  transform: translateY(0);
}
.plugin-row {
  opacity: 0;
  transform: translateX(-20px);
  transition: opacity 0.4s ease 0.1s, transform 0.4s ease 0.1s;
}
.plugin-row.visible {
  opacity: 1;
  transform: translateX(0);
}
:::

:::html
<div style="text-align:center;margin-bottom:14px;">
  <span style="color:#f59e0b;font-size:1.45rem;font-weight:bold;">"AI가 잘 달릴 수 있는 레일을 깔아주는 것"</span>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:12px;">
  <div class="fragment harness-card" data-fragment-index="1" style="background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.3);border-radius:10px;padding:16px;">
    <div style="color:#00d4ff;font-size:1.8rem;margin-bottom:6px;">📄</div>
    <div style="color:#00d4ff;font-weight:bold;font-size:1.45rem;margin-bottom:10px;">CLAUDE.md</div>
    <div style="color:#8b95a5;font-size:1.27rem;line-height:1.7;">
      프로젝트 컨텍스트 제공<br>
      빌드/테스트 명령어<br>
      코딩 컨벤션 정의<br>
      <span style="color:#00d4ff;">→ 매 세션 자동 로드</span>
    </div>
  </div>
  <div class="fragment harness-card" data-fragment-index="2" style="background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:10px;padding:16px;">
    <div style="color:#00ff88;font-size:1.8rem;margin-bottom:6px;">🪝</div>
    <div style="color:#00ff88;font-weight:bold;font-size:1.45rem;margin-bottom:10px;">Hooks</div>
    <div style="color:#8b95a5;font-size:1.27rem;line-height:1.7;">
      PostToolUse: 빌드 경고 감지<br>
      SessionStart: 도메인 로드<br>
      자동 검증 파이프라인<br>
      <span style="color:#00ff88;">→ 실수 자동 차단</span>
    </div>
  </div>
  <div class="fragment harness-card" data-fragment-index="3" style="background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.3);border-radius:10px;padding:16px;">
    <div style="color:#a855f7;font-size:1.8rem;margin-bottom:6px;">🏆</div>
    <div style="color:#a855f7;font-weight:bold;font-size:1.45rem;margin-bottom:10px;">Quality Gate</div>
    <div style="color:#8b95a5;font-size:1.27rem;line-height:1.7;">
      content-review-agent<br>
      100점 만점 평가 체계<br>
      85점 미만 배포 차단<br>
      <span style="color:#a855f7;">→ 품질 보장 자동화</span>
    </div>
  </div>
</div>
<div class="fragment plugin-row" data-fragment-index="4" style="background:rgba(15,22,41,0.7);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:12px 16px;">
  <div style="color:#fff;font-size:1.27rem;font-weight:bold;margin-bottom:8px;">플러그인에서 활용되는 하네스</div>
  <div style="display:flex;gap:10px;flex-wrap:wrap;">
    <span style="background:rgba(0,212,255,0.15);border:1px solid rgba(0,212,255,0.3);border-radius:6px;padding:5px 12px;font-size:1.17rem;color:#00d4ff;">aws-content-plugin → Quality Gate (≥85점)</span>
    <span style="background:rgba(0,255,136,0.15);border:1px solid rgba(0,255,136,0.3);border-radius:6px;padding:5px 12px;font-size:1.17rem;color:#00ff88;">aws-ops-plugin → PostToolUse 보안 감지</span>
    <span style="background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.3);border-radius:6px;padding:5px 12px;font-size:1.17rem;color:#f59e0b;">kiro-review → SessionStart 자동 로드</span>
  </div>
</div>
:::
:::notes
{timing: 1.5min}
하네스 엔지니어링이라는 표현은 제가 이 작업을 하면서 계속 느낀 핵심 개념입니다. AI 에이전트는 자유도가 높으면 오히려 결과가 불안정해집니다. CLAUDE.md로 프로젝트 컨텍스트를 매 세션 주입하고, Hooks로 빌드 경고나 보안 위반을 자동 감지하고, Quality Gate로 품질 미달 결과물의 배포를 차단합니다. 중요한 건 이 세 가지가 모두 선언적이라는 점입니다. 마크다운과 JSON만으로 AI의 행동 범위를 정의할 수 있습니다.
{cue: transition}
이제 제가 가장 많은 시간을 쏟은 Remarp에 대해 이야기하겠습니다.
:::

---
<!-- Slide 8: Remarp Title -->
@type: title
@transition: zoom

# Remarp
# 프레젠테이션 프레임워크

---
<!-- Slide 9: Why Remarp -->
@type: content

## Marp의 한계 → Remarp 탄생

:::html
<div style="text-align:center;margin-bottom:12px;">
  <span style="background:rgba(108,92,231,0.2);border:1px solid rgba(108,92,231,0.4);border-radius:20px;padding:6px 16px;font-size:1.3rem;">
    <span style="color:#a29bfe;font-weight:bold;">Re</span><span style="color:#999;">active </span><span style="color:#a29bfe;font-weight:bold;">Mar</span><span style="color:#999;">kdown </span><span style="color:#a29bfe;font-weight:bold;">P</span><span style="color:#999;">resentation — </span><span style="color:#00d4ff;">마크다운 → 동적 인터랙티브 HTML 생성</span>
  </span>
</div>
<div style="display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:start;">
  <div class="fragment fade-up" data-fragment-index="1" style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:10px;padding:16px;">
    <div style="color:#ef4444;font-weight:bold;font-size:1.45rem;margin-bottom:10px;">Marp 😕</div>
    <div style="color:#8b95a5;font-size:1.27rem;line-height:1.75;">
      ✗ 프래그먼트 애니메이션 없음<br>
      ✗ Canvas 애니메이션 불가<br>
      ✗ 스피커 노트 제한적<br>
      ✗ 인터랙티브 요소 불가<br>
      ✗ 테마 커스터마이징 한계
    </div>
  </div>
  <div class="fragment fade-up" data-fragment-index="2" style="color:#6c5ce7;font-size:2rem;padding-top:44px;">→</div>
  <div class="fragment fade-up" data-fragment-index="3" style="background:rgba(108,92,231,0.1);border:1px solid rgba(108,92,231,0.3);border-radius:10px;padding:16px;">
    <div style="color:#a29bfe;font-weight:bold;font-size:1.45rem;margin-bottom:10px;">Remarp ✨</div>
    <div style="color:#8b95a5;font-size:1.27rem;line-height:1.75;">
      ✓ <span style="color:#00d4ff;">{.click}</span> 인라인 프래그먼트<br>
      ✓ <span style="color:#00d4ff;">::: canvas</span> DSL 애니메이션<br>
      ✓ 풍부한 :::notes + 타이밍<br>
      ✓ :::html + :::css + :::script 블록<br>
      ✓ PPTX 테마 추출 + CSS
    </div>
  </div>
</div>
<div class="fragment fade-up" data-fragment-index="4" style="text-align:center;margin-top:10px;padding:10px;background:rgba(108,92,231,0.1);border-radius:8px;">
  <code style="color:#a29bfe;font-size:1.27rem;">remarp_to_slides.py build → 마크다운을 <span style="color:#00d4ff;">동적 인터랙티브 HTML</span>로 변환</code>
</div>
<div class="fragment fade-up" data-fragment-index="5" style="text-align:center;margin-top:8px;padding:8px 12px;background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.15);border-radius:8px;">
  <span style="color:#a29bfe;font-size:1.15rem;font-weight:bold;">레이아웃 타입 →</span>
  <code style="color:#00d4ff;font-size:1.15rem;margin-left:8px;">@type: title</code>
  <span style="color:#555;"> · </span>
  <code style="color:#00d4ff;font-size:1.15rem;">@type: content</code>
  <span style="color:#555;"> · </span>
  <code style="color:#00d4ff;font-size:1.15rem;">@type: agenda</code>
  <span style="color:#555;"> · </span>
  <code style="color:#00d4ff;font-size:1.15rem;">@type: 2column</code>
  <span style="color:#555;"> · </span>
  <code style="color:#00d4ff;font-size:1.15rem;">@type: left</code>
  <span style="color:#555;"> · </span>
  <code style="color:#00d4ff;font-size:1.15rem;">@type: right</code>
</div>
:::
:::notes
{timing: 1.5min}
Marp는 마크다운으로 슬라이드를 만드는 훌륭한 도구이지만, 실무 발표에서 필수적인 프래그먼트 애니메이션이나 인터랙티브 요소를 넣을 수 없었습니다. 그래서 Remarp를 만들었습니다. Remarp는 Reactive Markdown Presentation의 약자로, 마크다운에서 동적인 인터랙티브 HTML을 생성하는 게 핵심 목적입니다. 중괄호 .click으로 프래그먼트를 제어하고, :::canvas 블록으로 Canvas 애니메이션을 선언적으로 작성할 수 있습니다. Python 스크립트 하나로 마크다운이 동적 HTML 프레젠테이션으로 변환됩니다. 지금 이 슬라이드가 바로 Remarp로 만든 것입니다.
{cue: transition}
Remarp의 핵심 컨셉 중 하나인 Rejection Loop에 대해 알려드리겠습니다.
:::

---
<!-- Slide 10: Rejection Loop -->
@type: content

## Rejection Loop — AI의 공간 추론 한계 극복

:::css
.step-slide {
  opacity: 0;
  transform: translateX(-40px);
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.step-slide.visible {
  opacity: 1;
  transform: translateX(0);
}
.step-arrow {
  opacity: 0;
  transform: translateX(-20px);
  transition: opacity 0.3s ease 0.15s, transform 0.3s ease 0.15s;
}
.step-arrow.visible {
  opacity: 1;
  transform: translateX(0);
}
:::

:::html
<div style="display:flex;align-items:center;justify-content:center;gap:6px;margin-bottom:14px;">
  <div class="fragment step-slide" data-fragment-index="1" style="background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.3);border-radius:10px;padding:14px 18px;text-align:center;min-width:130px;">
    <div style="font-size:1.3rem;margin-bottom:4px;">✍️</div>
    <div style="color:#00d4ff;font-weight:bold;font-size:1.27rem;">Remarp 작성</div>
    <div style="color:#666;font-size:1.0rem;margin-top:4px;">마크다운 편집</div>
  </div>
  <div class="fragment step-arrow" data-fragment-index="2" style="color:#6c5ce7;font-size:1.8rem;flex-shrink:0;">→</div>
  <div class="fragment step-slide" data-fragment-index="2" style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:10px;padding:14px 18px;text-align:center;min-width:130px;">
    <div style="font-size:1.3rem;margin-bottom:4px;">🔍</div>
    <div style="color:#f59e0b;font-weight:bold;font-size:1.27rem;">validate</div>
    <div style="color:#666;font-size:1.0rem;margin-top:4px;">7가지 규칙 검증</div>
  </div>
  <div class="fragment step-arrow" data-fragment-index="3" style="color:#6c5ce7;font-size:1.8rem;flex-shrink:0;">→</div>
  <div class="fragment step-slide" data-fragment-index="3" style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:10px;padding:14px 18px;text-align:center;min-width:130px;">
    <div style="font-size:1.3rem;margin-bottom:4px;">🚨</div>
    <div style="color:#ef4444;font-weight:bold;font-size:1.27rem;">CRITICAL?</div>
    <div style="color:#666;font-size:1.0rem;margin-top:4px;">오버플로우, 겹침</div>
  </div>
  <div class="fragment step-arrow" data-fragment-index="4" style="color:#6c5ce7;font-size:1.8rem;flex-shrink:0;">→</div>
  <div class="fragment step-slide" data-fragment-index="4" style="background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:10px;padding:14px 18px;text-align:center;min-width:130px;">
    <div style="font-size:1.3rem;margin-bottom:4px;">🏗️</div>
    <div style="color:#00ff88;font-weight:bold;font-size:1.27rem;">build</div>
    <div style="color:#666;font-size:1.0rem;margin-top:4px;">HTML 생성</div>
  </div>
</div>
<div class="fragment fade-up" data-fragment-index="5" style="margin-top:4px;">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
    <div style="background:rgba(15,22,41,0.8);border-radius:8px;padding:12px;">
      <div style="color:#ef4444;font-weight:bold;font-size:1.15rem;margin-bottom:6px;">🔴 CRITICAL (빌드 차단)</div>
      <div style="color:#8b95a5;font-size:1.05rem;line-height:1.6;">
        CONTENT_OVERFLOW: 불릿 8개 이상<br>
        CANVAS_OVERLAP: 요소 겹침<br>
        CANVAS_COMPLEXITY: 시각 요소 8개+
      </div>
    </div>
    <div style="background:rgba(15,22,41,0.8);border-radius:8px;padding:12px;">
      <div style="color:#f59e0b;font-weight:bold;font-size:1.15rem;margin-bottom:6px;">🟡 WARNING (검토 권장)</div>
      <div style="color:#8b95a5;font-size:1.05rem;line-height:1.6;">
        INTERACTIVE_FIRST: 카드/탭 미사용<br>
        MISSING_NOTES: 스피커 노트 누락<br>
        STATIC_HTML: fragment 없는 HTML
      </div>
    </div>
  </div>
</div>
:::
:::notes
{timing: 1.5min}
LLM은 텍스트 기반 추론에는 뛰어나지만, 2D 캔버스 위에서 요소가 겹치는지, 정렬이 맞는지 같은 공간적 판단은 잘 못합니다. 그래서 Rejection Loop라는 외부 검증 시스템을 만들었습니다. validate 명령을 실행하면 7가지 규칙으로 마크다운을 검사합니다. CRITICAL 이슈가 있으면 빌드 자체가 차단됩니다. 이걸 통해 AI가 만든 결과물의 품질을 기계적으로 보장할 수 있습니다. 프랑켄슈타인 레이아웃을 방지하는 안전장치라고 생각하시면 됩니다.
{cue: transition}
이제 VSCode Extension 이야기로 넘어가겠습니다.
:::

---
<!-- Slide 11: VSCode Extension Title -->
@type: title
@transition: zoom

# VSCode Extension
# 개발기

---
<!-- Slide 12: VSCode Extension Features -->
@type: tabs

## Remarp VSCode Extension

### Preview Mode
:::html
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
  <div style="background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.3);border-radius:10px;padding:14px;">
    <div style="color:#00d4ff;font-weight:bold;margin-bottom:6px;">Markdown Preview</div>
    <div style="color:#8b95a5;font-size:0.78rem;line-height:1.6;">
      .remarp.md 실시간 렌더링<br>
      슬라이드 파싱 → HTML 변환<br>
      사이드바: 노트 + 이슈 배지<br>
      ←→ 키보드 네비게이션
    </div>
  </div>
  <div style="background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:10px;padding:14px;">
    <div style="color:#00ff88;font-weight:bold;margin-bottom:6px;">HTML Preview</div>
    <div style="color:#8b95a5;font-size:0.78rem;line-height:1.6;">
      빌드된 HTML 직접 로드<br>
      리소스 경로 → webview URI<br>
      CSP 자동 주입<br>
      remarp-source 메타 연결
    </div>
  </div>
</div>
:::

### Visual Edit
:::html
<div style="background:rgba(168,85,247,0.1);border:1px solid rgba(168,85,247,0.3);border-radius:10px;padding:14px;">
  <div style="color:#a855f7;font-weight:bold;margin-bottom:8px;">PPT-like 비주얼 편집 모드</div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;">
    <div style="background:rgba(15,22,41,0.6);border-radius:6px;padding:8px;text-align:center;">
      <div style="color:#00d4ff;font-size:0.8rem;font-weight:bold;">드래그</div>
      <div style="color:#666;font-size:0.7rem;">요소 위치 이동</div>
    </div>
    <div style="background:rgba(15,22,41,0.6);border-radius:6px;padding:8px;text-align:center;">
      <div style="color:#00ff88;font-size:0.8rem;font-weight:bold;">리사이즈</div>
      <div style="color:#666;font-size:0.7rem;">크기 조절</div>
    </div>
    <div style="background:rgba(15,22,41,0.6);border-radius:6px;padding:8px;text-align:center;">
      <div style="color:#f59e0b;font-size:0.8rem;font-weight:bold;">속성 패널</div>
      <div style="color:#666;font-size:0.7rem;">폰트/색상/마진</div>
    </div>
  </div>
  <div style="color:#8b95a5;font-size:0.75rem;margin-top:8px;text-align:center;">Cmd+Shift+E 또는 슬라이드 위 Edit 버튼 → 변경사항이 :::css / :::canvas 블록에 자동 기록</div>
</div>
:::

### Issue System
:::html
<div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:10px;padding:14px;">
  <div style="color:#f59e0b;font-weight:bold;margin-bottom:8px;">이슈 어노테이션 시스템</div>
  <div style="display:grid;grid-template-columns:1fr;gap:8px;">
    <div style="display:flex;align-items:center;gap:10px;">
      <div style="background:rgba(245,158,11,0.3);border-radius:4px;padding:4px 8px;font-size:0.75rem;color:#f59e0b;font-weight:bold;white-space:nowrap;">1</div>
      <div style="color:#8b95a5;font-size:0.78rem;">사이드바 프롬프트 바에서 이슈 입력 → <code style="color:#f59e0b;font-size:0.73rem;">&lt;!-- issue: 텍스트 --&gt;</code> 자동 삽입</div>
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
      <div style="background:rgba(245,158,11,0.3);border-radius:4px;padding:4px 8px;font-size:0.75rem;color:#f59e0b;font-weight:bold;white-space:nowrap;">2</div>
      <div style="color:#8b95a5;font-size:0.78rem;">노란 배지로 시각화 → × 버튼으로 개별 제거 가능</div>
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
      <div style="background:rgba(245,158,11,0.3);border-radius:4px;padding:4px 8px;font-size:0.75rem;color:#f59e0b;font-weight:bold;white-space:nowrap;">3</div>
      <div style="color:#8b95a5;font-size:0.78rem;">Claude Code에서 <code style="color:#a29bfe;font-size:0.73rem;">/slide-fix</code> → AI가 이슈 읽고 자동 수정 후 어노테이션 제거</div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 3min}
VSCode Extension은 세 가지 핵심 기능이 있습니다.

첫째, Preview 모드입니다. 마크다운과 빌드된 HTML 모두 실시간으로 프리뷰할 수 있고, 사이드바에 스피커 노트와 이슈 배지가 표시됩니다.

둘째, Visual Edit 모드입니다. Cmd+Shift+E를 누르면 PPT처럼 요소를 드래그해서 위치를 바꾸거나 크기를 조절할 수 있고, 변경사항이 자동으로 소스 마크다운의 :::css나 :::canvas 블록에 기록됩니다.

셋째, Issue Annotation 시스템입니다. 이게 제가 가장 자랑하고 싶은 기능인데요. 프리뷰 사이드바에서 "이 다이어그램 너무 복잡해" 같은 이슈를 입력하면, 소스에 HTML 주석으로 자동 삽입됩니다. 그리고 Claude Code에서 /slide-fix를 실행하면 AI가 이슈를 읽고 자동으로 수정해줍니다. 사람과 AI 사이의 피드백 루프를 Extension 안에서 완성한 거죠.
{cue: transition}
그런데 생산성 도구를 프레젠테이션만으로 끝내기엔 아쉬웠습니다. 동료와 함께 일하는 방식도 바꿔보고 싶었거든요.
:::

---
<!-- Slide 13: Ttobak — 협업 워크플로우 -->
@type: content

## 함께 일하는 방식

:::html
<div style="display:grid;grid-template-columns:1fr;gap:10px;">
  <div class="fragment fade-up" data-fragment-index="1" style="background:rgba(0,212,255,0.08);border-left:3px solid #00d4ff;border-radius:0 10px 10px 0;padding:14px 16px;display:flex;align-items:center;gap:14px;">
    <div style="min-width:36px;height:36px;background:rgba(0,212,255,0.2);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.1rem;">📝</div>
    <div>
      <div style="color:#00d4ff;font-weight:bold;font-size:1.15rem;">미팅 중 — 같은 기록을 공유</div>
      <div style="color:#8b95a5;font-size:0.98rem;margin-top:3px;">한 명이 녹음하면 실시간 자막 + 번역이 팀 전체에 공유. 미팅 끝나면 AI 요약이 SA와 AM에게 동일하게 전달됩니다.</div>
    </div>
  </div>
  <div class="fragment fade-up" data-fragment-index="2" style="background:rgba(0,255,136,0.08);border-left:3px solid #00ff88;border-radius:0 10px 10px 0;padding:14px 16px;display:flex;align-items:center;gap:14px;">
    <div style="min-width:36px;height:36px;background:rgba(0,255,136,0.2);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.1rem;">✅</div>
    <div>
      <div style="color:#00ff88;font-weight:bold;font-size:1.15rem;">미팅 후 — 액션 아이템이 명확</div>
      <div style="color:#8b95a5;font-size:0.98rem;margin-top:3px;">AI가 대화에서 액션 아이템을 추출하고 담당자를 제안합니다. "네가 하는 거 아니었어?" 가 사라집니다.</div>
    </div>
  </div>
  <div class="fragment fade-up" data-fragment-index="3" style="background:rgba(168,85,247,0.08);border-left:3px solid #a855f7;border-radius:0 10px 10px 0;padding:14px 16px;display:flex;align-items:center;gap:14px;">
    <div style="min-width:36px;height:36px;background:rgba(168,85,247,0.2);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.1rem;">🔍</div>
    <div>
      <div style="color:#a855f7;font-weight:bold;font-size:1.15rem;">고객 미팅 전 — 같은 맥락으로 준비</div>
      <div style="color:#8b95a5;font-size:0.98rem;margin-top:3px;">고객사 뉴스 크롤링 + AI 브리핑이 팀 KB에 자동 축적. AM이 발견한 기회를 SA가 기술로 뒷받침하는 흐름이 자연스러워집니다.</div>
    </div>
  </div>
  <div class="fragment fade-up" data-fragment-index="4" style="background:rgba(245,158,11,0.08);border-left:3px solid #f59e0b;border-radius:0 10px 10px 0;padding:14px 16px;display:flex;align-items:center;gap:14px;">
    <div style="min-width:36px;height:36px;background:rgba(245,158,11,0.2);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:1.1rem;">🔗</div>
    <div>
      <div style="color:#f59e0b;font-weight:bold;font-size:1.15rem;">도구 연결 — Claude Code에서 미팅 데이터 접근</div>
      <div style="color:#8b95a5;font-size:0.98rem;margin-top:3px;">MCP Server로 연동하면 Claude Code에서 "지난 미팅에서 고객이 요청한 아키텍처가 뭐였지?" 같은 질문을 바로 할 수 있습니다.</div>
    </div>
  </div>
</div>
:::
:::notes
{timing: 1min}
또박의 워크플로우는 SA와 AM이 같은 정보를 보는 것에서 시작합니다.

미팅 중에는 녹음과 실시간 자막이 공유되고, 미팅이 끝나면 AI 요약이 둘 다에게 전달됩니다. 액션 아이템도 AI가 추출해서 담당자를 제안하니까, 후속 조치가 명확해집니다.

특히 고객 인텔리전스가 핵심인데요, 고객사 관련 뉴스를 매일 크롤링해서 AI가 SA 관점의 브리핑을 만들어줍니다. AM이 영업 기회를 발견하면 SA가 기술 맥락을 이미 알고 있는 상태에서 바로 뒷받침할 수 있습니다.

그리고 이 모든 데이터를 MCP Server로 Claude Code에서도 접근할 수 있어서, 프레젠테이션 준비할 때 미팅 내용을 바로 참조할 수 있습니다.
{cue: transition}
이런 워크플로우를 가능하게 한 배경을 말씀드리겠습니다.
:::

---
<!-- Slide 14: Ttobak — 왜 만들었나 -->
@type: content

## 또박(Ttobak) — 왜 만들었나

:::html
<div style="text-align:center;margin-bottom:16px;">
  <span style="background:rgba(108,92,231,0.2);border:1px solid rgba(108,92,231,0.4);border-radius:20px;padding:6px 16px;font-size:1.2rem;color:#a29bfe;">SA + AM 협업을 위한 AI 미팅 어시스턴트</span>
</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
  <div>
    <div class="fragment fade-up" data-fragment-index="1" style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:10px;padding:14px;">
      <div style="color:#ef4444;font-weight:bold;font-size:1.27rem;margin-bottom:6px;">SA + AM 협업의 현실</div>
      <div style="color:#8b95a5;font-size:1.12rem;line-height:1.7;">
        미팅 끝나면 기억이 다름<br>
        액션 아이템 누가 맡았는지 불분명<br>
        고객사 맥락이 각자 머릿속에만 존재<br>
        뉴스/기술 동향을 따로따로 추적<br>
        고객 심층 조사도 각자 따로 수행
      </div>
    </div>
  </div>
  <div>
    <div class="fragment fade-up" data-fragment-index="2" style="background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:10px;padding:14px;">
      <div style="color:#00ff88;font-weight:bold;font-size:1.27rem;margin-bottom:6px;">함께 쓰는 도구로 해결</div>
      <div style="color:#8b95a5;font-size:1.12rem;line-height:1.7;">
        미팅 녹음 → AI가 동일한 요약 공유<br>
        액션 아이템 자동 추출 + 담당자 지정<br>
        고객 인텔리전스를 팀 KB로 축적<br>
        뉴스 브리핑을 AM과 SA가 함께 확인<br>
        <span style="color:#00ff88;">Deep Research Agent로 고객사 심층 분석</span>
      </div>
    </div>
  </div>
</div>
<div class="fragment fade-up" data-fragment-index="3" style="text-align:center;margin-top:14px;">
  <span style="color:#a29bfe;font-size:1.2rem;">ttobak.atomai.click</span>
  <span style="color:#666;font-size:1.15rem;margin-left:8px;">| Go + Next.js · 9 CDK Stacks · Bedrock Agent + Claude</span>
</div>
:::
:::notes
{timing: 1min}
프레젠테이션 도구를 만들면서 생산성이 많이 올랐는데, 한 가지 더 해결하고 싶은 문제가 있었습니다. 바로 동료와의 협업이었어요.

SA와 AM이 같은 고객 미팅에 들어가는데, 미팅이 끝나면 서로 기억하는 내용이 다릅니다. 액션 아이템도 "그거 네가 하는 거 아니었어?" 같은 상황이 생기고요. 고객사에 대한 맥락도 각자 머릿속에만 있어서, 한 명이 휴가 가면 이어받기가 어렵습니다.

그래서 미팅 녹음부터 요약, 액션 아이템 추출, 고객 인텔리전스까지 SA와 AM이 같은 도구를 보면서 일할 수 있는 프로젝트를 만들었습니다. Deep Research Agent로 고객사 심층 분석까지 가능합니다.
{cue: transition}
마지막으로 이 경험에서 배운 점을 정리하겠습니다.
:::

---
<!-- Slide 15: Lessons Learned -->
@type: content

## 배운 점

:::html
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
  <div class="fragment fade-up" data-fragment-index="1" style="background:rgba(108,92,231,0.1);border:1px solid rgba(108,92,231,0.3);border-radius:12px;padding:16px;">
    <div style="color:#a29bfe;font-size:1.3rem;margin-bottom:6px;">🎯</div>
    <div style="color:#a29bfe;font-weight:bold;font-size:1.17rem;margin-bottom:6px;">제약이 품질을 만든다</div>
    <div style="color:#8b95a5;font-size:1.0rem;line-height:1.6;">AI에게 자유를 주면 결과가 불안정합니다. Rejection Loop, Quality Gate, CLAUDE.md 같은 제약을 잘 설계하는 것이 핵심입니다.</div>
  </div>
  <div class="fragment fade-up" data-fragment-index="2" style="background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.3);border-radius:12px;padding:16px;">
    <div style="color:#00d4ff;font-size:1.3rem;margin-bottom:6px;">🔄</div>
    <div style="color:#00d4ff;font-weight:bold;font-size:1.17rem;margin-bottom:6px;">Dogfooding의 힘</div>
    <div style="color:#8b95a5;font-size:1.0rem;line-height:1.6;">자기가 만든 도구를 직접 쓰면 개선점이 명확하게 보입니다. 이 발표도 Remarp로 만들면서 버그를 3개 잡았습니다.</div>
  </div>
  <div class="fragment fade-up" data-fragment-index="3" style="background:rgba(0,255,136,0.1);border:1px solid rgba(0,255,136,0.3);border-radius:12px;padding:16px;">
    <div style="color:#00ff88;font-size:1.3rem;margin-bottom:6px;">📦</div>
    <div style="color:#00ff88;font-weight:bold;font-size:1.17rem;margin-bottom:6px;">지식을 코드로 축적</div>
    <div style="color:#8b95a5;font-size:1.0rem;line-height:1.6;">노하우가 문서에 머물면 찾기 어렵습니다. Agent와 Skill로 캡슐화하면 팀 누구나 한 줄로 활용할 수 있습니다.</div>
  </div>
  <div class="fragment fade-up" data-fragment-index="4" style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:12px;padding:16px;">
    <div style="color:#f59e0b;font-size:1.3rem;margin-bottom:6px;">🤝</div>
    <div style="color:#f59e0b;font-weight:bold;font-size:1.17rem;margin-bottom:6px;">공유가 성장을 가속</div>
    <div style="color:#8b95a5;font-size:1.0rem;line-height:1.6;">혼자 쓰려고 만들었지만, 공유하니까 피드백으로 더 좋아졌습니다. 오늘 이 톡도 그 과정의 일부입니다.</div>
  </div>
</div>
:::

:::notes
{timing: 1.5min}
이 프로젝트를 하면서 가장 크게 배운 것은 네 가지입니다.

첫째, AI에게는 자유보다 잘 설계된 제약이 중요합니다. Rejection Loop, Quality Gate 같은 메커니즘이 결과 품질을 만듭니다.

둘째, Dogfooding의 힘입니다. 이 발표 자체를 Remarp로 만들면서 실제로 버그도 발견하고 개선점도 찾았습니다.

셋째, 노하우를 문서가 아닌 코드로 축적하면 팀 전체가 활용할 수 있습니다.

넷째, 공유하면 피드백이 돌아오고, 그 피드백이 도구를 더 좋게 만듭니다.
{cue: transition}
마지막 슬라이드입니다.
:::

---
<!-- Slide 16: Thank You -->
@type: content

# 감사합니다!

:::html
<div style="text-align:center;margin-top:20px;">
  <div style="display:inline-flex;gap:16px;flex-wrap:wrap;justify-content:center;">
    <div style="background:rgba(108,92,231,0.15);border:1px solid rgba(108,92,231,0.3);border-radius:8px;padding:10px 18px;">
      <div style="color:#a29bfe;font-size:0.8rem;font-weight:bold;">oh-my-cloud-skills</div>
      <div style="color:#666;font-size:0.7rem;">github.com/Atom-oh</div>
    </div>
    <div style="background:rgba(0,212,255,0.15);border:1px solid rgba(0,212,255,0.3);border-radius:8px;padding:10px 18px;">
      <div style="color:#00d4ff;font-size:0.8rem;font-weight:bold;">또박(Ttobak)</div>
      <div style="color:#666;font-size:0.7rem;">ttobak.atomai.click</div>
    </div>
  </div>
  <div style="color:#8b95a5;font-size:0.85rem;margin-top:20px;">
    "만들어 보고, 직접 쓰고, 공유하자"
  </div>
  <div style="color:#666;font-size:0.75rem;margin-top:8px;">
    오준석 (Junseok Oh) · Sr. Solutions Architect · AWS
  </div>
</div>
:::

:::notes
{timing: 0.5min}
오늘 보여드린 플러그인과 또박 모두 GitHub에 있으니 관심 있으시면 살펴보시고, 궁금한 점은 편하게 물어봐 주세요. 감사합니다!
:::
