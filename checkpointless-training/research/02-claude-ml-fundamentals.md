# Claude Agent: ML Training Fundamentals

_Source: Claude Agent (subagent with WebFetch)_

---


---
_=== a0ec8c75f4e7713aa.output === 153 lines_


I have gathered substantial information from the successful fetches. Let me now synthesize everything into a comprehensive research document for your conference talk.

## Research: ML Training Checkpointing and Fault Tolerance Fundamentals

### Findings

Based on the documentation I was able to retrieve, here is a comprehensive synthesis of ML training checkpointing and fault tolerance concepts suitable for an AWS Solutions Architect audience.

---

## 1. How Distributed Training Works

### The Training Step Analogy

Think of training a neural network like a factory assembly line where each step involves:

1. **Forward Pass**: Raw materials (input data) flow through the assembly line (model layers), with each station (layer) transforming the product until you get the final output (prediction).

2. **Loss Calculation**: Quality control compares the output against the expected result and measures how far off it is.

3. **Backward Pass (Backpropagation)**: Error reports flow backward through the factory, telling each station exactly how to adjust its machinery to reduce defects.

4. **Gradient Synchronization**: In distributed training, all parallel factories must agree on the same adjustments before updating their machinery.

5. **Optimizer Step**: Each station updates its settings based on the aggregated feedback.

### Types of Parallelism

**Source**: https://huggingface.co/docs/transformers/main/en/perf_train_gpu_many

| Parallelism Type | What It Splits | Memory Benefit | Communication Overhead | When to Use |
|------------------|----------------|----------------|------------------------|-------------|
| **Data Parallelism (DP/DDP)** | Input batch | None (full model replicated) | Gradient all-reduce | Model fits in single GPU |
| **Tensor Parallelism (TP)** | Individual layer computations | Proportional to split | High (within each operation) | Single layer too large for GPU |
| **Pipeline Parallelism (PP)** | Model layers across stages | Proportional to stages | Moderate (between stages) | Model too large, layers fit |
| **ZeRO / FSDP** | Optimizer state, gradients, parameters | Up to N-fold (N = GPU count) | Additional all-gather/reduce-scatter | Large models, memory-constrained |

**Analogy for a Solutions Architect**:
- **Data Parallelism** = Running multiple identical EC2 instances behind a load balancer, each processing different requests
- **Tensor Parallelism** = Splitting a single database query across multiple shards that must coordinate for each operation
- **Pipeline Parallelism** = A Step Functions workflow where each Lambda handles a stage
- **FSDP/ZeRO** = S3 Intelligent Tiering that stores data sharded but reassembles on-demand

---

## 2. Model State Components

What gets checkpointed (and why it is large):

| Component | Size Factor | Description |
|-----------|-------------|-------------|
| **Model Parameters** | 2 bytes/param (FP16) or 4 bytes (FP32) | The actual neural network weights |
| **Optimizer State** | 8-12 bytes/param for Adam | First moment (momentum), second moment (variance), and FP32 master weights |
| **Gradient Buffers** | 2-4 bytes/param | Accumulated gradients before optimizer step |
| **Activation Memory** | Variable, can exceed params | Intermediate values needed for backpropagation |

**Example**: A 70B parameter model:
- Parameters (FP16): 70B x 2 bytes = **140 GB**
- Adam Optimizer State: 70B x 12 bytes = **840 GB**
- Total checkpoint size: **~1 TB** per full checkpoint

---

## 3. FSDP (Fully Sharded Data Parallel)

**Source**: https://docs.pytorch.org/tutorials/intermediate/FSDP_tutorial.html

FSDP is PyTorch's implementation of ZeRO Stage 3. It shards parameters, gradients, and optimizer states across all GPUs.

### How FSDP Works

```
At Rest:           Each GPU holds 1/N of parameters (as DTensor shards)
                   
Before Forward:    all-gather → Reconstruct full parameters
                   
Forward Pass:      Compute with full parameters
                   
After Forward:     (optionally) discard unsharded params, keep only local shard
                   
Before Backward:   all-gather → Reconstruct full parameters again
                   
Backward Pass:     Compute gradients
                   
After Backward:    reduce-scatter → Each GPU gets 1/N of gradients
                   
Optimizer Step:    Each GPU updates only its 1/N shard
```

### Why FSDP Makes Checkpointing Complex

1. **Sharded State**: Parameters exist as DTensor fragments across GPUs - no single GPU has the full model
2. **Reconstruction Required**: Saving a "full" checkpoint requires all-gathering from all ranks
3. **Memory Spike**: Gathering full state can temporarily double memory usage
4. **Coordination**: All ranks must synchronize during checkpoint save

**FSDP Sharding Strategies**:

| Strategy | Behavior | Memory | Performance |
|----------|----------|--------|-------------|
| `FULL_SHARD` | Reshard after forward pass | Minimum | More communication |
| `SHARD_GRAD_OP` | Keep unsharded through forward | Higher | Less communication |
| `HYBRID_SHARD` | Shard within node, replicate across nodes | Balanced | Optimizes network topology |

---

## 4. ZeRO Optimizer Stages

**Source**: https://www.deepspeed.ai/tutorials/zero/

| Stage | What Gets Partitioned | Memory per GPU | Communication |
|-------|----------------------|----------------|---------------|
| **ZeRO-1** | Optimizer states only | ~4x reduction | Baseline |
| **ZeRO-2** | + Gradients | ~8x reduction | + reduce-scatter |
| **ZeRO-3** | + Parameters | ~N-fold reduction | + all-gather for params |
| **ZeRO-Offload** | Stage 2 + CPU offload | Beyond GPU memory | + PCIe transfers |
| **ZeRO-Infinity** | Stage 3 + NVMe offload | Beyond system memory | + NVMe I/O |

**Real Example from DeepSpeed**:
- 1.5B parameter model with Adam optimizer consumes **18GB** for optimizer states alone
- ZeRO Stage 1 across 8 GPUs reduces this to **2.25GB per GPU**

---

## 5. NCCL (NVIDIA Collective Communications Library)

**Source**: https://developer.nvidia.com/nccl

NCCL is the communication backbone for distributed GPU training. Think of it as the "network stack" that GPUs use to talk to each other.

### Key Collective Operations

| Operation | Purpose in Training | Pattern |
|-----------|---------------------|---------|
| **All-Reduce** | Synchronize gradients in DDP | All GPUs contribute, all receive sum |
| **All-Gather** | Reconstruct sharded params in FSDP | All GPUs contribute shards, all receive full tensor |
| **Reduce-Scatter** | Distribute gradient shards in FSDP | All GPUs contribute, each receives different shard |
| **Broadcast** | Distribute initial weights | One GPU sends, all receive |

### Topology Awareness

NCCL automatically optimizes for:
- **PCIe** connections (within node, slower)
- **NVLink/NVSwitch** (within node, 600+ GB/s)
- **InfiniBand/RoCE** (across nodes)

It constructs optimal **rings and trees** for communication patterns based on detected topology.

---

## 6. Megatron-LM Model Parallelism

**Source**: https://docs.nvidia.com/megatron-core/developer-guide/latest/

Megatron-Core supports multiple parallelism dimensions:

| Parallelism | Abbreviation | What It Does |
|-------------|--------------|--------------|
| Tensor | TP | Splits individual matrix multiplications across GPUs |
| Pipeline | PP | Splits model layers into stages |
| Data | DP | Replicates model, splits data |
| Expert | EP | For Mixture-of-Experts models |
| Context/Sequence | CP | Splits long sequences across GPUs |

**3D Parallelism** combines TP + PP + DP:

**Source**: https://www.microsoft.com/en-us/research/blog/deepspeed-extreme-scale-model-training-for-everyone/

- **Tensor Parallelism**: Within a node (uses fast NVLink)
- **Pipeline Parallelism**: Across nodes (uses network)
- **Data Parallelism**: Across pipeline replicas (gradient sync)

**Benchmark**: 1 trillion parameters trained on 800 V100 GPUs achieving **47 TFLOPS per GPU**

---

## 7. Real-World Failure Rates and Goodput

### Meta Llama 3 Training Statistics

**Source**: https://ai.meta.com/blog/meta-llama-3/

- **Scale**: Two custom-built **24K GPU clusters**
- **Training**: 16K GPUs simultaneously
- **Compute Utilization**: Over **400 TFLOPS per GPU**
- **Effective Training Time**: Over **95%** (this is goodput)
- **Efficiency Improvement**: **3x better** than Llama 2 training
- **Data Scale**: 15T+ tokens (7x larger than Llama 2)

Key infrastructure investments:
- Automated error detection, handling, and maintenance
- Improved hardware reliability
- Silent data corruption detection mechanisms
- Scalable checkpoint storage systems with reduced overhead

### Goodput Calculation

```
Goodput = Useful Training Time / Total Wall-Clock Time

Where "lost time" includes:
- Hardware failures (GPU, network, storage)
- Software crashes (NCCL timeouts, OOM)
- Checkpoint save time (if synchronous)
- Recovery/restart time after failures
- Straggler delays (slow GPUs holding back others)
```

**Industry Target**: >90% goodput is considered good; Meta achieved >95% with Llama 3

### Failure Types in Large Clusters

Common failure modes (from NVIDIA NVRx documentation):

1. **GPU failures**: Memory errors, thermal issues, hardware faults
2. **Network failures**: InfiniBand link failures, switch issues
3. **Storage failures**: Checkpoint write failures, I/O timeouts
4. **Software hangs**: NCCL timeouts, deadlocks
5. **Silent data corruption**: Bit flips that don't crash but corrupt training
6. **Stragglers**: Individual GPUs running slower, blocking synchronization

---

## 8. NVIDIA Resiliency Extension (NVRx)

**Source**: https://github.com/NVIDIA/nvidia-resiliency-ext

NVRx is NVIDIA's fault tolerance framework for PyTorch training.

### Key Features

| Feature | Description |
|---------|-------------|
| **Hung Rank Detection** | Identifies unresponsive training processes |
| **In-Job Restart** | Recovers training without SLURM reallocation |
| **Straggler Detection** | Monitors GPU/CPU performance to spot slow ranks |
| **Hierarchical Checkpointing** | Local + remote checkpoint strategies |
| **Async Checkpointing** | Non-blocking checkpoint saves |

### Requirements
- PyTorch >= 2.5.1
- NCCL (avoid versions 2.28.3-2.28.8 due to in-process restart issues)
- Enhanced fault attribution requires PyTorch >= 2.8.0

---

## 9. Checkpointing Strategies

### Synchronous vs Asynchronous Checkpointing

| Approach | How It Works | Pros | Cons |
|----------|--------------|------|------|
| **Synchronous** | Training stops, all GPUs write checkpoint | Simple, consistent | Lost training time |
| **Asynchronous** | Copy state to CPU/staging, write in background | Minimal training interruption | Memory overhead, complexity |
| **Hierarchical** | Fast local checkpoint + slower remote backup | Best of both worlds | Storage management complexity |

### PyTorch Distributed Checkpoint (DCP)

DCP is designed for sharded model states (FSDP, etc.):
- Saves sharded state directly (no all-gather required)
- Supports resharding on load (different GPU count)
- Enables async checkpointing
- Integrates with cloud storage

### Checkpoint Frequency Trade-off

```
More Frequent Checkpoints:
  + Less work lost on failure
  - More checkpoint overhead
  - More storage costs

Less Frequent Checkpoints:
  + Less overhead
  + Lower storage costs
  - More work lost on failure

Optimal frequency depends on:
  - MTBF (Mean Time Between Failures) of your cluster
  - Checkpoint save time
  - Cost of lost training time
```

**Rule of thumb**: If checkpoint takes 5 minutes and MTBF is 2 hours, checkpoint every 20-30 minutes loses ~15-20% to checkpointing but limits loss to 30 minutes of work.

---

## 10. Storage Architecture for Checkpoints

### Amazon FSx for Lustre Performance

**Source**: https://docs.aws.amazon.com/fsx/latest/LustreGuide/performance.html

| Configuration | Max Throughput per Client |
|---------------|---------------------------|
| Standard (non-EFA) | 100 Gbps |
| EFA-enabled | 100 Gbps (ENA) |
| EFA-enabled | **700 Gbps** (EFA) |
| EFA + GPUDirect Storage | **1200 Gbps** |

**Key Features for ML Checkpointing**:
- **Linear scaling**: Throughput increases with file system size
- **Automatic striping**: Large files distributed across Object Storage Targets
  - Files >100GB: stripe count 32
- **In-memory caching**: Reduces latency for repeated access
- **S3 integration**: Can lazy-load from and export to S3

### Storage Tier Recommendations

| Use Case | Recommended Storage | Why |
|----------|---------------------|-----|
| Fast checkpoint (< 5 min) | FSx for Lustre | Highest throughput |
| Async checkpoint staging | Local NVMe / Instance Store | Lowest latency for staging |
| Long-term checkpoint storage | Amazon S3 | Cost-effective, durable |
| Hierarchical checkpoint | Local NVMe → FSx → S3 | Tiered approach |

---

## 11. Key Analogies for Solutions Architects

| ML Concept | AWS Infrastructure Analogy |
|------------|----------------------------|
| **Checkpoint** | EBS Snapshot or RDS automated backup |
| **Gradient Sync** | DynamoDB Global Tables replication |
| **FSDP Sharding** | S3 multipart upload (data split, reassembled on read) |
| **Pipeline Parallelism** | Step Functions with parallel branches |
| **All-Reduce** | Global load balancer aggregating health checks |
| **NCCL** | VPC networking + Placement Groups |
| **Goodput** | EC2 effective uptime after accounting for maintenance |
| **Straggler** | Cold start Lambda in a parallel invocation |

---

### Version Notes

- **PyTorch**: Information based on PyTorch 2.x; FSDP2 is the current recommended API
- **NCCL**: Avoid versions 2.28.3-2.28.8 for NVRx compatibility
- **NVRx**: Requires PyTorch >= 2.5.1, enhanced features at >= 2.8.0
- **DeepSpeed**: ZeRO documentation reflects current stable release

### Sources Cited

1. **FSDP Tutorial**: https://docs.pytorch.org/tutorials/intermediate/FSDP_tutorial.html
2. **HuggingFace Parallelism Guide**: https://huggingface.co/docs/transformers/main/en/perf_train_gpu_many
3. **DeepSpeed ZeRO**: https://www.deepspeed.ai/tutorials/zero/
4. **DeepSpeed 3D Parallelism**: https://www.microsoft.com/en-us/research/blog/deepspeed-extreme-scale-model-training-for-everyone/
5. **NCCL**: https://developer.nvidia.com/nccl
6. **NVRx**: https://github.com/NVIDIA/nvidia-resiliency-ext
7. **Megatron-Core**: https://docs.nvidia.com/megatron-core/developer-guide/latest/
8. **Meta Llama 3**: https://ai.meta.com/blog/meta-llama-3/
9. **FSx for Lustre Performance**: https://docs.aws.amazon.com/fsx/latest/LustreGuide/performance.html
10. **PyTorch DDP**: https://docs.pytorch.org/tutorials/intermediate/ddp_tutorial.html

### Information I Could Not Retrieve

The following URLs returned errors or incomplete content:
- AWS Storage Blog on checkpoint architecture (CSS-only response)
- PyTorch Distributed Checkpoint API docs (navigation-only response)
- OPT-175B Logbook PDF (GitHub viewer, not PDF content)
- Google Cloud TPU best practices (JavaScript-only response)
- OpenAI Kubernetes scaling blog (403 Forbidden)

### Recommended Next Steps

1. **For the AWS checkpoint storage blog**: Access it directly at https://aws.amazon.com/blogs/storage/ and search for "checkpoint storage ML training"

2. **For OPT-175B failure data**: Download the PDF from https://github.com/facebookresearch/metaseq/blob/main/projects/OPT/chronicles/OPT175B_Logbook.pdf - it contains detailed day-by-day logs of training failures

3. **For async checkpointing details**: Review PyTorch's DCP documentation and NVRx GitHub repository examples

4. **Consider adding to your talk**:
   - Live demo of checkpoint sizes at different model scales
   - FSx for Lustre throughput calculator for audience's use cases
   - Decision tree for choosing parallelism strategy based on model size and GPU count


---
_=== a4d4c4dac57fb6d09.output === 143 lines_


I now have comprehensive research data. Let me compile the complete research findings for your presentation.

## Research: ML Training Checkpointing and SageMaker HyperPod Checkpointless Training

---

### Topic 1: Traditional Checkpointing in ML Training

#### What is Checkpointing?
Checkpointing is a critical reliability mechanism in distributed ML training that periodically saves the complete training state to durable storage. This includes:
- **Model parameters** (weights and biases)
- **Optimizer state** (momentum, variance for Adam, etc.)
- **Learning rate scheduler state**
- **Training loop metadata** (epoch, batch number, global step)
- **Data loader state** (to avoid duplicate/skipped samples)

**Source**: https://aws.amazon.com/blogs/storage/architecting-scalable-checkpoint-storage-for-large-scale-ml-training-on-aws/

#### Why is Checkpointing Needed?
1. **Fault tolerance**: At scale, failures become statistically inevitable
2. **Recovery from failures**: Resume training without losing all progress
3. **Point-in-time resumption**: Enable training continuation after interruptions

**Key statistic from Meta's Llama 3 training**: One failure occurred every 3 hours during training. GPU issues accounted for 60% of failures; network, CPU, and disk failures accounted for the remaining 40%.

**Source**: https://aws.amazon.com/blogs/machine-learning/accelerate-your-model-training-with-managed-tiered-checkpointing-on-amazon-sagemaker-hyperpod/ (citing Meta research)

#### Checkpoint Sizes for Large Models

| Model | Parameters | Checkpoint Size (weights only) | Checkpoint + Optimizer State |
|-------|-----------|-------------------------------|------------------------------|
| Llama 3 70B | 70 billion | 130 GB | **521 GB** |
| DeepSeek R1 671B | 671 billion | 1.43 TB | **5 TB** |

**Formula**: 
- Weights only: `Parameters x 2 bytes (BF16/FP16)`
- With Adam optimizer: `Parameters x 10 bytes` (2 bytes weights + 8 bytes optimizer state)

**Source**: https://aws.amazon.com/blogs/machine-learning/accelerate-your-model-training-with-managed-tiered-checkpointing-on-amazon-sagemaker-hyperpod/

#### Problems with Checkpointing at Scale

**1. I/O Overhead and Storage Bottlenecks**
- Writing terabytes of data to persistent storage throttles training
- Consumes expensive network bandwidth
- Requires complex orchestration across distributed systems
- NFS struggles with concurrent writes in FSDP scenarios

**2. Training Pause (Synchronous Barrier)**
- Standard checkpointing acts as a synchronous barrier
- ALL computation must pause while writing the checkpoint
- The entire cluster sits idle during recovery operations

**3. Checkpoint Frequency Tradeoffs**
- Frequent checkpoints: Better protection but higher overhead
- Infrequent checkpoints: Lower overhead but risk losing more training progress
- With infrequent checkpointing, accumulated failures can result in **losing days of training progress**

**4. Recovery Time is Multi-Stage and Sequential**
Traditional checkpoint-based recovery involves 6 sequential blocking stages:
1. **Job termination and restart** - Orchestrator terminates all processes
2. **Process and network initialization** - Can take **tens of minutes** on large clusters
3. **Checkpoint retrieval** - Loading from S3/FSx can take **tens of minutes to hours** for large models
4. **Data loader initialization** - Retrieving data checkpoint, prefetching
5. **First step overhead (FSO)** - CUDA context, memory allocation, graph compilation
6. **Lost steps overhead (LSO)** - Recomputing steps between last checkpoint and failure

**Source**: https://aws.amazon.com/blogs/machine-learning/checkpointless-training-on-amazon-sagemaker-hyperpod-production-scale-training-with-faster-fault-recovery/

#### Real Cost Example
A pre-training workload on a HyperPod cluster with **256 P5 instances**, checkpointing every 20 minutes:
- Each disruption: 10 minutes lost work + 10 minutes recovery
- ml.p5.24xlarge cost: $55/hour
- **Cost per disruption: $4,693**
- For a month-long training with daily disruptions: **$141,000 extra costs** and **10 hours delay**

**Source**: https://aws.amazon.com/blogs/machine-learning/checkpointless-training-on-amazon-sagemaker-hyperpod-production-scale-training-with-faster-fault-recovery/

---

### Topic 2: SageMaker HyperPod Checkpointless Training (NEW LAUNCH - December 2025)

#### What is SageMaker HyperPod?
Amazon SageMaker HyperPod is a purpose-built infrastructure for foundation model development that:
- Provisions resilient clusters across thousands of AI accelerators
- Supports Slurm and Amazon EKS orchestration
- Provides automatic cluster health checks and node repair
- Enables training of trillion-parameter models

**Source**: https://aws.amazon.com/sagemaker/ai/hyperpod/

#### What is Checkpointless Training?
Checkpointless training is a **paradigm shift** that eliminates the need for traditional checkpoint-based recovery by enabling **peer-to-peer state recovery**. Announced at **AWS re:Invent 2025 (December 3, 2025)**.

**Key Innovation**: Instead of periodically saving state to disk and reloading on failure, the system maintains continuous model state preservation across the distributed cluster using in-memory redundancy.

**Source**: https://aws.amazon.com/blogs/aws/introducing-checkpointless-and-elastic-training-on-amazon-sagemaker-hyperpod/

#### How Does It Work Technically?

Checkpointless training has **5 core components**:

**Component 1: TCPStore-less/Root-less NCCL and Gloo Initialization**
- Eliminates centralized TCPStore bottleneck where thousands of ranks contact rank 0
- Uses symmetric address pattern where each rank independently computes peer connection info
- Result: Process group initialization drops from **tens of minutes to seconds**

**Component 2: Memory-Mapped Data Loading (MMAP)**
- Training data mapped into shared memory regions that persist across process failures
- Reduces host CPU memory usage (1 copy per node vs. 8 copies for 8-GPU nodes)
- Training resumes immediately using cached batches

**Component 3: In-Process Recovery**
- Isolates failures at the process level (not job level)
- Failed process stays alive, preserving CUDA context, compiler cache, GPU state
- Healthy processes continue running without interruption
- For non-recoverable errors: automatic swap with pre-warmed hot spare

**Component 4: Peer-to-Peer State Replication**
- Model and optimizer states fully replicated across multiple node groups
- Weight updates synchronously replicated within each group
- When failure occurs, healthy replicas transmit updated states to recovering replicas
- **No disk I/O required for recovery**

**Component 5: SageMaker HyperPod Training Operator**
- Kubernetes extension that orchestrates all components
- Handles surgical recovery (restarts only affected resources)
- Includes hanging job monitoring and custom recovery policies

**Source**: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-checkpointless-features.html, https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-checkpointless-in-process-recovery.html

#### What is Elastic Training?
Elastic training (also announced December 2025) enables AI workloads to automatically scale based on resource availability:
- Training jobs automatically expand to use idle capacity
- Contract to yield resources when higher-priority workloads need them
- Uses data parallel replica scaling (add/remove replicas while keeping global batch size constant)
- Preserves model convergence through learning rate adaptation

**Source**: https://aws.amazon.com/about-aws/whats-new/2025/12/elastic-training-amazon-sagemaker-hyperpod/

#### Key Benefits and Performance Numbers

| Metric | Traditional Checkpointing | Checkpointless Training |
|--------|--------------------------|------------------------|
| Recovery time | 15-30+ minutes | **Under 2 minutes** |
| Recovery time reduction | Baseline | **80-93% reduction** |
| Training goodput | Varies (decreases at scale) | **Up to 95%** |
| Cluster size tested | - | Up to **thousands of GPUs** |
| Code changes required | - | **Zero** for popular models (Llama, GPT OSS) |

**Production Validation**: 
- Amazon Nova models were trained using this technology on **tens of thousands of accelerators**
- Validated across cluster sizes from 16 GPUs to over 2,000 GPUs

**Source**: https://aws.amazon.com/about-aws/whats-new/2025/12/amazon-sagemaker-hyperpod-checkpointless-training/

#### Availability
- Available in **all AWS Regions** where SageMaker HyperPod is available
- **No additional cost** to use these features
- Requires Amazon EKS orchestration and HyperPod Training Operator v1.2.0+

**Source**: https://aws.amazon.com/blogs/aws/introducing-checkpointless-and-elastic-training-on-amazon-sagemaker-hyperpod/

---

### Topic 3: Related Technologies Comparison

#### PyTorch Elastic Training (torchrun/torchelastic)
- Enables fault-tolerant distributed training with dynamic worker scaling
- Treats failures as **job-level events** requiring full restart
- All processes across the cluster must be killed and restarted
- Still relies on checkpoint-based recovery

#### NVIDIA Resiliency Extension (NVRx)
- Python package for fault-tolerant PyTorch workloads
- Features: hung rank detection, in-process restarting, asynchronous checkpointing, straggler detection
- Integrates with PyTorch Lightning and NeMo
- **Status**: Still under active development (experimental)
- AWS checkpointless training is **built on NeMo** and follows similar API patterns to NVRx

**Source**: https://github.com/NVIDIA/nvidia-resiliency-ext

#### DeepSpeed Checkpointing
- Offers parallel writing with pipeline stages
- `stage3_gather_16bit_weights_on_model_save` for ZeRO Stage 3
- Node-local storage option to eliminate shared filesystem dependency
- Still fundamentally checkpoint-based (saves to disk)

**Source**: https://www.deepspeed.ai/docs/config-json/#checkpoint-options

#### How AWS's Approach Differs

| Feature | PyTorch Elastic | NVIDIA NVRx | DeepSpeed | **AWS Checkpointless** |
|---------|----------------|-------------|-----------|----------------------|
| Failure handling | Job-level restart | In-process + checkpoint | Checkpoint-based | **In-process + peer-to-peer** |
| State recovery | From disk | From disk (async) | From disk | **From peer memory** |
| Recovery time | Minutes to hours | Improved | Standard | **Under 2 minutes** |
| Disk I/O on recovery | Required | Required | Required | **Not required** |
| Production validation | General | Experimental | General | **Tens of thousands of GPUs** |
| Integration | PyTorch | NeMo/Lightning | DeepSpeed | **NeMo + HyperPod Operator** |

**Key AWS Differentiator**: Complete elimination of disk I/O during fault recovery through peer-to-peer state replication, combined with managed infrastructure (HyperPod) that handles node health monitoring and automatic replacement.

---

### Additional Sources

1. **AWS Blog - Checkpointless Training Deep Dive**: https://aws.amazon.com/blogs/machine-learning/checkpointless-training-on-amazon-sagemaker-hyperpod-production-scale-training-with-faster-fault-recovery/

2. **AWS News Blog - Launch Announcement**: https://aws.amazon.com/blogs/aws/introducing-checkpointless-and-elastic-training-on-amazon-sagemaker-hyperpod/

3. **SageMaker HyperPod Product Page**: https://aws.amazon.com/sagemaker/ai/hyperpod/

4. **HyperPod Features Page**: https://aws.amazon.com/sagemaker/ai/hyperpod/features/

5. **Checkpointless Training GitHub**: https://github.com/aws/sagemaker-hyperpod-checkpointless-training

6. **HyperPod Recipes GitHub**: https://github.com/aws/sagemaker-hyperpod-recipes

7. **AWS Storage Blog - Checkpoint Architecture**: https://aws.amazon.com/blogs/storage/architecting-scalable-checkpoint-storage-for-large-scale-ml-training-on-aws/

8. **Managed Tiered Checkpointing Documentation**: https://docs.aws.amazon.com/sagemaker/latest/dg/managed-tier-checkpointing.html

---

### Version Notes
- **Launch Date**: December 3, 2025 (AWS re:Invent 2025)
- **HyperPod Training Operator**: v1.2.0+ required
- **Checkpointless Container**: PyTorch v2.6.0, CUDA v12.9, NCCL v2.27.5, NeMo v2.6.0rc0
- **Supported Models**: Pre-configured recipes for Llama 3 70B, GPT OSS 120B; custom models supported with minimal modifications

---

### Recommended Next Steps for Presentation

1. **Lead with the pain point**: Llama 3 training had failures every 3 hours; checkpoint sizes of 521GB-5TB create massive I/O overhead

2. **Show the cost**: $4,693 per disruption on 256 P5 instances; $141K/month in wasted compute

3. **Introduce the paradigm shift**: From "save-to-disk, restore-from-disk" to "peer-to-peer in-memory state preservation"

4. **Highlight the numbers**: 80-93% recovery time reduction, 95% training goodput, under 2 minutes recovery

5. **Credibility**: Amazon Nova trained on tens of thousands of accelerators using this technology

6. **Call to action**: Zero code changes for popular models, available now at no additional cost


---
_=== ac4057df39d850fa8.output === 122 lines_


I have gathered comprehensive documentation on SageMaker HyperPod Checkpointless Training. Let me provide you with a complete research synthesis.

## Research: SageMaker HyperPod Checkpointless Training

### Findings

**Answer**: SageMaker HyperPod Checkpointless Training is a fault-tolerance framework that enables faster recovery from infrastructure faults in large-scale distributed training without relying on traditional checkpoint-based recovery. It achieves this through five key components working in concert.

**Source**: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-checkpointless.html

**Version**: v1.0.0 (Released December 3, 2025)

---

### Technical Architecture: 5 Core Components

#### Component 1: Collective Communication Initialization Improvements (NCCL/Gloo)

**Problem Solved**: Traditional NCCL and Gloo initialization requires all processes to connect to a centralized TCPStore and coordinate through a root process, creating bottlenecks during fault recovery.

**Solution**: "Rootless" and "TCPStoreless" initialization that eliminates:
- Coordination overhead from mandatory TCPStore connections
- Recovery delays from repeating full initialization sequences
- Single point of failure in the root process

**Configuration**:
```bash
export HPCT_USE_ROOTLESS=1
sysctl -w net.ipv4.ip_local_port_range="20000 65535"
```

**Source**: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-checkpointless-features-communication.html

---

#### Component 2: Memory-Mapped Dataloader (MMAP)

**Problem Solved**: Training cluster remains idle while dataloader initializes, downloads data, and processes batches after restart.

**Solution**: Caches prefetched batches in persistent memory (`/dev/shm`), enabling:
- **Data Prefetching**: Proactively fetches and caches dataloader output
- **Persistent Caching**: Stores consumed and prefetched batches that survive process restarts
- **Reduced Memory Footprint**: Single shared copy in CPU memory (8 copies to 1 on p5 with 8 GPUs)
- **Faster Recovery**: Training resumes immediately from cached batches

**Code Example**:
```python
from hyperpod_checkpointless_training.dataloader.mmap_data_module import MMAPDataModule
from hyperpod_checkpointless_training.dataloader.config import CacheResumeMMAPConfig

data_module = MMAPDataModule(
    data_module=MY_DATA_MODULE(...),
    mmap_config=CacheResumeMMAPConfig(
        cache_dir="/dev/shm/pdl_cache",  # Default
        prefetch_length=10,               # Batches to prefetch
        val_prefetch_length=10,
        lookback_length=2,                # Recently consumed batches to keep
        checkpoint_frequency=None,
        enable_batch_encryption=False
    ),
)
```

**Source**: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-checkpointless-features-mmap.html

---

#### Component 3: In-Process Recovery (IPR)

**Core Principle**: Model and optimizer states are fully replicated across multiple node groups. When failure occurs, healthy replicas complete their optimizer steps and transmit updated states to recovering replicas.

**Key Mechanisms**:
- Processes remain active despite faults, keeping states in GPU memory
- Graceful abort handling with controlled cleanup
- Re-executable Code Block (RCB) re-execution for affected code segments
- No training progress lost - resumes from previous step, not last checkpoint

**Code Example**:
```python
from hyperpod_checkpointless_training.inprocess.train_utils import wait_rank, HPAgentK8sAPIFactory
from hyperpod_checkpointless_training.inprocess.wrap import HPWrapper
from hyperpod_checkpointless_training.inprocess.health_check import CudaHealthCheck
from hyperpod_checkpointless_training.inprocess.abort import CheckpointlessAbortManager, CheckpointlessFinalizeCleanup
from hyperpod_checkpointless_training.nemo_plugins.checkpoint_manager import CheckpointManager

wait_rank()  # Wait for rank info from HyperPod training operator

@HPWrapper(
    health_check=CudaHealthCheck(),
    hp_api_factory=HPAgentK8sAPIFactory(),
    abort_timeout=60.0,
    checkpoint_manager=CheckpointManager(enable_offload=False),
    abort=CheckpointlessAbortManager.get_default_checkpointless_abort(),
    finalize=CheckpointlessFinalizeCleanup(),
)
def run_main(cfg, caller=None):
    # Training code here
    trainer = Trainer(
        strategy=CheckpointlessMegatronStrategy(
            num_distributed_optimizer_instances=2  # Required: at least 2 for redundancy
        ),
        callbacks=[CheckpointlessCallback(...)],
    )
    trainer.wrapper = caller
```

**Source**: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-checkpointless-in-process-recovery.html

---

#### Component 4: Model Redundancy

**Concept**: Uses hybrid sharding (`num_distributed_optimizer_instances >= 2`) to replicate model/optimizer states across node groups.

**Trade-offs**:
- Higher device memory usage (roughly one DCP checkpoint size per replica)
- Low-precision weights, gradients, and activation memory unaffected (sharded via model parallelism)
- High-precision master weights/gradients and optimizer states affected

**Communication Pattern Change**:
- Before: reduce-scatter + all-gather across entire DP group
- After: reduce-scatter inside each replica + all-reduce across replica groups + all-gather inside replica
- Result: Same total communication volume, but smaller collective groups = better latency

---

#### Component 5: Failure Types and Recovery Hierarchy

| Failure Type | Cause | Recovery Type | Mechanism |
|-------------|-------|---------------|-----------|
| In-process failure | Code-level errors, exceptions | In-Process Recovery (IPR) | Rerun RCB within existing process |
| Process restart failure | Corrupted CUDA context, terminated process | Process Level Restart (PLR) | Training operator restarts processes; skips K8s pod restart |
| Node replacement failure | Permanent hardware failure | Job Level Restart (JLR) | Replace failed node; restart entire job |

**Atomic Lock Protection**: During optimizer step, healthy replicas complete under lock protection, then broadcast updated states. Forward/backward failures roll back to step beginning.

---

### Key API Reference

#### wait_rank()
Blocks until HyperPod provides rank information. Updates environment with `RANK`, `WORLD_SIZE`.

#### HPWrapper
Function wrapper enabling Re-executable Code Block (RCB) with fault tolerance.

**Parameters**:
- `health_check`: CudaHealthCheck with configurable timeout (default 30s)
- `hp_api_factory`: HPAgentK8sAPIFactory for K8s cluster communication
- `abort_timeout`: Timeout for abort operations (float)
- `checkpoint_manager`: CheckpointManager or PEFTCheckpointManager
- `abort`: CheckpointlessAbortManager (aborts TransformerEngine, Checkpointing, TorchDistributed, DataLoader)
- `finalize`: CheckpointlessFinalizeCleanup
- `enabled`: Boolean to enable/disable wrapper

#### CheckpointManager
Manages in-memory checkpoints and peer-to-peer recovery.

**Key Methods**:
- `save_checkpoint(trainer)`: Save to memory
- `try_checkpointless_load(trainer)`: Attempt P2P recovery
- `checkpointless_recovery_feasible(trainer)`: Validate recovery possibility
- `store_rng_states()` / `load_rng_states()`: Preserve Python, NumPy, PyTorch, Megatron RNG states

**Parameters**:
- `enable_checksum`: Model state checksum validation (default False)
- `enable_offload`: Offload checkpoint to CPU memory (default False)

#### PEFTCheckpointManager
Extends CheckpointManager for PEFT workflows, separating base model weights from adapter parameters.

---

### Prerequisites and Requirements

**Infrastructure**:
- SageMaker HyperPod cluster with Amazon EKS orchestration
- HyperPod Training Operator v1.2.0 or above
- HyperPod Elastic Agent v1.1.0 or above
- Latest HyperPod AMI release
- cert-manager installed
- EKS Pod Identity Agent

**Kubernetes Versions**: 1.28, 1.29, 1.30, 1.31, 1.32, 1.33

**Shared Storage**: Amazon FSx for Lustre or NFS accessible from cluster nodes

**Data Formats**: JSON, JSONGZ (compressed), ARROW

**Python**: >= 3.10, < 3.14

---

### Container Versions (v1.0.0)

```
PyTorch: v2.6.0
CUDA: v12.9
NCCL: v2.27.5
EFA: v1.43.0
AWS-OFI-NCCL: v1.16.0
Libfabric: v2.1
Megatron: v0.15.0
NeMo: v2.6.0rc0
```

**Container Registry** (example for ap-northeast-1):
```
356859066553.dkr.ecr.ap-northeast-1.amazonaws.com/hyperpod-checkpointless-training:v1.0.0
```

**Available Regions**: us-east-1, us-east-2, us-west-1, us-west-2, eu-west-1, eu-west-2, eu-central-1, eu-north-1, ap-northeast-1, ap-south-1, ap-southeast-1, ap-southeast-2, sa-east-1

**Source**: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-checkpointless-release-notes.html

---

### Supported Models and Recipes

| Model | Method | Size | Nodes | Instance | Accelerator |
|-------|--------|------|-------|----------|-------------|
| GPT OSS | Full finetune | 120b | 16 | p5.48xlarge | GPU H100 |
| GPT OSS | LoRA | 120b | 2 | p5.48xlarge | GPU H100 |
| Llama3 | Pretrain | 70b | 16 | p5.48xlarge | GPU H100 |
| Llama3 | LoRA | 70b | 2 | p5.48xlarge | GPU H100 |
| Custom | Any | Any | Any | p5.48xlarge | GPU H100 |

---

### HyperPod Training Operator Integration

**Job Submission YAML Example**:
```yaml
apiVersion: sagemaker.amazonaws.com/v1
kind: HyperPodPytorchJob
metadata:
  name: checkpointless-training-job
  namespace: default
spec:
  nprocPerNode: "8"
  runPolicy:
    cleanPodPolicy: "None"
  replicaSpecs:
    - name: worker
      replicas: 16
      template:
        spec:
          containers:
            - name: training
              image: 356859066553.dkr.ecr.ap-northeast-1.amazonaws.com/hyperpod-checkpointless-training:v1.0.0
              env:
                - name: HPCT_USE_ROOTLESS
                  value: "1"
              command:
                - hyperpodrun
                - --nproc_per_node=8
                - --inprocess-restart
                - training_script.py
```

**hyperpodrun Arguments**:
- `--inprocess-restart`: Enable in-process fault recovery
- `--inprocess-timeout`: Seconds to wait for sync barrier before PLR
- `--shutdown-signal`: SIGTERM or SIGKILL (default SIGKILL)
- `--shutdown-timeout`: Seconds between signals (default 15)

---

### Checkpointless Training Flow

1. Training loop starts
2. Fault occurs
3. Evaluate checkpointless resume feasibility
4. If feasible: Attempt checkpointless resume
   - Success: Training continues from recovered state
   - Failure: Fall back to checkpoint loading from storage
5. If not feasible: Fall back to checkpoint loading
6. Clean up resources (abort process groups, free resources)
7. Resume training loop (return to step 1)

---

### Additional Sources

- [HyperPod Checkpointless Training GitHub](https://github.com/aws/sagemaker-hyperpod-checkpointless-training) - Source code and examples
- [SageMaker HyperPod Recipes GitHub](https://github.com/aws/sagemaker-hyperpod-recipes) - Pre-configured training recipes
- [NVIDIA NeMo Framework User Guide](https://docs.nvidia.com/nemo-framework/user-guide/latest/overview.html) - Foundation framework
- https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-operator.html - Training operator documentation
- https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-checkpointless-recipes-custom.html - Custom model integration guide

---

### Version Notes

- **Training Operator**: v1.2.0+ required for checkpointless training
- **Elastic Agent**: v1.1.0+ required
- **PyTorch**: 2.4.0 - 2.7.1 supported
- **Kueue** (optional): v0.12.2 or v0.12.3 suggested for job scheduling

---

### Recommended Next Steps for Presentation

1. **Architecture Diagram**: Create visual showing the 5 components and their interaction
2. **Recovery Time Comparison**: Prepare metrics comparing traditional checkpoint recovery vs checkpointless (MTTR reduction)
3. **Memory Overhead Analysis**: Prepare slides on model redundancy memory trade-offs
4. **Demo Flow**: Consider showing kubectl job submission and fault injection/recovery
5. **Q&A Preparation Topics**:
   - Why `num_distributed_optimizer_instances >= 2` is required
   - Memory overhead calculation for model redundancy
   - NCCL rootless implementation details
   - Differences between IPR, PLR, and JLR recovery paths
   - RNG state preservation for deterministic recovery


---
_=== ac4d2ff55d7b8fe36.output === 53 lines_


## Research: SageMaker HyperPod Checkpointless Training - Deep Technical Extract

I have successfully extracted all technical details from the three AWS blog posts. Here is the comprehensive research output for your conference presentation:

---

# BLOG 1: Checkpointless Training on Amazon SageMaker HyperPod (Technical Deep Dive)
**Source**: https://aws.amazon.com/blogs/machine-learning/checkpointless-training-on-amazon-sagemaker-hyperpod-production-scale-training-with-faster-fault-recovery/
**Published**: December 15, 2025
**Authors**: Anirudh Viswanathan, Anirban Roy, Arun Nagarajan, Fei Wu, Trevor Harvey, Roy Allela

---

## Key Headline Numbers

| Metric | Value |
|--------|-------|
| Recovery time reduction | **80-93%** |
| Traditional recovery time | **15-30 minutes or more** |
| Checkpointless recovery time | **Under 2 minutes** |
| Training goodput achieved | **Up to 95%** |
| Amazon Nova training scale | **Tens of thousands of AI accelerators** |

---

## Understanding Goodput - The Core Problem

**Definition**: Goodput = actual useful work accomplished vs. theoretical maximum capacity

### Cost Analysis Example (Real Numbers)
- **Cluster**: 256 P5 instances
- **Checkpoint interval**: Every 20 minutes
- **Instance cost**: ml.p5.24xlarge = **$55/hour**
- **Per-disruption impact**:
  - 10 minutes lost work
  - 10 minutes recovery time
  - **Cost per disruption: $4,693**
- **Monthly training with daily disruptions**:
  - Extra cost: **$141,000**
  - Completion delay: **10 hours**

### The Scaling Problem
As clusters grow:
1. Failure frequency increases proportionally
2. Recovery times grow linearly with cluster size
3. Cumulative costs can reach **millions of dollars annually**

---

## Traditional Checkpoint-Based Recovery - The 6 Stage Bottleneck

### Stage 1: Training Job Restart
- Orchestrator detects failure
- **Terminates ALL processes in ALL nodes**
- Cluster-wide restart initiated

### Stage 2: Process and Network Initialization
- Every process re-executes training script from beginning
- Includes: rank initialization, loading Python modules from NFS/object storage
- Establishing training topology and communication backend
- **Process group initialization alone: tens of minutes on large clusters**

### Stage 3: Checkpoint Retrieval
- Identify last completely saved checkpoint
- Retrieve from persistent storage (NFS or object storage)
- Load multiple state dictionaries:
  - Model parameters and buffers
  - Optimizer internal state (momentum, variance, etc.)
  - Learning rate scheduler
  - Training loop metadata (epoch, batch number)
- **Duration: tens of minutes or longer**

### Stage 4: Data Loader Initialization
- Initialize data buffers
- Retrieve data checkpoint from FSx or S3
- Prefetch training data
- **Duration: few minutes** (depends on data mix strategy, locality, bandwidth)

### Stage 5: First Step Overhead (FSO)
- Memory allocation
- Creating/setting up CUDA context for GPU communication
- Compilation part of CUDA graph

### Stage 6: Lost Steps Overhead (LSO)
- All steps between checkpoint and fault must be recomputed
- Training resumes productive work only after recomputation

**Key insight**: Each stage is **sequential and blocking** - entire cluster waits

---

## The 5 Components of Checkpointless Training

### COMPONENT 1: TCPStore-less/Root-less NCCL and Gloo Initialization
**(Optimizes Stage 2)**

**The Problem**:
- Traditional torch.distributed uses TCPStore as rendezvous point
- All ranks contact designated root server (rank 0) simultaneously
- Creates bottleneck: network congestion, increased latency
- **Traditional init time: tens of minutes**

**The Solution**:
- Symmetric address pattern
- Each rank independently computes peer connection info using global group counter
- Ranks connect directly using predetermined port assignments
- **Checkpointless init time: seconds**
- Eliminates single-point-of-failure risk

### COMPONENT 2: Memory-Mapped Data Loading (MMAP)
**(Optimizes Stage 4)**

**The Problem**:
- Process restarts require reloading batches from disk
- Rebuilding data loader state
- Risk of duplicate samples or skipped data

**The Solution**:
- Training data mapped to shared memory regions
- Memory persists even when processes fail
- Recovered node reconnects to existing memory-mapped cache
- Data loader state preserved

**Benefits**:
- No disk reload needed
- Reduced host CPU memory: **1 copy per node** vs **8 copies with traditional data loaders** (on 8-GPU nodes)
- Training resumes immediately using cached batches
- Data loader prefetches next data concurrently in background

### COMPONENT 3: In-Process Recovery
**(Optimizes Stages 1, 2, and 5)**

**The Problem**:
- Single GPU error triggers complete cluster shutdown
- Entire distributed job treated as tightly coupled
- Every process must be killed and restarted

**The Solution**:
- Failures isolated at process level
- Failed process executes in-process recovery to rejoin training loop **within seconds**
- Healthy processes continue without interruption
- Failed process stays alive (no full process teardown)
- Preserves: CUDA context, compiler cache, GPU state

**Fallback**: For non-recoverable errors (hardware failure), system swaps faulty component with **pre-warmed hot spare**

### COMPONENT 4: Peer-to-Peer State Replication
**(Optimizes Stages 3 and 6)**

**The Problem**:
- Loading model/optimizer state from S3 or FSx for Lustre
- Transferring tens to hundreds of GB over network
- Deserializing state dictionaries
- Reconstructing optimizer buffers
- **Duration: tens of minutes**

**The Solution**:
- Continuous peer-to-peer state replication
- Each GPU maintains redundant copies of model shards on peer GPUs
- Recovery copies state directly from healthy peer
- Uses high-speed **Elastic Fabric Adapter (EFA)** network interconnect
- Recovering node pulls only specific shards needed
- **Duration: seconds**

### COMPONENT 5: SageMaker HyperPod Training Operator
**(Optimizes ALL Stages)**

**Functions**:
- Orchestrates all checkpointless training components
- Maintains centralized control plane with global view of training process health
- Coordinates: fault detection, recovery decisions, cluster-wide synchronization

**Intelligent Recovery Escalation**:
1. First attempts in-process restart for failed components
2. If not feasible (container crashes, node failures): escalates to process-level recovery
3. Process-level: restarts only training processes, keeps containers alive
4. Faster than job-level restart (avoids pod rescheduling, container pulls, environment init)

**Integration**: Works with HyperPod health-monitoring agent for automatic hardware issue detection

---

## Architecture Diagrams Described

### Diagram 1: Cluster Failure Probability
Shows: As cluster sizes grow, the probability and frequency of failures increases

### Diagram 2: Checkpointless Training Architecture
Shows the 5 components working together to eliminate checkpoint-restart bottlenecks

### Diagram 3: Memory-Mapped Data Loading Workflow
Shows data flow from GPU HBM -> CPU memory -> Shared memory regions -> Recovery

### Diagram 4: Animated GIF
Shows real-time visualization of checkpointless training in action

---

## Getting Started - Prerequisites

### Infrastructure Requirements
- Amazon SageMaker HyperPod cluster orchestrated by Amazon EKS
- HyperPod training operator **v1.2 or later**
- Recommended instances: **ml.p5., p5e., p5en.48xlarge, ml.p6.p6-b200.48xlarge, ml.p6e-gb200.36xlarge**
- Minimum cluster size: **2 nodes** (for peer-to-peer recovery)

### Software Requirements
- Supported frameworks: **Nemo, PyTorch, PyTorch Lightning**
- Training data formats: **JSON, JSONGZ (compressed JSON), ARROW**
- Amazon ECR for container images

### Container Image
```
658645717510.dkr.ecr.<region>.amazonaws.com/sagemaker-hyperpod/pytorch-training:2.3.0-checkpointless
```

---

## 4-Tier Integration Approach

### TIER 1: NCCL Initialization Optimization

**Benefits**:
- Faster process group initialization (seconds instead of minutes)
- Elimination of single-point-of-failure during startup

**Code**:
```yaml
# kubernetes job spec
env:
  - name: HPCT_USE_CONN_DATA # Enable Rootless
    value: "1"
  - name: TORCH_SKIP_TCPSTORE # Enable TCPStore Removal
    value: "1"
```

### TIER 2: Memory-Mapped Data Loading

**Benefits**:
- Instant data access during recovery
- No need to reload or re-shuffle data

**Code**:
```python
from hyperpod_checkpointless_training.dataloader.mmap_data_module import MMAPDataModule
from hyperpod_checkpointless_training.dataloader.config import CacheResumeMMAPConfig

base_data_module = MY_DATA_MODULE(...) # Customer's own datamodule

mmap_config = CacheResumeMMAPConfig(
    cache_dir=self.cfg.mmap.cache_dir,
)

mmap_dm = MMAPDataModule(
    data_module=base_data_module,
    mmap_config=CacheResumeMMAPConfig(
        cache_dir=self.cfg.mmap.cache_dir,
    ),
)
```

### TIER 3: In-Process Recovery

**Benefits**:
- Sub-minute recovery from process-level failures
- Healthy processes stay alive while failed recover independently

**Code**:
```python
from hyperpod_checkpointless_training.inprocess.health_check import CudaHealthCheck
from hyperpod_checkpointless_training.inprocess.wrap import HPCallWrapper, HPWrapper
from hyperpod_checkpointless_training.inprocess.train_utils import HPAgentK8sAPIFactory

@HPWrapper(
    health_check=CudaHealthCheck(),
    hp_api_factory=HPAgentK8sAPIFactory(),
    abort_timeout=60.0,
)
def re_executable_codeblock(): # The re-executable codeblock defined by user
    ...
```

### TIER 4: Checkpointless (Peer-to-Peer Recovery) - NeMo Integration

**Benefits**:
- Elimination of checkpoint loading
- Recovery from healthy replicas over high-speed EFA interconnect

**Code**:
```python
from hyperpod_checkpointless_training.inprocess.train_utils import wait_rank
    wait_rank() 
    
def main():   
    @HPWrapper(
        health_check=CudaHealthCheck(),
        hp_api_factory=HPAgentK8sAPIFactory(),
        abort_timeout=60.0,
        checkpoint_manager=PEFTCheckpointManager(enable_offload=True),
        abort=CheckpointlessAbortManager.get_default_checkpointless_abort(),
        finalize=CheckpointlessFinalizeCleanup(),
    )
    def run_main(cfg, caller: Optional[HPCallWrapper] = None):
        ...
        trainer = Trainer(
            strategy=CheckpointlessMegatronStrategy(...,
                num_distributed_optimizer_instances=2),
            callbacks=[..., CheckpointlessCallback(...)],
            )
        trainer.fresume = resume
        trainer._checkpoint_connector = CheckpointlessCompatibleConnector(trainer)
        trainer.wrapper = caller
```

**Key Functions Explained**:
- `wait_rank`: All ranks wait for rank information from HyperPod training operator
- `HPWrapper`: Python function wrapper enabling restart capabilities for a restart code block (RCB)
- `CudaHealthCheck`: Ensures CUDA context for current process is healthy, synchronizes with GPU
- `HPAgentK8sAPIFactory`: API for understanding training status from other pods in K8s cluster

---

## Performance Results - Benchmark Table

| Cluster (H100s) | Model | Traditional Recovery | Checkpointless Recovery | Improvement |
|-----------------|-------|---------------------|------------------------|-------------|
| 2,304 GPUs | Internal model | 15-30 minutes | Less than 2 minutes | **~87-93% faster** |
| 256 GPUs | Llama-3 70B (pre-training) | 4 min, 52 sec | 47 seconds | **~84% faster** |
| 16 GPUs | Llama-3 70B (fine-tuning) | 5 min 10 sec | 50 seconds | **~84% faster** |

### Goodput Results
- **Consistently observed: 95%+ goodput** across massive-scale deployments
- Validated on deployments exceeding **2,300 GPUs**

### Model Accuracy Verification
- Checksum matching verified for traditional vs checkpointless training
- **Bit-wise match on training loss** at every training step
- Llama-3 70B pre-training on 32 x ml.p5.48xlarge instances: identical training loss curves

---

## Resources

- Documentation: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod-checkpointless-training.html
- GitHub - Checkpointless Training: https://github.com/aws/sagemaker-hyperpod-checkpointless-training
- GitHub - HyperPod Recipes: http://github.com/aws/sagemaker-hyperpod-recipes

---

# BLOG 2: Introducing Checkpointless and Elastic Training (Launch Announcement)
**Source**: https://aws.amazon.com/blogs/aws/introducing-checkpointless-and-elastic-training-on-amazon-sagemaker-hyperpod/
**Published**: December 3, 2025 (AWS re:Invent announcement)
**Author**: Channy Yun

---

## Two New Features Announced

### Feature 1: Checkpointless Training
- Eliminates disruptive checkpoint-restart cycles
- Maintains forward training momentum despite failures
- **Recovery time: from hours to minutes**
- Enables confident scaling to thousands of AI accelerators

### Feature 2: Elastic Training
- Training workloads automatically scale based on resource availability
- **Expands** to use idle capacity as it becomes available
- **Contracts** to yield resources for higher-priority workloads (e.g., inference peaks)
- **Saves hours of engineering time per week** spent reconfiguring training jobs

---

## Checkpointless Training - 4 Core Components

1. **Collective communications initialization optimizations**
2. **Memory-mapped data loading with caching**
3. **In-process recovery**
4. **Checkpointless peer-to-peer state replication**

All orchestrated through the HyperPod training operator.

---

## Elastic Training - How It Works

### The Problem
- Accelerator availability changes continuously (training completions, inference spikes, experiments)
- Traditional workloads locked into initial compute allocation
- Unable to use idle accelerators without manual intervention

### The Solution: Scaling Mechanism
- Uses **adding/removing data parallel replicas**
- Scale up: new data parallel replicas join, accelerating throughput
- Scale down: replicas removed (not entire job termination), training continues at reduced capacity
- **Preserves global batch size and adapts learning rates**
- Prevents adverse impact on model convergence

### Monitoring Channels
HyperPod training operator monitors through:
1. Pod lifecycle events
2. Node availability changes
3. Resource scheduler priority signals

Enables **near-instantaneous detection** of scaling opportunities.

---

## Availability & Pricing

- **Available**: All AWS Regions where SageMaker HyperPod is available
- **Cost**: **No additional cost** for these training techniques
- Resources:
  - Checkpointless GitHub: https://github.com/aws/sagemaker-hyperpod-checkpointless-training
  - Checkpointless Docs: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-checkpointless.html
  - Elastic Training Docs: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-eks-elastic-training.html
  - HyperPod Recipes: https://github.com/aws/sagemaker-hyperpod-recipes

---

# BLOG 3: Managed Tiered Checkpointing (Traditional Checkpointing Enhancement)
**Source**: https://aws.amazon.com/blogs/machine-learning/accelerate-your-model-training-with-managed-tiered-checkpointing-on-amazon-sagemaker-hyperpod/
**Published**: September 9, 2025
**Authors**: Paulo Aragao, Kunal Jha, Mandar Kulkarni, Vivek Maran, Vinay Devadiga

---

## Meta Llama 3 Failure Statistics

According to Meta's research paper:
- **Failure frequency**: One failure every **3 hours** during Llama 3 training
- **GPU issues**: **60%** of total failures
- **Other failures**: Network, CPU, disks = **40%**

---

## Checkpoint Size Calculations

### Formula
```
Model checkpoint size (GB) = (Number of parameters × Bytes per parameter) ÷ 1024³ bytes
```

### Model Checkpoint Sizes Table

| Model | Checkpoint Size (Model Only) | Checkpoint Size + Optimizer States |
|-------|------------------------------|-----------------------------------|
| Meta Llama 3 70B | **130 GB** | **521 GB** |
| DeepSeek R1 671B | **1.43 TB** | **5 TB** |

### Optimizer State Impact
- Adam optimizer saves 3 additional float16 statistics per parameter
- Results in additional 6 bytes per parameter
- **4x increase in checkpoint size** when including optimizer state

---

## Traditional Checkpointing Challenges

### FSDP (Fully Sharded Data Parallel)
- Each rank saves its own part of checkpoint
- Concurrent writes create file system bottleneck
- NFS struggles with inode and metadata management

### DDP (Distributed Data Parallel)
- Single rank writes complete checkpoint
- All ranks read checkpoint when loading
- Single writer doesn't use full network throughput
- Many readers constrained by file system, network stack, queue size

---

## Managed Tiered Checkpointing - How It Works

### Storage Tiers

1. **GPU HBM Memory**: Stores model, parameters, intermediate results, heavy computation
2. **CPU RAM (Tier 1)**: Fast-access in-memory storage
3. **Adjacent Node RAM**: Asynchronous replication via RDMA over EFA
4. **Amazon S3 (Tier 2)**: Persistent backup storage

### Workflow

1. Define checkpoint frequency in training config
2. Triggering checkpoint stops model training
3. GPU converts model weights (tensors) to state dictionary
4. Data copied to instance's CPU, training resumes
5. Managed tiered checkpointing copies data to RAM
6. Asynchronously copies from host RAM to adjacent nodes using **RDMA over EFA**
7. Periodically copies to S3 for persistence

### Scale Validation
- Tested on **hundreds of GPU to over 15,000 GPU** clusters
- Checkpoints saved **within seconds**

---

## Code Examples

### Installation
```bash
# Install pre-requisites
pip install torch boto3 botocore tenacity s3torchconnector

# Install Managed Tiered Checkpointing library
pip install amzn-sagemaker-checkpointing
```

### Configuration
```python
import torch
import torch.distributed as dist
from torch.distributed.checkpoint import async_save, load
from amzn_sagemaker_checkpointing.config.sagemaker_checkpoint_config import SageMakerCheckpointConfig
from amzn_sagemaker_checkpointing.checkpointing.filesystem.filesystem import (
    SageMakerTieredStorageWriter,
    SageMakerTieredStorageReader
)

checkpoint_config = SageMakerCheckpointConfig(
    # Unique ID for your training job 
    namespace=os.environ.get('TRAINING_JOB_NAME', f'job-{int(time.time())}'), 
    
    # Number of distributed processes/available GPUs
    world_size=dist.get_world_size(), 
    
    # S3 storage location (required for fallbacks and backup)
    s3_tier_base_path="s3://<my-bucket>/checkpoints"
)
```

### Writing Checkpoints
```python
state_dict = {
    "model": model.state_dict(),
    "optimizer": optimizer.state_dict(),
    "step": training_step,
    "epoch": epoch
}

# Create storage writer for current step
checkpoint_config.save_to_s3 = training_step % s3_ckpt_freq == 0
storage_writer = SageMakerTieredStorageWriter(
    checkpoint_config=checkpoint_config,
    step=training_step
)

# Save checkpoint asynchronously
async_save(state_dict=state_dict, storage_writer=storage_writer)
```

### Reading Checkpoints
```python
storage_reader = SageMakerTieredStorageReader(checkpoint_config=checkpoint_config)
load(state_dict, storage_reader=storage_reader)
```

---

## Cluster Configuration

### Create Cluster with Tiered Checkpointing
```bash
aws sagemaker create-cluster \
 --cluster-name "ml-cluster" \
 --tiered-storage-config { "Mode": "Enable" } \
 --instance-groups '[{
    "InstanceCount": 1, 
  ....
 }]'
```

### Update Existing Cluster
```bash
aws sagemaker update-cluster \
    --cluster-name <my-training-cluster> \
    --tiered-storage-config {
            "Mode": "Enable"
            "InstanceMemoryAllocationPercentage": <percent>
            }
```

---

## IAM Policies

### Same Account S3 Access
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": [
                "s3:DeleteObject",
                "s3:GetBucketLocation",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::<bucket_name>",
                "arn:aws:s3:::<bucket_name>/*"
            ],
            "Effect": "Allow"
        }
    ]
}
```

### Cross-Account S3 Access
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CheckPointCrossAccountAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::<account_id>:root"
            },
            "Action": [
                "s3:DeleteObject",
                "s3:GetBucketLocation",
                "s3:GetObject",
                "s3:ListBucket",
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::<bucket_name>",
                "arn:aws:s3:::<bucket_name>/*"
            ]
        }
    ]
}
```

---

## Logging and Troubleshooting

### Log Location
```
/var/log/sagemaker_checkpointing/{namespace}_checkpointing.log
```

### Log Format Example
```
[timestamp] [namespace] [logger_name] [INFO] [filename:451] [Rank 0] Step 240: Starting checkpoint write ([SavePlan Items Count] items)
[timestamp] [namespace] [logger_name] [INFO] [filename:498] [Rank 0] Step 240: In-memory write completed in [Latency]s ([Throughput] MB/s)
[timestamp] [namespace] [logger_name] [INFO] [filename:530] [Rank 0] Step 240: S3 batch write completed in [Latency]s ([Size] total, [Throughput] MB/s average)
```

---

## Best Practices

1. **Two-tier frequency**: Write to in-memory every **10 steps**, write to S3 every **100 steps**
2. **All-or-nothing writing**: Ensures consistency with automatic fallback mechanism
3. **Metadata storage**: Step number stored alongside data for every tier
4. **Multiple TCP streams**: Used when writing to S3 to optimize throughput

---

## Pricing and Availability

- **Cost**: **Free feature** - no additional resources required
- **Supported**: SageMaker HyperPod on Amazon EKS only
- Documentation: https://docs.aws.amazon.com/sagemaker/latest/dg/managed-tier-checkpointing.html
- Python Package: https://pypi.org/project/amzn-sagemaker-checkpointing/

---

## Summary of All Key Numbers for Presentation

| Metric | Value | Source |
|--------|-------|--------|
| Recovery time improvement | 80-93% | Blog 1 |
| Traditional recovery (large cluster) | 15-30 minutes | Blog 1 |
| Checkpointless recovery | < 2 minutes | Blog 1 |
| Goodput achieved | 95%+ | Blog 1 |
| Cost per disruption (256 P5 instances) | $4,693 | Blog 1 |
| Monthly extra cost (daily disruptions) | $141,000 | Blog 1 |
| ml.p5.24xlarge cost | $55/hour | Blog 1 |
| Meta Llama 3 failure frequency | 1 every 3 hours | Blog 3 |
| GPU failure percentage | 60% | Blog 3 |
| Llama 3 70B checkpoint (model only) | 130 GB | Blog 3 |
| Llama 3 70B checkpoint (with optimizer) | 521 GB | Blog 3 |
| DeepSeek R1 checkpoint (model only) | 1.43 TB | Blog 3 |
| DeepSeek R1 checkpoint (with optimizer) | 5 TB | Blog 3 |
| Optimizer state multiplier | 4x | Blog 3 |
| Tiered checkpointing test scale | Up to 15,000+ GPU | Blog 3 |
| Amazon Nova training scale | Tens of thousands of accelerators | Blog 1 & 2 |
| Minimum cluster for checkpointless | 2 nodes | Blog 1 |
| Traditional NCCL init time | Tens of minutes | Blog 1 |
| Checkpointless NCCL init time | Seconds | Blog 1 |
| MMAP memory reduction | 8x to 1x copies per node | Blog 1 |

---

### Recommended Next Step

For your conference presentation, I recommend structuring the content around:
1. **The Problem**: Goodput degradation with scaling (use Meta Llama 3 statistics)
2. **Cost Impact**: The $141,000/month example for relatable business impact
3. **The 6-Stage Bottleneck**: Visual flow of traditional recovery
4. **The 5 Components**: Technical deep dive with architecture diagrams
5. **Results**: The performance benchmark table showing 80-93% improvement
6. **Getting Started**: The 4-tier adoption approach


---
_=== afe775ab2fb612b9e.output === 122 lines_


I have completed the exploration. Here is my comprehensive report:

---

## Exploration Report: Reactive Presentation Project

### 1. PPTX Content Extraction - Complete Text from All 52 Slides

**File**: `/home/ec2-user/reactive_presentation/AIM3338_[NEW-LAUNCH]-SageMaker-HyperPod-Checkpointless-and-elastic-training-for-AI-models.pptx`

**Session ID**: AIM 3338  
**Title**: Checkpointless & Elastic Training for AI Models - Amazon SageMaker HyperPod

**Speakers**:
- Anirudh Viswanathan (Sr. Product Manager, Technical, AWS)
- Arun Nagarajan (Principal Software Engineer, AWS)
- Antonio Ginart (Principal Research Scientist, Salesforce)

**Agenda** (Slide 2):
1. Introduction to Amazon SageMaker HyperPod
2. Large-scale model training
3. Elastic training on HyperPod
4. Checkpointless training on HyperPod
5. Salesforce AI Research
6. Takeaways
7. Resources

**Section 1: Introduction to Amazon SageMaker HyperPod** (Slides 3-6)
- Scale and accelerate generative AI model development across thousands of AI accelerators
- Benefits: Improved efficiency, Reduced time-to-train (up to 40%), Lower costs
- HyperPod benefits: Scalable, Resilient, Efficient, Versatile
- Customizable: Supports Slurm or EKS, PyTorch/TensorFlow/NeMo/JAX, various distributed training libraries (FSDP, DDP, SMDDP, SMP, DeepSpeed, MegatronLM)
- Hardware: GPUs (p5en, p5), AWS Trainium (trn2, trn1), EFA networking, S3/EFS/FSx storage

**Section 2: Challenges with Large-Scale Model Training** (Slides 7-11)
- AI training cluster sizes increased by 20x since 2016, growing to 100K+ GPUs
- As cluster sizes grow, failures are more probable (MTBF decreases)
- Larger clusters increase probability of training faults and idle time during recovery
- Shows checkpoint-based recovery timeline: Step -> Fault -> Rollback -> Re-do -> Resume
- Workloads exhibit diurnal patterns creating pockets of opportunity

**Section 3: Elastic Training on HyperPod** (Slides 12-22)
- **Problem**: Infrastructure Underutilization
  - Traditional training is inflexible (fixed number of accelerators)
  - Preemption problems (all-or-nothing)
  - Manual reconfiguration takes hours
  - Binary choice: terminate entire job or deny higher-priority workload

- **Solution**: Elastic training automatically scales up/down to absorb idle AI accelerators
  - Accelerate time to market
  - Simplify operations
  - Eliminate hours of manual reconfiguration
  - Preserve training convergence through elastic events

- **How it works**:
  1. Detection - Monitor resources & pod lifecycle events
  2. Coordination - Broadcast sync signal to ranks
  3. Checkpoint - Save state using PyTorch DCP
  4. Restart - Processes with new node configuration
  5. Resume - Load & redistribute checkpoint data

- **Getting started**:
  - HyperPod recipes (Llama, Qwen, GPT-OSS, DeepSeek) - zero code changes
  - Custom PyTorch scripts - specify Kueue labels, elastic policy with min/max replicas
  - Code example: `from hyperpod_elastic_agent.elastic_event_handler import elastic_event_detected`

**Section 4: Checkpointless Training on HyperPod** (Slides 23-36)
- **Problem**: Expensive failure recovery
  - All-or-nothing cascade (single failure = cluster-wide stop)
  - Sequential recovery steps (blocking)
  - Checkpoint-based recovery (tens of minutes overhead)
  - Recovery can take up to an hour, wasting millions in idle cluster time

- **Solution**: Checkpointless training reduces fault recovery from hours to minutes
  - Point of failure recovery with zero manual intervention
  - No rollbacks, no wasted compute
  - Train confidently at massive scales (thousands of nodes)

- **Performance** (achieve over 95% goodput):
  - Amazon Nova models trained using this technology on tens of thousands of accelerators
  - 2,304 GPUs: 15-30 min -> <2 min (~87-93% faster)
  - 256 GPUs Llama-3 70B pre-training: 4min 52sec -> 47 seconds (~84% faster)
  - 16 GPUs Llama-3 70B fine-tuning: 5min 10sec -> 50 seconds (~84% faster)

- **Under the hood** (4 components):
  1. Optimized collective communication initialization (rootless, peer-to-peer discovery)
  2. Memory-mapped data loading (training data cached in shared memory, persists across failures)
  3. In-process recovery (isolates failures at process level, failed process rejoins in seconds)
  4. Checkpointless recovery (hot-swap failed components, peer-to-peer recovery of model/optimizer state)

- **Getting started**:
  - HyperPod recipes for Llama and GPT-OSS
  - Custom scripts: Component 1 (env vars), Component 2 (MMAPDataModule wrapper), Components 3&4 (@HPWrapper decorator + CheckpointlessMegatronStrategy)

**Section 5: Salesforce AI Research** (Slides 37-49)
- Running heterogeneous jobs on HyperPod (LLM training, Multimodal, Fine-tuning/RL, Batch inference)
- Batch Inference with Sglang on HyperPod
- Challenge of Non-Determinism in AI Systems
- LZ Penalty: Information-Theoretic Repetition Control
  - Based on LZ77 compression algorithm
  - Considers n-gram repetitions over sliding window
  - Penalizes tokens based on pattern compressibility
- Validation at-scale: >25B tokens generated, >ZettaFLOP compute, validated over ~1 week

**Section 6: Takeaways** (Slides 50-51)
- Elastic training enables dynamic scale-up/down based on available compute
- Elastic training saves hours of engineering time per week
- Checkpointless training cuts recovery from hours to minutes
- Checkpointless training enables over 95% training goodput

**Resources** (Slide 52):
- Checkpointless training GitHub: github.com/aws/sagemaker-hyperpod-checkpointless-training
- HyperPod recipes GitHub: github.com/aws/sagemaker-hyperpod-recipes
- Documentation links for elastic and checkpointless training

---

### 2. Existing Presentation Folders

| Folder | Description | Structure | Slides |
|--------|-------------|-----------|--------|
| `eks-hybrid-nodes/` | EKS Hybrid Nodes | Single `index.html` with `content.md` source | 52 slides, 4 blocks |
| `eks-migration-from-ecs/` | ECS to EKS Migration | Multi-block: `01-multi-cluster.html` through `05-observability-next.html` + `index.html` (combined) + `toc.html` | 76 slides, 5 blocks |
| `eks-observability-ops/` | EKS Auto Mode & Observability | Multi-block: `01-architecture.html` through `04-resource-optimization.html` + `index.html` | 50 slides, 4 blocks |
| `multi-region-architecture/` | Multi-Region Shopping Mall | Multi-block: `01-architecture-overview.html` through `03-failover-resilience.html` + `index.html` + `toc.html` + `_presentation.md` | 36 slides, 3 blocks |

**Common structure per presentation**:
- `common/` folder (copy of framework per presentation)
  - `theme.css` - Dark theme, 16:9, CSS custom properties
  - `slide-framework.js` - SlideFramework class for navigation
  - `animation-utils.js` - Canvas primitives
  - `presenter-view.js` - Dual-window sync
  - `quiz-component.js` - Auto-grading quizzes
  - `export-utils.js` - PDF/ZIP/PPTX export
  - `pptx-theme/` - Theme images (logo, badge, background)
- Block HTML files (`01-*.html`, `02-*.html`, etc.)
- Optional Markdown source files (`.md`)
- `index.html` - Main presentation (combined slides or TOC)
- `toc.html` - Table of contents with block cards (optional)
- `_presentation.md` - Metadata file (optional, YAML frontmatter)

---

### 3. Hub Index Structure (`/home/ec2-user/reactive_presentation/index.html`)

The hub page lists all presentations as cards with:
- Icon, Title, Description
- Block tags (e.g., "Architecture", "Networking")
- Meta info (duration, slide count, language)
- Export buttons (PDF, ZIP, PPTX)

**Currently listed presentations**:
1. Multi-Region Shopping Mall Architecture (1h, 3 Blocks, 36 Slides)
2. EKS Auto Mode & Observability (2h, 4 Blocks, 50 Slides)
3. EKS Hybrid Nodes (~60min, 4 Blocks, 52 Slides)
4. ECS → EKS Migration (2h, 5 Blocks, 76 Slides)

**To add a new presentation**: Create folder, add TOC/index.html, add card to root `index.html`.

---

### Key Files for Reference

- **PPTX extraction output**: `/home/ec2-user/.claude/projects/-home-ec2-user-reactive-presentation/d0f97520-8183-47c4-8e89-8ff80897fb01/tool-results/bwm1u014m.txt`
- **Project CLAUDE.md**: `/home/ec2-user/reactive_presentation/CLAUDE.md`
- **Hub index**: `/home/ec2-user/reactive_presentation/index.html`
- **Example _presentation.md**: `/home/ec2-user/reactive_presentation/multi-region-architecture/_presentation.md`
- **Example multi-block structure**: `/home/ec2-user/reactive_presentation/eks-migration-from-ecs/`
- **Example TOC**: `/home/ec2-user/reactive_presentation/multi-region-architecture/toc.html`

