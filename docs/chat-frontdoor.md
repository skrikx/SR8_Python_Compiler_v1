# Chat Front Door

SR8 now supports a chat-native front door that accepts `compile:` and `resume:` invocations. The front door uses the same compile route contract as the core compiler, so chat input either reaches semantic compile, truthfully canonicalizes already-structured input, or returns intake XML when the request still needs refinement.

## Invocation

- `compile:` prefix triggers chat intake parsing.
- `resume:` prefix accepts a completed intake XML form and resumes compilation.

Example:

```
compile: Objective: Draft a launch plan
Scope:
- Phase one
Success Criteria:
- Ready to ship
```

If the intent is underspecified, the compiler returns the intake XML form. Complete the form and submit it again with `resume:`.

## Front Door Flow

1. Chat intent
2. Front door parser or intake fallback
3. Canonical SR8 artifact
4. Validation and governance
5. XML package emission

The front door never bypasses the core compiler. It always terminates in canonical SR8 artifacts before packages are emitted.
