# CoinPurse UI Restructure Implementation Plan

## Overview
Restructure the frontend to have a dashboard-focused main page showing account balances, with detailed management moved to an admin section.

## Changes Summary
1. Create new `/dashboard` route with account overview and balances
2. Create new `/admin` route with tabbed interface for Institutions and Accounts management
3. Implement full CRUD for Accounts (similar to Institutions pattern)
4. Add Select component from shadcn-svelte for dropdowns
5. Update navigation to include Dashboard and Admin

---

## File Structure Changes

### New Files to Create

#### Dashboard Page
- `src/pages/dashboard.svelte` - Main dashboard page
- `src/pages/dashboard/account-balance-card.svelte` - Card showing individual account balance
- `src/pages/dashboard/balance-chart-placeholder.svelte` - Placeholder for future charts

#### Admin Page
- `src/pages/admin.svelte` - Admin page with tabs
- `src/pages/admin/institutions-tab.svelte` - Institutions management (reuse existing logic)
- `src/pages/admin/accounts-tab.svelte` - Accounts management grid

#### Accounts Components (following institutions pattern)
- `src/pages/accounts/` - New folder
- `src/pages/accounts/columns.ts` - Table column definitions
- `src/pages/accounts/accounts-data-table.svelte` - Reusable table component
- `src/pages/accounts/add-edit-account-dialog.svelte` - Create/Edit modal
- `src/pages/accounts/delete-account-dialog.svelte` - Delete confirmation
- `src/pages/accounts/accounts-table-actions.svelte` - Inline action buttons

#### Shared Components
- `src/lib/components/ui/select/` - Add Select component from shadcn-svelte
- `src/lib/components/ui/tabs/` - Add Tabs component from shadcn-svelte (for admin page)

### Files to Modify
- `src/lib/routes.ts` - Add `/dashboard` and `/admin` routes
- `src/lib/layout.svelte` - Add Dashboard and Admin to sidebar navigation
- `src/pages/accounts.svelte` - Keep as placeholder or redirect to /admin?accounts tab

---

## Implementation Steps

### Step 1: Add Required UI Components
**Add shadcn-svelte components:**
1. Add Select component (needed for institution picker, account type picker)
2. Add Tabs component (needed for admin page)

**Files:**
- `src/lib/components/ui/select/` - Install via shadcn-svelte CLI or copy from docs
- `src/lib/components/ui/tabs/` - Install via shadcn-svelte CLI or copy from docs

### Step 2: Create Dashboard Page Structure
**Create basic dashboard page with account fetching:**

**File: `src/pages/dashboard.svelte`**
- Fetch all active accounts via `api.accounts.getAll(false)`
- Fetch all account balances via `api.accountBalances.getAll()`
- Match latest balance to each account
- Display accounts in grid of cards
- Add "Add Account" and "Add Institution" buttons that open modals
- Import and reuse `add-edit-account-dialog.svelte` and `add-edit-institution-dialog.svelte`

**File: `src/pages/dashboard/account-balance-card.svelte`**
- Props: `account`, `latestBalance`
- Display account name, institution name, account type
- Display balance prominently (large font, formatted as currency)
- Display "No data" if no balance exists
- Show last updated date if balance exists
- Maybe add quick action buttons (edit, add balance)

**File: `src/pages/dashboard/balance-chart-placeholder.svelte`**
- Simple card with text "Balance history chart - coming soon"
- Include commented-out structure for future chart implementation
- Props: `accountId` for when charts are implemented

### Step 3: Implement Accounts CRUD Components
**Follow institutions page pattern exactly:**

**File: `src/pages/accounts/columns.ts`**
- Define columns: Account Name, Institution, Type, Subtype, Last 4, Tracks Txns, Tracks Bal, Status, Created, Actions
- Use renderComponent for actions column
- Need to join institution name (will pass full data with institution info)

**File: `src/pages/accounts/accounts-data-table.svelte`**
- Copy from institutions-data-table.svelte
- Adapt for account columns
- Same patterns: pinning, inactive styling, empty states

**File: `src/pages/accounts/add-edit-account-dialog.svelte`**
- More complex form than institutions
- Fields:
  - Account Name (text input, required)
  - Institution (Select dropdown, required) - fetch institutions on mount
  - Account Type (Select dropdown, required) - from AccountType enum
  - Account Subtype (text input, optional)
  - Last 4 Digits (text input, optional, max 4 chars)
  - Tracks Transactions (checkbox)
  - Tracks Balances (checkbox)
  - Display Order (number input)
- Validation: required fields, last_4_digits max length
- State management: form fields, errors, loading
- API calls: fetch institutions for dropdown, create/update account

**File: `src/pages/accounts/delete-account-dialog.svelte`**
- Copy from delete-institution-dialog.svelte
- Adapt messaging for accounts
- Explain soft delete (sets active = false)

**File: `src/pages/accounts/accounts-table-actions.svelte`**
- Copy from institutions-table-actions.svelte
- Edit and Delete buttons
- Disable for inactive accounts

### Step 4: Create Admin Page with Tabs
**File: `src/pages/admin.svelte`**
- Import Tabs components
- Two tabs: "Institutions" and "Accounts"
- Each tab loads respective tab component
- Simple layout with tabs at top

**File: `src/pages/admin/institutions-tab.svelte`**
- Extract logic from current `src/pages/institutions.svelte`
- Keep all existing functionality: search, filters, table, modals
- This becomes the content for the Institutions tab

**File: `src/pages/admin/accounts-tab.svelte`**
- Similar to institutions-tab but for accounts
- Fetch accounts with institutions joined (need institution names for display)
- Search, filters (include inactive)
- Accounts data table with modals
- Create account button

### Step 5: Update Routing and Navigation
**File: `src/lib/routes.ts`**
- Add `/dashboard` route pointing to dashboard.svelte
- Add `/admin` route pointing to admin.svelte
- Keep existing routes as-is for now

**File: `src/lib/layout.svelte`**
- Add "Dashboard" navigation item (Chart/LineChart icon?) pointing to `/dashboard`
- Add "Admin" navigation item (Settings icon?) pointing to `/admin`
- Keep existing nav items in order

### Step 6: Data Fetching Strategy for Dashboard
**Challenge:** Need to show accounts with their latest balance

**Approach:**
1. Fetch all active accounts: `api.accounts.getAll(false)`
2. Fetch all account balances: `api.accountBalances.getAll()`
3. Group balances by account_id
4. Find latest balance per account (max balance_date)
5. Create derived array with account + latestBalance
6. Pass to card components

**Note:** AccountBalance uses `balance` field (number in cents), not `balance_amount`

**Alternative approach (if performance is concern):**
- Add backend endpoint `/api/accounts/with-latest-balance` that returns joined data
- For now, client-side joining is fine

**Institution names on dashboard:**
- Fetch all institutions to map institution_id to name
- Create lookup object: `institutionMap[institution_id] = institution.name`
- Pass to card components for display

### Step 7: Shared Modal Reuse
**Challenge:** Dashboard needs to open account/institution creation modals

**Approach:**
- Create account/institution dialogs as reusable components
- Dashboard imports and uses these same dialogs
- After successful create, dashboard refreshes its data
- Dialogs are self-contained with their own API calls

---

## Component Reuse Matrix

| Component | Used By | Notes |
|-----------|---------|-------|
| add-edit-institution-dialog | Dashboard, Admin > Institutions | Fully reusable |
| delete-institution-dialog | Admin > Institutions | Only in admin |
| add-edit-account-dialog | Dashboard, Admin > Accounts | Fully reusable |
| delete-account-dialog | Admin > Accounts | Only in admin |
| institutions-data-table | Admin > Institutions | Admin only |
| accounts-data-table | Admin > Accounts | Admin only |
| account-balance-card | Dashboard | Dashboard only |

---

## Critical Considerations

### 1. Institution Dropdown in Account Modal
**Challenge:** Account form needs to select an institution

**Solution:**
- In `add-edit-account-dialog.svelte`, fetch institutions on mount
- Use Select component with institutions list
- Bind selected institution_id to form state
- Filter to active institutions only

```typescript
let institutions: Institution[] = [];
let formData = {
  institution_id: 0,
  account_name: '',
  // ... other fields
};

onMount(async () => {
  institutions = await api.institutions.getAll(false); // active only
});
```

### 2. AccountType Enum Dropdown
**Challenge:** Need dropdown for account type

**Solution:**
- AccountType enum already defined in types.ts
- Use Select component with enum values
- Values from AccountType enum: "checking", "credit_card", "savings", "investment", "retirement", "brokerage"

```typescript
const accountTypes = [
  { value: AccountType.CHECKING, label: 'Checking' },
  { value: AccountType.CREDIT_CARD, label: 'Credit Card' },
  { value: AccountType.SAVINGS, label: 'Savings' },
  { value: AccountType.INVESTMENT, label: 'Investment' },
  { value: AccountType.RETIREMENT, label: 'Retirement' },
  { value: AccountType.BROKERAGE, label: 'Brokerage' }
];
```

### 3. Balance Data Joining
**Challenge:** Efficiently match balances to accounts

**Consideration:**
- Multiple balances per account (historical)
- Need to find most recent balance per account
- Some accounts may have zero balances

**Implementation:**
```typescript
// Group balances by account_id
const balancesByAccount = balances.reduce((acc, balance) => {
  if (!acc[balance.account_id]) {
    acc[balance.account_id] = [];
  }
  acc[balance.account_id].push(balance);
  return acc;
}, {} as Record<number, AccountBalance[]>);

// Find latest balance per account
const accountsWithBalances = accounts.map(account => {
  const accountBalances = balancesByAccount[account.account_id] || [];
  const latestBalance = accountBalances.sort((a, b) =>
    new Date(b.balance_date).getTime() - new Date(a.balance_date).getTime()
  )[0];

  return {
    account,
    latestBalance: latestBalance || null
  };
});
```

### 4. Tab State Management in Admin Page
**Challenge:** Should tab state persist across navigation?

**Recommendation:**
- Use URL hash or query param to track active tab
- Example: `/admin#accounts` or `/admin?tab=accounts`
- Falls back to "Institutions" tab as default
- Allows bookmarking specific tabs

### 5. Current Institutions Page
**Question:** What to do with existing `/institutions` page?

**Options:**
- Option A: Redirect to `/admin#institutions`
- Option B: Keep as-is for backward compatibility
- Option C: Remove and update all links

**Recommendation:** Option B for now, clean up later

### 6. Missing Select Component
**Blocker:** shadcn-svelte Select component not installed

**Solution:**
- Install via npx shadcn-svelte add select
- Or manually copy from shadcn-svelte docs
- Required for account form to work

### 7. Tabs Component
**Required for:** Admin page

**Solution:**
- Install via npx shadcn-svelte add tabs
- Or manually copy from shadcn-svelte docs

---

## Implementation Order

1. ✅ Add Select and Tabs components from shadcn-svelte
2. ✅ Create accounts CRUD components (reusable for both dashboard and admin)
3. ✅ Create admin page with tabs (institutions + accounts)
4. ✅ Create dashboard page with balance cards
5. ✅ Update routing to include /dashboard and /admin
6. ✅ Update sidebar navigation
7. ✅ Test full flow: create account from dashboard, manage in admin, view balance on dashboard

---

## Files Summary

### New Files (17 files)
1. `src/pages/dashboard.svelte`
2. `src/pages/dashboard/account-balance-card.svelte`
3. `src/pages/dashboard/balance-chart-placeholder.svelte`
4. `src/pages/admin.svelte`
5. `src/pages/admin/institutions-tab.svelte`
6. `src/pages/admin/accounts-tab.svelte`
7. `src/pages/accounts/columns.ts`
8. `src/pages/accounts/accounts-data-table.svelte`
9. `src/pages/accounts/add-edit-account-dialog.svelte`
10. `src/pages/accounts/delete-account-dialog.svelte`
11. `src/pages/accounts/accounts-table-actions.svelte`
12. `src/lib/components/ui/select/` (component files)
13. `src/lib/components/ui/tabs/` (component files)

### Modified Files (2 files)
1. `src/lib/routes.ts`
2. `src/lib/layout.svelte`

### Reference Files (no changes)
- `src/pages/institutions.svelte` (pattern reference)
- `src/pages/institutions/*` (pattern reference)
- `src/lib/api.ts` (already has all needed methods)
- `src/lib/types.ts` (already has all needed types)
