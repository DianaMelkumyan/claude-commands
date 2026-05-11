# Visual relevance keyword reference

Used by `/market-research` Phase 1 to infer the brief.md `visual_relevance` field.
The main command does a case-insensitive substring match of the topic + (for Branch A/B) the PRD scope text against the keyword sets below.

## High
> UX, UI, design, layout, mockup, wireframe, prototype, redemption, cart, checkout, picker, modal, popup, sheet, drawer, overlay, toast, banner, carousel, tile, card, badge, button, label, icon, avatar, screen, view, tab, nav, navigation, header, footer, sidebar, onboarding, signup, login, profile, home, landing, splash, settings page, empty state, error state, success state, loading state, hero, gallery, list view, grid view, accordion, dropdown, form, input, gesture, swipe, tap, scroll, animation, transition, theme, branding, color, typography, hierarchy, density, responsive, mobile app, web ordering

## Medium
> dashboard, admin, configuration, builder, editor, composer, preview, report, analytics view, chart, table view, filter panel, settings panel, permissions screen, audit log, inbox, queue, calendar view, kanban, timeline view

## Low
> export, import, integration, API, endpoint, schema, payload, rule, criteria, automation, trigger, webhook, sync, ingestion, pipeline, scoring, model, segmentation logic, pricing tier, plan comparison, contract terms, billing logic, permissions matrix, RBAC, data residency, retention policy, latency, throughput, SLA, deduplication, normalization

## Mixed signals
When the topic hits keywords across multiple tiers, default to **medium**. The user can override at the checkpoint.
