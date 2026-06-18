<!--
  Forge — conventions catalog (the curated seed library).

  This file is NOT copied into a project. It is the *source library* the
  conventions skills propose FROM: `/forge-init` reads it during the interview
  and `/forge-add-convention` lets a developer pick an entry to record into a
  project's `docs/requirements/conventions.md`.

  Every entry below is a CROSS-CUTTING ENGINEERING/UX DEFAULT — the kind of thing
  neither the developer nor an AI should have to remember from scratch on every
  feature (pagination, virtualization, async UI states, authz on every action,
  …). Forge curates them so they can be RECALLED (proposed at init) and ENFORCED
  (injected into feature prompts + checked by the reviewer).

  Each entry is a stack-neutral INTENT, never a tool/library/framework. The
  default parameter VALUES are starting points a project can edit; the RULE
  itself does not name a stack. The "relevant for" tag scopes which kinds of
  project an entry usually matters to (UI / API / CLI / data-heavy / any) so the
  interview proposes a sensible subset, not the whole library.

  ID prefix: EC (Engineering Convention). The suggested ids here (EC-C1, EC-F1,
  …) are stable handles for *reference inside this catalog*; a project renumbers
  to sequential EC-01, EC-02, … as it records them (see conventions.template.md).
-->

# Forge — conventions catalog (`EC-` seed library)

> The curated library of **cross-cutting engineering & UX conventions** that
> Forge proposes from. It exists so neither the developer nor the agent has to
> remember these defaults on every feature. The genesis interview
> ([`/forge-init`](../.claude/skills/forge-init/SKILL.md)) detects the project
> type and proposes the relevant entries (with their default thresholds) into
> `docs/requirements/conventions.md`; [`/forge-add-convention`](../.claude/commands/forge-add-convention.md)
> records more later.
>
> Every rule is a **stack-neutral intent**, parameterized by named thresholds
> with editable defaults. Nothing here names a language, framework, datastore, or
> UI toolkit — a project's stack lives only in
> [`forge.config.json`](../forge.config.json).

## How to read an entry

| Field            | Meaning                                                                                  |
| ---------------- | ---------------------------------------------------------------------------------------- |
| **Suggested id** | Stable handle *within this catalog* (`EC-C1`, …). A project renumbers to sequential `EC-01`. |
| **Rule (intent)**| The cross-cutting default, phrased as a stack-neutral intent — *what*, never *with what*. |
| **Applies to**   | The trigger scope: the kind of work that makes this convention relevant (the reviewer and feature prompts match against this). |
| **Parameters**   | Named thresholds with **default values** a project may edit. Defaults are starting points, not law. |
| **Relevant for** | Project types the entry usually matters to: `UI` · `API` · `CLI` · `data-heavy` · `any`. The interview proposes a subset from these. |
| **Rationale**    | Why it is a default worth honoring.                                                      |

> A recorded project entry also carries **Status** (`active` · `proposed` ·
> `waived + reason`); in this catalog every entry is a candidate — the project
> decides its status when recording it.

---

## (a) Collections, lists & tables

### EC-C1 — Paginate or window every unbounded collection

- **Rule (intent):** Never render or return an unbounded list. Any view or
  response over a collection that can grow is paginated (or virtualized/windowed
  when shown as one continuous scroll), so cost stays bounded regardless of total
  size.
- **Applies to:** any screen, endpoint, export, or command that lists items from
  a collection that can exceed the page threshold.
- **Parameters:** `defaultPageSize = 25`; `maxPageSize = 100`;
  `windowThreshold = 100` (rows beyond which a long list is virtualized rather
  than fully rendered).
- **Relevant for:** UI, API, data-heavy.
- **Rationale:** unbounded lists are the most common cause of slow pages, huge
  payloads, and memory blow-ups; bounding them is cheap insurance.

### EC-C2 — Virtualize long rendered lists

- **Rule (intent):** When a list of more than the window threshold is shown as a
  single scroll, render only the visible window (plus a small overscan) instead
  of every row, keeping scroll smooth and memory flat.
- **Applies to:** any long, continuously scrolling list/table/grid in a rendered
  surface.
- **Parameters:** `windowThreshold = 100`; `overscanRows = 5`.
- **Relevant for:** UI, data-heavy.
- **Rationale:** rendering thousands of rows janks the UI and bloats memory;
  windowing keeps cost proportional to what is on screen.

### EC-C3 — Sort and filter on the server for large collections

- **Rule (intent):** For collections larger than a page, sorting and filtering
  are applied at the source (server/query) over the whole set, not in-memory over
  one already-fetched page — so results are correct, not just the current page
  reordered.
- **Applies to:** any sortable/filterable list backed by a collection bigger than
  one page.
- **Parameters:** `serverSideThreshold = 1` page (i.e. as soon as the data is
  paginated).
- **Relevant for:** UI, API, data-heavy.
- **Rationale:** client-side sort/filter over a single page silently lies about
  the full dataset.

### EC-C4 — Stable identity keys for list items

- **Rule (intent):** Each item in a rendered or diffed list is keyed by a stable
  domain identifier, never by array index or position, so reorder/insert/delete
  preserve item identity and state.
- **Applies to:** any list/table that is re-rendered, reordered, or incrementally
  updated.
- **Parameters:** none.
- **Relevant for:** UI.
- **Rationale:** index keys cause wrong-row state, lost focus, and subtle
  update bugs when the collection changes.

---

## (b) Forms & inputs

### EC-F1 — Validate on the client and re-validate on the server

- **Rule (intent):** Every input is validated for fast feedback near the user
  **and** re-validated authoritatively at the trust boundary before it is
  accepted; the server never trusts client-side validation alone.
- **Applies to:** any form, command argument, or request body that accepts user
  input.
- **Parameters:** none.
- **Relevant for:** UI, API, CLI.
- **Rationale:** client validation is UX; server validation is correctness and
  security — both are required, neither replaces the other.

### EC-F2 — Dependent selects load and reset from their parent

- **Rule (intent):** When one selection scopes another, the dependent options are
  (re)loaded for the current parent value and the dependent selection is cleared
  when the parent changes, so a stale or impossible combination cannot be
  submitted.
- **Applies to:** any form with cascading/dependent choices (a child field whose
  valid options depend on a parent field).
- **Parameters:** none.
- **Relevant for:** UI.
- **Rationale:** dependent fields left unsynced are a classic source of invalid
  submissions and confusing UX.

### EC-F3 — Async option loading is searchable and debounced

- **Rule (intent):** A selector whose options come from a large or remote set
  loads them asynchronously, is searchable/typeable, debounces the lookup, shows
  loading and empty states, and caps the number of options fetched per query.
- **Applies to:** any select/autocomplete/combobox backed by a large or
  server-provided option set.
- **Parameters:** `debounceMs = 300`; `minQueryLength = 1`;
  `maxOptionsPerFetch = 50`.
- **Relevant for:** UI.
- **Rationale:** eagerly loading every option is slow and unscalable; a debounced
  searchable fetch stays responsive at any catalog size.

### EC-F4 — Guard against losing unsaved changes

- **Rule (intent):** When a form has unsaved edits, navigating or closing away
  prompts for confirmation (or otherwise preserves the work) so a user does not
  silently lose input.
- **Applies to:** any non-trivial form or editor where leaving would discard
  in-progress input.
- **Parameters:** none.
- **Relevant for:** UI.
- **Rationale:** silent data loss on accidental navigation is a high-frustration,
  easily-avoided failure.

### EC-F5 — Disable on submit and make mutations idempotent

- **Rule (intent):** Submitting disables the trigger until the operation
  resolves, and the underlying mutation is safe to retry without creating
  duplicates (a deduplication/idempotency key or a natural uniqueness guard).
- **Applies to:** any action that mutates state on submit (create/update/charge/
  send).
- **Parameters:** `idempotencyKeyTtl = 24h`.
- **Relevant for:** UI, API, CLI.
- **Rationale:** double-clicks and retries otherwise create duplicate records,
  double charges, or repeated side effects.

---

## (c) Data fetching & async

### EC-D1 — Pagination contract for collection endpoints

- **Rule (intent):** Endpoints that return a collection expose a pagination
  contract (cursor- or offset-based) with a bounded default and maximum page
  size, and never return the whole collection at once.
- **Applies to:** any read endpoint or query that returns a collection.
- **Parameters:** `defaultPageSize = 25`; `maxPageSize = 100`;
  `paginationStyle = cursor-preferred` (offset acceptable for small, stable
  sets).
- **Relevant for:** API, data-heavy.
- **Rationale:** an unpaginated collection endpoint is an unbounded payload and a
  latent outage.

### EC-D2 — Cache reads with stale-while-revalidate

- **Rule (intent):** Repeated reads of the same data are cached and served while
  a background refresh revalidates them, with explicit invalidation on the
  mutations that affect them, so the UI is fast without going stale silently.
- **Applies to:** any read that is fetched repeatedly or shared across views.
- **Parameters:** `staleTimeMs = 30000`; `cacheTtlMs = 300000`.
- **Relevant for:** UI, API, data-heavy.
- **Rationale:** refetching unchanged data on every view is wasteful; serving
  stale forever is wrong — SWR balances both.

### EC-D3 — Cancel superseded or abandoned requests

- **Rule (intent):** In-flight requests that have been superseded (a newer query,
  a navigation away) are cancelled, and their late responses are ignored, so a
  slow earlier response cannot overwrite a newer one.
- **Applies to:** any rapidly-changing fetch (search-as-you-type, switching
  tabs/filters, leaving a screen).
- **Parameters:** none.
- **Relevant for:** UI, API.
- **Rationale:** out-of-order responses cause flicker and show wrong data for the
  current state.

### EC-D4 — Retry transient failures with backoff

- **Rule (intent):** Transient failures (timeouts, throttling, transient network
  errors) are retried a bounded number of times with exponential backoff and
  jitter; non-idempotent operations are retried only when made idempotent.
- **Applies to:** any outbound call that can fail transiently.
- **Parameters:** `maxRetries = 3`; `baseBackoffMs = 200`;
  `backoffMultiplier = 2`; `jitter = true`.
- **Relevant for:** API, CLI, data-heavy.
- **Rationale:** blind immediate retries amplify outages; bounded backoff
  recovers from blips without stampeding.

### EC-D5 — Respect rate limits

- **Rule (intent):** Callers honor a dependency's rate-limit signals (throttle,
  queue, or back off on a limit response) and never hammer past a known quota;
  providers advertise their limits.
- **Applies to:** any integration with a rate-limited dependency, and any
  endpoint that needs protection.
- **Parameters:** `respectRetryAfter = true`; `clientMaxConcurrent = 8`.
- **Relevant for:** API, data-heavy.
- **Rationale:** ignoring rate limits gets the client throttled or banned and
  degrades everyone.

### EC-D6 — Avoid N+1 access patterns

- **Rule (intent):** Loading a list and its related data does not issue one
  lookup per row; related data is batched, joined, or pre-loaded so cost does not
  scale with row count.
- **Applies to:** any code that loads a collection together with per-item related
  data.
- **Parameters:** none.
- **Relevant for:** API, data-heavy.
- **Rationale:** N+1 access is the most common silent performance cliff as data
  grows.

### EC-D7 — Optimistic mutations reconcile and roll back

- **Rule (intent):** When a mutation changes data that is already shown from a
  cache (an inline edit, a list-row action, a toggle, a reassignment), apply the
  change optimistically, reconcile against the server outcome on settle
  (invalidate/refetch the affected query), and **roll back to the pre-mutation
  snapshot with a user-visible message if it fails** — so the view never strands a
  stale or phantom value after a failed or concurrent write.
- **Applies to:** any mutation whose effect is reflected in already-fetched or
  cached data shown to the user.
- **Parameters:** `reconcileOn = settle` (invalidate/refetch on success and
  error); `rollbackOnError = true`.
- **Relevant for:** UI, data-heavy.
- **Rationale:** optimistic updates make the UI feel instant, but without
  reconciliation and rollback a failed or concurrent write leaves the user acting
  on data that was never persisted. Pairs with EC-D2 (cache invalidation) and
  EC-F5 (idempotency); distinct from EC-A3, which covers *fetch* errors, not
  *write* reconciliation.

---

## (d) Async UI states

### EC-A1 — Explicit loading state without layout shift

- **Rule (intent):** Every asynchronous region shows a loading affordance
  (skeleton/placeholder) that reserves the final layout, so content appears
  without the surrounding UI jumping.
- **Applies to:** any region whose content is fetched asynchronously.
- **Parameters:** `skeletonForLoadsOverMs = 200` (below this, avoid a flash by
  showing nothing or a subtle indicator).
- **Relevant for:** UI.
- **Rationale:** blank-then-pop and shifting layouts read as broken and hurt
  perceived performance.

### EC-A2 — Explicit empty state

- **Rule (intent):** A successful result with no data renders a deliberate empty
  state (what it means and the next action), never a blank area or a spinner that
  never resolves.
- **Applies to:** any list/section that can legitimately return nothing.
- **Parameters:** none.
- **Relevant for:** UI, CLI.
- **Rationale:** "no data" and "still loading" must be distinguishable; a blank
  screen tells the user nothing.

### EC-A3 — Explicit error state with retry

- **Rule (intent):** A failed async operation renders a clear, human error state
  with a way to retry or recover, and never leaves the user stuck on a spinner or
  a silent blank.
- **Applies to:** any async operation that can fail.
- **Parameters:** none.
- **Relevant for:** UI, CLI.
- **Rationale:** unhandled failures that look like infinite loading are
  indistinguishable from a hang and erode trust.

---

## (e) Performance & rendering

### EC-P1 — Memoize expensive derived work

- **Rule (intent):** Expensive computations and re-renders are memoized/cached on
  their inputs so they recompute only when inputs change, not on every cycle.
- **Applies to:** any hot path with expensive derivation or frequent re-render.
- **Parameters:** none.
- **Relevant for:** UI, data-heavy.
- **Rationale:** recomputing the same result every cycle is a silent, compounding
  cost.

### EC-P2 — Debounce/throttle high-frequency events

- **Rule (intent):** High-frequency triggers (typing, scrolling, resizing,
  dragging) debounce or throttle the work they cause, so handlers do not fire on
  every raw event.
- **Applies to:** any handler bound to a high-frequency input/event.
- **Parameters:** `searchDebounceMs = 300`; `scrollThrottleMs = 100`;
  `resizeThrottleMs = 100`.
- **Relevant for:** UI.
- **Rationale:** unthrottled handlers flood the system with redundant work and
  requests.

### EC-P3 — Lazy-load and split heavy or below-the-fold work

- **Rule (intent):** Heavy or rarely-used code, assets, and data are loaded on
  demand (code-split, lazy-loaded, deferred) rather than all upfront, keeping the
  initial load small.
- **Applies to:** any heavy module, route, asset, or below-the-fold content.
- **Parameters:** none.
- **Relevant for:** UI.
- **Rationale:** front-loading everything makes the first interaction slow for
  features the user may never reach.

### EC-P4 — Bound every payload

- **Rule (intent):** Requests and responses carry only the fields and rows
  actually needed (selected fields, paginated rows, capped depth), never an
  entire object graph by default.
- **Applies to:** any request/response or query that could over-fetch.
- **Parameters:** `maxResponseRows = 100`; `maxExpansionDepth = 3`.
- **Relevant for:** API, data-heavy.
- **Rationale:** over-fetching wastes bandwidth, memory, and time, and couples
  clients to fields they do not use.

---

## (f) Navigation & routing

### EC-N1 — Reflect list state in the URL

- **Rule (intent):** Filters, sort, search, pagination, and the active tab are
  encoded in the URL/route so a view is shareable, bookmarkable, and survives a
  reload with the same state.
- **Applies to:** any list/search/filtered view in a navigable surface.
- **Parameters:** none.
- **Relevant for:** UI.
- **Rationale:** state trapped in memory cannot be shared, linked, or restored
  after reload.

### EC-N2 — Preserve scroll and view state across navigation

- **Rule (intent):** Returning to a previously visited list restores its scroll
  position and view state instead of resetting to the top, so back-navigation
  does not lose the user's place.
- **Applies to:** any navigation that returns to a previously scrolled view.
- **Parameters:** none.
- **Relevant for:** UI.
- **Rationale:** losing scroll position on back is a common, avoidable
  frustration in list-heavy apps.

---

## (g) Accessibility

### EC-Y1 — Full keyboard operability

- **Rule (intent):** Every interactive control is reachable and operable by
  keyboard alone, in a logical order, with a visible focus indicator and no
  keyboard traps.
- **Applies to:** any interactive UI control or surface.
- **Parameters:** none.
- **Relevant for:** UI.
- **Rationale:** keyboard operability is both an accessibility baseline and the
  foundation for power-user and assistive-tech use.

### EC-Y2 — Manage focus on dynamic UI

- **Rule (intent):** Opening, closing, and updating dynamic surfaces (dialogs,
  menus, async content) moves focus deliberately and returns it on close, so
  keyboard and screen-reader users are never stranded.
- **Applies to:** any modal, popover, drawer, or dynamically inserted region.
- **Parameters:** none.
- **Relevant for:** UI.
- **Rationale:** unmanaged focus leaves assistive-tech users lost when the UI
  changes under them.

### EC-Y3 — Accessible names, roles, and structure

- **Rule (intent):** Every control and region exposes an accessible name and the
  correct role/semantics (labels, headings, landmarks, state) so assistive
  technology can convey it.
- **Applies to:** any control, form field, icon-only button, or structural
  region.
- **Parameters:** none.
- **Relevant for:** UI.
- **Rationale:** without names and roles, assistive tech announces nothing
  meaningful.

### EC-Y4 — Sufficient contrast and respect reduced motion

- **Rule (intent):** Text and meaningful UI meet a minimum contrast ratio, color
  is never the sole carrier of meaning, and non-essential motion is reduced when
  the user requests it.
- **Applies to:** any visual styling, color coding, or animation.
- **Parameters:** `minContrastNormalText = 4.5:1`; `minContrastLargeText =
  3:1`; `honorReducedMotion = true`.
- **Relevant for:** UI.
- **Rationale:** low contrast, color-only meaning, and forced motion exclude or
  harm real users.

---

## (h) Security & authorization

### EC-S1 — Authorize every action server-side, not by hiding UI

- **Rule (intent):** Every action and data access is authorized at the trust
  boundary on each request; hiding or disabling a control in the UI is a
  convenience, never the access control.
- **Applies to:** any action, endpoint, or data access that is permission-gated.
- **Parameters:** none.
- **Relevant for:** UI, API, CLI, data-heavy.
- **Rationale:** UI-only gating is trivially bypassed; authorization must live
  where the action actually happens.

### EC-S2 — Validate and sanitize all untrusted input

- **Rule (intent):** Input crossing a trust boundary is validated against an
  allowlist of shape/type/range and is safely handled at every sink (storage,
  query, markup, shell, downstream call) to prevent injection.
- **Applies to:** any untrusted input that reaches a query, template, command, or
  downstream system.
- **Parameters:** none.
- **Relevant for:** UI, API, CLI, data-heavy.
- **Rationale:** unvalidated input is the root of injection and corruption
  classes of bugs.

### EC-S3 — Deny by default

- **Rule (intent):** Access, capabilities, and exposure default to denied/closed;
  anything permitted is explicitly granted, so a forgotten check fails safe.
- **Applies to:** any authorization rule, feature flag, or exposure decision.
- **Parameters:** none.
- **Relevant for:** API, CLI, data-heavy, UI.
- **Rationale:** deny-by-default turns an omission into a closed door instead of
  an open one.

### EC-S4 — No secrets on the client or in the repo

- **Rule (intent):** Secrets and credentials live only in server-side
  configuration/secret storage, never in client-delivered code, version control,
  or logs; privileged calls happen server-side.
- **Applies to:** any credential, token, key, or other secret.
- **Parameters:** none.
- **Relevant for:** UI, API, CLI, data-heavy.
- **Rationale:** a secret shipped to the client or committed to the repo is a
  secret already leaked.

---

## (i) Internationalization & formatting

### EC-I1 — No hardcoded user-facing strings

- **Rule (intent):** User-facing text comes from a message catalog/resource, not
  inline literals, so copy can change and (if ever needed) be localized without
  touching logic.
- **Applies to:** any user-facing text in UI or output.
- **Parameters:** none.
- **Relevant for:** UI, CLI.
- **Rationale:** inline strings make copy changes risky and localization
  impossible without a rewrite.

### EC-I2 — Locale-aware dates, numbers, and currency

- **Rule (intent):** Dates, numbers, and currency are formatted through
  locale-aware formatting using the user's locale, never hand-assembled or
  hardcoded to one region's conventions.
- **Applies to:** any rendering or output of a date, number, or monetary value.
- **Parameters:** none.
- **Relevant for:** UI, CLI, API.
- **Rationale:** hand-formatted dates/numbers are wrong for half the world and
  break as soon as the audience widens.

### EC-I3 — Store time in UTC, present in the user's timezone

- **Rule (intent):** Instants are stored and transmitted in an unambiguous
  absolute form (UTC) and converted to the user's timezone only for display, so
  comparisons and storage stay correct across zones and DST.
- **Applies to:** any timestamp that is stored, compared, or displayed.
- **Parameters:** `storageTimezone = UTC`.
- **Relevant for:** API, data-heavy, UI.
- **Rationale:** mixing local times in storage produces off-by-hours and DST bugs
  that are painful to unwind later.

---

## (j) Observability & resilience

### EC-O1 — Structured, context-rich logging without sensitive data

- **Rule (intent):** Significant operations log in a structured form with a
  correlation/request identifier and enough context to debug, while redacting
  secrets and sensitive personal data.
- **Applies to:** any meaningful operation, boundary call, or error path.
- **Parameters:** `logLevelDefault = info`; `redactSensitiveFields = true`.
- **Relevant for:** API, CLI, data-heavy, UI.
- **Rationale:** unstructured or context-free logs are unsearchable when it
  matters; logging secrets turns an incident into a breach.

### EC-O2 — Report and surface errors

- **Rule (intent):** Unexpected errors are captured and reported to an error
  channel with enough context to diagnose, instead of being swallowed silently.
- **Applies to:** any catch boundary or unexpected-failure path.
- **Parameters:** none.
- **Relevant for:** UI, API, CLI, data-heavy.
- **Rationale:** swallowed errors are invisible failures that surface as
  mysterious user reports much later.

### EC-O3 — Idempotency keys for at-least-once operations

- **Rule (intent):** Operations that may be delivered or retried more than once
  carry an idempotency key (or a natural dedup guard) so repeats produce one
  effect, not many.
- **Applies to:** any operation that can be retried, replayed, or redelivered
  (payments, sends, webhooks, queue consumers).
- **Parameters:** `idempotencyKeyTtl = 24h`.
- **Relevant for:** API, data-heavy.
- **Rationale:** at-least-once delivery without idempotency means duplicate
  charges, emails, and records.

### EC-O4 — Timeouts on every outbound call

- **Rule (intent):** Every call that can block (network, I/O, downstream
  dependency) has an explicit, bounded timeout; nothing waits indefinitely.
- **Applies to:** any outbound or blocking call.
- **Parameters:** `defaultTimeoutMs = 10000`.
- **Relevant for:** API, CLI, data-heavy, UI.
- **Rationale:** a missing timeout turns one slow dependency into a cascading
  hang that exhausts resources.

### EC-O5 — Degrade gracefully when a dependency fails

- **Rule (intent):** A non-critical dependency failing degrades the affected
  feature gracefully (fallback, cached value, partial result, clear message)
  instead of taking down the whole surface.
- **Applies to:** any feature that depends on a non-critical external or optional
  dependency.
- **Parameters:** none.
- **Relevant for:** UI, API, data-heavy.
- **Rationale:** one optional dependency should never be a single point of total
  failure.

---

## Using this catalog

- **At genesis** ([`/forge-init`](../.claude/skills/forge-init/SKILL.md)): the
  interview infers the project type (UI / API / CLI / data-heavy), proposes the
  entries whose **Relevant for** matches with their default parameters, and lets
  the developer confirm, adjust thresholds, add custom ones, or waive. Confirmed
  entries are written to `docs/requirements/conventions.md` as sequential
  `EC-01`, `EC-02`, … (see
  [`requirements/conventions.template.md`](requirements/conventions.template.md)).
- **Later** ([`/forge-add-convention`](../.claude/commands/forge-add-convention.md)):
  pick another entry from here (or define a custom one) to append to the project
  map. Agents that notice a recurring concern while building **propose** an entry
  through this same command; the developer approves.
- **Enforcement** is two-toothed and lives elsewhere: applicable `EC-` rules are
  injected into every feature-building prompt's context (the prompt reads
  `docs/requirements/conventions.md` and applies the matching entries), and the
  [`reviewer`](../.claude/agents/reviewer.md) subagent checks them as a dedicated
  dimension. This catalog is only the **source library** — it is not itself a
  gate.
