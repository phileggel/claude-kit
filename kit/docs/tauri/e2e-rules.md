# E2E Testability Rules

Defines what makes a component reliably driveable from the Tauri WebDriver E2E suite.
Read together with `docs/frontend-rules.md` and `docs/testing.md`.

⚠️ **AI AGENT MUST NEVER UPDATE THIS DOCUMENT**

---

## E1 — Forms MUST have a stable `id` attribute

```tsx
<form id="price-modal-form" ...>
```

E2E tests locate forms by `id` — the most stable selector.
Naming convention: `{feature}-{action}-form` (e.g. `price-modal-form`, `edit-price-form`).

## E2 — Form fields MUST have a stable `id` attribute

```tsx
<input id="price-modal-date" ... />
<input id="price-modal-price" ... />
```

Convention: `{form-prefix}-{field}` (e.g. `price-modal-date`, `edit-price-price`).
The `id` MUST be forwarded to the underlying DOM `<input>` — never stop at the wrapper component.

## E3 — Submit buttons MUST use `type="submit"` and `form="{form-id}"`

```tsx
<Button
  type="submit"
  form="price-modal-form"
  disabled={isSubmitting || !isFormValid}
>
  Save
</Button>
```

E2E selector: `button[type="submit"][form="price-modal-form"]`.
Never rely on an `onClick`-only submit path — there is no stable selector for it.

## E4 — Navigation and action buttons MUST have a stable `aria-label` from i18n

```tsx
<IconButton aria-label={t("account_details.action_enter_price")} ... />
```

E2E selector: `button[aria-label="Enter price"]`.
Always use `t()` — never hardcode strings. Verify the exact English value in `en/common.json`.

## E5 — Error messages MUST have `role="alert"`

```tsx
<p role="alert" className="...">
  {t(error)}
</p>
```

E2E selector: `[role="alert"]` scoped to the form.
This is already required by accessibility rules — it is also what E2E tests assert.

## E6 — React controlled inputs require `setReactInputValue` in E2E tests

Standard `setValue()` from WebdriverIO does **not** reliably trigger React's synthetic
`onChange` in WebKitGTK. The DOM value is set but React state never updates, so
`isFormValid` stays `false` and the submit button stays disabled.

Use this helper in every E2E test file that sets input values:

```typescript
async function setReactInputValue(
  elementId: string,
  value: string,
): Promise<void> {
  await browser.execute(
    (id, val) => {
      const el = document.getElementById(id) as HTMLInputElement | null;
      if (!el) return;
      // Bypass React's value tracker via the native prototype setter, then
      // dispatch native events that React's delegation converts to synthetic onChange.
      const nativeSetter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype,
        "value",
      )?.set;
      nativeSetter?.call(el, val);
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    },
    elementId,
    value,
  );
}
```

After calling `setReactInputValue`, React re-renders synchronously within the same
event-loop tick. The next `waitForEnabled` poll will see the updated disabled state.

## E7 — Custom date pickers require locale-formatted input

`DateField` renders `<input type="text">` and displays dates in the component locale
(default `fr-FR` → `DD/MM/YYYY`). `setReactInputValue` must receive the display format,
not ISO:

```typescript
// Convert ISO to the DateField display format (fr-FR locale)
function isoToDisplayDate(iso: string): string {
  const [year, month, day] = iso.split("-");
  return `${day}/${month}/${year}`; // "2020-01-15" → "15/01/2020"
}

await setReactInputValue("price-modal-date", isoToDisplayDate("2020-01-15"));
```

`DateField.handleInputChange` then parses the display value back to ISO and calls
the parent `onChange` with the ISO date — React state updates correctly.

## E8 — Tests MUST NOT call `browser.url()`

The Tauri WebView uses a custom protocol (`tauri://` or `http://tauri.localhost/`)
and is already loaded at the app's initial route when the session starts.
`browser.url()` breaks the WebView — navigate only through UI clicks.

## E9 — Tests MUST use deterministic, unique values per write operation

Use fixed past dates (not today's date) to avoid `DuplicateDate` errors from prior runs:

```typescript
// One constant per test that writes data — never share dates between seeding ops.
const DATES = {
  record: "15/01/2020", // locale format for DateField
  update_original: "10/02/2020",
  delete: "05/03/2020",
} as const;
```

Today's date is pre-filled by default; always override it with a fixed past date.

## E10 — `waitForEnabled` / `waitForExist` MUST always specify `{ timeout: N }`

```typescript
await submitBtn.waitForEnabled({ timeout: 5000 });
await modal.waitForExist({ timeout: 8000, reverse: true });
```

Never rely on the WebdriverIO default timeout — always be explicit.
