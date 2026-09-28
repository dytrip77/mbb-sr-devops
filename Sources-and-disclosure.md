**Selected cloud: Microsoft Azure**

# Sources and disclosure

Reviewed 25 September 2026. Provider references are linked beside their claims in the assessment. Numeric SLOs, rollout weights, sample requirements, time limits and adoption targets are proposed policy choices, not vendor defaults or measured outcomes.

## Design background

The design combines reusable pipeline libraries, federated identities, GitOps, digest-based artifact promotion, migration locking and deployment-event metrics. Implementation details and targets are proposed for this scenario. Service names, repository names, resource names and release identifiers in the examples are illustrative.

## Primary public references

| Topic | Reference |
|---|---|
| Workload federation | [Azure Resource Manager workload identity service connections](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/configure-workload-identity?view=azure-devops) |
| Protected resources, approval and locks | [Azure Pipelines approvals and checks](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/approvals?view=azure-devops) |
| Automated approval callbacks | [Invoke Azure Function / REST API checks](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/invoke-checks?view=azure-devops) |
| Tenant emergency recovery | [Microsoft Entra emergency-access accounts](https://learn.microsoft.com/en-us/entra/identity/role-based-access-control/security-emergency-access) |
| Storage TLS retirement | [TLS 1.2 migration](https://learn.microsoft.com/en-us/azure/storage/common/transport-layer-security-configure-migrate-to-tls2) |
| Functions storage compatibility | [Functions storage considerations](https://learn.microsoft.com/en-us/azure/azure-functions/storage-considerations) |
| Human elevation | [PIM Azure resource role settings](https://learn.microsoft.com/en-us/entra/id-governance/privileged-identity-management/pim-resource-roles-configure-role-settings) |
| Container deployment semantics | [Container Apps revisions](https://learn.microsoft.com/en-us/azure/container-apps/revisions) and [traffic splitting](https://learn.microsoft.com/en-us/azure/container-apps/traffic-splitting) |
| Container availability | [Reliability in Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/disaster-recovery) |
| Serverless release semantics | [Functions deployment slots](https://learn.microsoft.com/en-us/azure/azure-functions/functions-deployment-slots) |
| Serverless availability | [Functions zone redundancy](https://learn.microsoft.com/en-us/azure/azure-functions/functions-zone-redundancy) |
| Private edge/origin trust | [Front Door origins](https://learn.microsoft.com/en-us/azure/frontdoor/origin), [Front Door Premium Private Link](https://learn.microsoft.com/en-us/azure/frontdoor/private-link), [Container Apps integration](https://learn.microsoft.com/en-us/azure/container-apps/how-to-integrate-with-azure-front-door), [internal load balancer integration](https://learn.microsoft.com/en-us/azure/frontdoor/standard-premium/how-to-enable-private-link-internal-load-balancer) |
| Signing and trust | [OCI signing/verification overview](https://learn.microsoft.com/en-us/azure/container-registry/overview-sign-verify-artifacts) and [Notation/Key Vault signing](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-tutorial-sign-trusted-ca) |
| Supply-chain artifact promotion | [ACR OCI artifacts and recursive ORAS copy](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-manage-artifact) |
| Continuous vulnerability assessment | [Defender for Cloud registry scanning](https://learn.microsoft.com/en-us/azure/container-registry/scan-images-defender) |
| AKS signature admission | [Ratify and Azure Policy guidance](https://learn.microsoft.com/en-us/azure/security/container-secure-supply-chain/articles/validating-image-signatures-using-ratify-aks) |
| AKS rollout controllers | [Argo Rollouts analysis](https://argo-rollouts.readthedocs.io/en/stable/features/analysis/) and [traffic management](https://argo-rollouts.readthedocs.io/en/stable/features/traffic-management/) |
| Resource policy | [Azure Policy effect semantics](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/effect-basics) and [definition structure](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/definition-structure-basics) |
| Sample storage policy | [Disable anonymous Blob access](https://learn.microsoft.com/en-us/azure/storage/blobs/anonymous-read-access-prevent) and [Shared Key authorization](https://learn.microsoft.com/en-us/azure/storage/common/shared-key-authorization-prevent) and [Storage policy reference](https://learn.microsoft.com/en-us/azure/storage/common/policy-reference) |
| Database disaster recovery | [PostgreSQL replica promotion](https://learn.microsoft.com/en-us/azure/postgresql/read-replica/concepts-read-replicas-promote) and [geo-replication](https://learn.microsoft.com/en-us/azure/postgresql/read-replica/concepts-read-replicas-geo) |
| Database corruption recovery | [PostgreSQL backup and restore](https://learn.microsoft.com/en-us/azure/postgresql/backup-restore/concepts-backup-restore) |
| Immutable evidence | [Configure Blob immutability](https://learn.microsoft.com/en-us/azure/storage/blobs/immutable-policy-configure-container-scope) |
| Audit export | [Azure DevOps audit streaming](https://learn.microsoft.com/en-us/azure/devops/organizations/audit/auditing-streaming?view=azure-devops) |
| Metrics ingestion | [Azure Monitor Logs Ingestion API](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/logs-ingestion-api-overview) |
| Query schema | [Application Insights AppRequests table](https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/apprequests) |
| Delivery measures | [DORA's software delivery performance metrics](https://dora.dev/guides/dora-metrics/) |

DORA is cited for measurement definitions only. It adds no non-Azure service dependency. Argo Rollouts documentation is the primary source for the optional open-source controller's behavior.

## AI assistance and validation disclosure

Anthropic Claude provided review feedback on the design, examples and packaging. OpenAI Codex assisted with primary-documentation research, drafting, applying Claude’s feedback, example-code fixes and local tests. Archify generated and checked the architecture diagrams. This repository includes three static diagrams and their editable source specifications. Codex also prepared the repository layout and reviewed the retained files for private information.

Local validation results and their scope are recorded in [validation/README.md](validation/README.md). Azure template compilation, WIF/RBAC and policy enforcement, KQL execution, real traffic switching, database restoration and regional failover remain pending live acceptance. The proposal distinguishes these states explicitly.
