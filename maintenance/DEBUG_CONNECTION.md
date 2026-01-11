# Debugging: No Such File or Directory

- **Symptom:** User sees "No such file or directory" when running `./maintenance/start_termux.sh`.
- **Potential Causes:**
    1. User is not in the `Flow` directory (e.g., still in home `~`).
    2. Script permissions (`chmod +x`).
    3. CRLF line endings (Windows style) on the script file, causing shebang failure.

- **Action Plan:**
    1. Ask user to run `ls -F` to see where they are.
    2. Instruct to `cd Flow`.
    3. Suggest running with `bash` explicitly to avoid permission/shebang issues: `bash maintenance/start_termux.sh`.
