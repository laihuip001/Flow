# Debugging: Build Failure (pydantic-core)

- **Symptom:** `Failed to build pydantic-core`.
- **Cause:** Termux (aarch64) often lacks pre-built wheels for Pydantic v2, requiring compilation from source. This needs the Rust compiler.
- **Solution:** Install build dependencies: `pkg install rust build-essential binutils`.

- **Constraint Check:**
  - Is `pydantic-core` strictly required? Yes, by `pydantic>=2.0.0`.
  - Can we downgrade? V1 is pure python but deprecated.
  - **Action:** Instruct user to install Rust compiler.
