---
remarp: true
block: 02-architecture
---

---
<!-- Slide 1: Part 2 섹션 헤더 (Section) -->
@type: section

# Part 2 — EKS 아키텍처 & 인프라

Inference-Ready Cluster 구성, GPU 스택, Karpenter 동작 원리

:::notes
{timing: 0.5min}
Part 2에서는 EKS 위에 LLM 서빙 인프라를 구축하는 데 필요한 컴포넌트들을 차례로 살펴보겠습니다.
클러스터 전체 아키텍처부터 시작해서, 6가지 배포 패턴 비교, GPU 인스턴스 선택 가이드, Terraform 배포, 그리고 Karpenter 동작 원리까지 다룹니다.
{cue: transition}
시작합니다.
:::

---
<!-- Slide 2: 전체 클러스터 아키텍처 (Content with HTML) -->
@type: content
@title: Inference-Ready Cluster 전체 아키텍처

:::html
<div style="display:grid;grid-template-columns:1fr auto 1fr;gap:16px;align-items:start;height:440px;">
  <!-- Left: VPC/EKS -->
  <div style="background:#0d1a35;border:1px solid #41b3ff;border-radius:12px;padding:16px;">
    <div style="color:#41b3ff;font-weight:700;font-size:14px;margin-bottom:12px;">VPC + EKS Cluster</div>
    <div data-fragment-index="1" style="background:#162840;border-radius:8px;padding:10px;margin-bottom:10px;font-size:12px;color:#bbb;">
      <div style="color:#41b3ff;font-weight:700;margin-bottom:4px;">EKS Control Plane (Managed)</div>
      <div>API Server | etcd | Scheduler | 99.95% SLA</div>
    </div>
    <div data-fragment-index="2" style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px;">
      <div style="background:#1a2e1a;border:1px solid #06d6a0;border-radius:6px;padding:8px;font-size:11px;text-align:center;color:#06d6a0;">
        <div style="font-weight:700;">CPU Nodes</div>
        <div style="color:#bbb;margin-top:3px;">System Pods<br>Karpenter</div>
      </div>
      <div style="background:#2e1a1a;border:1px solid #ff9900;border-radius:6px;padding:8px;font-size:11px;text-align:center;color:#ff9900;">
        <div style="font-weight:700;">GPU Nodes</div>
        <div style="color:#bbb;margin-top:3px;">vLLM Pods<br>g5/g6/p4d/p5</div>
      </div>
    </div>
    <div data-fragment-index="3" style="background:#162840;border-radius:6px;padding:10px;font-size:12px;">
      <div style="color:#41b3ff;font-weight:700;margin-bottom:4px;">애드온 (자동 설치)</div>
      <div style="color:#bbb;font-size:11px;line-height:1.8;">
        KubeRay Operator | NVIDIA Device Plugin<br>
        Karpenter | Prometheus + Grafana<br>
        AWS LB Controller | EBS/EFS CSI
      </div>
    </div>
  </div>
  <!-- Middle: Arrow -->
  <div style="display:flex;flex-direction:column;justify-content:center;align-items:center;gap:12px;padding:8px;">
    <div style="color:#bbb;font-size:22px;">⟷</div>
  </div>
  <!-- Right: AWS Services -->
  <div style="background:#0d1a1a;border:1px solid #06d6a0;border-radius:12px;padding:16px;">
    <div style="color:#06d6a0;font-weight:700;font-size:14px;margin-bottom:12px;">AWS 관리 서비스</div>
    <div style="display:flex;flex-direction:column;gap:8px;">
      <div data-fragment-index="4" style="background:#162828;border-radius:6px;padding:8px;font-size:12px;">
        <span style="color:#06d6a0;font-weight:700;">ECR</span> <span style="color:#bbb;">— 컨테이너 이미지</span>
      </div>
      <div data-fragment-index="4" style="background:#162828;border-radius:6px;padding:8px;font-size:12px;">
        <span style="color:#06d6a0;font-weight:700;">S3</span> <span style="color:#bbb;">— 모델 아티팩트 캐시</span>
      </div>
      <div data-fragment-index="4" style="background:#162828;border-radius:6px;padding:8px;font-size:12px;">
        <span style="color:#06d6a0;font-weight:700;">EFS</span> <span style="color:#bbb;">— 공유 모델 스토리지</span>
      </div>
      <div data-fragment-index="5" style="background:#162828;border-radius:6px;padding:8px;font-size:12px;">
        <span style="color:#ff9900;font-weight:700;">Secrets Manager</span> <span style="color:#bbb;">— HF Token 보안 관리</span>
      </div>
      <div data-fragment-index="5" style="background:#162828;border-radius:6px;padding:8px;font-size:12px;">
        <span style="color:#ff9900;font-weight:700;">IAM + IRSA</span> <span style="color:#bbb;">— Pod 레벨 권한</span>
      </div>
      <div data-fragment-index="5" style="background:#162828;border-radius:6px;padding:8px;font-size:12px;">
        <span style="color:#ff9900;font-weight:700;">CloudWatch</span> <span style="color:#bbb;">— 로그 & 감사 추적</span>
      </div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 2min}
전체 아키텍처를 보면 크게 두 부분입니다. 왼쪽은 EKS 클러스터, 오른쪽은 AWS 관리 서비스입니다.
EKS 클러스터 안에는 CPU 노드 그룹과 GPU 노드 그룹이 있습니다. CPU 노드에는 Karpenter, Prometheus 같은 시스템 Pod들이 올라가고, GPU 노드에는 vLLM Pod들이 올라갑니다.
GPU 노드는 Karpenter가 관리합니다. Pod이 Pending 상태가 되면 자동으로 EC2 인스턴스를 생성하고, Pod이 없어지면 인스턴스를 종료합니다.
{cue: pause}
오른쪽 AWS 서비스들은 클러스터를 지원합니다. ECR에서 컨테이너 이미지를 가져오고, EFS로 모델 파일을 공유하고, Secrets Manager로 HuggingFace 토큰을 안전하게 관리합니다.
IRSA(IAM Roles for Service Accounts)를 통해 Pod 레벨에서 IAM 역할을 부여합니다. 쿠버네티스 ServiceAccount와 AWS IAM을 연결하는 방식으로, 노드 전체가 아닌 특정 Pod에만 필요한 권한을 줄 수 있습니다.
{cue: transition}
이 아키텍처 위에서 어떤 배포 패턴을 쓸지 결정해야 합니다.
:::

---
<!-- Slide 3: 6가지 배포 패턴 비교 (Tab Content) -->
@type: content
@title: 6가지 vLLM 배포 패턴 비교

:::html
<table style="width:100%;border-collapse:collapse;font-size:12px;margin-bottom:12px;">
  <thead>
    <tr style="background:#232f4a;">
      <th style="padding:10px;color:#ff9900;text-align:left;">배포 패턴</th>
      <th style="padding:10px;color:#ff9900;">적합 시나리오</th>
      <th style="padding:10px;color:#ff9900;">복잡도</th>
      <th style="padding:10px;color:#ff9900;">스케일링</th>
      <th style="padding:10px;color:#ff9900;">GPU</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#1a283a;border:2px solid #41b3ff;">
      <td style="padding:9px;color:#41b3ff;font-weight:700;">Ray-vLLM ⭐ 권장</td>
      <td style="padding:9px;color:#bbb;">프로덕션, 자동 스케일링</td>
      <td style="padding:9px;color:#06d6a0;text-align:center;">중간</td>
      <td style="padding:9px;color:#bbb;text-align:center;">RayServe 내장</td>
      <td style="padding:9px;color:#bbb;text-align:center;">1+</td>
    </tr>
    <tr style="background:#15152a;">
      <td style="padding:9px;color:#ddd;">vLLM Standalone</td>
      <td style="padding:9px;color:#bbb;">PoC, 빠른 시작</td>
      <td style="padding:9px;color:#06d6a0;text-align:center;">낮음</td>
      <td style="padding:9px;color:#bbb;text-align:center;">HPA</td>
      <td style="padding:9px;color:#bbb;text-align:center;">1+</td>
    </tr>
    <tr style="background:#1a1a2e;">
      <td style="padding:9px;color:#ddd;">Triton-vLLM</td>
      <td style="padding:9px;color:#bbb;">멀티모델, A/B 테스트</td>
      <td style="padding:9px;color:#ff9900;text-align:center;">높음</td>
      <td style="padding:9px;color:#bbb;text-align:center;">HPA + Custom</td>
      <td style="padding:9px;color:#bbb;text-align:center;">1+/모델</td>
    </tr>
    <tr style="background:#15152a;">
      <td style="padding:9px;color:#ddd;">AIBrix-vLLM</td>
      <td style="padding:9px;color:#bbb;">관리형, 라우팅 최적화</td>
      <td style="padding:9px;color:#06d6a0;text-align:center;">낮음</td>
      <td style="padding:9px;color:#bbb;text-align:center;">내장 옵티마이저</td>
      <td style="padding:9px;color:#bbb;text-align:center;">1+</td>
    </tr>
    <tr style="background:#1a1a2e;">
      <td style="padding:9px;color:#ddd;">LWS-vLLM</td>
      <td style="padding:9px;color:#bbb;">초대형 모델 (405B+)</td>
      <td style="padding:9px;color:#ef476f;text-align:center;">높음</td>
      <td style="padding:9px;color:#bbb;text-align:center;">멀티노드</td>
      <td style="padding:9px;color:#bbb;text-align:center;">4+ 노드</td>
    </tr>
    <tr style="background:#15152a;">
      <td style="padding:9px;color:#ddd;">Dynamo-vLLM</td>
      <td style="padding:9px;color:#bbb;">KV-aware 라우팅</td>
      <td style="padding:9px;color:#ef476f;text-align:center;">매우 높음</td>
      <td style="padding:9px;color:#bbb;text-align:center;">SLA 기반</td>
      <td style="padding:9px;color:#bbb;text-align:center;">2+</td>
    </tr>
  </tbody>
</table>
<div style="background:#1a2035;border:1px solid #41b3ff;border-radius:8px;padding:14px;">
  <div style="color:#41b3ff;font-weight:700;font-size:14px;margin-bottom:6px;">⭐ Ray-vLLM 권장 이유</div>
  <div style="color:#bbb;font-size:13px;line-height:1.8;">
    RayServe 오토스케일링 내장 (요청 수 기반 자동 확장) |
    Karpenter와 연동하여 GPU 노드 자동 프로비저닝 |
    Helm Chart 3줄로 배포 가능 (inference-charts) |
    프로덕션 환경에서 가장 검증된 패턴
  </div>
</div>
:::

:::notes
{timing: 2min}
ai-on-eks에는 6가지 vLLM 배포 패턴이 있습니다.
대부분의 경우 Ray-vLLM을 추천합니다. RayServe가 오토스케일링을 내장하고 있어서 별도의 HPA 설정 없이도 요청 수 기반으로 자동 확장됩니다.
{cue: pause}
70B 이상의 초대형 모델은 LWS-vLLM을 사용해야 합니다. 단일 노드의 GPU 메모리로는 모델이 안 올라가기 때문에 여러 노드에 모델을 분산합니다. LeaderWorkerSet은 이를 위한 K8s 컨트롤러입니다.
Dynamo-vLLM은 NVIDIA Dynamo를 사용하는 패턴으로 Disaggregated Serving을 지원하지만 설정이 매우 복잡합니다. 대규모 서비스에서 KV Cache 재사용율을 극대화하고 싶을 때 검토하세요.
{cue: transition}
패턴을 결정했다면 다음은 GPU 인스턴스를 선택해야 합니다.
:::

---
<!-- Slide 4: GPU 인스턴스 선택 (Content with table) -->
@type: content
@title: GPU 인스턴스 선택 가이드: 모델 크기별 매핑

:::html
<table style="width:100%;border-collapse:collapse;font-size:12px;margin-bottom:16px;">
  <thead>
    <tr style="background:#232f4a;">
      <th style="padding:9px;color:#ff9900;text-align:left;">인스턴스</th>
      <th style="padding:9px;color:#ff9900;">GPU</th>
      <th style="padding:9px;color:#ff9900;text-align:right;">VRAM</th>
      <th style="padding:9px;color:#ff9900;text-align:right;">$/hr</th>
      <th style="padding:9px;color:#ff9900;">적합 모델</th>
      <th style="padding:9px;color:#ff9900;">비고</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#1a1a2e;">
      <td style="padding:8px;color:#06d6a0;font-weight:700;">g5.xlarge</td>
      <td style="padding:8px;color:#bbb;">1× A10G</td>
      <td style="padding:8px;color:#fff;text-align:right;">24 GB</td>
      <td style="padding:8px;color:#06d6a0;text-align:right;">~$1.01</td>
      <td style="padding:8px;color:#bbb;">7B (Mistral, Llama-3.2)</td>
      <td style="padding:8px;color:#06d6a0;">가장 경제적</td>
    </tr>
    <tr style="background:#15152a;">
      <td style="padding:8px;color:#ddd;">g6.xlarge</td>
      <td style="padding:8px;color:#bbb;">1× L4</td>
      <td style="padding:8px;color:#fff;text-align:right;">24 GB</td>
      <td style="padding:8px;color:#06d6a0;text-align:right;">~$0.80</td>
      <td style="padding:8px;color:#bbb;">7B</td>
      <td style="padding:8px;color:#06d6a0;">g5 대비 저렴</td>
    </tr>
    <tr style="background:#1a1a2e;">
      <td style="padding:8px;color:#ddd;">g5.12xlarge</td>
      <td style="padding:8px;color:#bbb;">4× A10G</td>
      <td style="padding:8px;color:#fff;text-align:right;">96 GB</td>
      <td style="padding:8px;color:#ff9900;text-align:right;">~$5.67</td>
      <td style="padding:8px;color:#bbb;">13B~34B</td>
      <td style="padding:8px;color:#bbb;">TP=4 분산</td>
    </tr>
    <tr style="background:#15152a;">
      <td style="padding:8px;color:#ddd;">g6e.12xlarge</td>
      <td style="padding:8px;color:#bbb;">4× L40S</td>
      <td style="padding:8px;color:#fff;text-align:right;">192 GB</td>
      <td style="padding:8px;color:#ff9900;text-align:right;">~$8.49</td>
      <td style="padding:8px;color:#bbb;">34B~70B</td>
      <td style="padding:8px;color:#bbb;">차세대 GPU</td>
    </tr>
    <tr style="background:#1a1a2e;">
      <td style="padding:8px;color:#ddd;">p4d.24xlarge</td>
      <td style="padding:8px;color:#bbb;">8× A100</td>
      <td style="padding:8px;color:#fff;text-align:right;">320 GB</td>
      <td style="padding:8px;color:#ef476f;text-align:right;">~$32.77</td>
      <td style="padding:8px;color:#bbb;">70B</td>
      <td style="padding:8px;color:#bbb;">고성능</td>
    </tr>
    <tr style="background:#15152a;">
      <td style="padding:8px;color:#ddd;">p5.48xlarge</td>
      <td style="padding:8px;color:#bbb;">8× H100</td>
      <td style="padding:8px;color:#fff;text-align:right;">640 GB</td>
      <td style="padding:8px;color:#ef476f;text-align:right;">~$98.32</td>
      <td style="padding:8px;color:#bbb;">405B+</td>
      <td style="padding:8px;color:#bbb;">최대 성능</td>
    </tr>
  </tbody>
</table>
<div style="background:#0d1117;border-radius:8px;padding:14px;font-size:13px;color:#bbb;line-height:1.9;">
  <b style="color:#ff9900;">VRAM 계산 공식 (BF16 기준):</b><br>
  모델 가중치(GB) ≈ 파라미터 수(B) × 2 &nbsp;|&nbsp; 7B ≈ 14GB → g5.xlarge 충분 &nbsp;|&nbsp; 70B ≈ 140GB → p4d.24xlarge TP=8<br>
  <b style="color:#06d6a0;">Spot 절감:</b> g5 Spot = On-Demand 대비 60~70% 할인 (가용성 사전 확인 필수)
</div>
:::

:::notes
{timing: 2min}
GPU 인스턴스 선택에서 가장 중요한 것은 모델 가중치 크기입니다.
BF16 기준으로 파라미터 수에 2를 곱하면 됩니다. 7B 모델은 14GB, 13B는 26GB, 70B는 140GB입니다.
g5.xlarge는 A10G 24GB라서 7B 모델 하나를 올릴 수 있습니다. 나머지 메모리가 KV Cache로 사용됩니다.
{cue: pause}
p5.48xlarge는 H100 8개, 640GB입니다. 시간당 98달러이지만 Llama-3 405B처럼 810GB 이상이 필요한 모델은 이 인스턴스 두 개를 LWS로 연결해야 합니다.
Spot 인스턴스를 쓰면 비용을 60~70% 줄일 수 있습니다. g5.xlarge Spot이 시간당 약 0.30달러입니다. vLLM은 Stateless라서 Spot 중단 시 빠르게 재시작할 수 있습니다.
{cue: transition}
이제 이 인프라를 Terraform으로 어떻게 한 번에 배포하는지 보겠습니다.
:::

---
<!-- Slide 5: Terraform 인프라 구성 (Code + List) -->
@type: content
@title: Terraform으로 전체 인프라 20분 배포

:::html
<div style="display:grid;grid-template-columns:1fr auto;gap:20px;">
  <div>
    <div style="background:#0d1117;border:1px solid #333;border-radius:8px;padding:16px;font-family:monospace;font-size:12px;line-height:1.8;">
      <div style="color:#666;margin-bottom:8px;"># ai-on-eks/infra/solutions/inference-ready-cluster/</div>
      <div style="color:#ff9900;"># 1. Clone & Configure</div>
      <div style="color:#06d6a0;">git clone https://github.com/awslabs/ai-on-eks.git</div>
      <div style="color:#06d6a0;">cd ai-on-eks/infra/solutions/inference-ready-cluster</div>
      <div style="margin-top:10px;color:#ff9900;"># 2. blueprint.tfvars 편집</div>
      <div style="color:#41b3ff;">region               = <span style="color:#06d6a0;">"us-west-2"</span></div>
      <div style="color:#41b3ff;">enable_karpenter     = <span style="color:#ff9900;">true</span></div>
      <div style="color:#41b3ff;">enable_kuberay       = <span style="color:#ff9900;">true</span></div>
      <div style="color:#41b3ff;">enable_lws           = <span style="color:#ff9900;">true</span></div>
      <div style="color:#41b3ff;">enable_nvidia_plugin = <span style="color:#ff9900;">true</span></div>
      <div style="color:#41b3ff;">enable_observability  = <span style="color:#ff9900;">true</span></div>
      <div style="margin-top:10px;color:#ff9900;"># 3. Deploy (약 20분)</div>
      <div style="color:#06d6a0;">terraform init && terraform apply -var-file=blueprint.tfvars</div>
    </div>
  </div>
  <div style="min-width:220px;">
    <div style="color:#ff9900;font-weight:700;font-size:14px;margin-bottom:12px;">자동 설치 컴포넌트</div>
    <div style="display:flex;flex-direction:column;gap:7px;font-size:12px;">
      <div data-fragment-index="1" style="background:#1a1a2e;padding:7px 10px;border-radius:4px;color:#bbb;">✦ VPC (Multi-AZ, Private Subnet)</div>
      <div data-fragment-index="1" style="background:#1a1a2e;padding:7px 10px;border-radius:4px;color:#bbb;">✦ EKS Cluster + Managed Node Group</div>
      <div data-fragment-index="2" style="background:#1a1a2e;padding:7px 10px;border-radius:4px;color:#ff9900;">✦ Karpenter (GPU/CPU NodePools)</div>
      <div data-fragment-index="2" style="background:#1a1a2e;padding:7px 10px;border-radius:4px;color:#ff9900;">✦ KubeRay Operator</div>
      <div data-fragment-index="3" style="background:#1a1a2e;padding:7px 10px;border-radius:4px;color:#06d6a0;">✦ NVIDIA Device Plugin + NFD</div>
      <div data-fragment-index="3" style="background:#1a1a2e;padding:7px 10px;border-radius:4px;color:#06d6a0;">✦ DCGM Exporter</div>
      <div data-fragment-index="4" style="background:#1a1a2e;padding:7px 10px;border-radius:4px;color:#41b3ff;">✦ Prometheus + Grafana</div>
      <div data-fragment-index="4" style="background:#1a1a2e;padding:7px 10px;border-radius:4px;color:#41b3ff;">✦ AWS LB Controller + EBS CSI</div>
    </div>
  </div>
</div>
:::

:::notes
{timing: 2min}
ai-on-eks의 inference-ready-cluster 모듈을 쓰면 Terraform 명령 하나로 전체 인프라가 배포됩니다.
blueprint.tfvars에서 필요한 컴포넌트를 true/false로 켜고 끕니다. enable_karpenter=true이면 Karpenter가, enable_kuberay=true이면 KubeRay Operator가 자동으로 설치됩니다.
{cue: pause}
terraform apply 후 약 20분이면 EKS 클러스터부터 Prometheus, Grafana, NVIDIA Device Plugin까지 모두 준비됩니다.
여기서 주의할 점이 있습니다. enable_observability=true로 설정하면 Prometheus와 Grafana가 설치되는데, Grafana에는 vLLM 대시보드 JSON을 import하면 바로 쓸 수 있는 대시보드가 제공됩니다.
{cue: transition}
클러스터가 준비됐습니다. 이제 GPU 노드에 어떤 소프트웨어 스택이 있는지 살펴보겠습니다.
:::

---
<!-- Slide 6: GPU 소프트웨어 스택 (Content with HTML layers) -->
@type: content
@title: GPU 노드 소프트웨어 스택: NVIDIA 생태계

:::html
<div style="display:flex;flex-direction:column;gap:8px;height:440px;justify-content:center;">
  <div data-fragment-index="6" style="background:#28180a;border:1px solid #ff9900;border-radius:8px;padding:12px;display:grid;grid-template-columns:130px 1fr;gap:12px;align-items:center;">
    <div style="color:#ff9900;font-weight:700;font-size:13px;text-align:center;">Application</div>
    <div style="color:#bbb;font-size:13px;"><b style="color:#fff;">vLLM Engine</b> — CUDA 애플리케이션, PyTorch, FlashAttention-2</div>
  </div>
  <div style="text-align:center;color:#555;font-size:18px;">↕</div>
  <div data-fragment-index="5" style="background:#1a2816;border:1px solid #06d6a0;border-radius:8px;padding:12px;display:grid;grid-template-columns:130px 1fr;gap:12px;align-items:center;">
    <div style="color:#06d6a0;font-weight:700;font-size:13px;text-align:center;">K8s Metrics</div>
    <div style="color:#bbb;font-size:13px;"><b style="color:#fff;">DCGM Exporter</b> — GPU 활용률, 온도, 전력, VRAM 메트릭 노출</div>
  </div>
  <div style="text-align:center;color:#555;font-size:18px;">↕</div>
  <div data-fragment-index="4" style="background:#162840;border:1px solid #41b3ff;border-radius:8px;padding:12px;display:grid;grid-template-columns:130px 1fr;gap:12px;align-items:center;">
    <div style="color:#41b3ff;font-weight:700;font-size:13px;text-align:center;">K8s Discovery</div>
    <div style="color:#bbb;font-size:13px;"><b style="color:#fff;">Node Feature Discovery</b> — GPU 특성 자동 라벨링 (CUDA 버전, GPU 모델)</div>
  </div>
  <div style="text-align:center;color:#555;font-size:18px;">↕</div>
  <div data-fragment-index="3" style="background:#162840;border:1px solid #41b3ff;border-radius:8px;padding:12px;display:grid;grid-template-columns:130px 1fr;gap:12px;align-items:center;">
    <div style="color:#41b3ff;font-weight:700;font-size:13px;text-align:center;">K8s Plugin</div>
    <div style="color:#bbb;font-size:13px;"><b style="color:#fff;">NVIDIA Device Plugin</b> — GPU 리소스 등록 및 Pod 할당 관리</div>
  </div>
  <div style="text-align:center;color:#555;font-size:18px;">↕</div>
  <div data-fragment-index="2" style="background:#221800;border:1px solid #ff9900;border-radius:8px;padding:12px;display:grid;grid-template-columns:130px 1fr;gap:12px;align-items:center;">
    <div style="color:#ff9900;font-weight:700;font-size:13px;text-align:center;">Container</div>
    <div style="color:#bbb;font-size:13px;"><b style="color:#fff;">NVIDIA Container Toolkit</b> — GPU를 컨테이너에 노출 (nvidia-docker2)</div>
  </div>
  <div style="text-align:center;color:#555;font-size:18px;">↕</div>
  <div data-fragment-index="1" style="background:#1a0a00;border:1px solid #ef476f;border-radius:8px;padding:12px;display:grid;grid-template-columns:130px 1fr;gap:12px;align-items:center;">
    <div style="color:#ef476f;font-weight:700;font-size:13px;text-align:center;">Hardware</div>
    <div style="color:#bbb;font-size:13px;"><b style="color:#fff;">NVIDIA GPU</b> — A10G 24GB / L4 24GB / A100 80GB / H100 80GB</div>
  </div>
</div>
:::

:::notes
{timing: 1.5min}
GPU 노드에는 여러 레이어의 소프트웨어가 필요합니다.
맨 아래가 NVIDIA GPU 하드웨어입니다. 그 위에 NVIDIA Container Toolkit이 GPU를 컨테이너에 노출합니다.
NVIDIA Device Plugin은 쿠버네티스가 nvidia.com/gpu 리소스를 이해하게 해줍니다. Pod에 "GPU 1개 필요"라고 적으면 이 플러그인이 실제 GPU를 할당합니다.
{cue: pause}
Node Feature Discovery는 노드에 어떤 GPU가 있는지, CUDA 버전이 무엇인지 자동으로 라벨을 붙여줍니다. Karpenter가 NodeSelector로 특정 GPU 타입을 선택할 때 이 라벨을 사용합니다.
DCGM Exporter는 GPU의 심층 메트릭을 Prometheus로 내보냅니다. GPU 활용률, 온도, 전력, VRAM 사용량 등을 실시간으로 모니터링할 수 있습니다.
{cue: transition}
이제 Karpenter가 실제로 어떻게 GPU 노드를 자동으로 만들어주는지 살펴보겠습니다.
:::

---
<!-- Slide 7: Karpenter 동작 원리 (Canvas Step Animation) -->
@type: canvas
@title: Karpenter: GPU 노드 자동 프로비저닝 흐름

:::canvas
box s1 "① GPU Pod 생성\n요청" at 30,180 size 130,60 color #41b3ff step 1
arrow s1 -> s2 "Pending" color #ff9900 step 2
box s2 "② Pod Pending\n(GPU 부족)" at 220,180 size 130,60 color #ff9900 step 2
arrow s2 -> s3 "감지" color #06d6a0 step 3
box s3 "③ Karpenter\n감지" at 410,180 size 130,60 color #06d6a0 step 3
arrow s3 -> s4 "NodePool 매칭" color #06d6a0 step 4
box s4 "④ AWS EC2\nRunInstances" at 600,180 size 130,60 color #ff9900 step 4
arrow s4 -> s5 "2~5분" color #41b3ff step 5
box s5 "⑤ Node Ready\n→ Pod Running" at 790,180 size 130,60 color #41b3ff step 5

box nodepool "Karpenter NodePool\ng5-gpu-karpenter" at 380,80 size 200,50 color #ad5cff step 3
arrow nodepool -> s3 "" step 3
:::

:::notes
{timing: 2min}
Karpenter의 동작 흐름을 순서대로 보겠습니다.
GPU Pod 생성 요청이 들어오면, 현재 클러스터에 GPU가 없으면 Pod이 Pending 상태가 됩니다.
Karpenter는 Pending Pod을 감지하고, 해당 Pod의 요구사항(GPU 타입, 메모리 등)을 분석합니다.
NodePool 설정과 매칭하여 가장 적합한 EC2 인스턴스 타입을 선택합니다. g5.xlarge NodePool이라면 g5.xlarge 인스턴스를 선택합니다.
{cue: pause}
AWS RunInstances API를 호출해서 EC2 인스턴스를 생성합니다. 인스턴스가 준비되고 K8s 노드로 등록되면 Pod이 스케줄링됩니다. 전체 과정이 2~5분입니다.
트래픽이 줄어서 Pod이 삭제되면 Karpenter는 빈 노드를 감지하고 EC2 인스턴스를 자동으로 종료합니다. 이것이 비용 최적화의 핵심입니다.
{cue: transition}
Part 2를 마칩니다. 다음은 실제 Ray-vLLM 배포로 넘어가겠습니다.
:::

---
<!-- Slide 8: Part 2 마무리 (Thank You) -->
@type: content
@title: Part 2 핵심 정리

:::html
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:24px;">
  <div style="background:#1a1a2e;border-top:3px solid #41b3ff;border-radius:8px;padding:14px;text-align:center;">
    <div style="font-size:28px;margin-bottom:6px;">🏗️</div>
    <div style="color:#41b3ff;font-weight:700;font-size:13px;margin-bottom:4px;">클러스터 아키텍처</div>
    <div style="color:#bbb;font-size:11px;line-height:1.5;">EKS + Terraform<br>40+ 애드온 자동 설치</div>
  </div>
  <div style="background:#1a1a2e;border-top:3px solid #ff9900;border-radius:8px;padding:14px;text-align:center;">
    <div style="font-size:28px;margin-bottom:6px;">🎯</div>
    <div style="color:#ff9900;font-weight:700;font-size:13px;margin-bottom:4px;">Ray-vLLM 권장</div>
    <div style="color:#bbb;font-size:11px;line-height:1.5;">6가지 패턴 중<br>프로덕션 검증 완료</div>
  </div>
  <div style="background:#1a1a2e;border-top:3px solid #06d6a0;border-radius:8px;padding:14px;text-align:center;">
    <div style="font-size:28px;margin-bottom:6px;">🖥️</div>
    <div style="color:#06d6a0;font-weight:700;font-size:13px;margin-bottom:4px;">GPU 스택</div>
    <div style="color:#bbb;font-size:11px;line-height:1.5;">Device Plugin →<br>DCGM → vLLM</div>
  </div>
  <div style="background:#1a1a2e;border-top:3px solid #ad5cff;border-radius:8px;padding:14px;text-align:center;">
    <div style="font-size:28px;margin-bottom:6px;">⚡</div>
    <div style="color:#ad5cff;font-weight:700;font-size:13px;margin-bottom:4px;">Karpenter</div>
    <div style="color:#bbb;font-size:11px;line-height:1.5;">Pending → Node Ready<br>2~5분 자동 프로비저닝</div>
  </div>
</div>
<div style="text-align:center;padding:16px;background:#0d1117;border-radius:8px;">
  <a href="index.html" style="color:#bbb;font-size:13px;text-decoration:none;margin-right:24px;">← 목차로 돌아가기</a>
  <a href="03-deployment.html" style="color:#ff9900;font-size:14px;font-weight:700;text-decoration:none;">다음: Ray-vLLM 배포 딥다이브 →</a>
</div>
:::

:::notes
{timing: 1min}
Part 2를 정리하겠습니다.
EKS 클러스터는 Terraform 한 줄로 만들 수 있고, 40개 이상의 애드온이 자동으로 설치됩니다.
배포 패턴은 Ray-vLLM이 프로덕션에서 가장 검증되었습니다. GPU 소프트웨어 스택은 Device Plugin → DCGM → vLLM 순서로 쌓입니다.
Karpenter는 GPU Pod이 Pending되면 자동으로 EC2를 생성하고, Pod이 없어지면 자동으로 종료합니다.
{cue: transition}
다음 파트에서는 실제 배포 코드를 보겠습니다. Helm Chart, RayService 매니페스트, 그리고 모델별 최적 설정까지 다룹니다.
:::
