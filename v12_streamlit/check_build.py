"""
V12 Streamlit — Pre-deploy Quality Gate
Run: python check_build.py

Checks syntax, file structure, and code quality patterns.
Does NOT require streamlit to be installed locally — uses py_compile for syntax checks.
"""
import sys
import os
import py_compile

ROOT = os.path.dirname(os.path.abspath(__file__))

GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"
PASS  = f"{GREEN}PASS{RESET}"
FAIL  = f"{RED}FAIL{RESET}"
results = []

def check(name, fn):
    try:
        ok, detail = fn()
        status = PASS if ok else FAIL
        print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
        results.append(ok)
    except Exception as exc:
        print(f"  [{FAIL}] {name} — Exception: {exc}")
        results.append(False)

def read_file(path):
    return open(path, encoding="utf-8").read()

print("\n=== V12 Streamlit Pre-deploy Quality Gate ===\n")

# ── 1. Syntax check — all .py files ──────────────────────────────────────────
print("1. Python syntax checks:")
ALL_PY = []
for subdir in ["pages", "data", "utils", ""]:
    dirpath = os.path.join(ROOT, subdir) if subdir else ROOT
    for fname in os.listdir(dirpath):
        if fname.endswith(".py") and fname != "check_build.py":
            ALL_PY.append(os.path.join(dirpath, fname))

for fpath in sorted(ALL_PY):
    rel = fpath.replace(ROOT + os.sep, "")
    def _syn(p=fpath, r=rel):
        try:
            py_compile.compile(p, doraise=True)
            return True, None
        except py_compile.PyCompileError as e:
            return False, str(e)
    check(rel, _syn)

# ── 2. config.toml ────────────────────────────────────────────────────────────
print("\n2. config.toml:")
def check_toml():
    path = os.path.join(ROOT, ".streamlit", "config.toml")
    if not os.path.exists(path):
        return False, "NOT FOUND at .streamlit/config.toml — this is why colors break on Cloud!"
    content = read_file(path)
    required = ["base", "primaryColor", "backgroundColor", "secondaryBackgroundColor", "textColor"]
    missing = [k for k in required if k not in content]
    if missing:
        return False, f"Missing keys: {missing}"
    if '"dark"' not in content and "'dark'" not in content and "dark" not in content:
        return False, "base theme not set to dark"
    return True, "All required theme keys present, base=dark"
check("config.toml exists and has all theme keys", check_toml)

# ── 3. requirements.txt ───────────────────────────────────────────────────────
print("\n3. requirements.txt:")
def check_requirements():
    path = os.path.join(ROOT, "requirements.txt")
    if not os.path.exists(path):
        return False, "requirements.txt not found"
    reqs = read_file(path).lower()
    needed = ["streamlit", "plotly", "pandas", "openai", "openpyxl", "python-dotenv"]
    missing = [p for p in needed if p not in reqs]
    if missing:
        return False, f"Missing packages: {missing}"
    return True, f"All {len(needed)} required packages listed"
check("requirements.txt has all needed packages", check_requirements)

# ── 4. idea_gen.py code quality ───────────────────────────────────────────────
print("\n4. idea_gen.py code quality (V12 fixes):")
idea_gen_src = read_file(os.path.join(ROOT, "pages", "idea_gen.py"))

def check_no_col_layout():
    if "col_input, col_clear = st.columns" in idea_gen_src:
        return False, "B1: Broken crossing col_input/col_clear layout still present"
    return True, "B1: No crossing column layout"
check("B1 layout fix — no col_input/col_clear", check_no_col_layout)

def check_no_duplication():
    # V12 fix pattern: messages += chat_history then messages.append(user msg)
    # i.e., new user msg added to messages list separately, not via history
    has_fixed_pattern = (
        "messages += st.session_state.chat_history" in idea_gen_src and
        'messages.append({"role": "user", "content": prompt})' in idea_gen_src
    )
    # V9 bug pattern: history.append user first, then messages = [system] + chat_history
    # (where the history already contains the new message)
    has_bug_pattern = (
        'st.session_state.chat_history.append({"role": "user", "content": prompt})' in idea_gen_src and
        "messages += st.session_state.chat_history" in idea_gen_src and
        not has_fixed_pattern
    )
    if has_fixed_pattern:
        return True, "B3: Fixed pattern detected (messages += history, then messages.append new msg)"
    if has_bug_pattern:
        return False, "B3: V9 duplication bug pattern detected — fix not applied"
    return True, "B3: Pattern differs from both — review manually"
check("B3 deduplication fix — messages before append", check_no_duplication)

def check_grounded_badge():
    if "v12-badge" in idea_gen_src or "Grounded in 107" in idea_gen_src:
        return True, "B4: Grounded-in badge present"
    return False, "B4: Grounded-in badge missing"
check("B4 grounded-in badge present", check_grounded_badge)

def check_token_expiry():
    if "_token_is_expired" in idea_gen_src:
        return True, "B3: Token expiry detection present"
    return False, "B3: Token expiry detection missing"
check("B3 token expiry detection present", check_token_expiry)

def check_session_status():
    if "turn_count" in idea_gen_src or "Turn" in idea_gen_src:
        return True, "B4: Session status/turn counter present"
    return False, "B4: Session status line missing"
check("B4 session status line present", check_session_status)

# ── 5. app.py code quality ────────────────────────────────────────────────────
print("\n5. app.py code quality (V12 fixes):")
app_src = read_file(os.path.join(ROOT, "app.py"))

def check_no_color_css():
    fragile = ["stMetricLabel", "stMetricValue", "stMetricDelta", "stRadio label"]
    found = [s for s in fragile if s in app_src]
    if found:
        return False, f"B2: Fragile internal CSS selectors still present: {found}"
    return True, "B2: No fragile internal Streamlit color selectors"
check("B2 CSS fix — no fragile data-testid color overrides", check_no_color_css)

def check_config_toml_comment():
    if "config.toml" in app_src or "theme" in app_src:
        return True, "B2: References config.toml for theming"
    return False, "B2: No reference to config.toml — colors may not load"
check("B2 app.py defers colors to config.toml", check_config_toml_comment)

# ── 6. .gitignore ─────────────────────────────────────────────────────────────
print("\n6. Security:")
def check_gitignore():
    path = os.path.join(ROOT, ".gitignore")
    if not os.path.exists(path):
        return False, ".gitignore not found — .env may be committed!"
    content = read_file(path)
    if ".env" not in content:
        return False, ".env not listed in .gitignore — JWT token at risk!"
    if "secrets.toml" not in content:
        return False, "secrets.toml not listed in .gitignore"
    return True, ".env and secrets.toml both gitignored"
check(".gitignore excludes .env and secrets.toml", check_gitignore)

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
total  = len(results)
passed = sum(results)
failed = total - passed
if failed == 0:
    print(f"{GREEN}  ALL {total} CHECKS PASSED — V12 is ready to deploy!{RESET}")
else:
    print(f"{RED}  {failed}/{total} CHECKS FAILED — fix issues above before pushing to GitHub.{RESET}")
print(f"{'='*50}\n")
sys.exit(0 if failed == 0 else 1)
