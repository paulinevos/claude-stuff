---
name: php-object-calisthenics
description: "Apply object-calisthenics conventions when writing, refactoring, or reviewing PHP: flat control flow, domain types and collections, behaviour-rich objects, and PHP-specific type and immutability practices."
---

# PHP object calisthenics

Apply these rules fully to new code when they improve clarity. In existing code,
preserve local consistency: do not turn a narrow task into a style refactor. If
a rule would make code less clear, deviate explicitly and explain why. Always
honour the repository's PHP version, PSR/style tooling, and static-analysis
level.

For Laravel with Boost, read its project guidance first and use its
version-matched documentation and inspection tools. Boost wins on framework
concerns; these rules still guide the domain layer.

## Types and values

- Put `declare(strict_types=1);` in every PHP file. Type parameters, returns,
  and properties; use `mixed` only with a stated reason. Use generic docblocks
  for collection contents.
- Wrap domain-significant primitives and strings in value objects. Validate in
  named constructors, compare by value, and make the objects `final readonly`.
  Use backed enums for closed sets and put their behaviour on the enum.
- Prefer first-class collection types to bare domain arrays. A collection holds
  only its elements and owns operations and invariants such as uniqueness,
  filtering, and totals.

## Object shape

- Keep one indentation level per method. Use guard clauses, extraction, and
  named private methods instead of nesting.
- Do not use `else`; return or throw early, use `match` for closed choices, or
  model the variation with polymorphism, an enum, or a null object. `?->` and
  `??` are for genuinely optional data, not invalid object graphs.
- One dot per line: ask the object in hand for the result instead of traversing
  its collaborators. Fluent builders and collection pipelines are exceptions.
- Use full domain names; short local closure variables are fine. Keep methods,
  classes, and packages small enough to make responsibilities obvious.
- Tell, do not ask. Prefer behaviour over getters; expose genuinely readable
  data as promoted `public readonly` properties. Never add setters: use a
  domain operation or an immutable `with*()` method.

## PHP design

- Make classes `final` by default. Use constructor promotion; make value
  objects and injected dependencies `readonly` where possible.
- Inject collaborators. Do not use static state, service locators, or construct
  collaborators inside domain logic. Keep HTTP, ORM, and console concerns at
  the boundary.
- Use domain-specific exceptions with named constructors; let them reach the
  presentation boundary. Do not use generic failures, silent nulls, or
  catch-log-continue to conceal domain errors.

## Tests and code quality

- Follow the repository's test style. Otherwise, test public behaviour; use
  sentence-style test names, builders or named constructors, and mocks only at
  real boundaries (time, HTTP, persistence).
- Extract abstractions by shared domain meaning, not mechanical similarity.
  Duplication across separate concepts can be intentional; state that choice
  when it could look accidental.
- Comments explain non-obvious *why*: constraints, trade-offs, or surprising
  correct behaviour. Replace comments that narrate code with better names.
- Treat long parameter lists as a missing type, boolean flags as a missing
  operation, and mutability as opt-in.
