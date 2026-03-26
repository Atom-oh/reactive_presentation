**Amazon SageMaker HyperPod Checkpointless Training**에 대한 상세 기술 분석 리포트입니다. 대규모 분산 학습에서 발생하는 근본적인 문제와 이를 해결하기 위한 AWS의 최신 혁신 아키텍처를 7가지 요청하신 항목에 맞추어 심층적으로 설명해 드립니다.

---

### 1. SageMaker HyperPod란 무엇인가?

SageMaker HyperPod는 수천에서 수만 개의 AI 가속기(GPU/Trainium)를 활용하여 Foundation Model(FM)을 학습하기 위해 설계된 AWS의 특수 목적 인프라스트럭처입니다.

*   **아키텍처 (Architecture):** Kubernetes(Amazon EKS) 또는 Slurm 기반의 오케스트레이션을 지원하며, 클러스터 상태를 지속적으로 모니터링하여 결함이 발생한 노드를 자동으로 감지하고 교체(Auto-recovery)하는 관리형 환경을 제공합니다.
*   **인스턴스 타입 (Instance Types):** 대규모 학습에 주로 사용되는 **Amazon EC2 P5 인스턴스 (p5.48xlarge)** 환경을 기본으로 합니다. 이는 노드당 8개의 NVIDIA H100 Tensor Core GPU와 막대한 CPU RAM 및 로컬 NVMe 스토리지를 갖추고 있습니다.
*   **EFA 네트워킹 (Elastic Fabric Adapter):** AWS의 고성능 네트워크 인터페이스인 EFA를 통해 노드 간 최대 **3,200 Gbps**의 초저지연 네트워크 대역폭을 제공합니다. OS 커널을 우회(OS Bypass)하여 GPU 간 직접 통신(GPUDirect RDMA)을 극대화하므로 병렬 학습 시 통신 병목을 최소화합니다.

---

### 2. 대규모 ML 학습에서 기존 Checkpointing의 문제점

수만 개의 GPU를 사용하는 "Frontier Scale" 학습에서는 하드웨어 장애가 예외가 아닌 **통계적 필연**입니다. (예: Meta의 Llama 3 405B 학습 시 54일간 466번의 장애 발생, 평균 3시간마다 중단)

*   **크기 계산 (Checkpoint Sizes):** 
    체크포인트는 모델 가중치(Weights)뿐만 아니라 Optimizer State(Adam의 경우 Momentum, Variance 등)를 포함해야 합니다.
    *   *공식:* Weights (파라미터 수 × 2 bytes, BF16) + Optimizer State (파라미터 수 × 8 bytes) = **파라미터 당 총 10 bytes**
    *   *예시:* Llama 3 70B 모델은 약 **521 GB**, DeepSeek-V3 (671B) 모델은 **5 TB** 이상의 스토리지를 한 번에 기록해야 합니다.
*   **I/O 병목 (The I/O Bottleneck):**
    수십~수백 개의 노드가 동시에 테라바이트 급의 데이터를 S3나 FSx for Lustre와 같은 영구 스토리지에 동기적(Synchronous)으로 기록해야 합니다. 이 과정에서 학습 연산이 완전히 일시 정지(Synchronous Barrier)되며, 네트워크 대역폭을 극심하게 소모합니다.
*   **복구 시간 (Recovery Time):** 
    장애 발생 시 1) 전체 Job 강제 종료, 2) 클러스터 재할당 및 프로세스 초기화, 3) S3에서 수 TB 데이터 로드, 4) Dataloader 초기화 등 6단계의 순차적 복구 단계를 거치며 **15분에서 최대 1시간 이상** 소요됩니다. 이는 고가의 GPU 클러스터를 유휴 상태로 만들어 막대한 비용 손실을 초래합니다.

---

### 3. Checkpointless Training의 5가지 핵심 컴포넌트

AWS가 2025년 말 새롭게 발표한 Checkpointless Training은 데이터를 디스크에 저장(Save-to-Disk)하는 대신, 클러스터 전체의 **메모리(RAM) 기반 Peer-to-Peer 상태 복제**로 패러다임을 전환한 기술입니다.

#### Component 1: Rootless/TCPStore-less NCCL 초기화
*   **기술 상세:** 기존의 분산 통신 라이브러리(NCCL, Gloo)는 중앙의 'Rank 0 (Master)' 노드가 TCPStore를 관리하여 프로세스를 동기화했습니다. Master 노드가 죽으면 전체 통신 링(Ring)이 붕괴되어 재설정에 수십 분이 걸렸습니다.
*   **해결책:** 중앙 집중식 TCPStore를 제거하고, 각 Rank가 독립적으로 피어(Peer) 연결 정보를 계산하는 **Decentralized Handshake(대칭형 주소 지정 패턴)** 방식을 도입했습니다. 이를 통해 프로세스 그룹 재초기화 시간을 수십 분에서 **단 몇 초**로 단축시켰습니다.

#### Component 2: Memory-Mapped Data Loading (MMAP)
*   **기술 상세:** 데이터 로더가 데이터를 읽어오는 과정은 상당한 CPU 오버헤드와 시간을 소모합니다. 프로세스가 재시작될 때마다 데이터 인덱스를 처음부터 다시 스캔하는 것은 비효율적입니다.
*   **해결책:** 훈련 데이터 인덱스와 Pre-fetch 된 배치 데이터를 호스트의 영구 공유 메모리 영역인 `/dev/shm`에 **Memory-Mapping** 합니다. 프로세스 장애로 Python 런타임이 재시작되더라도, 캐시된 배치 데이터가 RAM에 그대로 유지되므로 즉시 학습을 재개할 수 있습니다. 노드당 8개 GPU가 1개의 공유 복사본만 사용하여 메모리 점유율도 획기적으로 낮췄습니다.

#### Component 3: In-Process Recovery (IPR)
*   **기술 상세:** 기존에는 하나의 GPU에서 Cuda Error가 발생하면 전체 클러스터의 Job을 강제로 죽이고 처음부터 다시 시작했습니다(Job-level Restart).
*   **해결책:** 장애를 **프로세스 레벨(Process-level)** 로 격리합니다. 결함이 없는 정상 노드들은 프로세스를 종료하지 않고 기존의 CUDA Context와 컴파일러 캐시를 유지한 채 대기 상태(Wait state)에 진입합니다. 장애가 발생한 코드 블록(Re-executable Code Block, RCB)만 캡슐화하여, 문제가 해결된 후 해당 스텝을 재실행합니다.

#### Component 4: Peer-to-Peer State Replication
*   **기술 상세:** 이것이 "디스크 I/O를 없앤" 핵심입니다. `num_distributed_optimizer_instances >= 2` 와 같은 하이브리드 샤딩 기법을 사용하여, 모델의 Weights와 Optimizer State를 여러 노드 그룹에 중복 복제(N+1 또는 M-copy Redundancy)합니다.
*   **복구 메커니즘:** 노드 교체가 발생하면, S3에서 수 TB의 체크포인트를 다운로드하는 대신 **초고속 EFA 네트워크(3,200 Gbps)** 를 통해 살아있는 피어(Peer) 노드의 CPU/GPU 메모리에서 직접 상태 데이터를 가져옵니다. 

#### Component 5: HyperPod Training Operator
*   **기술 상세:** 이 모든 과정을 조율하는 K8s 네이티브 오퍼레이터입니다.
*   **동작 흐름:** Hanging(멈춤) 등 노드 헬스 모니터링 $\rightarrow$ 결함 노드 Cordon 처리 $\rightarrow$ 미리 준비된 **Hot Spare(예비 노드)** 즉시 투입 $\rightarrow$ 프로세스 레벨 재시작 지시 $\rightarrow$ P2P 상태 복원 트리거 $\rightarrow$ 학습 재개. 전체 복구 과정을 외과 수술처럼 정밀하고 자동화되게 제어합니다.

---

### 4. 성능 벤치마크

*   **복구 시간 (Recovery Time):** 기존 15~30분 이상 소요되던 복구 시간을 **90초 미만 (2분 이내)** 으로 단축했습니다. (전통 방식 대비 80~93% 시간 단축)
*   **Goodput (유효 학습 시간 비율):** 잦은 장애에도 불구하고 클러스터의 전체 Goodput을 **95% 이상**으로 유지합니다.
*   **검증 결과 (Amazon Nova):** 이 기술은 수만 개의 가속기가 투입된 거대 언어 모델인 **Amazon Nova** 제품군 학습에 직접 사용되어 프로덕션 레벨의 검증을 마쳤습니다. 초대규모 스케일에서도 스토리지 병목 없이 안정적인 스케일링을 증명했습니다.

---

### 5. 코드 예시 (Code Examples)

기존 PyTorch 코드에 최소한의 수정만으로 적용할 수 있도록 설계되었습니다.

**1) 환경 변수 (Environment Variables):**
Rootless NCCL 통신을 활성화하기 위한 설정입니다.
```bash
export HPCT_USE_ROOTLESS=1
sysctl -w net.ipv4.ip_local_port_range="20000 65535"
```

**2) Python Decorator & MMAP Dataloader:**
장애 발생 시 재실행 가능한 코드 블록(RCB)을 지정하는 데코레이터와 공유 메모리 데이터 로더 설정입니다.
```python
from hyperpod_checkpointless_training.dataloader.mmap_data_module import MMAPDataModule
from hyperpod_checkpointless_training.inprocess.wrap import HPWrapper

# 1. MMAP Data Loader 설정
data_module = MMAPDataModule(
    data_module=MY_DATA_MODULE(...),
    mmap_config=CacheResumeMMAPConfig(
        cache_dir="/dev/shm/pdl_cache", # 공유 메모리 활용
        prefetch_length=10
    ),
)

# 2. In-Process Recovery Wrapper
@HPWrapper(
    health_check=CudaHealthCheck(),
    hp_api_factory=HPAgentK8sAPIFactory(),
    abort=CheckpointlessAbortManager.get_default_checkpointless_abort(),
)
def run_main(cfg, caller=None):
    trainer = Trainer(
        strategy=CheckpointlessMegatronStrategy(
            # N+1 Redundancy를 위한 다중 인스턴스 설정
            num_distributed_optimizer_instances=2 
        )
    )
    trainer.wrapper = caller
```

**3) K8s/HyperPod Operator YAML 설정:**
실행 시 `hyperpodrun` 커맨드에 `--inprocess-restart` 플래그를 주입합니다.
```yaml
apiVersion: sagemaker.amazonaws.com/v1
kind: HyperPodPytorchJob
metadata:
  name: checkpointless-training-job
spec:
  nprocPerNode: "8"
  replicaSpecs:
    - name: worker
      replicas: 16
      template:
        spec:
          containers:
            - name: training
              image: <hyperpod-checkpointless-container-image>
              command:
                - hyperpodrun
                - --nproc_per_node=8
                - --inprocess-restart  # In-Process Recovery 활성화
                - training_script.py
```

---

### 6. 경쟁 기술 비교

| 기술/프레임워크 | Failure Handling | State Recovery (복구 방식) | 기술적 차별점 / 한계점 |
| :--- | :--- | :--- | :--- |
| **AWS Checkpointless** | In-Process + P2P | **From Peer Memory** (RAM) | 디스크 I/O를 완전히 제거. EFA를 통한 실시간 메모리 복제. HyperPod K8s 오퍼레이터 기반의 Hot-spare 즉시 교체. |
| **PyTorch Elastic (torchelastic)** | Job-Level Restart | From Disk (S3/NFS) | 클러스터 규모 동적 변경에는 유리하나, 단일 노드 장애 시 전체 프로세스를 죽이고 디스크에서 다시 로드해야 함. |
| **NVIDIA NVRx (NeMo Resiliency)** | In-Process Restart | From Disk (Async) | 비동기 체크포인팅과 In-Process 재시작을 지원하나 본질적으로 스토리지(Disk) 에 의존. (참고: AWS 솔루션도 NeMo 기반이지만 P2P Memory State가 핵심 차별점임) |
| **DeepSpeed** | Node-local / S3 | From Disk | ZeRO Stage 3에서 병렬 쓰기를 지원하나 복구 시 동기화 오버헤드 존재. |
| **Google Pathways (OCS)** | Job-Level/Dynamic | Hardware Re-routing | Optical Circuit Switch(광스위치) 하드웨어를 활용해 물리적 네트워크 토폴로지를 재구성. 반면 AWS는 고정 패브릭 위에서 소프트웨어 정의 '인메모리 복제'에 집중. |

---

### 7. 관련 학술 연구 배경

이러한 Checkpointless 설계는 다음과 같은 핵심 학술 연구와 분산 시스템 이론에 깊은 뿌리를 두고 있습니다.

*   **CheckFreq (USENIX FAST '21):** 빈번한 체크포인팅으로 인한 I/O 병목(스톨)을 해결하기 위해 'Fine-grained Snapshot-and-Persist' 기법을 제안한 논문입니다. 백그라운드 프로세스를 통해 학습과 스토리지 I/O를 비동기적으로 분리하여 오버헤드를 숨기는 개념을 발전시켰습니다.
*   **Bamboo (NSDI '23):** 분산 파이프라인 병렬 학습 시 필연적으로 발생하는 유휴 시간(Pipeline Bubbles)을 활용하여 "잉여 연산(Redundant Computation)"을 수행하는 연구입니다. 한 노드가 죽었을 때 이웃 노드가 이미 연산해 둔 상태를 즉시 넘겨받아 복구 지연을 없애는 개념이 AWS P2P State Replication에 영향을 주었습니다.
*   **Varuna (Microsoft, EuroSys '22):** 저렴하지만 불안정한 Spot VM 환경에서 대규모 모델을 훈련하기 위해 모델 파티셔닝을 동적으로 재구성하는 연구입니다. 탄력적(Elastic)인 클러스터 축소/확장 시나리오의 기초가 되었습니다.
*   **Oobleck (SOSP '23):** 파이프라인 템플릿 인스턴스화 및 분산 캐싱을 통해 노드 장애 시 파이프라인을 매우 빠르게 재구성하고 결함 허용(Fault Tolerance)을 달성하는 연구로, AWS의 In-Process Recovery 메커니즘과 빠른 장애 격리 사상과 맥락을 같이 합니다.
