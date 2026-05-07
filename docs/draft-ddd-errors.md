# Errors in a DDD application

> Draft for inclusion in `kit/docs/ddd-reference.md` (or as a sibling doc). See `docs/TODO.md` for status.

## Three categories of errors

- **Domain error** — a violation of a business rule or invariant. Belongs to the domain layer. Expressed in ubiquitous language. Examples: `OrderNotPaid`, `InsufficientStock`, `CannotCancelShippedOrder`.
- **Application error** — a use-case / orchestration concern that is not itself a business rule. Examples: `OrderNotFound`, `Unauthorized`, precondition for running the use case not met.
- **Infrastructure error** — a purely technical failure with no business meaning. Examples: I/O failure, file not found, DB timeout, deserialization error, network failure.

Test for classification: _would a domain expert recognize this concept?_ If yes → domain. If it's about running the use case → application. If it's plumbing → infrastructure.

## Scoping rule

Domain errors should be scoped per aggregate or operation (`OrderError`, `PaymentError`), not collected into a single mega-enum for the whole bounded context. This keeps the language tight and the variants meaningful.

## Travel rule

An error may move up a layer only if it is meaningful in that layer's vocabulary. Otherwise it must be translated at the boundary.

- Domain errors are meaningful at every layer (they are business language).
- Application errors are meaningful at the application and UI layers.
- Infrastructure errors are meaningful only at the infrastructure layer.

## Flow toward the UI

- **Domain error** → reaches the UI essentially as-is. It may be structurally wrapped in the outer error enum so the application boundary returns a single `Result<T, E>`, but its meaning is not transformed.
- **Application error** → goes straight to the UI. It was born at the application layer speaking the UI's language.
- **Infrastructure error** → must be translated at the application boundary. Either into a meaningful application error (e.g. `RepoError::NotFound` → `OrderNotFound`), or into an opaque variant (e.g. `Io`, `Deserialize` → generic `Infrastructure` / 500). Raw infrastructure errors never cross into the UI.

## Principles

- Lower layers do not know about upper layers. Errors flow upward and become progressively more abstract and user-appropriate.
- Infrastructure error _details_ are logged, not returned. The user-facing response stays generic ("something went wrong"); the diagnostic detail goes to the logs.
- Structural wrapping (putting a domain error inside the outer enum) is not the same as semantic translation (changing what the error means). Domain errors are wrapped, not translated. Infrastructure errors are translated.
- The dependency arrow points inward: the domain must not depend on infrastructure error types. If `FileNotFound` leaks into a domain `Result`, the domain has implicitly become coupled to a storage choice.

## Application boundary: use case vs application service

The error contract is identical whether the UI calls:

- a **use case / interactor / orchestrator** (one class per use case, Clean Architecture style), or
- an **application service** (one class grouping related use cases as methods, classical DDD style).

In both cases the application boundary:

1. Exposes `Result<T, AppError>` (or a per-operation error enum) to the UI.
2. Orchestrates domain and infrastructure.
3. Translates infrastructure errors into application errors.
4. Wraps domain errors structurally without altering their meaning.

The choice between the two is about code organization (granularity, cohesion, testability), not about how errors are modeled or propagated.

## Rust shape (illustrative)

```rust
// domain layer
pub enum OrderError {
    NotPaid,
    AlreadyShipped,
    EmptyCart,
}

// infrastructure layer
pub enum RepoError {
    NotFound,
    Io(std::io::Error),
    Deserialize(serde_json::Error),
}

// application layer — per use case, or grouped in a service
pub enum PlaceOrderError {
    Domain(OrderError),         // wrapped, not translated
    OrderNotFound,              // translated from RepoError::NotFound
    Unauthorized,               // born at this layer
    Infrastructure,             // opaque catch-all for plumbing failures
}
```

At the UI boundary, `PlaceOrderError` is mapped to the user-facing response (HTTP status, view model, CLI exit code, etc.). Domain and application variants get specific messages; the `Infrastructure` variant becomes a generic failure response, with details only in logs.
