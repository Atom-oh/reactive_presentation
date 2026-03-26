# Claude Agent: Checkpointing & HyperPod Research

_Source: Claude Agent (subagent)_

---

I'll research these ML/AI training topics thoroughly for your conference presentation. Let me start by searching AWS documentation and then expand to web sources for comprehensive coverage.

I found excellent AWS documentation. Let me now fetch the detailed content from the most relevant pages and also search for additional information about traditional checkpointing problems and related technologies.

Excellent data from AWS documentation. Now let me search for additional information about traditional checkpointing problems, checkpoint sizes for large models, and related technologies like PyTorch elastic, NVIDIA NeMo Resiliency, and DeepSpeed.

Let me follow the redirect and search for more information about checkpoint sizes and related technologies.

Let me search for more information about checkpoint sizes, industry statistics on training overhead, and NVIDIA resiliency tools.

Let me search for more specific information about checkpoint sizes and NVIDIA NeMo resiliency.

Let me search for additional technical papers and resources about checkpoint overhead and model sizes.

Excellent, let me get the detailed blog post about checkpoint storage architecture which has specific numbers.

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

