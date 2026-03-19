# SR8 Feature Matrix

| Surface | Status | Notes |
| --- | --- | --- |
| CLI compile | Available | `sr8 compile` with profile selection and output path support |
| CLI validate | Available | `sr8 validate` for artifact validation |
| CLI inspect | Available | Supports artifact paths and source inputs |
| CLI transform | Available | Transform targets enforced by profile compatibility |
| CLI diff | Available | Semantic field diff with impact levels |
| CLI lint | Available | Rule-based lint report (`L001` to `L010`) |
| Workspace storage | Available | `.sr8` local persistence, catalog, receipts |
| Python compile API | Available | `sr8.compiler.compile_intent` |
| FastAPI endpoints | Available | `/health`, `/compile`, `/validate`, `/transform` |
| CI quality gates | Available | lint, mypy, pytest, examples smoke, build smoke |
| Release publish | Available | tag-driven release and trusted publishing path |
| Code scanning | Available | CodeQL and dependency review workflows |
