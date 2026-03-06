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
Subscribes to 5 NATS subjects, scores risk, enforces:
- Risk ≥ 0.85 + nemesis threat → **IP quarantine**
- Risk ≥ 0.80 + payment event → **payment hold**
- Risk ≥ 0.65 → **Slack/Discord alert**

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
