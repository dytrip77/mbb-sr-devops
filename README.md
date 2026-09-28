**Selected cloud: Microsoft Azure**

# Senior DevOps Engineer Assessment

A proposed delivery platform for forty teams using Azure Container Apps, Azure Kubernetes Service and Azure Functions. The design covers reusable pipelines, federated production access, release controls, progressive delivery, emergency changes, delivery metrics and incremental adoption.

**[Read the assessment](Senior-DevOps-Assessment-Azure.md)**

## Review guide

| Deliverable | Location |
|---|---|
| Platform design, controls, runbooks, metrics and adoption | [Assessment](Senior-DevOps-Assessment-Azure.md) |
| Artifact flow and trust boundaries | [Delivery diagram](architecture/delivery.png) |
| Private runtime connections and automated recovery | [Runtime diagram](architecture/runtime.png) |
| Availability zones and regional recovery | [Failure-domain diagram](architecture/resilience.png) |
| Pipeline, release contract, Azure Policy, KQL and HTTP health gate | [Examples](examples/README.md) |
| Local checks and live acceptance requirements | [Validation](validation/README.md) |
| Primary references and AI assistance | [Sources and disclosure](Sources-and-disclosure.md) |

Diagrams are embedded in the assessment and open at full size from the links above. Their editable JSON specifications are in `architecture/`.

## Run the example tests

Requires Python 3.10 or later; uses the standard library. From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s examples -p 'test_*.py' -v
```

The HTTP health gate has **34 passing tests** recorded in the validation summary. It evaluates supplied observations without deploying resources or requiring Azure credentials.

## Implementation status

This is a design submission with focused reference examples. The Azure Pipelines consumer file specifies a proposed platform-template interface. Live Azure template compilation, permissions, policy enforcement and recovery drills remain acceptance work before implementation sign-off.
