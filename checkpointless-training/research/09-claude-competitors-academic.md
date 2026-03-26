# ML 학습 내결함성(Fault Tolerance) 기술 심층 연구

> **연구 목적**: 대규모 ML 학습에서의 내결함성 기술 비교 분석
> **연구 범위**: PyTorch Elastic, NVIDIA NVRx, DeepSpeed, Google Pathways/TPU, AWS Checkpointless, 학술 논문
> **작성일**: 2024년

---

## 목차

1. [PyTorch Elastic (torchrun / torchelastic)](#1-pytorch-elastic)
2. [NVIDIA Resiliency Extension (NVRx)](#2-nvidia-resiliency-extension-nvrx)
3. [DeepSpeed Fault Tolerance](#3-deepspeed-fault-tolerance)
4. [Google's Approach (Pathways / TPU Multislice)](#4-googles-approach)
5. [학술 논문 분석](#5-학술-논문-분석)
6. [기술 비교표](#6-기술-비교표)
7. [핵심 인사이트 및 결론](#7-핵심-인사이트-및-결론)

---

## 1. PyTorch Elastic

**공식 문서**: https://pytorch.org/docs/stable/distributed.elastic.html

### 1.1 아키텍처 개요

PyTorch Elastic (torchelastic)은 분산 학습에서 **동적 스케일링**과 **내결함성**을 제공하는 프레임워크입니다. `torchrun` 명령어를 통해 실행되며, 기존 `torch.distributed.launch`를 대체합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    PyTorch Elastic Architecture              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│  │  Agent   │    │  Agent   │    │  Agent   │               │
│  │ (Node 0) │    │ (Node 1) │    │ (Node 2) │               │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘               │
│       │               │               │                      │
│       └───────────────┼───────────────┘                      │
│                       │                                      │
│              ┌────────▼────────┐                            │
│              │   Rendezvous    │                            │
│              │    Backend      │                            │
│              │  (etcd/c10d)    │                            │
│              └─────────────────┘                            │
│                                                              │
│  Worker Group: [W0, W1, W2, ... Wn]                         │
│  - 동적으로 크기 조절 가능                                    │
│  - min_nodes ~ max_nodes 범위 내 탄력적 운영                  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Rendezvous Backends

Rendezvous는 분산 학습 참여자들이 서로를 발견하고 동기화하는 메커니즘입니다.

| Backend | 특징 | 사용 시나리오 |
|---------|------|--------------|
| **etcd** | 외부 키-값 저장소 기반, 고가용성 | 대규모 프로덕션 클러스터 |
| **c10d** | PyTorch 내장, TCPStore 기반 | 단일 노드 또는 소규모 클러스터 |
| **static** | 고정된 노드 목록 | 변경 없는 환경 |

**etcd Rendezvous 동작**:
```python
# torchrun 실행 예시
torchrun \
    --nnodes=1:4 \           # min:max 노드 수
    --nproc_per_node=8 \     # 노드당 GPU 수
    --rdzv_backend=etcd \    # Rendezvous 백엔드
    --rdzv_endpoint=etcd-server:2379 \
    --rdzv_id=my_job \
    train.py
```

### 1.3 동적 스케일링 메커니즘

```
┌─────────────────────────────────────────────────────────────┐
│                   Dynamic Scaling Flow                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Worker 장애 감지                                         │
│     └─→ Agent가 heartbeat 모니터링                          │
│                                                              │
│  2. Rendezvous 재실행                                        │
│     └─→ 살아있는 Worker들이 새로운 world_size 협상           │
│                                                              │
│  3. 모든 Worker 재시작                                       │
│     └─→ 최신 체크포인트에서 복구                             │
│                                                              │
│  4. 학습 재개                                                │
│     └─→ 새로운 topology로 계속                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**핵심 특징**:
- **min_nodes/max_nodes**: 탄력적 범위 설정
- **자동 Worker 재시작**: 장애 시 Agent가 Worker 프로세스 재시작
- **전체 재시작 모델**: 일부 Worker 장애 시에도 **모든 Worker가 재시작**

### 1.4 Fault Tolerance 모델

PyTorch Elastic의 내결함성은 **체크포인트 기반 복구**입니다:

```python
# 학습 코드에서 체크포인트 저장/로드 패턴
def train():
    # 체크포인트 로드 (존재하는 경우)
    if os.path.exists(CHECKPOINT_PATH):
        checkpoint = torch.load(CHECKPOINT_PATH)
        model.load_state_dict(checkpoint['model'])
        optimizer.load_state_dict(checkpoint['optimizer'])
        start_epoch = checkpoint['epoch']
    
    for epoch in range(start_epoch, total_epochs):
        train_one_epoch()
        
        # 주기적 체크포인트 저장
        if epoch % save_interval == 0:
            torch.save({
                'epoch': epoch,
                'model': model.state_dict(),
                'optimizer': optimizer.state_dict(),
            }, CHECKPOINT_PATH)
```

### 1.5 한계점

| 한계 | 설명 |
|------|------|
| **체크포인트 I/O 오버헤드** | 대규모 모델(수백 GB)에서 체크포인트 저장/로드에 수 분 소요 |
| **전체 Worker 재시작** | 단일 노드 장애에도 전체 학습 job이 중단되고 재시작 |
| **복구 시간** | 체크포인트 로드 + Rendezvous + 재시작 = 수 분~수십 분 |
| **체크포인트 빈도 트레이드오프** | 자주 저장하면 I/O 오버헤드, 드물게 저장하면 작업 손실 증가 |
| **Hot spare 미지원** | 대기 노드를 활용한 즉시 대체 불가 |

---

## 2. NVIDIA Resiliency Extension (NVRx)

**GitHub**: https://github.com/NVIDIA/nvidia-resiliency-ext
**상태**: Experimental (활발한 개발 중, Breaking changes 예상)

### 2.1 아키텍처 개요

NVRx는 PyTorch 기반 대규모 학습의 **생산성 극대화**를 위한 통합 내결함성 플랫폼입니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    NVRx Architecture                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Fault Tolerance Layer                   │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │    │
│  │  │ Hung Rank    │  │ Straggler    │  │ In-Process│  │    │
│  │  │ Detection    │  │ Detection    │  │ Restart   │  │    │
│  │  └──────────────┘  └──────────────┘  └───────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Checkpointing Layer                     │    │
│  │  ┌──────────────┐  ┌──────────────┐                 │    │
│  │  │ Async        │  │ Hierarchical │                 │    │
│  │  │ Checkpointing│  │ (Local+Remote)│                │    │
│  │  └──────────────┘  └──────────────┘                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Integration Layer                       │    │
│  │  ┌──────────────┐  ┌──────────────┐                 │    │
│  │  │ PyTorch      │  │ NVIDIA NeMo  │                 │    │
│  │  │ Lightning    │  │ Framework    │                 │    │
│  │  └──────────────┘  └──────────────┘                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 In-Process Restart 메커니즘

**핵심 혁신**: SLURM 재할당 없이 **동일 Job 내에서** 장애 복구

```
┌─────────────────────────────────────────────────────────────┐
│              In-Process Restart Flow                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  기존 방식 (PyTorch Elastic):                                │
│  ┌────────┐     ┌────────┐     ┌────────┐     ┌────────┐   │
│  │ 장애   │ ──→ │ Job    │ ──→ │ SLURM  │ ──→ │ 재시작 │   │
│  │ 감지   │     │ 종료   │     │ 재할당 │     │        │   │
│  └────────┘     └────────┘     └────────┘     └────────┘   │
│       ↓              ↓              ↓              ↓        │
│     즉시          수 초         수 분~수십 분    수 분       │
│                                                              │
│  NVRx In-Process Restart:                                   │
│  ┌────────┐     ┌────────┐     ┌────────┐                  │
│  │ 장애   │ ──→ │ 프로세스│ ──→ │ 학습   │                  │
│  │ 감지   │     │ 내 복구 │     │ 재개   │                  │
│  └────────┘     └────────┘     └────────┘                  │
│       ↓              ↓              ↓                       │
│     즉시          수 초          즉시                        │
│                                                              │
│  총 복구 시간: 수 분 → 수 초                                 │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Hung Rank Detection

학습 중 **응답하지 않는 Rank**를 탐지하는 메커니즘:

```python
# NVRx Hung Rank Detection 개념
class HungRankDetector:
    """
    각 Rank의 heartbeat를 모니터링하여 
    hang 상태를 탐지하고 자동 개입
    """
    def __init__(self, timeout_seconds=300):
        self.timeout = timeout_seconds
        self.last_heartbeat = {}
    
    def check_ranks(self):
        for rank, last_time in self.last_heartbeat.items():
            if time.time() - last_time > self.timeout:
                self.handle_hung_rank(rank)
```

**탐지 시나리오**:
- NCCL collective 연산 중 무한 대기
- GPU 메모리 오류로 인한 hang
- 네트워크 파티션으로 인한 통신 불가

### 2.4 Straggler Detection

**Straggler**: 다른 노드보다 느리게 연산을 수행하여 전체 학습 속도를 저하시키는 노드

```
┌─────────────────────────────────────────────────────────────┐
│              Straggler Detection & Mitigation                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Performance Monitoring:                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │ Rank 0  │  │ Rank 1  │  │ Rank 2  │  │ Rank 3  │        │
│  │ 100ms   │  │ 102ms   │  │ 98ms    │  │ 250ms ⚠│        │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
│                                              │               │
│                                    Straggler 감지!           │
│                                              │               │
│  대응 옵션:                                  ▼               │
│  1. 경고 로깅 및 모니터링                                    │
│  2. 해당 노드 제외 및 재할당                                 │
│  3. 동적 배치 크기 조절                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.5 Hierarchical Checkpointing

**2단계 체크포인트 전략**으로 I/O 병목 해결:

```
┌─────────────────────────────────────────────────────────────┐
│              Hierarchical Checkpointing                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Level 1: Local Checkpointing (빠름)                        │
│  ┌──────────────────────────────────────────────────┐       │
│  │  각 노드의 Local SSD/NVMe에 빠르게 저장           │       │
│  │  - 저장 시간: 수 초                               │       │
│  │  - 용도: 빈번한 스냅샷, 빠른 복구                 │       │
│  │  - 한계: 노드 장애 시 손실                        │       │
│  └──────────────────────────────────────────────────┘       │
│                          │                                   │
│                          ▼                                   │
│  Level 2: Remote Checkpointing (내구성)                     │
│  ┌──────────────────────────────────────────────────┐       │
│  │  공유 스토리지(S3, Lustre 등)에 비동기 전송       │       │
│  │  - 저장 시간: 수 분 (백그라운드)                  │       │
│  │  - 용도: 영구 보존, 노드 장애 복구                │       │
│  │  - 장점: 학습 중단 없이 진행                      │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.6 Async Checkpointing

체크포인트 저장을 **비동기로 수행**하여 학습 중단 최소화:

```python
# Async Checkpointing 개념적 구현
import threading

class AsyncCheckpointer:
    def __init__(self):
        self.pending_saves = []
    
    def save_async(self, state_dict, path):
        # 메모리에 스냅샷 생성 (빠름)
        snapshot = self._create_snapshot(state_dict)
        
        # 백그라운드 스레드에서 저장
        thread = threading.Thread(
            target=self._persist_snapshot,
            args=(snapshot, path)
        )
        thread.start()
        
        # 학습은 즉시 계속
        return
```

### 2.7 AWS Checkpointless와의 비교

| 특성 | NVRx | AWS Checkpointless |
|------|------|-------------------|
| **복구 방식** | 체크포인트 기반 (최적화됨) | 인메모리 상태 복제 |
| **In-Process Restart** | ✅ 지원 | ✅ 지원 |
| **디스크 I/O 필요** | 필요 (비동기/계층적) | 불필요 |
| **Hot Spare** | ❌ 미지원 | ✅ 지원 |
| **복구 시간** | 수 초~수십 초 | 수 초 |
| **메모리 오버헤드** | 낮음 | 높음 (복제본 유지) |
| **오픈소스** | ✅ 완전 오픈소스 | ❌ AWS 서비스 |

### 2.8 시스템 요구사항

```yaml
Platform Requirements:
  Architecture: x86_64, arm64
  OS: Ubuntu 22.04, 24.04
  Python: 3.10 ~ 3.12
  PyTorch: ≥ 2.5.1 (Fault Attribution: ≥ 2.8.0)
  CUDA: ≥ 12.8
  NCCL: 2.28.3 ~ 2.28.8 버전 회피 권장

Installation:
  pip install nvidia-resiliency-ext
  # 또는 소스에서 빌드
  git clone https://github.com/NVIDIA/nvidia-resiliency-ext
  pip install .
```

---

## 3. DeepSpeed Fault Tolerance

**공식 문서**: https://www.deepspeed.ai/training/

### 3.1 아키텍처 개요

DeepSpeed는 Microsoft에서 개발한 대규모 모델 학습 최적화 라이브러리입니다. **메모리 효율성**과 **성능**에 초점을 맞추며, 내결함성은 체크포인트 시스템을 통해 제공됩니다.

```
┌─────────────────────────────────────────────────────────────┐
│                   DeepSpeed Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                 ZeRO Optimizer                       │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │    │
│  │  │ Stage 1  │  │ Stage 2  │  │ Stage 3  │          │    │
│  │  │Optimizer │  │+Gradients│  │+Parameters│          │    │
│  │  │Partitioning│ │Partitioning│ │Partitioning│        │    │
│  │  └──────────┘  └──────────┘  └──────────┘          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Memory Optimizations                    │    │
│  │  • Activation Partitioning                          │    │
│  │  • Constant Buffer Optimization (CBO)               │    │
│  │  • Contiguous Memory Optimization (CMO)             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Checkpointing System                    │    │
│  │  • Training-agnostic checkpoint format              │    │
│  │  • Universal Checkpointing                          │    │
│  │  • Parallel write support                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 ZeRO (Zero Redundancy Optimizer)

ZeRO는 DeepSpeed의 핵심 기술로, 모델 상태를 프로세스 간에 **분할**하여 메모리 사용을 최적화합니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    ZeRO Stages                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  기존 Data Parallelism (모든 것을 복제):                     │
│  GPU 0: [Model] [Optimizer] [Gradients]                     │
│  GPU 1: [Model] [Optimizer] [Gradients]  ← 중복!            │
│  GPU 2: [Model] [Optimizer] [Gradients]  ← 중복!            │
│  GPU 3: [Model] [Optimizer] [Gradients]  ← 중복!            │
│                                                              │
│  ZeRO Stage 1 (Optimizer State Partitioning):               │
│  - Optimizer 상태를 GPU 간 분할                              │
│  - 메모리 절약: ~4x                                          │
│                                                              │
│  ZeRO Stage 2 (+ Gradient Partitioning):                    │
│  - Gradient도 분할                                           │
│  - 메모리 절약: ~8x                                          │
│                                                              │
│  ZeRO Stage 3 (+ Parameter Partitioning):                   │
│  - 모델 파라미터까지 분할                                    │
│  - 메모리 절약: GPU 수에 비례                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 체크포인트 설정 옵션

```json
{
  "checkpoint": {
    "tag_validation": "Warn",
    "load_universal": true,
    "use_node_local_storage": false,
    "parallel_write": {
      "pipeline_stage": true
    }
  },
  "zero_optimization": {
    "stage": 3,
    "stage3_gather_16bit_weights_on_model_save": true
  }
}
```

| 옵션 | 설명 |
|------|------|
| `tag_validation` | Rank 간 체크포인트 일관성 검증 (Ignore/Warn/Fail) |
| `load_universal` | 최신 체크포인트 자동 로드 |
| `use_node_local_storage` | 로컬 스토리지 사용 (공유 파일시스템 불필요) |
| `parallel_write.pipeline_stage` | 파이프라인 단계별 병렬 쓰기 |

### 3.4 Universal Checkpointing

**클러스터 크기 변경 시에도 체크포인트 호환성 유지**:

```
┌─────────────────────────────────────────────────────────────┐
│              Universal Checkpointing Flow                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 학습 중 ZeRO 체크포인트 저장                             │
│     └─→ 분할된 상태 저장 (각 GPU별 파티션)                  │
│                                                              │
│  2. ds_to_universal.py 스크립트로 변환                       │
│     └─→ 파티션된 체크포인트를 통합 포맷으로 변환            │
│                                                              │
│  3. --universal-checkpoint 플래그로 재개                    │
│     └─→ 다른 GPU 수, 다른 병렬화 설정에서도 로드 가능       │
│                                                              │
│  사용 사례:                                                  │
│  - 8 GPU → 16 GPU 클러스터 업스케일                         │
│  - TP=4, PP=2 → TP=8, PP=1 설정 변경                        │
│  - 다른 하드웨어로 마이그레이션                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.5 ZeRO-Infinity

**CPU/NVMe로 오프로드**하여 GPU 메모리 한계 극복:

```
┌─────────────────────────────────────────────────────────────┐
│                    ZeRO-Infinity                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  GPU Memory          CPU Memory           NVMe Storage       │
│  ┌──────────┐       ┌──────────┐        ┌──────────┐        │
│  │ Active   │ ←───→ │ Optimizer│ ←────→ │ Overflow │        │
│  │ Params   │       │ States   │        │ Storage  │        │
│  └──────────┘       └──────────┘        └──────────┘        │
│                                                              │
│  • 단일 GPU에서 수 조 개 파라미터 학습 가능                  │
│  • 자동 데이터 이동 (prefetch/offload)                       │
│  • NVMe 대역폭 활용으로 CPU 메모리 한계도 극복               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.6 내결함성 한계점

DeepSpeed는 **성능/메모리 최적화**에 집중하며, 내결함성은 상대적으로 기본적입니다:

| 한계 | 설명 |
|------|------|
| **체크포인트 의존** | 모든 복구가 디스크 체크포인트 기반 |
| **In-Process Restart 미지원** | 장애 시 Job 재시작 필요 |
| **Hung Rank Detection 미지원** | 외부 모니터링 필요 |
| **Hot Spare 미지원** | 대기 노드 활용 불가 |
| **Straggler Detection 미지원** | 느린 노드 자동 감지/대응 없음 |

---

## 4. Google's Approach

### 4.1 Pathways System

**논문**: "Pathways: Asynchronous Distributed Dataflow for ML" (MLSys 2022)
**Source**: https://arxiv.org/abs/2203.12533

#### 아키텍처

Pathways는 Google의 대규모 ML 학습을 위한 **비동기 분산 데이터플로우** 시스템입니다.

```
┌─────────────────────────────────────────────────────────────┐
│                   Pathways Architecture                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Single Controller Model                 │    │
│  │  • 복잡한 병렬화 패턴을 단일 프로그램으로 표현       │    │
│  │  • 제어 플레인과 데이터 플레인 분리                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         Sharded Dataflow Graph                       │    │
│  │  • 비동기 연산자들의 샤딩된 그래프                   │    │
│  │  • Futures 기반 데이터 의존성 관리                   │    │
│  │  • 제어 플레인: 데이터 의존성에도 병렬 실행          │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                   │
│                          ▼                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Accelerator Clusters                       │    │
│  │  ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐        │    │
│  │  │TPU Pod│  │TPU Pod│  │TPU Pod│  │TPU Pod│        │    │
│  │  │ Slice │  │ Slice │  │ Slice │  │ Slice │        │    │
│  │  └───────┘  └───────┘  └───────┘  └───────┘        │    │
│  │      ↑          ↑          ↑          ↑             │    │
│  │      └──────────┴──────────┴──────────┘             │    │
│  │           Gang Scheduling + Data Transfer            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 핵심 특징

- **~100% Accelerator Utilization**: 2,048 TPU에서 SPMD 학습 시 달성
- **유연한 병렬화**: 16단계 파이프라인 병렬화, 지리적으로 분산된 가속기 그룹 지원
- **비동기 데이터플로우**: Futures 기반으로 데이터 의존성 있어도 제어 플레인 병렬 실행

### 4.2 Optical Circuit Switches (OCS)

Google은 데이터센터 네트워크에 **광학 회로 스위치**를 사용하여 동적 네트워크 재구성을 지원합니다.

```
┌─────────────────────────────────────────────────────────────┐
│              Optical Circuit Switch Architecture             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  기존 전기 스위치:                                           │
│  • 고정된 토폴로지                                          │
│  • 장애 시 물리적 재배선 필요                               │
│                                                              │
│  OCS (Optical Circuit Switch):                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                                                      │    │
│  │    TPU Pod A ←──┐      ┌──→ TPU Pod C              │    │
│  │                  │      │                           │    │
│  │              ┌───┴──────┴───┐                       │    │
│  │              │    OCS       │                       │    │
│  │              │  (동적 광학  │                       │    │
│  │              │   경로 전환) │                       │    │
│  │              └───┬──────┬───┘                       │    │
│  │                  │      │                           │    │
│  │    TPU Pod B ←──┘      └──→ TPU Pod D              │    │
│  │                                                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  장점:                                                       │
│  • 밀리초 단위 네트워크 토폴로지 변경                       │
│  • 장애 노드 우회 경로 즉시 구성                            │
│  • 동적 대역폭 할당                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 TPU Multislice Training

**TPU v4/v5**에서 여러 Pod Slice를 연결하여 대규모 학습:

```
┌─────────────────────────────────────────────────────────────┐
│              TPU Multislice Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  TPU v4 Pod (4,096 chips):                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Slice 0      Slice 1      Slice 2      Slice 3    │    │
│  │  ┌─────┐      ┌─────┐      ┌─────┐      ┌─────┐    │    │
│  │  │1024 │      │1024 │      │1024 │      │1024 │    │    │
│  │  │chips│      │chips│      │chips│      │chips│    │    │
│  │  └──┬──┘      └──┬──┘      └──┬──┘      └──┬──┘    │    │
│  │     │            │            │            │        │    │
│  │     └────────────┴────────────┴────────────┘        │    │
│  │              Inter-Slice Network (ICI)              │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Multislice Fault Tolerance:                                │
│  • Slice 단위 장애 격리                                     │
│  • 장애 Slice 제외하고 나머지로 학습 계속                   │
│  • 자동 리밸런싱                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.4 Goodput 최적화 전략

**Goodput** = 유효 처리량 (장애로 손실된 작업 제외)

```
┌─────────────────────────────────────────────────────────────┐
│              Goodput Optimization                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Goodput = Throughput × (1 - Failure_Rate × Recovery_Time)  │
│                                                              │
│  Google의 접근법:                                            │
│                                                              │
│  1. 하드웨어 중복성                                         │
│     • Hot spare TPU chips 배치                              │
│     • 즉시 대체 가능한 예비 노드                            │
│                                                              │
│  2. 소프트웨어 복원력                                       │
│     • 빈번한 체크포인트 (매 수백 스텝)                      │
│     • 비동기 체크포인트로 오버헤드 최소화                   │
│                                                              │
│  3. 네트워크 유연성                                         │
│     • OCS로 동적 경로 재구성                                │
│     • 장애 노드 우회                                        │
│                                                              │
│  4. 작업 스케줄링 최적화                                    │
│     • 장애 발생 시 빠른 작업 재배치                         │
│     • Preemption 최소화                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.5 하드웨어 중복성 접근법

Google은 **하드웨어 레벨 중복성**으로 내결함성 확보:

| 전략 | 설명 |
|------|------|
| **Spare Chips** | Pod 내 예비 TPU 칩 배치, 장애 시 자동 대체 |
| **Redundant Interconnects** | 이중화된 네트워크 경로 |
| **자동 Failover** | 장애 감지 후 자동으로 예비 리소스로 전환 |
| **Slice 격리** | 장애가 Slice 내로 격리, 다른 Slice 영향 최소화 |

---

## 5. 학술 논문 분석

### 5.1 CheckFreq (USENIX FAST '21)

**제목**: "CheckFreq: Frequent, Fine-Grained DNN Checkpointing"
**저자**: Mohan et al.
**Source**: https://www.usenix.org/conference/fast21/presentation/mohan

#### 핵심 문제

대규모 DNN 학습에서 체크포인트 주기 설정의 딜레마:
- **자주 저장**: I/O 오버헤드로 학습 속도 저하
- **드물게 저장**: 장애 시 많은 작업 손실

#### 핵심 기여

```
┌─────────────────────────────────────────────────────────────┐
│              CheckFreq Architecture                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Snapshot-and-Persist 분리                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                                                      │    │
│  │   학습 스레드          체크포인트 스레드             │    │
│  │   ┌─────────┐         ┌─────────────────┐           │    │
│  │   │ Forward │         │                 │           │    │
│  │   │ Backward│ ──────→ │ Snapshot (메모리│           │    │
│  │   │ Update  │  빠름   │   복사, ~ms)   │           │    │
│  │   └─────────┘         └────────┬────────┘           │    │
│  │       │                        │                    │    │
│  │       │                        ▼                    │    │
│  │       │               ┌─────────────────┐           │    │
│  │   계속 학습            │ Persist (디스크 │           │    │
│  │                       │   쓰기, ~초)    │           │    │
│  │                       └─────────────────┘           │    │
│  │                              비동기                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  2. Fine-Grained Checkpointing                              │
│  • 전체 모델이 아닌 변경된 부분만 선택적 저장               │
│  • 레이어별 체크포인트 관리                                 │
│                                                              │
│  3. I/O Latency Hiding                                      │
│  • 학습 연산과 체크포인트 I/O를 오버랩                      │
│  • GPU 연산 중 백그라운드로 디스크 쓰기                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 핵심 결과

- 체크포인트 주기를 **5-10배 단축** 가능
- 학습 오버헤드 **5% 미만** 유지
- 장애 시 작업 손실 대폭 감소

#### 한계점

- 여전히 **디스크 I/O 필요**
- 인메모리 복구 미지원
- 대규모 클러스터에서 스토리지 병목 가능

---

### 5.2 Bamboo (NSDI '23)

**제목**: "Bamboo: Making Preemptible Instances Resilient for Affordable Training of Large DNNs"
**저자**: Thorpe et al.
**학회**: USENIX NSDI 2023

#### 핵심 아이디어

**파이프라인 버블**을 활용한 **중복 연산**으로 즉시 대체(instant takeover) 구현

```
┌─────────────────────────────────────────────────────────────┐
│              Bamboo: Redundant Computation                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  기존 Pipeline Parallelism의 버블:                          │
│                                                              │
│  Stage 0: [F0][F1][F2][F3][ ][ ][ ][B3][B2][B1][B0]         │
│  Stage 1: [ ][F0][F1][F2][F3][ ][B3][B2][B1][B0][ ]         │
│  Stage 2: [ ][ ][F0][F1][F2][F3][B2][B1][B0][ ][ ]          │
│  Stage 3: [ ][ ][ ][F0][F1][F2][B1][B0][ ][ ][ ]            │
│           ▲                    ▲                             │
│           버블 (유휴 시간)      버블                         │
│                                                              │
│  Bamboo의 접근법 - 버블에 중복 연산 삽입:                   │
│                                                              │
│  Stage 0: [F0][F1][F2][F3][F0'][F1'][B3][B2][B1][B0]        │
│  Stage 1: [F0'][F0][F1][F2][F3][F1'][B3][B2][B1][B0]        │
│                 ▲                                            │
│                 이웃 스테이지의 연산을 중복 실행            │
│                                                              │
│  장점:                                                       │
│  • Stage 장애 시 이웃이 즉시 대체 (Instant Takeover)        │
│  • 체크포인트 로드 불필요                                   │
│  • 추가 하드웨어 없이 구현                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### Instant Takeover 메커니즘

```
┌─────────────────────────────────────────────────────────────┐
│              Instant Takeover Flow                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  정상 상태:                                                  │
│  ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐      │
│  │Stage 0 │───→│Stage 1 │───→│Stage 2 │───→│Stage 3 │      │
│  │        │    │ (중복: │    │ (중복: │    │        │      │
│  │        │    │Stage 2)│    │Stage 1)│    │        │      │
│  └────────┘    └────────┘    └────────┘    └────────┘      │
│                                                              │
│  Stage 2 장애 발생:                                         │
│  ┌────────┐    ┌────────┐                  ┌────────┐      │
│  │Stage 0 │───→│Stage 1 │─────────────────→│Stage 3 │      │
│  │        │    │즉시    │                  │        │      │
│  │        │    │Stage 2 │                  │        │      │
│  │        │    │역할 수행│                  │        │      │
│  └────────┘    └────────┘                  └────────┘      │
│                     │                                       │
│                     ▼                                       │
│              체크포인트 로드 없이 즉시 계속!                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 핵심 결과

- **복구 시간**: 수 분 → **수 초**
- **Preemptible VM 활용**: 비용 70-90% 절감하면서 안정적 학습
- **처리량 손실**: 버블 활용으로 **5-15%** 미만

#### 한계점

- 파이프라인 병렬화 필수
- 중복 연산으로 메모리 사용량 증가
- 복잡한 구현

---

### 5.3 Varuna (EuroSys '22 Best Paper)

**제목**: "Varuna: Scalable, Low-cost Training of Massive Deep Learning Models"
**저자**: Microsoft Research
**Source**: https://www.microsoft.com/en-us/research/publication/varuna-scalable-low-cost-training-of-massive-deep-learning-models/

#### 핵심 문제

대규모 모델 학습에는 고가의 전용 클러스터가 필요하지만, **Spot/Low-priority VM**은 5배 저렴

#### 핵심 기여

```
┌─────────────────────────────────────────────────────────────┐
│              Varuna Architecture                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 동적 모델 재분할 (Job Morphing)                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                                                      │    │
│  │   8 GPU 상태:          4 GPU로 축소:                │    │
│  │   ┌──┬──┬──┬──┐        ┌────┬────┐                  │    │
│  │   │S0│S1│S2│S3│   ──→  │S0+1│S2+3│                  │    │
│  │   │S4│S5│S6│S7│        │S4+5│S6+7│                  │    │
│  │   └──┴──┴──┴──┘        └────┴────┘                  │    │
│  │                                                      │    │
│  │   CutPoint로 분할 경계 정의                          │    │
│  │   리소스 변화에 따라 자동 재구성                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  2. Preemption 처리                                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  • SIGUSR1 시그널로 graceful shutdown               │    │
│  │  • 체크포인트 저장 후 종료                           │    │
│  │  • 새 리소스에서 재시작                              │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  3. 하이브리드 병렬화                                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Pipeline Parallelism + Data Parallelism             │    │
│  │  • 대역폭 효율적 사용                                │    │
│  │  • Commodity 네트워크에서도 성능 유지               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### CutPoint 정의

```python
from varuna import CutPoint

class MyModel(nn.Module):
    def __init__(self):
        self.layer1 = nn.Linear(...)
        self.cutpoint1 = CutPoint()  # 여기서 분할 가능
        self.layer2 = nn.Linear(...)
        self.cutpoint2 = CutPoint()  # 여기서도 분할 가능
        self.layer3 = nn.Linear(...)
    
    def forward(self, x):
        x = self.layer1(x)
        x = self.cutpoint1(x)  # 파이프라인 스테이지 경계
        x = self.layer2(x)
        x = self.cutpoint2(x)  # 다른 경계
        x = self.layer3(x)
        return x
```

#### 핵심 결과

- 기존 대비 **18배** 빠른 학습 시간
- 다른 파이프라인 병렬화 대비 **26%** 성능 향상
- **200B 파라미터** 모델을 Spot VM에서 학습 성공

#### 한계점

- 체크포인트 기반 복구 (디스크 I/O 필요)
- Preemption 시 전체 Job 재시작
- Hot spare 미지원

---

### 5.4 Oobleck (SOSP '23)

**제목**: "Oobleck: Resilient Distributed Training of Large Models Using Pipeline Templates"
**학회**: ACM SOSP 2023

#### 핵심 아이디어

**Pipeline Template** 기반 동적 재구성으로 노드 장애/추가에 즉시 대응

```
┌─────────────────────────────────────────────────────────────┐
│              Oobleck: Pipeline Templates                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Pipeline Template = 미리 정의된 파이프라인 구성            │
│                                                              │
│  Template Library:                                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Template A (8 GPU):  [S0|S1|S2|S3|S4|S5|S6|S7]     │    │
│  │  Template B (6 GPU):  [S0+1|S2|S3|S4|S5+6+7]        │    │
│  │  Template C (4 GPU):  [S0+1|S2+3|S4+5|S6+7]         │    │
│  │  Template D (2 GPU):  [S0+1+2+3|S4+5+6+7]           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  장애 발생 시:                                              │
│  1. 현재 가용 GPU 수 파악                                   │
│  2. 적합한 Template 선택                                    │
│  3. 모델 상태 재배치                                        │
│  4. 학습 즉시 재개                                          │
│                                                              │
│  장점:                                                       │
│  • 미리 계산된 Template으로 빠른 전환                       │
│  • 최적화된 구성 보장                                       │
│  • 다양한 클러스터 크기 지원                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 핵심 결과

- Spot VM에서 **안정적인** 대규모 모델 학습
- 노드 장애 시 **수 초** 내 재구성
- 기존 체크포인트 기반 복구 대비 **10배 이상** 빠른 복구

---

### 5.5 MegaScale (ByteDance, 2024)

**제목**: "MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs"
**저자**: ByteDance
**Source**: https://arxiv.org/abs/2402.15627

#### 핵심 성과

- **12,288 GPU**에서 **175B 파라미터** 모델 학습
- **55.2% MFU (Model FLOPs Utilization)** 달성
- Megatron-LM 대비 **1.34배** 효율 향상

#### Full-Stack Co-Design 접근법

```
┌─────────────────────────────────────────────────────────────┐
│              MegaScale Full-Stack Optimization               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: Model Architecture & Optimizer                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  • 학습 안정성을 위한 아키텍처 조정                  │    │
│  │  • 최적화된 Optimizer 설정                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 2: Computation & Communication                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  • Overlapping computation and communication        │    │
│  │  • Efficient collective operations                   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 3: Operator Optimization                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  • Fused kernels                                     │    │
│  │  • Memory-efficient attention                        │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 4: Data Pipeline                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  • Async data loading                                │    │
│  │  • Efficient preprocessing                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Layer 5: Network Performance                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  • Topology-aware placement                          │    │
│  │  • Congestion control                                │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 안정성 및 내결함성

> "Stability is an important consideration in production given the long extent of LLM training jobs."

- **진단 도구**: 시스템 컴포넌트 모니터링, 장애 원인 식별
- **Straggler 완화**: 느린 노드 감지 및 대응
- **체크포인트 전략**: 장기 학습을 위한 안정적인 체크포인트

---

### 5.6 GEMINI (Google) - 학습 인프라

Gemini 모델의 학습 인프라에 대한 공개 정보는 제한적이지만, 알려진 내용:

- **TPU v4/v5** 기반 대규모 학습
- **Pathways** 시스템 활용 추정
- **Multislice Training** 적용
- 상세 내결함성 메커니즘은 비공개

---

## 6. 기술 비교표

### 6.1 주요 기능 비교

| 기능 | PyTorch Elastic | NVRx | DeepSpeed | Google (Pathways/TPU) | AWS Checkpointless |
|------|----------------|------|-----------|----------------------|-------------------|
| **장애 감지** | Agent heartbeat | Hung Rank Detection | 외부 의존 | 시스템 레벨 | 분산 Health Monitor |
| **상태 복구 방식** | 체크포인트 로드 | 계층적 체크포인트 | 체크포인트 로드 | 체크포인트 + 하드웨어 중복 | 인메모리 상태 복제 |
| **복구 시간** | 수 분 ~ 수십 분 | 수 초 ~ 수십 초 | 수 분 ~ 수십 분 | 수 초 ~ 수 분 | **수 초** |
| **디스크 I/O 필요** | ✅ 필수 | ✅ (최적화됨) | ✅ 필수 | ✅ (비동기) | ❌ **불필요** |
| **Hot Spare 지원** | ❌ | ❌ | ❌ | ✅ (하드웨어 레벨) | ✅ |
| **In-Process Restart** | ❌ | ✅ | ❌ | 부분적 | ✅ |
| **검증된 규모** | 수백 GPU | 수천 GPU | 수천 GPU | 수만 TPU | 수천 GPU |
| **오픈소스** | ✅ | ✅ | ✅ | ❌ (비공개) | ❌ (AWS 서비스) |

### 6.2 복구 메커니즘 상세 비교

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Recovery Mechanism Comparison                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PyTorch Elastic:                                                       │
│  장애 → 전체 Worker 중단 → Rendezvous → 체크포인트 로드 → 재시작       │
│  [====== 수 분 ~ 수십 분 ======]                                        │
│                                                                          │
│  NVRx:                                                                  │
│  장애 → In-Process 감지 → 로컬 체크포인트 로드 → 재시작                 │
│  [== 수 초 ~ 수십 초 ==]                                                │
│                                                                          │
│  DeepSpeed:                                                             │
│  장애 → Job 재시작 → 체크포인트 로드 → 학습 재개                        │
│  [====== 수 분 ~ 수십 분 ======]                                        │
│                                                                          │
│  Google TPU:                                                            │
│  장애 → Hot Spare 활성화 → 상태 전송 → 학습 재개                        │
│  [== 수 초 ~ 수 분 ==]                                                  │
│                                                                          │
│  AWS Checkpointless:                                                    │
│  장애 → Hot Spare 활성화 → 인메모리 복제본 사용 → 즉시 재개             │
│  [= 수 초 =]                                                            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.3 학술 연구 비교

| 논문 | 핵심 기법 | 복구 시간 | 추가 오버헤드 | 적용 대상 |
|------|----------|----------|--------------|----------|
| **CheckFreq** | Snapshot-and-Persist | 체크포인트 간격 단축 | <5% | 모든 학습 |
| **Bamboo** | 파이프라인 버블 중복 연산 | **즉시** (Instant Takeover) | 5-15% | Pipeline Parallelism |
| **Varuna** | 동적 모델 재분할 | 수 분 (체크포인트 기반) | 낮음 | Spot VM |
| **Oobleck** | Pipeline Template 재구성 | **수 초** | 중간 | Spot VM, Pipeline |
| **MegaScale** | Full-Stack Co-Design | N/A (예방 중심) | 최적화됨 | 10,000+ GPU |

---

## 7. 핵심 인사이트 및 결론

### 7.1 기술 발전 방향

```
┌─────────────────────────────────────────────────────────────┐
│              Fault Tolerance Evolution                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1세대: 체크포인트 기반                                      │
│  └─→ 주기적 저장, 장애 시 전체 재시작                       │
│      예: PyTorch Elastic, DeepSpeed                         │
│                                                              │
│  2세대: 최적화된 체크포인트                                  │
│  └─→ 비동기/계층적 체크포인트, 빠른 복구                    │
│      예: NVRx, CheckFreq                                    │
│                                                              │
│  3세대: 중복 연산 기반                                       │
│  └─→ 파이프라인 버블 활용, Instant Takeover                 │
│      예: Bamboo                                             │
│                                                              │
│  4세대: 인메모리 복제                                        │
│  └─→ 디스크 I/O 제거, Hot Spare, 즉시 복구                  │
│      예: AWS Checkpointless                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 AWS Checkpointless의 차별점

| 기존 접근법의 한계 | AWS Checkpointless 해결책 |
|-------------------|-------------------------|
| 디스크 I/O 병목 | 인메모리 상태 복제로 I/O 제거 |
| 긴 복구 시간 | Hot Spare로 즉시 대체 |
| 전체 재시작 필요 | In-Process Recovery로 부분 복구 |
| Straggler 대응 어려움 | Hot Spare를 Straggler 대체에도 활용 |

### 7.3 선택 가이드

| 시나리오 | 권장 기술 |
|----------|----------|
| **소규모 학습 (< 100 GPU)** | PyTorch Elastic + 빈번한 체크포인트 |
| **중규모 학습 (100-1000 GPU)** | NVRx 또는 DeepSpeed |
| **대규모 학습 (1000+ GPU)** | AWS Checkpointless 또는 NVRx |
| **Spot VM 활용** | Varuna, Oobleck, Bamboo |
| **최대 Goodput 필요** | AWS Checkpointless |
| **오픈소스 필수** | NVRx + Bamboo 조합 |

### 7.4 미래 연구 방향

1. **하이브리드 접근법**: 인메모리 복제 + 비동기 체크포인트 조합
2. **예측적 장애 대응**: ML 기반 장애 예측으로 선제적 마이그레이션
3. **이기종 클러스터**: GPU + TPU + NPU 혼합 환경 내결함성
4. **분산 상태 관리**: Consistent Hashing 기반 효율적 상태 분산

---

## 참고 문헌

### 공식 문서
- PyTorch Elastic: https://pytorch.org/docs/stable/distributed.elastic.html
- NVIDIA NVRx: https://github.com/NVIDIA/nvidia-resiliency-ext
- DeepSpeed: https://www.deepspeed.ai/training/
- Varuna: https://github.com/microsoft/varuna

### 학술 논문
- Mohan et al., "CheckFreq: Frequent, Fine-Grained DNN Checkpointing," USENIX FAST '21
- Thorpe et al., "Bamboo: Making Preemptible Instances Resilient for Affordable Training of Large DNNs," USENIX NSDI '23
- Athlur et al., "Varuna: Scalable, Low-cost Training of Massive Deep Learning Models," EuroSys '22
- Jang et al., "Oobleck: Resilient Distributed Training of Large Models Using Pipeline Templates," ACM SOSP '23
- Jiang et al., "MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs," arXiv 2024
- Barham et al., "Pathways: Asynchronous Distributed Dataflow for ML," MLSys '22

---

> **문서 작성**: AI Research Document
> **최종 수정**: 2024년
> **참고**: 일부 URL은 접근 제한으로 인해 2차 자료를 참조하였습니다.
