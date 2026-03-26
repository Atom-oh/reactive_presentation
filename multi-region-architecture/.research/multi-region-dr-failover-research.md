# Multi-Region DR & Failover Automation: Deep Research Report (L300+)
**Author:** Senior AWS Reliability Engineer
**Topic:** Multi-Region DR & Failover Automation

## 1. RTO/RPO Framework

### Definitions & Business Impact
*   **RPO (Recovery Point Objective):** The maximum acceptable amount of data loss measured in time. (e.g., "We can lose at most 1 minute of data").
*   **RTO (Recovery Time Objective):** The maximum acceptable time to restore service after a failure. (e.g., "The service must be back online within 15 minutes").

**Business Impact:**
- **High RPO:** Direct loss of revenue, regulatory fines (GDPR/compliance), and loss of customer trust.
- **High RTO:** Operational downtime, brand damage, and productivity loss.

### Per-Component RTO/RPO Matrix
| Service | RPO Target | RTO Target | Mechanism |
| :--- | :--- | :--- | :--- |
| **Route 53 (ARC)** | 0 (Control Plane) | < 1 min | Routing Controls / Readiness Checks |
| **CloudFront** | 0 | < 1 min | Origin Failover / Lambda@Edge |
| **Aurora Global Database** | < 1 sec | < 1 min | Storage-level replication; Global failover |
| **DocumentDB Global Cluster** | < 1 sec | < 10 mins | Storage-level replication; Manual/Scripted failover |
| **ElastiCache Global Datastore** | < 1 sec | < 1 min | Asynchronous replication; Manual/Scripted failover |
| **Amazon MSK Multi-Region** | < 1 sec | < 15 mins | MSK Replicator (Cross-cluster replication) |
| **Amazon EKS** | 0 (Code/Config) | < 30 mins | GitOps / Cluster Re-creation / Global LB |
| **Amazon S3 (CRR)** | < 15 mins (99.9%) | < 1 min | Cross-Region Replication; S3 Multi-Region Access Points |

### Cost vs. RTO/RPO Trade-off Curve
As RTO/RPO approaches zero, cost increases exponentially.
- **Backup/Restore:** Low cost, High RTO/RPO (Hours/Days).
- **Pilot Light:** Medium cost, Medium RTO/RPO (Minutes).
- **Warm Standby:** High cost, Low RTO/RPO (Minutes/Seconds).
- **Multi-Site Active-Active:** Highest cost, Zero RTO/Near-Zero RPO.

### Tier Classification
- **Tier 0 (Automatic):** 0-1 min RTO/RPO. Active-Active setups. Route 53 ARC routing controls.
- **Tier 1 (Semi-Auto):** 1-15 min RTO/RPO. Warm standby with automated failover pipelines (Lambda).
- **Tier 2 (Manual):** 15+ min RTO. Pilot light or Backup/Restore requiring human intervention.

---

## 2. Failure Scenarios Deep Dive

### Scenario 1: Full Region Failure (e.g., us-east-1 Outage)
*   **Cascade Impact:** Global services (IAM, Route 53) might be impacted if they rely on the control plane of the failed region.
*   **Auto-failover:** S3 Multi-Region Access Points, CloudFront Origin Failover, Aurora Global Database (with managed failover).
*   **Manual/Scripted:** DocumentDB, ElastiCache, EKS cluster traffic shifting (unless using Global Accelerator/Route 53 ARC).

### Scenario 2: Single Database Failure (Corruption vs. Infrastructure)
*   **Graceful Degradation:** Use Circuit Breakers in the application to serve stale data from cache (ElastiCache) or return a 202 Accepted for writes to be processed later.
*   **Patterns:** Read-only mode in the primary region, redirecting writes to the secondary region if a global database failover is triggered.

### Scenario 3: EKS Cluster Failure (Control Plane or Node Group)
*   **Pod Rescheduling:** EKS control plane automatically reschedules pods on healthy nodes.
*   **Node Group Recovery:** Auto Scaling Groups (ASG) replace unhealthy nodes.
*   **Regional Strategy:** If the entire cluster is gone, GitOps (ArgoCD/Flux) should immediately bootstrap a new cluster in the DR region or shift traffic to an existing warm cluster.

### Scenario 4: Network Partition (Split-Brain Prevention)
*   **Risk:** Both regions think they are primary and accept writes.
*   **Mitigation:** Use a **Quorum-based** witness (like Route 53 ARC) or a centralized state store (DynamoDB Global Tables) to determine which region holds the "Master" lock. Route 53 ARC Routing Controls are the AWS-native way to prevent split-brain.

---

## 3. Automated Failover Pipeline

### Architecture
`CloudWatch Alarm (Primary Health)` → `EventBridge Rule` → `Lambda (Failover Logic)` → `SNS Notification`

### DocumentDB Failover Lambda (Python)
```python
import boto3
import os

client = boto3.client('docdb')

def lambda_handler(event, context):
    global_cluster_id = os.environ['GLOBAL_CLUSTER_ID']
    target_region_cluster_arn = os.environ['TARGET_CLUSTER_ARN']
    
    print(f"Triggering failover for {global_cluster_id} to {target_region_cluster_arn}")
    
    try:
        response = client.failover_global_cluster(
            GlobalClusterIdentifier=global_cluster_id,
            TargetDbClusterIdentifier=target_region_cluster_arn
        )
        return response
    except Exception as e:
        print(f"Error during failover: {str(e)}")
        raise e
```

### ElastiCache Promotion Lambda (Python)
```python
import boto3
import os

client = boto3.client('elasticache')

def lambda_handler(event, context):
    global_id = os.environ['GLOBAL_REPLICATION_GROUP_ID']
    primary_region = os.environ['PRIMARY_REGION']
    secondary_region = os.environ['SECONDARY_REGION']
    
    print(f"Promoting secondary region {secondary_region} for {global_id}")
    
    try:
        response = client.failover_global_replication_group(
            GlobalReplicationGroupIdentifier=global_id,
            PrimaryRegion=secondary_region,
            PrimaryReplicationGroupId=os.environ['SECONDARY_REPLICATION_GROUP_ID']
        )
        return response
    except Exception as e:
        print(e)
        raise e
```

### EventBridge Rule JSON
```json
{
  "source": ["aws.cloudwatch"],
  "detail-type": ["CloudWatch Alarm State Change"],
  "detail": {
    "state": {
      "value": ["ALARM"]
    },
    "alarmName": ["Primary-Region-Health-Alarm"]
  }
}
```

### Route 53 ARC Readiness Checks
Route 53 Application Recovery Controller (ARC) ensures that your DR region is actually ready to take traffic before you flip the switch.

---

## 4. DSQL Single-Region Risk & Mitigation

### Current Risk: Single-Region Availability
Amazon DSQL (Distributed SQL) is currently available in a limited set of regions (e.g., us-east-1). If that region fails, the DSQL cluster is unavailable, posing a high risk for mission-critical apps.

### Mitigation Strategies
1.  **Linked Clusters (Roadmap):** AWS is working on multi-region active-active clusters for DSQL.
2.  **Periodic Snapshots:** Export data to S3 and use Cross-Region Replication (CRR) to move snapshots to another region.
3.  **Application-level Fallback:** Use a secondary database (like Aurora) for DR, with an application layer that can transform and write data to both.
4.  **Read Replicas (if supported):** If read replicas can be cross-region, use them for "Read-Only" mode during a primary failure.

---

## 5. DR Testing Strategy

### GameDay Planning
- **Frequency:** Quarterly or Bi-Annually.
- **Scope:** Full region failover, Data corruption recovery, Network isolation.
- **Participants:** DevOps, SREs, Product Owners, Security, and Communication teams.

### Chaos Engineering with AWS FIS
Use **AWS Fault Injection Service (FIS)** to simulate:
- API throttling.
- Network latency between regions.
- Instance/Node termination in EKS.
- Database failover events.

### SSM Automation YAML (Failover Runbook)
```yaml
description: "Promote Secondary Region to Primary"
schemaVersion: '0.3'
assumeRole: "{{ AutomationAssumeRole }}"
parameters:
  AutomationAssumeRole:
    type: String
mainSteps:
  - name: FailoverDocDB
    action: 'aws:executeAwsApi'
    inputs:
      Service: docdb
      Api: FailoverGlobalCluster
      GlobalClusterIdentifier: "my-global-docdb"
      TargetDbClusterIdentifier: "arn:aws:rds:us-west-2:123456789012:cluster:dr-cluster"
  - name: UpdateRoute53ARC
    action: 'aws:executeAwsApi'
    inputs:
      Service: route53-recovery-control-config
      Api: UpdateRoutingControlState
      RoutingControlArn: "arn:aws:route53-recovery-control::..."
      RoutingControlState: "On"
```

### DR Drill Metrics
- **TTD (Time to Detect):** How long before monitoring triggered an alert.
- **TTF (Time to Failover):** Total time from decision to service restoration.
- **Data Loss:** Measured gap in sequence IDs or timestamps between regions.

### Post-Incident Review (PIR) Template
1.  **Summary:** High-level timeline.
2.  **Impact:** Users/Services affected.
3.  **Root Cause:** Why the failure occurred (or why the test behaved as it did).
4.  **Correction Action Items (COEs):** What will be fixed to prevent/improve next time.
