# Claude Agent: AWS Official Docs Research

_Source: Claude Agent (subagent)_

---

I'll search AWS documentation for SageMaker HyperPod Checkpointless Training information. Let me start with multiple parallel searches to gather comprehensive documentation.

Excellent. I found the key documentation pages. Let me now read the main documentation pages in detail.

Good progress. Let me continue reading the truncated content and get more documentation pages.

Now let me read the specific documentation pages for NCCL communication improvements and memory-mapped dataloader.

Excellent. Now let me get the training operator documentation and the custom models tutorial for more details.

Now let me search for additional details on the tutorials and get more specific code examples.

Let me also read more about the training operator installation details and search for any additional checkpointless training documentation I might have missed.

Now let me also fetch the ToolSearch to access the Write tool for creating the research plan.

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

