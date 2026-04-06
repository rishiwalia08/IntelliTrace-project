# CipherLink Demo Script (3–5 Minutes)

## 0:00–0:30 — Problem

"Supply Chain Finance loses billions because fraud is usually invisible at invoice level. A known case showed around $47M exposure from hundreds of invoices that looked normal individually. Traditional systems check documents one-by-one, so they miss cross-company fraud patterns like circular trades and repeated financing." 

## 0:30–1:00 — Solution

"CipherLink is a fraud decision engine for lenders. We ingest invoices, create a unique fingerprint, map supplier-buyer relationships as a graph, and produce an explainable risk score before funds are released." 

## 1:00–3:30 — Live Demo

### Step 1: Upload an invoice
- Open API client or upload form
- Submit invoice payload
- Narration: "CipherLink validates required fields and stores invoice + line items in PostgreSQL."

### Step 2: Show duplicate prevention
- Re-submit same invoice (or near-same)
- Narration: "The platform blocks duplicate identity using deterministic hash and invoice ID checks."
- Show API error: `Duplicate invoice detected`

### Step 3: Show graph intelligence
- Open Graph page
- Narration: "Each invoice creates a directed relationship from supplier to buyer. Red links indicate cycle-like patterns that may signal carousel fraud."

### Step 4: Show risk score + explanation
- Open Dashboard table and select invoice
- Narration: "Risk scoring combines cycle signals, duplicate similarity, transaction velocity, and hub anomalies into one interpretable score."
- Read reasons from detail panel (human-readable)

### Step 5: Show alert panel
- Narration: "High-risk decisions trigger real-time-style alerts for operations teams. This gives banks a stop-payment signal before disbursement." 

## 3:30–4:00 — Impact

"CipherLink shifts fraud control from post-loss investigation to pre-disbursement prevention. It works across tiered supply chains and can evolve into cross-lender intelligence with privacy-preserving methods." 

## Closing Line

"CipherLink helps banks fund real trade, not fraudulent paper." 
