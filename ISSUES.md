# Open
- 슬라이드의 좌우의 폭에 의해 비율이 조정되고 위아래로는 screen사이즈가 조절은 되지만 컨텐츠가 비율에 맞게 줄어들지 않음 (대규모 리팩토링 필요 — 후순위)



# In-Progress


# Resolved
A. code-block에 max-height: 45vh + overflow-y: auto 추가 → 스크롤 동작 복구
B. tab-btn에 z-index: 5 추가 + fragment 제거로 탭 클릭 가능
D. canvas→HTML 다이어그램, 플로우 차트, 인포그래픽 도입으로 디자인 다양화
1. 6 슬라이드 canvas→HTML Service/Data Plane 아키텍처 다이어그램으로 교체
2. 8 슬라이드 canvas→HTML 멀티 계정 네트워크 토폴로지 인포그래픽으로 교체
3. 22 슬라이드 화살표 → CSS styled ▸ 커넥터로 재디자인
4. 23 슬라이드 code-block 스크롤 (이슈 A로 자동 해결)
5. 27 타임라인 dot 3rem 확대 + gradient progress 커넥터 추가
6. 29 ARC 개요 탭 fragment 6개 제거 → 즉시 표시
7. 29 아키텍처 ASCII→HTML/CSS 세로 플로우 다이어그램 (GitHub/EKS/ArgoCD 색상 구분)
8. 27 하단에 Argo Rollouts 지원 Traffic Provider callout 추가
9. 38 CA vs Karpenter fragment 15개 제거 → 탭 전환 시 즉시 표시
10. 39 return arrow 라벨 "Schedule Pod"→"Pod Bound"로 방향 명확화
11. 41 KEDA canvas component/arrow 배열 패턴으로 리팩토링 (eks-observability-ops 참조)
12. 52 ol { padding-left: 1.5rem } 추가 → 숫자 잘림 해소
13. 59 조사 완료 — 12개 슬라이드 모두 콘텐츠 정상 (크로스블록 카운트 불일치로 추정)
14. 65 canvas→HTML 3-column Logs/Metrics/Traces 다이어그램 교체
15. 70 checklist-text 1.1rem + code-block 0.8rem/1.5 + 간격 조정
20. 5/4 Prometheus canvas → HTML 아키텍처 다이어그램으로 변경
21. 5/7 Blue/Green timeline 5개 독립 step으로 분리, canvasMaxStep 수정
22. 5/12 Deep Dive 링크 fragment fade-in 제거 → 한번에 표시
23. 5/1 커버 슬라이드 subtitle 포맷 Block 02-04와 일치시킴
24. common/ 폴더를 프로젝트별 독립 복사본으로 분리 (eks-hybrid-nodes: HEAD, eks-migration-from-ecs: HEAD, eks-observability-ops: 7cd7041), aws-icons 불필요 파일 정리, root common/은 허브 전용으로 최소화
1. footer CSS bottom 위치 수정 (bottom: 2%)
2. 1/4 compare-content fragment 제거 → Tab 전환 시 즉시 표시
3. 1/7 NGF+Istio 중복 슬라이드 삭제 (s7-s10)
4. 1/10 timeline 4개 독립 step으로 분리 완료
5. 1/12 Q3 질문 Multi-Cluster 관련으로 교체
6. 2/4 compare-content fragment 제거
7. 2/5 Argo Rollouts + Istio Canary HTML 카드 레이아웃으로 교체
8. 2/6 timeline 5개 독립 step으로 분리 완료
9. 2/7 zone-aware-rollouts canvas 재작성
10. 2/10 compare-content fragment 제거 + Istio "미포함 (향후 검토)" 표시
11. 1/6 Gateway API 슬라이드 폰트 사이즈 증가
12. 1/10 Timeline 폰트 사이즈 증가 및 글내림 추가
13. 3/4 Karpenter Architecture 화살표 곡선으로 개선
14. 3/6 Consolidation canvas 텍스트 줄바꿈 수정
15. 3/8 KEDA Architecture canvas 개선
16. 4/2 aws-auth vs Access Entries compare fragment 제거 (숫자 가림 해소)
17. 4/5 Network Policy 슬라이드 z-index 수정
18. 화해 설문 갭 보강: SGP 슬라이드 (Block 01), ACK 의사결정 (Block 02), Batch 워크로드 (Block 03), DR/비용/Tracing (Block 05)
19. Block 01 Quiz Q3/Q4 중복 해소
