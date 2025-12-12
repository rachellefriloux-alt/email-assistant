# Email Assistant – Product & UI Design

AI-powered Gmail helper that fetches, categorizes, and summarizes emails with GPT-powered reply suggestions. Ships with backend (FastAPI), frontend (React + Vite + Tailwind), Docker/Helm/Kubernetes/Terraform artifacts, monitoring, CI/CD skeleton, and a sample dataset for offline testing.

## Product Goals

- Rapid triage: quickly surface important/relevant emails and flag deletion candidates.
- Safety: avoid losing sensitive/account emails; provide review-before-delete flow.
- Guidance: GPT-powered suggestions for summaries and replies.

## User Flows

1) Launch dashboard → fetch sample or live Gmail → see categorized list.
2) Switch tabs to focus (Important, Credentials, Billing, Promotions, Spam, etc.).
3) Open assistant panel → click GPT suggestion (summarize, draft reply) → view reply.
4) Toggle dark/light to match preference.
5) (Future) Mark items “Keep” vs “Delete review” and feed back to model.

## IA & Layout

- Header: product title, refresh button, dark/light toggle.
- Tabs: All + smart categories; horizontal chips for quick filtering.
- Content grid: 2/3 email list, 1/3 assistant.
- Email card: sender, subject, category pill, snippet preview.
- Assistant: suggestion chips, prompt textarea, CTA button, reply area.

## Visual System

- Typography: Inter, 16px base; weights 400/600/700.
- Palette (light):
  - Background: #F8FAFC
  - Surface: #FFFFFF
  - Text primary: #0F172A
  - Muted: #475569
  - Accent: #2563EB
  - Success: #059669
  - Warning: #F59E0B
- Palette (dark):
  - Background: #0F172A
  - Surface: #1E293B
  - Text primary: #E2E8F0
  - Muted: #94A3B8
  - Accent: #60A5FA
- Components:
  - Buttons: filled accent for primary, subtle bordered for secondary.
  - Pills: soft background + border per category; keep consistent sizes.
  - Cards: 12px radius, light shadow in light mode; subtle border in dark mode.

## Interaction & States

- Loading: skeleton or “Loading emails…” placeholder.
- Empty: “No emails to display yet.”
- Errors: inline banner near assistant reply area when GPT fails.
- Disabled: buttons dimmed while loading/processing.

## GPT Suggestions (preset chips)

- “Summarize today’s important emails”
- “Draft a polite reply to the latest billing email”
- “Mark promotional emails for deletion review”

## Accessibility

- Minimum 16px body text; 14px pills.
- Focus rings on buttons/inputs.
- Color contrast AA: accent on white (4.5:1), text on surfaces.
- Keyboard: tab through chips, prompt, and send.

## Responsive

- Mobile: stack header, tabs scroll horizontally; assistant below list.
- Desktop: grid (2/3 list, 1/3 assistant).

## Future Enhancements

- Bulk actions: select & move to “Review for deletion”.
- Feedback loop: thumbs up/down on categorization to improve model.
- Attachments preview chip and PII detection badge.
- Activity log of actions (kept/deleted/replied).

## Monitoring Dashboard (intent)

- Uptime (backend FastAPI).
- GPT latency and error rate.
- Categorization throughput.
- Alerting on downtime or 5xx spikes.

Use this document as the design reference when iterating UI and dashboards.
