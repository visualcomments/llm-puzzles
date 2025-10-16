#!/usr/bin/env python3
import argparse
from importlib import import_module
from src.universal_adapter import build_submission
from src.kaggle_utils import ensure_auth, submit_file

def main():
    p = argparse.ArgumentParser(description="Universal Kaggle submission builder for CayleyPy & similar comps")
    p.add_argument("--competition", required=True, help="Kaggle competition slug")
    p.add_argument("--puzzles", required=True, help="Path to puzzles.csv (downloaded from Kaggle)")
    p.add_argument("--out", default="submission.csv", help="Output submission.csv path")
    p.add_argument("--solver", default="examples.cayleypy_solver.baseline:solve_row",
                   help="Dotted path to solver function (row, cfg) -> moves (str|list[str]|dict)")
    p.add_argument("--submit", action="store_true", help="Also submit via Kaggle API")
    p.add_argument("--message", default="perm-llm-starter auto-submit", help="Submission message")
    args = p.parse_args()

    # load solver
    mod_name, func_name = (args.solver.split(":") + ["solve_row"])[:2]
    mod = import_module(mod_name)
    solver_fn = getattr(mod, func_name)

    print(f"[+] Building submission for {args.competition} from {args.puzzles} using {args.solver}")
    build_submission(args.puzzles, args.out, args.competition, solver_fn)
    print(f"[+] Saved submission to {args.out}")

    if args.submit:
        print("[+] Authenticating Kaggle API...")
        api = ensure_auth()
        print(f"[+] Submitting to {args.competition} with message: {args.message}")
        submit_file(api, args.competition, args.out, args.message)
        print("[+] Submission requested (check Kaggle site for status).")

if __name__ == "__main__":
    main()
