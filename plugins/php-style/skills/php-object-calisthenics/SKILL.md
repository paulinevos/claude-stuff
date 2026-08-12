---
name: php-object-calisthenics
description: PHP code conventions centred on object calisthenics — one level of indentation, no else, wrapped primitives, first-class collections, no train wrecks, no abbreviations, small entities, no getters or setters — plus the PHP specifics that support them (strict types, readonly value objects, backed enums, match, final by default, domain exceptions). Consult this skill whenever you are about to write, refactor, or review PHP of any kind, including small edits, bug fixes, tests, and scripts, and even when the user has not mentioned style at all.
---

# PHP object calisthenics

Write PHP according to **object calisthenics**. Apply the rules below fully to
new code, where the cost is low and the payoff in clarity is high. Go lighter on
existing code — they're not a licence to refactor what you weren't asked to
touch, and a codebase in two conflicting styles is worse than one consistently in
the lesser style.

When a rule genuinely makes code harder to read, break it and say so in one
sentence. Silent deviation is the real failure mode — it's indistinguishable from
not knowing the rule.

Defer to the repository throughout: its PSR level, PHPStan/Psalm level, CS-fixer
rules, and the PHP version pinned in `composer.json` — don't reach for syntax it
doesn't have.

## Laravel projects: follow Boost

If the project has Laravel Boost installed, its guidelines take precedence over
this skill wherever they overlap. Boost ships version-specific conventions for the
exact Laravel, Livewire, Inertia, Pest and Filament versions in play, plus an MCP
server for querying the app.

- Look for Boost's guidelines in the project's `AGENTS.md` / `CLAUDE.md` and read
  them before writing Laravel code.
- Use Boost's documentation search rather than recalling APIs from memory — it
  returns docs matched to the installed versions, which is where memory is
  least reliable.
- Prefer its tooling for inspecting the running app (tinker, database queries,
  logs, artisan commands) over guessing at application state.

Everything below still applies to the domain layer, which is the part of a
Laravel app Boost has least to say about.

## Types

- `declare(strict_types=1);` in every file. Coercion hides exactly the bugs that
  wrapping primitives is meant to eliminate.
- Type every parameter, return, and property. `mixed` is an admission, not a
  type; if you need it, say why.
- Generics in docblocks (`@param list<OrderLine> $lines`,
  `@return array<string, Money>`) — the only way to type a collection's contents
  precisely, and the static analyser reads them.

## 1. One level of indentation per method

The highest-leverage rule. When a second `if` or loop wants to go inside a first,
extract the inner block into a private method named for what it does. The nesting
becomes a name, and names are what a reader can follow.

Guard clauses are the other half: most deep nesting is unhandled preconditions.
Invert, return early, and the happy path flattens to the left margin.

```php
// instead of
if ($user->isActive()) {
    if ($order->isPaid()) {
        foreach ($order->lines() as $line) { ... }
    }
}

// prefer
if (!$user->isActive()) { return; }
if (!$order->isPaid()) { return; }
$this->fulfil($order);
```

## 2. Don't use `else`

An `else` means the method is holding two responsibilities apart with an
indentation level instead of a name. Replace it with an early return, a guard
clause, polymorphism, a `match` expression, or a null object.

`else` branches accumulate: one is fine, the third `else if` is where a method
becomes a decision tree nobody can hold in their head, and by then the refactor
is expensive. Removing them on sight keeps that from starting.

Branches over a closed set — a status, a type, a mode — want an enum carrying
behaviour or polymorphic types, not conditionals repeated at every call site.

In PHP specifically:

- `match` over `switch` — an expression, exhaustive, strict, so no fall-through
  or default-case sprawl to breed `else`.
- Guard clauses with early `return` or `throw`.
- Polymorphism or a behaviour-carrying enum for closed sets.
- `?->` and `??` are fine for genuinely optional data, a smell when papering over
  an object that should never have been null.

## 3. Wrap all primitives and strings

A primitive carrying meaning and rules wants to be a type: a `string` that must
be a valid email, an `int` that must be non-negative, a `float` that is always
euros.

Wrapping moves validation to construction. Once an `EmailAddress` exists it is
valid everywhere, and every downstream "but what if it's malformed" check
disappears. Give these types named constructors so each construction path states
its intent, and equality by value rather than identity.

```php
final readonly class EmailAddress
{
    private function __construct(public string $value)
    {
        if (!filter_var($value, FILTER_VALIDATE_EMAIL)) {
            throw InvalidEmailAddress::forInput($value);
        }
    }

    public static function fromString(string $value): self
    {
        return new self($value);
    }

    public function equals(self $other): bool
    {
        return $this->value === $other->value;
    }
}
```

`readonly` class, private constructor behind a named constructor, validation at
construction, public readonly property rather than `getValue()`, value equality.

**Backed enums** are the wrapper for closed sets. Put behaviour on the enum
(`OrderStatus::canTransitionTo()`) instead of matching on it in three services —
rules 2 and 8 at once.

## 4. First-class collections

A class holding a collection holds *nothing else*. An array plus a couple of
fields alongside it is a missing class.

Collections attract behaviour — filtering, summing, finding, enforcing "at least
one" or "no duplicates". With a bare array that scatters across every consumer;
with an `OrderLines` class it lives in one place, gets a domain name, and can
hold invariants the array can't.

```php
final readonly class OrderLines
{
    /** @param list<OrderLine> $lines */
    private function __construct(private array $lines) {}

    public function total(): Money { ... }
    public function containsRestrictedGoods(): bool { ... }
}
```

Where you'd reach for `array_map`/`array_filter` at a call site, ask whether that
operation has a domain name and belongs on the collection.

## 5. One dot per line

`$order->getCustomer()->getAddress()->getCity()` depends on the internals of
three objects, and any of them changing breaks the line. Ask the object you're
holding for what you need and let it delegate. This pairs with rule 8: without
getters, train wrecks are hard to write in the first place — when you need
something deep in a graph, add a method to the object you're holding and let it
delegate.

**Exception:** fluent interfaces and collection pipelines. A builder chain, a
query builder, or a map/filter/reduce is one object handing back itself or a new
value at each step, not a walk through someone else's object graph.

## 6. Don't abbreviate

If you want to abbreviate, ask why. Usually the name is long because the thing
does too much, or because it repeats context its class already provides
(`Order::getOrderTotal()` wants to be `Order::total()`). Fix the cause.

Write domain words in full, using the words domain experts use — if the business
says "policy holder", the class is not `UsrAcct`, and not `UserAccount` either.
Short names are fine in short scopes: a one-line closure's `$u` is not an
abbreviation problem.

## 7. Keep all entities small

Small classes, small methods, small packages. Roughly: methods that fit on a
screen, classes in the low tens of lines. Smells, not thresholds.

Smallness forces naming. A large class absorbs a new responsibility silently; a
small one makes you notice you're adding something that doesn't belong, while
moving it is still cheap.

DI constructors are exempt from pressure to keep field counts down; a service
with four collaborators is normal. What matters is that each is an interface you
own at a domain boundary.

## 8. No getters or setters — prefer readonly public properties

Tell, don't ask. Objects expose behaviour; callers ask them to *do* things rather
than extract state and decide on their behalf. Pulling data out of an object to
decide something about it means the decision belongs on the object.

Where data genuinely needs to be readable, expose a `readonly` public property
set through constructor property promotion. Same guarantee a getter pretended to
give — nobody can mutate it — without `getFoo()` wrapping `$this->foo`.

Setters are out. An object mutable into an invalid state after construction has
given up enforcing its invariants. Use `with*()` methods returning new instances,
or a method named for the domain operation actually happening
(`$order->cancel()`, not `$order->setStatus(CANCELLED)`).

## Class design

- `final` by default. Inheritance for reuse is where PHP codebases go to die;
  open a class deliberately at a designed extension point, or not at all.
- Constructor property promotion everywhere — it's what makes readonly public
  properties cheaper than the getters they replace.
- `readonly` on value objects and injected dependencies. Evolve value objects
  with `with*()` methods returning new instances, never setters.
- Name methods for domain operations: `$order->cancel()`, not
  `$order->setStatus(OrderStatus::Cancelled)`.
- No static state, no service locators, no `new`-ing collaborators inside domain
  logic. Inject through the constructor.
- Keep HTTP, Eloquent/Doctrine and console concerns out of domain classes — a
  domain object shouldn't know what delivered the request.

## Exceptions

Domain-specific classes named for what went wrong (`InsufficientBalance`,
`OrderAlreadyShipped`), with named constructors building the message from context
(`InvalidEmailAddress::forInput($value)`). Extend the right base and let them
bubble to a boundary that decides on presentation; don't catch-log-continue
inside domain logic.

Prefer explicit, typed, domain-meaningful failures over generic exceptions or
silent nulls, and never swallow an error to make a signature tidy.

## Tests

Follow the project's existing test style. Absent one: test behaviour through the
public API, name test methods as sentences describing the behaviour, and build
objects with test data builders or named constructors rather than sprawling
setup. Mock only at real boundaries — clock, HTTP, persistence. Needing to mock
your own value objects means the design wants adjusting, not that the test wants
a mock.

## Beyond the rules

**Abstractions follow the domain, not the code.** Code that *looks* alike isn't
necessarily the *same thing*. Extracting on mechanical similarity welds together
concepts free to evolve separately, and the seam tears later — a flag parameter,
then a second, then a branch nobody understands. Duplication spanning two domain
concepts is fine; leave it, and say you're leaving it so it doesn't read as an
oversight. Duplication *within* one concept is the real smell.

**Comments explain why, never what.** A comment restating the line below it rots
the moment the line changes, and readers learn to distrust all the comments.
Write one when the reasoning isn't visible: a tradeoff, a rejected alternative, an
external constraint, or code that looks wrong but is right (compensating for an
upstream bug, an ordering requirement). Those last are the highest-value comments
anywhere — without them someone will "fix" the code back into a bug.

Don't comment when the fix is a better name: `// check if the user can edit`
means the condition wants to be `$user->canEdit($document)`. No banner headers,
no step-by-step narration, no `// Constructor` above a constructor.

**Other shape.** A long parameter list is often a missing type; a boolean flag
parameter is two functions wearing a trench coat. Immutability by default.

## When the repo disagrees

Consistency within a codebase beats these preferences. Follow the repo, mention
the tension in a sentence, and don't turn a small request into a refactor.
