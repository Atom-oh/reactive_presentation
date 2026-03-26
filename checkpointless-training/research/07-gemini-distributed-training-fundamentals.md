분산 머신러닝 학습(Distributed Machine Learning Training)의 기초부터 심화 개념까지, 요청하신 목차에 따라 교과서 수준으로 상세히 설명해 드리겠습니다.

---

### 1. Neural Network Training 기초

#### 1.1 Forward Pass & Backward Pass (Backpropagation)
Neural Network의 학습은 데이터를 통과시켜 예측값을 얻는 **Forward pass**와, 오차를 계산해 가중치를 업데이트하는 **Backward pass**의 반복입니다.

*   **Forward Pass**: 입력 데이터 $X$가 각 레이어를 통과하며 연산됩니다. 특정 레이어 $l$에서의 연산은 다음과 같습니다.
    *   선형 변환 (Linear Transformation): $Z^{(l)} = W^{(l)}A^{(l-1)} + b^{(l)}$
    *   활성화 함수 (Activation): $A^{(l)} = \sigma(Z^{(l)})$
    *   최종적으로 모델의 출력 $\hat{Y}$를 얻고, 실제 정답 $Y$와의 차이를 손실 함수(Loss Function) $\mathcal{L}(\hat{Y}, Y)$로 계산합니다.
*   **Backward Pass (Backpropagation)**: 오차를 최소화하기 위해 **연쇄 법칙(Chain Rule)**을 사용하여 각 가중치(Weight)에 대한 손실 함수의 그래디언트(Gradient)를 계산합니다.
    *   $\frac{\partial \mathcal{L}}{\partial W^{(l)}} = \frac{\partial \mathcal{L}}{\partial A^{(l)}} \cdot \frac{\partial A^{(l)}}{\partial Z^{(l)}} \cdot \frac{\partial Z^{(l)}}{\partial W^{(l)}}$
    *   이 그래디언트는 해당 가중치를 어느 방향으로 얼마나 수정해야 손실이 줄어드는지를 나타내는 벡터입니다.

#### 1.2 옵티마이저 (Optimizer): SGD, Adam, AdamW
계산된 그래디언트를 바탕으로 파라미터 $\theta$를 업데이트하는 알고리즘입니다.

*   **SGD (Stochastic Gradient Descent)**: 가장 기본적인 형태로, 학습률(Learning Rate) $\eta$만큼 그래디언트의 반대 방향으로 이동합니다.
    *   $\theta_{t+1} = \theta_t - \eta \nabla \mathcal{L}(\theta_t)$
    *   여기에 **Momentum**을 추가하여 이전 그래디언트의 이동 방향을 기억($v_{t}$)하게 하면 진동을 줄이고 수렴 속도를 높일 수 있습니다.
*   **Adam (Adaptive Moment Estimation)**: 각 파라미터마다 학습률을 적응적으로 조절합니다. 그래디언트의 1차 모멘트(평균, $m_t$)와 2차 모멘트(분산, $v_t$)를 지수 이동 평균으로 계산합니다.
    *   $m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t$ (Momentum 역할)
    *   $v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2$ (RMSProp 역할)
    *   Bias Correction: 초기 학습 시 0으로 편향되는 것을 막기 위해 보정합니다. $\hat{m}_t = \frac{m_t}{1-\beta_1^t}$, $\hat{v}_t = \frac{v_t}{1-\beta_2^t}$
    *   Update: $\theta_{t+1} = \theta_t - \eta \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}$
*   **AdamW**: Adam 옵티마이저에서 Weight Decay(L2 정규화)를 분리(Decouple)한 버전입니다. 표준 Adam은 $v_t$ 계산에 Weight Decay가 포함되어 학습률 적응에 왜곡을 주지만, AdamW는 그래디언트 업데이트와 Weight Decay를 독립적으로 수행하여 일반화(Generalization) 성능을 높입니다.
    *   $\theta_{t+1} = \theta_t - \eta \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon} - \eta \lambda \theta_t$ ($\lambda$는 Weight decay coefficient)

#### 1.3 Mixed Precision Training
메모리 사용량을 줄이고 연산 속도를 높이기 위해 다양한 정밀도(Precision)의 부동소수점 데이터 타입을 혼합하여 사용합니다.

*   **FP32 (Single Precision)**: 32-bit (부호 1, 지수 8, 가수 23). 딥러닝의 표준 데이터 타입이지만 메모리와 대역폭을 많이 차지합니다.
*   **FP16 (Half Precision)**: 16-bit (부호 1, 지수 5, 가수 10). 표현 가능한 범위(Dynamic Range)가 좁아 너무 작은 그래디언트는 0이 되는 Underflow, 너무 큰 값은 무한대가 되는 Overflow가 발생합니다. 이를 막기 위해 Loss를 임시로 키우는 **Loss Scaling** 기법이 필수적입니다.
*   **BF16 (Brain Floating Point)**: 16-bit (부호 1, 지수 8, 가수 7). 구글이 제안한 포맷으로, 지수부가 FP32와 동일하여 표현 범위가 넓습니다. 정밀도는 낮지만 딥러닝은 노이즈에 강하므로 Loss Scaling 없이도 안정적인 학습이 가능하여 LLM 학습의 표준으로 자리 잡았습니다.
*   **FP8**: NVIDIA Hopper 아키텍처 등에서 지원하는 8-bit 포맷입니다. 메모리 대역폭을 극대화하며, E4M3(정밀도 우선)와 E5M2(범위 우선) 두 가지 포맷을 상황에 맞게 섞어 씁니다.
*   **Mixed Precision 훈련 방식**: Forward/Backward 연산은 빠르고 메모리를 적게 먹는 BF16/FP16으로 수행하고, 파라미터 업데이트 시 누적 오차를 막기 위해 마스터 가중치(Master Weights)를 FP32로 유지하여 업데이트합니다.

#### 1.4 Learning Rate Scheduler
학습 과정에서 학습률(Learning Rate)을 동적으로 조절하여 수렴을 돕습니다.

*   **Warmup**: 학습 초기에 초기화된 불안정한 가중치에 큰 그래디언트가 곱해져 모델이 망가지는 것(Divergence)을 막기 위해, 매우 작은 학습률에서 시작하여 목표 학습률까지 선형적으로 증가시킵니다.
*   **Cosine Decay**: Warmup 이후, 코사인 함수 곡선을 따라 학습률을 0에 가깝게 서서히 감소시킵니다. 학습 후반부에 미세한 가중치 조정(Fine-tuning)을 가능하게 하여 Local Minima를 더 잘 찾아가게 돕습니다.
    *   $\eta_t = \eta_{min} + \frac{1}{2}(\eta_{max} - \eta_{min})\left(1 + \cos\left(\frac{T_{cur}}{T_{max}}\pi\right)\right)$

---

### 2. 분산 학습 패러다임 상세

LLM과 같이 거대한 모델은 단일 GPU의 메모리(VRAM)에 올라가지 않으므로, 여러 GPU에 연산과 데이터를 분산해야 합니다.

*   **Data Parallelism (DP/DDP - Distributed Data Parallel)**
    *   **개념**: 모든 GPU가 동일한 전체 모델(Model Replica)을 가집니다. 전체 데이터셋을 쪼개어(Mini-batch) 각 GPU에 할당합니다.
    *   **동작**: 각 GPU는 할당된 데이터로 Forward/Backward pass를 독립적으로 수행하여 각자의 그래디언트를 구합니다.
    *   **동기화**: 파라미터 업데이트 전, `All-Reduce` 연산을 통해 모든 GPU의 그래디언트를 평균 내어 합칩니다. 이후 각 GPU가 동일한 그래디언트로 파라미터를 업데이트하여 모델을 똑같은 상태로 유지합니다.
*   **Tensor Parallelism (TP)**
    *   **개념**: 하나의 거대한 행렬 곱셈 연산(예: Attention QKV 투영, FFN 레이어)을 여러 GPU로 쪼개어 분산 연산합니다. Megatron-LM에 의해 널리 알려졌습니다.
    *   **동작**: 행렬을 가로(Row) 또는 세로(Column)로 분할합니다. 레이어 내부의 연산 과정 중에 결과값을 합치기 위해 빈번한 `All-Reduce`나 `All-Gather` 통신이 발생합니다.
    *   **특징**: 통신 오버헤드가 매우 크기 때문에, 대역폭이 극도로 높은 단일 노드 내부(Intra-node, NVLink 환경)에서만 주로 사용됩니다.
*   **Pipeline Parallelism (PP)**
    *   **개념**: 모델의 레이어를 순차적으로 쪼개어 여러 GPU에 올립니다. (예: GPU 0은 Layer 1~10, GPU 1은 Layer 11~20).
    *   **Micro-batch**: 단순히 데이터를 넘기면 한 GPU가 연산할 때 나머지 GPU는 노는 현상이 발생합니다. 이를 해결하기 위해 하나의 배치를 여러 개의 **마이크로배치(Micro-batch)**로 잘라서 파이프라인에 밀어 넣습니다.
    *   **Pipeline Bubble**: 파이프라인의 시작과 끝, Backward로 전환되는 시점 등에서 어쩔 수 없이 GPU가 유휴 상태로 대기하는 시간을 Bubble이라고 합니다. 이를 줄이기 위해 1F1B(One Forward, One Backward) 등의 스케줄링 기법이 사용됩니다.
*   **Sequence / Context Parallelism (CP)**
    *   **개념**: 최근 100k, 1M 이상의 긴 컨텍스트(Long Context)를 처리하기 위해 등장했습니다. 시퀀스 길이(Sequence Length) 차원을 여러 GPU로 분할합니다.
    *   **동작**: Ring-Attention이나 DeepSpeed-Ulysses 같은 알고리즘을 사용하여, 쪼개진 시퀀스 조각들이 Attention 연산을 수행하기 위해 키(Key)와 밸류(Value)를 링 구조로 통신하며 계산을 완성합니다.
*   **Expert Parallelism (EP)**
    *   **개념**: Mixture of Experts (MoE) 아키텍처에서 사용됩니다. 모델 전체가 아닌 특정 FFN 레이어들이 여러 개의 'Expert' 네트워크로 나뉘어 있을 때, 이 Expert들을 다른 GPU에 분산 배치합니다.
    *   **동작**: 라우터가 토큰을 평가한 후, 해당 토큰을 처리할 Expert가 있는 GPU로 토큰 데이터를 보냅니다(`All-to-All` 통신). 연산 후 결과를 다시 원래 GPU로 가져옵니다.
*   **3D Parallelism**
    *   대규모 학습에서는 위 패러다임을 조합합니다. 보통 **DP (노드 간) + PP (노드 간/내) + TP (노드 내)** 형태로 구성하여 수천 개의 GPU를 효율적으로 활용합니다.

---

### 3. FSDP와 ZeRO 상세

표준 Data Parallelism(DP)은 각 GPU가 동일한 모델, 옵티마이저 상태, 그래디언트를 모두 메모리에 들고 있어 심각한 메모리 중복을 야기합니다. 이를 해결하기 위해 **Zero Redundancy Optimizer (ZeRO)**가 제안되었고, PyTorch 네이티브로 구현된 것이 **FSDP(Fully Sharded Data Parallel)**입니다.

#### 3.1 ZeRO Stages
ZeRO는 학습 상태(Model States)를 여러 GPU에 조각내어(Sharding) 저장하고, 필요할 때만 통신으로 가져와 메모리 효율을 극대화합니다.
*   **ZeRO Stage 1 ($P_{os}$)**: **Optimizer States**를 샤딩합니다. (가장 메모리를 많이 차지하는 FP32 Adam 상태 변수들). 각 GPU는 전체 파라미터 중 자신이 맡은 부분의 옵티마이저 상태만 유지하고 업데이트합니다.
*   **ZeRO Stage 2 ($P_{os+g}$)**: Optimizer States와 **Gradients(그래디언트)**를 샤딩합니다. Backward pass 후 각 GPU는 자신이 담당하는 파라미터의 그래디언트만 유지합니다.
*   **ZeRO Stage 3 ($P_{os+g+p}$)**: **Model Parameters(가중치)**까지 모두 샤딩합니다. 각 GPU는 모델의 일부분만 메모리에 상주시키며, 연산이 필요할 때만 다른 GPU로부터 파라미터를 가져옵니다. (이것이 FSDP와 기술적으로 거의 동일합니다).

#### 3.2 FSDP 동작 과정 (ZeRO-3와 동일)
*   **Forward Pass**: 특정 레이어 $L$의 연산이 시작되기 직전, 모든 GPU가 통신(`All-Gather`)하여 흩어져 있는 $L$의 가중치를 하나로 모읍니다. 연산이 끝나면 모아둔 파라미터를 즉시 버려(Free) 메모리를 확보합니다.
*   **Backward Pass**: Backward 연산을 위해 다시 $L$의 가중치를 `All-Gather`합니다. 로컬 그래디언트를 계산한 뒤, `Reduce-Scatter` 연산을 통해 전체 그래디언트를 합산함과 동시에 샤딩된 형태로 각 파라미터를 담당하는 GPU에게 분배합니다. 분배가 끝난 그래디언트와 파라미터는 메모리에서 해제합니다.
*   **Update**: 각 GPU는 자신이 온전히 담당하고 있는 파라미터 조각(Shard)에 대해서만 옵티마이저 스텝을 실행하여 가중치를 업데이트합니다.

#### 3.3 메모리 계산 예시: 70B 모델, 256 GPU, ZeRO-3 적용 시
*   **단일 파라미터당 필요 메모리 (Mixed Precision, Adam 기준)**:
    *   FP16/BF16 Model Weights: 2 Bytes
    *   FP16/BF16 Gradients: 2 Bytes
    *   FP32 Master Weights (Optimizer State): 4 Bytes
    *   FP32 Momentum (Optimizer State): 4 Bytes
    *   FP32 Variance (Optimizer State): 4 Bytes
    *   **총계: 1 파라미터당 16 Bytes**
*   **전체 모델 상태 메모리**: 70 Billion * 16 Bytes $\approx$ **1,120 GB (1.12 TB)**. (단일 GPU에는 절대 올라가지 않습니다).
*   **ZeRO-3 (256 GPU 분산)**:
    *   GPU당 모델 상태 메모리: 1,120 GB / 256 GPU $\approx$ **4.375 GB**.
    *   *참고: 실제 환경에서는 여기에 Forward Pass 시 발생하는 Activation 메모리와 NCCL 통신 버퍼가 추가되지만, 순수 모델 구동용 정적 메모리 공간은 80GB VRAM 중 약 4.4GB만 차지하게 되어 학습이 가능해집니다.*

---

### 4. NCCL 상세 (NVIDIA Collective Communications Library)

분산 학습에서 GPU 간의 데이터를 주고받는 고성능 통신 라이브러리입니다.

#### 4.1 Collective Operations (집단 통신)
*   **All-Reduce**: 모든 GPU가 가진 텐서의 동일한 위치의 값들을 더하거나 평균 내고(Reduce), 그 최종 결과를 다시 모든 GPU가 동일하게 나누어 가집니다(All). DP에서 그래디언트 동기화에 필수적입니다.
*   **All-Gather**: 각 GPU가 가지고 있는 텐서 조각들을 하나로 이어 붙여(Concatenate), 전체 텐서를 완성한 뒤 모든 GPU가 동일하게 복사본을 가집니다. (FSDP에서 파라미터 모을 때 사용).
*   **Reduce-Scatter**: 모든 GPU의 텐서를 Reduce 연산(합산)한 뒤, 그 결과를 N개의 조각으로 나누어 각 GPU가 자기에게 할당된 하나의 조각만 가져갑니다(Scatter). (All-Reduce는 사실 `Reduce-Scatter` 후 `All-Gather`를 수행하는 것과 같습니다).

#### 4.2 알고리즘: Ring vs Tree
*   **Ring Algorithm**: GPU들을 논리적인 링(Ring) 형태로 연결합니다. 데이터를 청크(Chunk)로 쪼개어 이웃한 GPU로 순환시킵니다. 대역폭 활용도는 매우 높지만, 노드 수가 많아지면 링을 한 바퀴 도는 데 걸리는 지연 시간(Latency)이 선형적으로 증가합니다.
*   **Tree Algorithm (Double Binary Tree)**: 수많은 노드를 트리 구조로 연결합니다. 하위 노드에서 상위 노드로 데이터를 올리면서 Reduce하고, 최상위에서 다시 하위로 Broadcast 합니다. 대규모 클러스터에서 지연 시간을 줄이는 데 유리합니다. NCCL은 네트워크 규모에 따라 두 알고리즘을 최적화하여 선택합니다.

#### 4.3 NCCL 초기화 (TCPStore, Rendezvous)
분산 학습을 시작하려면 수백 개의 프로세스(GPU)가 서로의 존재와 위치를 알아야 합니다.
*   **Rendezvous**: PyTorch 등은 분산 환경 초기화 시 `init_process_group`을 호출합니다. 이때 마스터 노드(보통 Rank 0)에 `TCPStore`라는 키-밸류 저장소를 엽니다.
*   나머지 노드들이 마스터 노드의 IP와 Port로 접속하여 자신의 주소 정보를 등록하고, 서로 연결할 준비를 마칩니다. 이후 NCCL이 고유 식별자(Unique ID)를 생성하여 본격적인 집단 통신 그룹(Communicator)을 형성합니다.

#### 4.4 토폴로지 탐색 (Topology Discovery)
NCCL은 시작 시 하드웨어 구성을 자동으로 탐색(hwloc 기반)하여 최적의 통신 경로 그래프를 그립니다.
*   **Intra-node (노드 내부)**: GPU 간 연결에 **NVLink** 및 NVSwitch를 우선적으로 사용합니다. (H100 기준 GPU당 900 GB/s의 양방향 대역폭). NVLink가 없으면 PCIe 브리지를 거쳐 통신합니다.
*   **Inter-node (노드 간)**: 노드 간 통신에는 네트워크 인터페이스 카드(NIC)를 사용합니다. 이때 CPU와 시스템 메모리를 우회하여 다른 노드의 GPU VRAM에 직접 데이터를 쏘는 **RDMA(Remote Direct Memory Access)** 기술을 사용합니다. 이를 위해 **InfiniBand** 하드웨어나 AWS의 **EFA (Elastic Fabric Adapter)**와 같은 고성능 네트워크 패브릭이 사용됩니다.

---

### 5. Checkpoint가 저장하는 것들 & 크기 계산

학습이 중단되더라도 이전 상태를 완벽히 복원(Resuming)하기 위해 체크포인트에는 단순히 모델의 가중치뿐만 아니라 학습의 "맥락"이 모두 저장되어야 합니다.

#### 5.1 체크포인트의 구성 요소
1.  **Model Parameters**: 현재 시점의 모델 가중치. 보통 정밀도(BF16 또는 FP32)를 유지하여 저장합니다.
2.  **Optimizer States**: **가장 용량이 큽니다.** Adam 옵티마이저의 경우 파라미터별 1차 모멘텀(Momentum)과 2차 모멘텀(Variance), 그리고 누적 스텝 수(Step)를 저장합니다. 이를 잃어버리면 학습 재개 시 Loss 스파이크가 발생합니다.
3.  **LR Scheduler State**: 현재 어느 에포크/스텝인지, 현재 Learning Rate 값은 얼마인지 저장합니다.
4.  **RNG States (Random Number Generator)**: PyTorch, CUDA (cuDNN 포함), Numpy 등의 난수 생성기 시드(Seed) 및 현재 상태. 데이터 셔플링 순서나 Dropout 등이 정확히 이전 시점과 이어지도록 하기 위해 필수적입니다.
5.  **Data Loader Position**: 수백만 개의 문서를 처리하는 도중 끊겼다면, 어느 파일의 몇 번째 배치까지 처리했는지 인덱스를 저장합니다. (Gradient Buffers는 보통 저장하지 않습니다. 스텝이 끝나면 업데이트 후 버려지기 때문입니다.)

#### 5.2 체크포인트 크기 계산 (Llama 3 모델 기준)
학습 체크포인트(Full Training Checkpoint)의 크기를 계산할 때는 Mixed Precision (ZeRO 사용) 환경을 가정합니다.
*   **단일 파라미터당 필요 저장 공간**: BF16 파라미터 가중치(2 Bytes) + FP32 Master Weights(4 Bytes) + FP32 Momentum(4 Bytes) + FP32 Variance(4 Bytes) = **총 14 Bytes**. (구현체에 따라 FP32 가중치를 버리고 BF16 가중치만 저장하기도 하지만, 완벽한 FP32 정밀도 보존을 가정하면 14 Bytes가 표준적입니다).
*   순수 추론(Inference) 목적의 배포 모델은 가중치(BF16/FP16, 2 Bytes)만 필요합니다.

*   **Llama 3 8B (약 80억 개 파라미터)**
    *   추론용 모델 (BF16 Weights): 8 Billion * 2 Bytes $\approx$ **16 GB**
    *   학습용 풀 체크포인트: 8 Billion * 14 Bytes $\approx$ **112 GB**
*   **Llama 3 70B (약 700억 개 파라미터)**
    *   추론용 모델 (BF16 Weights): 70 Billion * 2 Bytes $\approx$ **140 GB**
    *   학습용 풀 체크포인트: 70 Billion * 14 Bytes $\approx$ **980 GB (거의 1 TB)**
*   **Llama 3 405B (약 4,050억 개 파라미터)**
    *   추론용 모델 (BF16 Weights): 405 Billion * 2 Bytes $\approx$ **810 GB**
    *   학습용 풀 체크포인트: 405 Billion * 14 Bytes $\approx$ **5,670 GB (약 5.67 TB)**

이처럼 초거대 모델은 단 한 번의 체크포인트를 저장하는 데에도 수 테라바이트의 스토리지 입출력(I/O) 병목이 발생하기 때문에, 비동기식(Asynchronous) 체크포인팅이나 분산 파일 시스템(Lustre 등)의 활용이 필수적입니다.
