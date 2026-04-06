# Judge Q&A Prep

## Q1) Why not existing systems?

Most existing systems validate single documents, not multi-tier transaction networks. Fraud today is often relationship-driven, so document-level checks alone miss circular trades, repeated links, and network velocity anomalies.

## Q2) Why is blockchain not required initially?

For hackathon speed and practical adoption, CipherLink starts with API + database + graph intelligence, which already blocks major fraud patterns. Blockchain is a planned trust layer for cross-lender uniqueness and auditability, not a prerequisite for immediate risk reduction.

## Q3) How scalable is this?

The architecture is modular: ingestion, graph analysis, and risk scoring are separated. It can scale horizontally at API level, move graph processing to dedicated workers, and later migrate persistent graph storage to Neo4j for larger production workloads.

## Q4) What makes this unique?

CipherLink combines three strengths in one flow: deterministic duplicate prevention, network-level fraud detection, and explainable risk output for credit teams. It is not just detection, it is decision support before disbursement.

## Q5) How do you handle false positives?

We use transparent weighted rules and expose reasons for every score, so analysts can review context quickly. Thresholds are tunable by lender policy, and future ML calibration can optimize precision-recall without losing explainability.
