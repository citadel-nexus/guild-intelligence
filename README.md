# Guild: Intelligence

> *"We don't react to threats. We predict them."*

The Intelligence Guild is Citadel's surveillance and threat-response layer.
It runs the **Nemesis** adversarial AI framework, monitors all guild systems,
and feeds intel into the governance bridge. Where other guilds build, Intelligence
watches — and acts when necessary.

---

## Identity

| | |
|---|---|
| **Sigil** | The All-Seeing Eye |
| **Vibe** | Cold. Calculated. Moves before you know it moved. |
| **Color** | Deep Violet `#3D0066` |
| **NATS Prefix** | `citadel.intel.*` |
| **Port** | `8000` |
| **Parent Guild** | Intelligence (root) |
| **Sub-guild** | Research |

---

## Purpose

- Run **Nemesis v2** — 7 adversary classes, sanctions ladder, collusion graph
- Operate the **Pen Test Engine** — OWASP, SSO flow tests, infra scanning
- Feed threat events to the **Governance Bridge** for real-time enforcement
- IP quarantine, rate limiting, honeypot trap paths
- Security telemetry to Datadog + PostHog

---

## Domains of Operation

### Nemesis Framework
| Phase | Status | Scope |
|-------|--------|-------|
| Phase 1 | Live | 7 adversary classes, 53 tests |
| Phase 2 (Runtime) | Live | Red-team engine, fault injection, collusion |
| Phase 3 (Pen Test) | Live | OWASP + SSO + Infra + Credential scanning |

### Governance Bridge
Subscribes to 5 NATS subjects, scores risk in real time, and enforces tiered
enforcement actions: IP quarantine, payment holds, and Slack/Discord alerts.
Thresholds are configurable and governed by internal policy — not published here.

---

## Services & Integrations

| Service | Role |
|---------|------|
| **NATS** | `nemesis.threat.*`, `health.alert`, `cicd.pipeline.failed` |
| **Supabase** | `governance_events` table + RPC insert |
| **Datadog** | L1–L6 StatsD metrics, APM traces |
| **PostHog** | Security events, feature flags |
| **Discord** | Threat alert webhooks |
| **Slack** | `#voice-agents`, `#platform` alert channels |

---

## NATS Event Subjects

```
nemesis.threat.detected         — New adversarial event
nemesis.threat.escalated        — Sanctions ladder escalation
citadel.intel.quarantine        — IP added to quarantine list
citadel.intel.scan.complete     — Pen test cycle finished
citadel.intel.governance.event  — Governance decision emitted
health.alert                    — System health degradation
```

---

## Mission System

Intelligence missions reward threat detection, defensive operations, and governance compliance.

| Mission | Description | XP | Unlock |
|---------|-------------|-----|--------|
| First Assessment | Run a full Nemesis Phase 1 threat evaluation | 200 | Default |
| Pattern Identified | Detect and log an adversarial pattern | 150 | Default |
| Quarantine Executed | Enforce an automated IP quarantine action | 300 | Operator rank |
| Pen Test Complete | Complete a full pen test cycle and file a report | 400 | Intel rank |
| 30-Day Clean | Zero governance escalations for 30 days | 500 | Director rank |
| Collusion Graph | Detect a multi-agent collusion cluster | 600 | Director rank |

**Daily missions (reset 00:00 UTC):**
- Emit a `nemesis.threat.detected` event — 25 XP
- Clear a pending governance queue item — 30 XP

Trust Points (TP) are the primary currency here. Successful threat detections earn TP;
false positives or missed threats reduce it. Your CAPS score determines autonomy level.

---

## Guild Expectations

**Members:**
- Maintain zero unreviewed governance escalations for >24 hours
- CAPS composite score ≥ 0.65 required to handle Phase 3 pen test duties
- Complete Intelligence onboarding (Nemesis primer) within 7 days of placement
- Active participation in `#threat-intel` and `#gov-review` lobby channels

**Contributors:**
- All security-affecting PRs require dual review (2 approvals minimum)
- Any changes to governance enforcement logic require a risk impact note in the PR
- Pen test payloads must be stored in `tests/fixtures/` only — never in `src/`
- Code review turnaround: 24 hours for security-critical files

**Guild Lead (Director of Intelligence Operations):**
- Daily governance queue review
- Weekly threat summary to `#announcements`
- Coordinate with Builder guild on any infra-level response actions

---

## Contributing

**Branch naming:**
```
feat/<srs-code>/<short-description>
fix/<srs-code>/<short-description>
sec/<srs-code>/<short-description>
```

**PR checklist:**
- [ ] SRS code referenced (e.g., `SRS: NEM-PENTEST-003`)
- [ ] `npm test` passes — security regression tests included
- [ ] No threshold values, scoring weights, or enforcement logic in public comments
- [ ] New NATS subjects documented in this README
- [ ] Governance event payloads validated against Supabase schema

**Commit format:** `<type>(<srs-code>): <description>`
Example: `sec(NEM-PENTEST-003): add SQL injection probe to pen test engine`

**SAKE compliance:** New threat detection modules require a `.sake` file stub.
See [guild-sdk](https://github.com/citadel-nexus/guild-sdk) for the format.

---

## Getting Started

```bash
npm install
cp .env.example .env
# Fill NATS_URL, SUPABASE_SERVICE_ROLE_KEY, NEMESIS_ADMIN_TOKEN
npm run dev
```

## Environment Variables

```
NATS_URL=nats://<your-nats-host>:4222
SUPABASE_SERVICE_ROLE_KEY=<key>
NEMESIS_ENABLED=true
NEMESIS_ADMIN_TOKEN=<token>
DD_API_KEY=<key>
GUILD_PORT=8000
```
