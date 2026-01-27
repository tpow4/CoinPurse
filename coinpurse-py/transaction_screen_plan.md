---

Phase 1: Backend — Add Joined Fields

1. Create response schema with account_name and category_name
2. Update repository to eager-load relationships
3. Update router to return enriched response  


---

Phase 2: Frontend — Core Grid

4. Update types — add TransactionWithNames interface
5. Update API — adjust for new response shape
6. Create columns.ts — column definitions with formatters

---

Phase 3: Frontend — Data Table

7. Create transactions-data-table.svelte — TanStack table with sorting and pagination

---

Phase 4: Frontend — Filters

8. Create amount-range-slider.svelte — dual-handle slider component
9. Create transactions-filters.svelte — filter bar with all controls
10. Wire up filter state — connect filters to table

---

Phase 5: Frontend — Page Assembly

11. Update +page.svelte — combine filters, table, load data
12. Handle empty state — "No transactions found" display

---

Order of Work  
 ┌───────┬──────────────────┬────────────┐  
 │ Step │ Task │ Depends On │  
 ├───────┼──────────────────┼────────────┤  
 │ 1-3 │ Backend changes │ — │  
 ├───────┼──────────────────┼────────────┤  
 │ 4-5 │ Types & API │ Backend │  
 ├───────┼──────────────────┼────────────┤  
 │ 6-7 │ Columns & Table │ Types │  
 ├───────┼──────────────────┼────────────┤  
 │ 8-9 │ Slider & Filters │ — │  
 ├───────┼──────────────────┼────────────┤  
 │ 10-12 │ Integration │ All above │  
 └───────┴──────────────────┴────────────┘

---
