# Error Model

Reference for handling errors in this codebase. Directive, not historical. Conceptual framing lives in [`ddd-reference.md`](ddd-reference.md) § Errors; this doc gives the how-to.

---

## Rules

1. **Repos return `anyhow::Error`.** The application layer translates to a typed enum. Domain and use-case layers never see `anyhow`.
2. **Infra failures translate to `{BC}ApplicationError::DatabaseError`** at the application layer. Unit variant — no payload on the wire. The diagnostic chain is logged server-side via `tracing::error!` at the same site as the translation.
3. **Domain errors are raised by aggregate methods on their own loaded state.** Anything else (NotFound from a repo lookup, cross-aggregate uniqueness checks, cross-BC orchestration verdicts) is an application error.
4. **Composites at the boundary, tagged leaves underneath.** Composites use `#[serde(untagged)]`; leaves use `#[serde(tag = "code")]`. Wire shape is always `{ code: "VariantName", ...payload }`.
5. **New variants go in the leaf, not the composite.** The composite reflects what its leaves expose; never re-declare leaf codes inside the composite.

---

## Decision tree

> I'm adding or changing an error path. Where does it go?

- **Raised by an aggregate method on its own loaded state?** (e.g. `Order::apply_payment` rejecting `InsufficientFunds`)
  → Domain leaf (`{bc}/domain/error.rs`).

- **Raised by a service-layer check** (NotFound from `repo.get_by_id`, uniqueness pre-check, cross-aggregate gating)?
  → Application leaf (`{bc}/application/error.rs`).

- **Raised by a use-case orchestrator** (cross-BC verdict like `InventoryUnavailable`, `OrderAlreadyShipped`)?
  → Use-case-owned application leaf (`use_cases/{name}/error.rs`).

- **Raised by an infra failure** (sqlx error, repo I/O, connection lost)?
  → Do NOT add a new variant. Translate to the relevant `{BC}ApplicationError::DatabaseError` at the call site:

  ```rust
  repo.something().await.map_err(|e| {
      tracing::error!(target: BACKEND, ..context fields.., err = ?e, "service_method: what failed");
      OrderApplicationError::DatabaseError
  })?;
  ```

- **Need a payload on the wire?**
  → Use a struct variant. Tuple variants don't survive `#[serde(tag = "code")]`.

  ```rust
  { code: "OutOfStock"; available: number; requested: number }
  ```

- **Need a new command surface that composes errors from multiple sources?**
  → New composite in the layer that owns the surface (BC for BC writes, use-case for cross-BC orchestration). Each leaf via `#[from]`.

---

## Recipes

### Leaf enum

```rust
#[derive(Debug, thiserror::Error, serde::Serialize, specta::Type, Clone)]
#[serde(tag = "code")]
pub enum OrderApplicationError {
    #[error("Order not found: {order_id}")]
    OrderNotFound { order_id: String },

    #[error("Order reference already exists")]
    ReferenceAlreadyExists,

    #[error("An unexpected database error occurred")]
    DatabaseError,
}
```

### Composite

```rust
#[derive(Debug, thiserror::Error, serde::Serialize, specta::Type)]
#[serde(untagged)]
pub enum RecordPaymentError {
    #[error(transparent)]
    Application(#[from] OrderApplicationError),
    #[error(transparent)]
    Operation(#[from] OrderOperationError),
    #[error(transparent)]
    Validation(#[from] PaymentDomainError),
}
```

### Service method signature

```rust
pub async fn record_payment(...) -> Result<Payment, RecordPaymentError> {
    let mut order = load_order(&*self.order_repo, order_id).await?;  // OrderApplicationError → ?
    let payment = Payment::new(...)?;                                 // PaymentDomainError    → ?
    let payment = order.apply_payment(payment)?;                      // OrderOperationError   → ?
    save_order(&*self.order_repo, &mut order).await?;                 // OrderApplicationError → ?
    Ok(payment)
}
```

### Tauri command boundary

The composite IS the FE-facing contract. No mapper, no boundary type:

```rust
#[tauri::command]
#[specta::specta]
pub async fn record_payment(
    uc: State<'_, RecordPaymentUseCase>,
    dto: PaymentDTO,
) -> Result<Payment, RecordPaymentError> {
    uc.record_payment(...).await
}
```

### Frontend handling

The wire shape is a flat union of every leaf's variants. Narrow on `code`:

```ts
const result = await orderGateway.recordPayment(dto);
if (result.status === "error") {
  switch (result.error.code) {
    case "OrderNotFound": // ...
    case "InsufficientFunds": // ...
    case "DatabaseError": // i18n key: error.DatabaseError
    // ...
  }
}
```

---

## Anti-patterns

- ❌ Returning `anyhow::Result<T>` from an application service method that surfaces to a Tauri command.
- ❌ Adding a `Database` / `Infrastructure` / `Unknown` variant carrying a `String` hint to the FE.
- ❌ `format!("{e:#}")` into a wire-visible payload.
- ❌ Re-declaring leaf variant codes inside a composite (e.g. flattening `OrderApplicationError`'s codes into `RecordPaymentError`).
- ❌ Putting `NotFound` in the domain layer (it's a service-layer translation of `Ok(None)`).
- ❌ Using tuple variants on a leaf (`#[serde(tag = "code")]` rejects them — use struct variants).
- ❌ Two leaves of the same composite with the same `code` discriminant under `#[serde(untagged)]` (silent collision; first arm wins in declaration order).
- ❌ A shared `InfrastructureError` (or any cross-BC wire-visible infra type) returned from a Tauri command, included in any composite, or Specta-derived. Per-BC translation is the rule.
- ❌ `panic!` / `unwrap` / `expect` in production paths. Tests only.
- ❌ Documenting per-leaf variants in the composite's docstring (rots the moment a leaf changes — point at the leaf type instead).
- ❌ Comments like `// Replaces the anyhow-era X` or `// Per the Y rule` (rationale-as-comment; doc what the code IS, not what it used to be).

---

## Where things live

| What                                     | Where                                                                        |
| ---------------------------------------- | ---------------------------------------------------------------------------- |
| Per-BC application leaves                | `src-tauri/src/context/{bc}/application/error.rs`                            |
| Per-BC domain leaves                     | `src-tauri/src/context/{bc}/domain/` (each aggregate has its own error type) |
| Use-case composites and leaves           | `src-tauri/src/use_cases/{name}/error.rs`                                    |
| All composites + leaves on the FE wire   | `src/bindings.ts` (auto-generated; do not edit)                              |
| Per-command reachable code surface       | `docs/contracts/{domain}-contract.md`                                        |
| Layering rules (domain vs application)   | [`docs/ddd-reference.md`](ddd-reference.md) § Errors                         |
| Backend coding rules (B31 in particular) | [`docs/backend-rules.md`](backend-rules.md)                                  |
