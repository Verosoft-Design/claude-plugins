---
fno-version: [all]
domain: performance
keywords: [select, firstonly, where-clause, order-by, exists-join, function-call]
technologies: [xpp]
countries: [w1]
application-area: [all]
---

# Shape X++ selects for the database: firstOnly, plain where values, flat joins

## Description

An X++ select is translated to SQL. `firstOnly` (and the fixed `firstOnly10`, `firstOnly100`, `firstOnly1000`) tells the plan how many rows are wanted, and `firstFast` is only a priority hint. The select-statement rules the d365fo MCP draws from shipped code say not to call functions in a `where` clause: assign the result to a local variable first, for performance and best-practice compliance. `exists join` and `notexists join` are semi-joins that fetch no fields. Clause order is fixed per join segment: `order by` or `group by` before `where`, otherwise the compiler stops with "'join' expected".

## Best Practice

Use `firstOnly` when one record is needed. Assign computed values (dates, IDs from `::find`) to local variables before the select and compare against the variables. Filter with `exists join` when the joined table only restricts the result. Keep joins flat, each joined buffer with its own `where`. For an arbitrary top-N, use the Query framework.

## Anti Pattern

`select * from table where table.Date >= systemDateGet() - 7`, fetching a full row to test existence, nested joins, or `select x where ... order by y`.
