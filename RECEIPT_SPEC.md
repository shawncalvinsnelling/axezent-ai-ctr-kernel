# Axezent AI CTR Receipt Spec v1

Schema identifier:

```text
AXEZENT-AI-CTR-RECEIPT-v1
```

Truth label:

```text
BOUNDED_AI_TRACE_POLICY_CHECK
```

A receipt records:

- agent metadata
- task metadata
- allowed write paths
- policy pack identity
- finite trace steps
- SHA-256 evidence references
- final answer claim
- expected checker result for demos/tests

The reference checker uses deterministic rules only. It does not evaluate hidden chain-of-thought or unobservable model internals.
