## 2025-05-23 - Authentication Implementation Pattern
**Vulnerability:** Timing Attack on Token Verification & Missing Auth on Sensitive Endpoints
**Learning:** `src/api/routes/` modules may not inherit dependencies from `src/api/main.py` router includes automatically if `router` is defined independently without `verify_token` dependency. Also, direct string comparison for API tokens exposes timing side-channels.
**Prevention:**
1. Centralize authentication logic in `src/api/auth.py` using `secrets.compare_digest`.
2. Apply `dependencies=[Depends(verify_token)]` explicitly on sensitive routes or routers in submodules, or ensure `main.py` applies it correctly to the `include_router` call.
3. Verify endpoint security by attempting unauthenticated requests in tests.

## 2025-05-23 - FastAPI Background Tasks
**Vulnerability:** DoS / Server Crash via Improper Task Scheduling
**Learning:** Passing `asyncio.create_task` to `BackgroundTasks.add_task` causes `RuntimeError: no running event loop` in some contexts (like TestClient or specific async setups) because `add_task` expects a function reference, not a coroutine object or task.
**Prevention:** Always pass the function reference and arguments separately: `bg_tasks.add_task(func, arg1, arg2)`, not `bg_tasks.add_task(func(arg1, arg2))` or `bg_tasks.add_task(asyncio.create_task, ...)`.
