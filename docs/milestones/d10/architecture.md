# D10 Architecture — ML Evidence Boundary

D10 extends the governed-data and project seams; it does not create a provider, broker, model-approval, or execution seam. `ml_experiments` is a deterministic pure computation boundary over an immutable Parquet payload. A D10 desktop service resolves the dataset revision server-side, constructs a bounded request, invokes that engine, and persists only retained evidence/lineage. The UI receives typed records, never paths or arbitrary code.

The existing `ml` package owns durable ML contract families; `ml_experiments` owns bounded baseline/training computations. D11 may consume D10 immutable result records but owns registry/promotion decisions.

`desktop_api.ml_lab` owns `d10-ml-lab.sqlite3`, its schema migration, recovery, feature/label catalog projection, experiment definition records, lifecycle events, and result evidence. It consumes governed dataset information only through `resolve_governed_dataset`; it never reads another capability's database directly. D6 stores only a typed `ml_experiment` pin reference.

The Rust broker classifies create/run/cancel as profile mutations but contains no ML rules. React uses `mlLabApi.ts` and has no filesystem, database, provider, subprocess, or network authority.
