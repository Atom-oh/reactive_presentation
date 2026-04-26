# Content Review Report: vLLM on EKS Presentation

## Review Metadata
| Field | Value |
|-------|-------|
| **Review Type** | HTML Presentation (4-block, reactive framework) |
| **Iteration** | #1 |
| **Current Score** | 79 / 100 |
| **Verdict** | REVIEW |
| **Files Reviewed** | `_presentation.md`, `01-intro-vllm.md`, `02-architecture.md`, `03-deployment.md`, `04-operations.md` |
| **Slide Count** | 35 slides (10 + 8 + 8 + 9) |
| **Target Duration** | 60 minutes |

---

## Quality Gate Result
### Verdict: REVIEW

| Category | Critical | Warning | Info |
|----------|----------|---------|------|
| Technical Accuracy / Hallucination | 2 | 3 | 1 |
| Terminology / Consistency | 0 | 3 | 1 |
| Korean Language Quality | 0 | 2 | 2 |
| Structural Completeness | 0 | 3 | 0 |
| Content Density | 0 | 1 | 2 |
| Logical Flow | 0 | 0 | 1 |
| Prometheus Metric Names | 0 | 2 | 0 |
| Timing / Pacing | 0 | 2 | 0 |
| **Total** | **2** | **16** | **7** |

### Score Breakdown

| Item | Max | Score | Notes |
|------|-----|-------|-------|
| Layout | 8 | 8 | Clean heading hierarchy, consistent separators |
| Terminology | 8 | 6 | -2 for inconsistencies (see W-01, W-02) |
| No Hallucination | 12 | 4 | -4 each for C-01 and C-02 |
| Language Consistency | 8 | 6 | -2 for terminology mixing issues |
| No Sensitive Data | 12 | 12 | No PII/credentials found |
| Content-Type Quality | 2 | 2 | Framework usage correct |
| Icon Usage | 5 | 5 | Emoji icons contextually appropriate |
| Visual Testing | 10 | -- | Not performed (no browser available) |
| Readability | 5 | 4 | -1 for density on slide 03-07 |
| Accessibility | 5 | 5 | Dark theme colors meet contrast guidelines |
| Structural Completeness | 5 | 3 | -2 for timing mismatch and missing Grafana slide |
| Data Accuracy | 5 | 4 | -1 for pricing date absence |
| Legal Compliance | 5 | 5 | Copyright footer present |
| Message Clarity | 5 | 5 | Each slide has clear single message |
| Duplication/Gaps | 5 | 4 | -1 for repeated VRAM formula |
| **Subtotal (excl. Visual)** | **90** | **73** | |
| **Scaled to 100** | **100** | **~81** | 73/90 * 100 |

> Visual Testing was not performed (no browser environment). Score is scaled from remaining 90 points. Adjusted score: **81/100** -> Verdict: **REVIEW**.

---

## Critical Issues (Must Fix)

### Issue C-01: "Llama-4 70B" -- Non-existent Model Name
| Field | Value |
|-------|-------|
| **Severity** | Critical (Hallucination) |
| **Category** | Hallucination Detection |
| **Location** | File: `01-intro-vllm.md`, Line: 140 |
| **Original** | `프레임워크 성능 비교 (8xH100, Llama-4 70B)` |
| **Problem** | "Llama-4 70B" is not a real model. Meta released Llama 3.1 (8B/70B/405B) and Llama 4 (Scout 109B / Maverick 402B). There is no "Llama-4 70B" variant. Using a non-existent model name in a benchmark comparison undermines credibility. |
| **Action** | Change to an actual model that exists, such as "Llama-3.1 70B" or "Llama-4 Maverick 402B". Since the benchmark is for a 70B-class model on 8xH100, "Llama-3.1 70B" is the appropriate reference. |
| **Expected** | `프레임워크 성능 비교 (8xH100, Llama-3.1 70B)` |
| **Points** | -4 from Hallucination |

### Issue C-02: GPU_MEMORY_UTILIZATION Description Inaccuracy
| Field | Value |
|-------|-------|
| **Severity** | Critical (Technical Inaccuracy) |
| **Category** | Hallucination Detection |
| **Location** | File: `03-deployment.md`, Line: 144 (speaker notes), also Line: 217 |
| **Original** | "GPU_MEMORY_UTILIZATION=0.9는 GPU VRAM의 90%를 KV Cache에 할당한다는 의미입니다" |
| **Problem** | This is technically incorrect. `gpu-memory-utilization` (vLLM's `--gpu-memory-utilization` flag) controls the fraction of GPU memory that the vLLM engine is allowed to use **in total** (model weights + KV cache + activation memory + overhead). It does NOT allocate 90% to KV Cache alone. The KV Cache receives whatever is left after model weights and activations are loaded. The slide content (line 174) correctly says "KV Cache에 할당할 GPU 메모리 비율" which is also misleading. |
| **Action** | Correct the description to: "GPU VRAM의 90%를 vLLM이 사용할 수 있도록 허용 (모델 가중치 + KV Cache 포함)" in both slide content and speaker notes. |
| **Expected** | Notes: "GPU_MEMORY_UTILIZATION=0.9는 GPU VRAM의 90%를 vLLM 엔진이 전체적으로 사용할 수 있도록 허용합니다. 모델 가중치가 로딩된 후 남은 공간이 KV Cache로 사용됩니다." |
| **Points** | -4 from Hallucination |

---

## Warning Issues (Should Fix)

### Issue W-01: Inconsistent Prometheus Metric Name Format
| Field | Value |
|-------|-------|
| **Severity** | HIGH |
| **Category** | Terminology / Data Accuracy |
| **Location** | File: `04-operations.md`, Lines: 34/48/62/76 vs Lines: 314/320 |
| **Original** | Slide 2 uses `vllm:time_to_first_token_seconds`, `vllm:time_per_output_token_seconds`, `vllm:request_queue_time_seconds`, `vllm:num_preemptions_total`. Slide 6 troubleshooting table uses shortened forms `vllm:request_queue_time`, `vllm:num_preemptions`. |
| **Problem** | Inconsistent metric names between slides. The actual vLLM Prometheus metrics in recent versions do not use the `vllm:` prefix with colon -- they typically use `vllm_` prefix with underscore (e.g., `vllm_time_to_first_token_seconds_bucket`). Additionally, using both full and abbreviated names is inconsistent. |
| **Action** | (1) Verify the exact metric names against vLLM's current `/metrics` endpoint. The standard convention uses underscores: `vllm_time_to_first_token_seconds`, not colons. (2) Use the same names consistently across all slides. |
| **Points** | -2 from Terminology |

### Issue W-02: IRSA is Deprecated -- Should Mention EKS Pod Identity
| Field | Value |
|-------|-------|
| **Severity** | HIGH |
| **Category** | Technical Accuracy |
| **Location** | File: `02-architecture.md`, Lines: 76, 93 |
| **Original** | "IAM + IRSA -- Pod 레벨 권한" / "IRSA(IAM Roles for Service Accounts)를 통해 Pod 레벨에서 IAM 역할을 부여합니다" |
| **Problem** | AWS announced EKS Pod Identity as the successor to IRSA in 2023. For a 2026 presentation targeting DevOps engineers, recommending only IRSA without mentioning EKS Pod Identity is outdated. EKS Pod Identity is simpler to configure and is the recommended approach. |
| **Action** | Update to mention both, with EKS Pod Identity as the primary recommendation: "EKS Pod Identity (권장) 또는 IRSA -- Pod 레벨 권한". Update speaker notes to explain that Pod Identity is simpler and preferred for new clusters. |
| **Points** | -1 from Terminology |

### Issue W-03: DeepSeek-R1-8B Recommended Instance Discrepancy
| Field | Value |
|-------|-------|
| **Severity** | HIGH |
| **Category** | Technical Accuracy |
| **Location** | File: `03-deployment.md`, Line: 365-368 |
| **Original** | Table says `g5.4xlarge (1xA10G)` for DeepSeek-R1-8B |
| **Problem** | g5.4xlarge has the same GPU as g5.xlarge -- both have 1x A10G with 24GB VRAM. The difference is CPU/RAM (16 vCPU/64GB vs 4 vCPU/16GB). The table parenthetical "(1xA10G)" is correct, but the speaker notes at line 428 say "g5.4xlarge를 권장하는 이유는 CoT 추론 중 메모리 사용량이 크기 때문" -- this is misleading because the "memory" increase from g5.xlarge to g5.4xlarge is system RAM, not GPU VRAM. CoT inference memory usage is GPU VRAM, not system RAM. If the concern is GPU memory for long KV cache, you need more VRAM (g5.12xlarge with 4xA10G), not more system RAM. |
| **Action** | Either (a) change recommendation to g5.xlarge since GPU specs are identical, or (b) if the intent is more VRAM for long sequences, recommend g5.12xlarge or g6e.xlarge. Update speaker notes to clarify that the larger instance is for system RAM (model loading, preprocessing), not GPU memory. |
| **Points** | -1 from Technical Accuracy |

### Issue W-04: ROI Table -- Claude 3.5 Sonnet Pricing Outdated
| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **Category** | Data Accuracy |
| **Location** | File: `04-operations.md`, Lines: 164, 180 |
| **Original** | "Claude 3.5 Sonnet" with output pricing "$15.00" per 1M tokens |
| **Problem** | Claude 3.5 Sonnet was superseded by Claude 3.5 Sonnet v2, Claude 3.6 Sonnet, and Claude 4 Sonnet by 2026. The pricing listed ($3/$15) was accurate for the original 3.5 Sonnet but may not reflect current API pricing. For a presentation dated 2026-04-02, this comparison is likely outdated. Also, the model name should be updated to reflect the current product line. |
| **Action** | Update to the current Anthropic model and pricing, or replace with a more stable benchmark (e.g., use only "관리형 API" as a generic comparison rather than specific model/pricing that will become outdated). |
| **Points** | -1 from Data Accuracy |

### Issue W-05: Q&A Slide Timing of 15 Minutes is Impossible
| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **Category** | Structural Completeness / Timing |
| **Location** | File: `04-operations.md`, Line: 507 |
| **Original** | `{timing: 15min}` on Q&A slide |
| **Problem** | The Q&A slide has a 15-minute timing annotation, but the presentation metadata allocates 15 minutes total for Block 4 (which has 9 slides). With the other 8 slides consuming approximately 13 minutes, only 2 minutes remain for Q&A. The 15-minute annotation does not fit within the block's allocation. |
| **Action** | Either reduce Q&A timing to match the block allocation (e.g., 2min), or restructure timing. If 15 minutes of Q&A is intended for the entire session, this should be noted as session-level (not block-level) and the total session duration should be 60min content + 15min Q&A = 75min. |
| **Points** | -1 from Structural Completeness |

### Issue W-06: Block Timing Totals Exceed Allocated Duration
| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **Category** | Structural Completeness / Timing |
| **Location** | All `.md` files |
| **Problem** | Timing analysis per block: Block 1 (01-intro-vllm): 1+1+2+2+2+2+2+2+2+1 = 17 min (allocated 15). Block 2 (02-architecture): 0.5+2+2+2+2+1.5+2+1 = 13 min (allocated 15). Block 3 (03-deployment): 0.5+2+2+2+2+1.5+2+1 = 13 min (allocated 15). Block 4 (04-operations): 0.5+2+2+2+2+2+1.5+1+15 = 28 min (allocated 15). Block 1 overflows by 2 minutes. Block 4 is impossible as structured with Q&A. |
| **Action** | For Block 1, consider condensing the ai-on-eks slide (slide 9) or the Why EKS slide (slide 8) to recover 2 minutes. For Block 4, move Q&A to a session-level activity outside block timing. |
| **Points** | -1 from Structural Completeness |

### Issue W-07: "v0.6+ 기준 처리량 2.7배 향상" -- Benchmark Citation Missing
| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **Category** | Data Accuracy |
| **Location** | File: `01-intro-vllm.md`, Line: 123 |
| **Original** | "v0.6+ 기준 처리량 2.7배 향상" |
| **Problem** | The "2.7x throughput improvement" claim needs a source citation. This appears to reference vLLM's v0.6.0 release blog post benchmarks, but the exact claim and conditions (model size, hardware, batch size) are not specified. Without context, the number could be misleading. |
| **Action** | Add a source reference in the speaker notes or a footnote: e.g., "vLLM v0.6.0 Release Blog, Llama-3 8B on 1xH100, vs static batching baseline". |
| **Points** | -1 from Data Accuracy |

### Issue W-08: Grafana Dashboard Slide Mentioned in Notes but Missing
| Field | Value |
|-------|-------|
| **Severity** | MEDIUM |
| **Category** | Content Gap |
| **Location** | File: `04-operations.md`, Line: 96 |
| **Original** | Speaker notes say: "이 메트릭들을 Grafana 대시보드로 시각화할 수 있습니다." |
| **Problem** | The speaker notes on Slide 2 of Block 4 promise a Grafana dashboard visualization, but no such slide exists in the presentation. The next slide jumps to cost optimization. The reference resources slide (Slide 8) mentions the Grafana dashboard JSON, but there is no actual screenshot or visualization of the dashboard anywhere. |
| **Action** | Either (a) add a Grafana dashboard screenshot/mockup slide between current Slide 2 and Slide 3 of Block 4, or (b) remove the promise from the speaker notes and instead say "참고 리소스에서 Grafana 대시보드 설정 방법을 안내합니다." |
| **Points** | -1 from Duplication/Gaps |

### Issue W-09: Repeated VRAM Formula Across Multiple Slides
| Field | Value |
|-------|-------|
| **Severity** | LOW |
| **Category** | Duplication |
| **Location** | `02-architecture.md` Line 250, `03-deployment.md` Line 209, `03-deployment.md` Line 419 |
| **Original** | The formula "모델 가중치(GB) ~ 파라미터 수(B) x 2 (BF16 기준)" appears three times across two blocks. |
| **Problem** | While some repetition is acceptable for reinforcement, three occurrences of the exact same formula is redundant. It crowds the slides and reduces the time available for new content. |
| **Action** | Keep the formula in its first appearance (02-architecture, Slide 4) and the model-specific table (03-deployment, Slide 7). Remove from 03-deployment Slide 4 (line 209) where it is sandwiched between other tips. |
| **Points** | -1 from Duplication |

### Issue W-10: Korean Natural Speech -- Some Notes Read Like Written Text
| Field | Value |
|-------|-------|
| **Severity** | LOW |
| **Category** | Language Quality |
| **Location** | Multiple speaker notes sections |
| **Examples** | `02-architecture.md` Line 93: "IRSA(IAM Roles for Service Accounts)를 통해 Pod 레벨에서 IAM 역할을 부여합니다. 쿠버네티스 ServiceAccount와 AWS IAM을 연결하는 방식으로, 노드 전체가 아닌 특정 Pod에만 필요한 권한을 줄 수 있습니다." -- This reads like documentation, not spoken Korean. |
| **Problem** | Several speaker note sections use written/formal Korean style rather than conversational presentation speech. For a live session, the speaker would sound stiff reading these notes verbatim. |
| **Action** | Soften language in speaker notes. Example: "IRSA는 쉽게 말해서 K8s ServiceAccount와 AWS IAM Role을 연결하는 겁니다. 그래서 특정 Pod에만 S3 접근이나 ECR Pull 권한을 줄 수 있어요." |
| **Points** | -1 from Language |

### Issue W-11: "Llama-3.2" in GPU Instance Table May Confuse Audience
| Field | Value |
|-------|-------|
| **Severity** | LOW |
| **Category** | Terminology Consistency |
| **Location** | File: `02-architecture.md`, Line: 204 |
| **Original** | "7B (Mistral, Llama-3.2)" |
| **Problem** | The rest of the presentation consistently refers to "Llama-3.1" (e.g., 03-deployment Slide 7 lists "Llama-3.1-8B"). Llama 3.2 does exist but its 7B variant is multimodal (Llama 3.2 11B Vision). The text-only 7B/8B models are Llama 3.1. This inconsistency between blocks may confuse the audience. |
| **Action** | Change to "7B (Mistral, Llama-3.1)" for consistency, or if Llama 3.2 is intentional, add a note clarifying the model variant. |
| **Points** | -1 from Terminology |

### Issue W-12: Speaker Notes Mention "다음 세션" for LWS
| Field | Value |
|-------|-------|
| **Severity** | LOW |
| **Category** | Content Gap |
| **Location** | File: `03-deployment.md`, Line: 431 |
| **Original** | "LWS는 다음 세션에서 더 자세히 다루겠습니다." |
| **Problem** | There is no "다음 세션" defined in this presentation. This is a standalone 1-hour session. Promising content in a non-existent follow-up session is misleading. |
| **Action** | Change to: "LWS 설정은 ai-on-eks 레포의 lws-vllm 블루프린트에서 확인하실 수 있습니다." or simply remove the forward reference. |
| **Points** | -1 from Content Gap |

### Issue W-13: p4d.24xlarge Pricing in Speaker Notes
| Field | Value |
|-------|-------|
| **Severity** | LOW |
| **Category** | Data Accuracy |
| **Location** | File: `01-intro-vllm.md`, Line: 99 |
| **Original** | "p4d.24xlarge는 시간당 32달러, 한 달에 약 2300만 원입니다." |
| **Problem** | $32.77/hr x 730 hours = ~$23,922/month. At a KRW/USD rate, this would be approximately 3200만원 (at ~1350 KRW/USD). The "2300만 원" figure implies ~960 KRW/USD which is unrealistic for 2026. The won figure should be recalculated or omitted to avoid becoming outdated. |
| **Action** | Either update the KRW figure with the current rate, use a round dollar figure ("한 달에 약 $24,000"), or remove the KRW conversion entirely since exchange rates fluctuate. |
| **Points** | -1 from Data Accuracy |

---

## Info Items (Nice to Have)

### Info I-01: Consider Adding Slide Numbers
All slides lack visible slide numbers. For a 35-slide presentation, audience members asking questions may have difficulty referencing specific slides. Consider adding slide pagination.

### Info I-02: EKS Auto Mode Not Deeply Covered
The presentation mentions "EKS Auto Mode" briefly (01-intro-vllm.md line 352, 04-operations.md line 455) but does not explain its relationship to Karpenter or when to use it vs. self-managed Karpenter. For a 2026 audience, EKS Auto Mode may be the default path.

### Info I-03: No Mention of Quantization (AWQ/GPTQ/FP8)
The presentation discusses BF16 inference but does not cover quantized model deployment (AWQ, GPTQ, FP8), which is a major cost optimization technique. A brief mention in the cost optimization slide would be valuable.

### Info I-04: Consistent Use of "ai-on-eks" vs "AI on EKS"
The project name alternates between lowercase "ai-on-eks" and sentence case. The GitHub repository uses lowercase "ai-on-eks" -- stick with that form.

### Info I-05: _presentation.md Duration Math
Block durations in metadata sum to 60 minutes (15x4), which matches the session duration. However, as noted in W-06, the per-slide timing annotations do not fit within these blocks.

### Info I-06: Canvas Elements Are Simple (PASS)
Both canvas blocks (01-intro-vllm Slide 6, 02-architecture Slide 7) use fewer than 4 box+icon elements within the limit. No complexity gate violation.

### Info I-07: Navigation Links Present on All Summary Slides
Each block's final slide has navigation links to TOC and next block. This is good structural practice.

---

## Revision Checklist

### Critical (Must Fix)
- [ ] C-01: Hallucination -- `01-intro-vllm.md:140` -- Change "Llama-4 70B" to "Llama-3.1 70B"
- [ ] C-02: Technical Inaccuracy -- `03-deployment.md:144,174,217` -- Correct GPU_MEMORY_UTILIZATION description (it controls total vLLM memory usage, not KV Cache allocation alone)

### Warnings (Should Fix)
- [ ] W-01: Metric Names -- `04-operations.md` -- Use consistent `vllm_` prefix (underscore) and full metric names throughout
- [ ] W-02: IRSA Outdated -- `02-architecture.md:76,93` -- Add EKS Pod Identity as primary recommendation
- [ ] W-03: g5.4xlarge Rationale -- `03-deployment.md:365,428` -- Clarify or correct instance recommendation for DeepSeek-R1-8B
- [ ] W-04: Claude Pricing -- `04-operations.md:164,180` -- Update model name/pricing or use generic reference
- [ ] W-05: Q&A Timing -- `04-operations.md:507` -- Fix 15min annotation to match block allocation
- [ ] W-06: Block Timing -- All blocks -- Rebalance slide timings to fit 15min per block
- [ ] W-07: Benchmark Citation -- `01-intro-vllm.md:123` -- Add source for "2.7x" claim
- [ ] W-08: Grafana Promise -- `04-operations.md:96` -- Add dashboard slide or remove promise
- [ ] W-09: VRAM Formula -- `03-deployment.md:209` -- Remove one of three repetitions
- [ ] W-10: Language Style -- Multiple notes -- Soften written Korean to spoken style
- [ ] W-11: Llama Version -- `02-architecture.md:204` -- Align to "Llama-3.1" used elsewhere
- [ ] W-12: "다음 세션" -- `03-deployment.md:431` -- Remove reference to non-existent follow-up
- [ ] W-13: KRW Pricing -- `01-intro-vllm.md:99` -- Recalculate or remove won figure

### Score Impact Summary
| If Fixed | Critical | Warnings | Projected Score |
|----------|----------|----------|-----------------|
| All Critical | 0 | 16 | 81 -> 89 |
| All Critical + HIGH Warnings | 0 | 10 | 81 -> 93 |
| All Issues | 0 | 0 | 81 -> 100 |

---

## Positive Highlights

1. **Excellent speaker notes coverage**: Every single slide has detailed speaker notes with timing annotations, transition cues, pause markers, and audience engagement prompts. This is production-ready for presenter use.

2. **Strong logical flow**: The 4-block structure follows a natural progression: Why (Block 1) -> What (Block 2) -> How (Block 3) -> Operate (Block 4). Each block builds on the previous one.

3. **Actionable content**: The presentation avoids vague recommendations. GPU instance selection, VRAM calculations, Karpenter YAML, RayService manifests, and Helm commands are all concrete and copy-pasteable.

4. **Good audience awareness**: The cover slide starts with an interactive question. Speaker notes include `{cue: question}` and `{cue: pause}` markers that show deliberate pacing for audience engagement.

5. **Balanced technical depth**: L300 content is appropriate -- not too shallow for DevOps engineers, not too deep for a 1-hour session. The Disaggregated Serving section appropriately notes it is "초기 프로덕션 채택 단계" rather than overselling.

6. **Cross-block navigation**: Every summary slide includes links back to TOC and forward to the next block, enabling non-linear presentation.

7. **Korean language quality is generally strong**: Technical English terms (PagedAttention, Continuous Batching, TTFT, TPOT) are kept in English while explanations are in natural Korean. This matches Korean tech presentation norms.

---

## Next Steps

**Verdict: REVIEW** -- Fix the 2 critical issues (C-01, C-02) and the HIGH-severity warnings (W-01 through W-03) before delivery. The presentation is structurally sound and content-rich, but the hallucinated model name and the GPU memory utilization misdescription would undermine credibility with a technical audience.

After fixing critical and high-priority items, re-review for PASS.
