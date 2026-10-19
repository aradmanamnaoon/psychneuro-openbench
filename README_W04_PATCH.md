# W04 additive private integration patch

Copy `src/psychneuro/w04/` into existing `psychneuro-openbench` source and `tests/test_w04_*` alongside existing W03 tests. Inspect the diff and run the full tests before any merge or network host.

`create_app(db_path=Path('/private/aggregate.sqlite'), registry_path=Path('data/registry.json'), credentials={'<64-character-secret>': Principal(subject='internal', role='maintainer')})` returns a private FastAPI app. Bind only to localhost in an authorized isolated environment; do not put the token into client JavaScript or logs. The UI prompts for a token at runtime; no token cookie or storage.

**Policy:** private original synthetic aggregate only. Real human or unlicensed datasets are not supported. Cross-system data rights are checked via P25 before P1 execution and P13 export. This is an in-progress review patch, not a production or public launch.

See `docs/W04_REVIEW.md` for verified vs unverified gates.

Additional new W04 paths: `src/psychneuro/w04/{ledger,cli,server}.py`, `benchmarks/measure_w04.py`, `tests/test_w04_server.py`, `infra/Dockerfile`, `.github/workflows/w04-private-manual.yml`. The Dockerfile is a non-deployed candidate: build from the existing W03 branch root (`docker build -f infra/Dockerfile .`); no base-image digest, full lock, remote host, package-vulnerability scanner or Docker execution verified. Do not map to a public interface. CLI: `python -m psychneuro.w04.cli review-rights --rights rights.json --action run --role researcher --ledger private.sqlite`; `verify-ledger --ledger private.sqlite --trusted-root <independently-anchored-sha>`.
