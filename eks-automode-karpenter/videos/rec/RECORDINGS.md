# 실제 터미널 녹화 (V1~V4용), 2026-10-20

클러스터 `akd-auto`(EKS Auto Mode), `akd-karp`(직접 설치 Karpenter), 둘 다 EKS 1.37 (platform eks.5), ap-northeast-2, fsi-demo-vpc의 데모 전용 private 서브넷 2개(10.0.32.0/20 2a, 10.0.48.0/20 2b). 재구성 화면이 아니라 실행 중인 터미널 출력 그대로입니다. 모든 측정은 1회 실행 결과이며 벤치마크가 아닙니다.

공통 사항
- 녹화: asciinema (`asciinema rec -c 'bash rec/dN-driver.sh' --cols 120 -i 2`). driver가 프롬프트(`~/eks-akd-demo $`)와 명령을 먼저 출력한 뒤 실행합니다.
- 변환: `rec/to-mp4.sh` (agg 1.9.0, Source Code Pro 28, idle-time-limit 2 → ffmpeg h264, 1920 폭, 무음). 2초 넘는 무출력 구간은 2초로 줄였으므로 영상 길이는 실제보다 짧습니다. 화면의 `elapsed`, `+Ns`는 실제 시간입니다.
- 가린 값: 12자리 계정 ID 패턴을 `.cast`에서 치환(4개 녹화 모두 0건). 노드 이름, private IP, 인스턴스 ID는 그대로 둡니다.
- 환경 값(라이브 확인): Auto Mode 노드 OS `Bottlerocket (EKS Auto, Standard) 2026.10.9`, kubelet `v1.37.0-eks-29d7970`. Karpenter 노드 `Amazon Linux 2023.12.20261012`(AMI v20261012) / 시작 시 v20261003, kubelet `v1.37.0-eks-b9510e3`. Karpenter controller `public.ecr.aws/karpenter/controller:1.15.0`.
- NodePool 설정: 두 클러스터 모두 `demo` NodePool에 `consolidationPolicy`를 지정하지 않았습니다. 라이브 값: Auto Mode `Balanced`, expireAfter `336h` / Karpenter `WhenEmptyOrUnderutilized`, `720h`. 둘 다 consolidateAfter 30s, budget `nodes: "1"`, on-demand, c/m/r, generation > 5, amd64. Auto Mode built-in `general-purpose`, `system`도 `Balanced`, 30s, 336h, budget 10%.
- 워크로드: pause 이미지, replica당 requests 1 vCPU / 1.5Gi.
- 네트워크 보안: 노드는 private 서브넷, 공인 IP 없음. EKS API endpoint는 public+private, public은 작업 PC NAT 출구 IP /32만 허용(`01-cluster/common.yaml.tmpl` `publicAccessCIDRs`).

| 파일 | 녹화 시작(UTC) | 원본 cast 길이 | mp4 길이 | 해상도 |
|---|---|---|---|---|
| d1-scaleout.mp4 | 13:53:58 | 69.2초 | 29초 | 1920x1358 |
| d2-consolidation.mp4 | 14:04:59 | 224.5초 | 37초 | 1920x1212 |
| d3-drift.mp4 | 14:19:52 | 150.2초 | 37초 | 1920x1212 |
| d4-spot.mp4 | 14:23:00 | 88.8초 | 32초 | 1920x1284 |

## D1: 스케일 아웃 (V1)
- 두 클러스터에 동시에 `scale --replicas=10` (0 → 10).
- 두 클러스터 모두 NodeClaim 1개, `c7i-flex.4xlarge` on-demand(2b)를 선택.
- NodeClaim 생성 13:54:15(두 클러스터 같음) → Ready: Auto Mode 13:54:30(15초), Karpenter 13:54:55(40초).
- 10개 모두 Ready: Auto Mode **+28초**, Karpenter **+47초** (scale 명령 기준).

## D2: 스케일 인 후 consolidation (V2)
- 10 → 4. 시작 시 두 클러스터 모두 `c7i-flex.4xlarge` 1대.
- 녹화 회차(14:05): 두 클러스터 모두 `c7i-flex.2xlarge`로 교체(replace), Pod 4개 이동. 처음 이동한 Pod 관찰 Auto Mode +67초, Karpenter +75초.
- Auto Mode 이벤트: `ConsolidationCandidate ... replace ... -> [1 replacement] (savings: $0.38)`, `ConsolidationApproved score 0.50 >= threshold 0.50 (k: 2, savings 50.0%, disruption 100.0%)`.
- 이벤트 순서(양쪽 같음): DisruptionLaunching(새 NodeClaim) → 새 노드 Ready → DisruptionTerminating(기존) → Evicted 4개.
- 앞선 회차(13:55, 녹화 중단으로 미사용): 같은 결과(4xlarge → 2xlarge, 4개 이동). Karpenter는 scale-in 약 1분 뒤, Auto Mode는 약 5분 30초 뒤 실행. **두 회차의 시점이 달라 정책 간 속도 차이로 해석하지 않습니다.**

## D3: Drift 교체 (V3)
- 시작: 각 클러스터 demo 노드 2대(2a, 2b), Pod 6개(zone topology spread, minDomains 2).
- Karpenter: EC2NodeClass `amiSelectorTerms` alias `al2023@v20261003` → `al2023@v20261012`. Auto Mode: NodeClass `advancedCompute.kubelet.maxPods: 64` 추가.
- 패치 직후 두 클러스터 모두 기존 NodeClaim 2개가 `Drifted=True`.
- 교체 순서(budget 1): Launch → Terminate → Launch → Terminate. Auto Mode 14:20:12 / 14:20:30 / 14:20:45 / 14:21:00, Karpenter 14:20:10 / 14:20:46 / 14:20:57 / 14:21:27.
- 완료(기존 NodeClaim 0, 6/6 Running): Auto Mode **+98초**, Karpenter **+127초**.
- 결과: Karpenter 새 노드 AMI `amazon-eks-node-al2023-x86_64-standard-1.37-v20261012`. Auto Mode 새 노드 `capacity.pods` = **56**(설정 64보다 작음: 실제값 = min(설정값, 인스턴스 IP 수, 110)).
- 같은 EC2NodeClass를 쓰는 `spot` NodePool 노드도 함께 Drift 교체됨(spot-8wplw → spot-89g4w).

## D4: Spot 중단 (V4, akd-karp만)
- Auto Mode는 FIS EC2 액션을 지원하지 않으므로 Karpenter 클러스터에서만 실행.
- FIS `aws:ec2:send-spot-instance-interruptions`, durationBeforeInterruption PT2M, 대상 1대(태그 `karpenter.sh/nodepool=spot`, `eks:eks-cluster-name=akd-karp`). 실험 14:23:15 시작, 14:23:28 완료.
- 대상: `spot-89g4w` m7i.xlarge spot(2b), spot-app Pod 3개가 모두 이 노드에 있음.
- 이벤트: 14:23:28 `SpotRebalanceRecommendation` → 14:23:29 `SpotInterrupted`, `TerminatingOnInterruption`, Pod 3개 `Evicted: Forceful Termination`, 대체 NodeClaim `spot-cx877` 지명 → 14:23:33 Launched → 14:23:35 기존 인스턴스 `InstanceTerminating` → 14:24:00 대체 노드(c7i-flex.xlarge spot) Ready.
- Karpenter는 2분을 기다리지 않고 경고 직후 기존 노드를 비우고 종료했습니다. Pod 3개가 한 노드에 있었으므로 **약 30초 동안 Running 0개**(Evicted 14:23:29 → 대체 노드 Ready 14:24:00). 녹화 driver 기준 대상 노드 삭제와 3/3 Running 회복 +65초(FIS 시작 기준).
- 교훈: replica를 여러 노드에 분산(topology spread)해야 Spot 중단 때 서비스 공백이 줄어듭니다.
