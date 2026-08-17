#!/usr/bin/env python3
"""
LeetCode Backfill & Backdated Commit Automation
-----------------------------------------------
Processes uncommitted solution files from a backlog, determines their true
chronological solve order, assigns one commit per day counting backward from today,
generates folder scaffolding & notes, updates README stats, and creates backdated Git commits.

Usage:
    python backfill_solutions.py                     # Interactive mode
    python backfill_solutions.py --dry-run           # Preview solve order & dates without changes
    python backfill_solutions.py --backlog my_folder # Custom backlog path
    python backfill_solutions.py --order my_order.txt# Custom solve order file
    python backfill_solutions.py --yes               # Non-interactive execution (uses detected order)
"""

import os
import sys
import re
import shutil
import argparse
import subprocess
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

# Base repository root
REPO_ROOT = Path(__file__).resolve().parent
SOLUTIONS_DIR = REPO_ROOT / "solutions"
BACKLOG_DIR = REPO_ROOT / "backlog"
README_FILE = REPO_ROOT / "README.md"
SOLVE_ORDER_FILE = REPO_ROOT / "solve_order.txt"
BACKLOG_SOLVE_ORDER_FILE = BACKLOG_DIR / "solve_order.txt"

# Configure UTF-8 for standard output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Safe status symbols
CHECK = "[OK]"
WARN = "[!]"
INFO = "[i]"

# ANSI Colors
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def print_banner():
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("================================================================")
    print("          LEETCODE BACKFILL & BACKDATED COMMIT ENGINE           ")
    print("================================================================")
    print(f"{Colors.RESET}")


def slugify(text: str) -> str:
    """Convert problem title to a clean URL/folder slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def format_problem_num(num_input: str) -> str:
    """Format problem number into 4-digit zero-padded string (e.g., 1 -> '0001')."""
    clean = re.sub(r"\D", "", str(num_input))
    if not clean:
        raise ValueError(f"Invalid problem number: {num_input}")
    return f"{int(clean):04d}"


def get_difficulty_badge(difficulty: str) -> str:
    """Return markdown badge for difficulty."""
    diff = difficulty.capitalize()
    if diff == "Easy":
        return "🟢 `Easy`"
    elif diff == "Medium":
        return "🟡 `Medium`"
    elif diff == "Hard":
        return "🔴 `Hard`"
    return f"`{diff}`"


def get_language_from_ext(ext: str) -> str:
    """Map file extension to language display name."""
    mapping = {
        ".py": "Python",
        ".cpp": "C++",
        ".cc": "C++",
        ".c": "C",
        ".java": "Java",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".go": "Go",
        ".rs": "Rust",
        ".cs": "C#",
        ".kt": "Kotlin",
        ".swift": "Swift",
        ".sql": "SQL",
    }
    return mapping.get(ext.lower(), "Code")


def get_local_timezone_offset() -> str:
    """Return local timezone offset string (e.g., '+0530' or '-0400')."""
    now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    offset = now.strftime("%z")
    return offset if offset else "+0000"


def generate_notes_md(
    num_str: str,
    title: str,
    difficulty: str,
    tags: List[str],
    approach: str,
    time_comp: str,
    space_comp: str,
    solution_filename: str,
    problem_url: Optional[str] = None,
) -> str:
    """Generate notes.md markdown content."""
    slug = slugify(title)
    if not problem_url:
        problem_url = f"https://leetcode.com/problems/{slug}/"

    diff_badge = get_difficulty_badge(difficulty)
    tags_formatted = ", ".join([f"`{t.strip()}`" for t in tags if t.strip()]) or "`None`"

    content = f"""# {int(num_str)}. {title}

{diff_badge} | [LeetCode Problem Link]({problem_url})

---

## 🏷️ Topics / Tags
{tags_formatted}

---

## 💡 Approach Summary
{approach if approach.strip() else "Direct simulation / optimal implementation."}

---

## ⏱️ Complexity Analysis

| Metric | Complexity | Explanation |
| :--- | :--- | :--- |
| **Time Complexity** | `{time_comp}` | Optimized pass over input elements. |
| **Space Complexity** | `{space_comp}` | Auxiliary memory used during execution. |

---

## 💻 Solution File
- [`{solution_filename}`](./{solution_filename})
"""
    return content


def scan_committed_problems() -> Tuple[Set[str], Set[str], List[Dict]]:
    """Scan existing solutions/ and return committed numbers, slugs, and full problem dicts."""
    if not SOLUTIONS_DIR.exists():
        SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
        return set(), set(), []

    committed_numbers = set()
    committed_slugs = set()
    problems = []

    for item in sorted(SOLUTIONS_DIR.iterdir()):
        if item.is_dir() and re.match(r"^\d{4}-", item.name):
            num_str = item.name[:4]
            slug = item.name[5:]
            committed_numbers.add(num_str)
            committed_slugs.add(slug)

            title_guess = slug.replace("-", " ").title()
            notes_file = item / "notes.md"
            difficulty = "Medium"
            tags = []
            problem_url = f"https://leetcode.com/problems/{slug}/"

            solution_files = [f for f in item.iterdir() if f.is_file() and f.name != "notes.md"]
            sol_link = ""
            if solution_files:
                sol_file = solution_files[0]
                sol_lang = get_language_from_ext(sol_file.suffix)
                sol_link = f"[{sol_lang}](solutions/{item.name}/{sol_file.name})"
            else:
                sol_link = "—"

            if notes_file.exists():
                try:
                    text = notes_file.read_text(encoding="utf-8")
                    title_match = re.search(r"^#\s+\d+\.\s+(.+)$", text, re.MULTILINE)
                    if title_match:
                        title_guess = title_match.group(1).strip()

                    if "Easy" in text:
                        difficulty = "Easy"
                    elif "Hard" in text:
                        difficulty = "Hard"
                    elif "Medium" in text:
                        difficulty = "Medium"

                    tags_match = re.search(r"## 🏷️ Topics / Tags\s*\n([^\n]+)", text)
                    if tags_match:
                        raw_tags = tags_match.group(1)
                        tags = [t.strip("` ") for t in raw_tags.split(",") if t.strip()]

                    url_match = re.search(r"\[LeetCode Problem Link\]\((https://[^\)]+)\)", text)
                    if url_match:
                        problem_url = url_match.group(1)
                except Exception:
                    pass

            problems.append({
                "number": num_str,
                "int_num": int(num_str),
                "title": title_guess,
                "slug": slug,
                "difficulty": difficulty,
                "tags": tags,
                "url": problem_url,
                "sol_link": sol_link,
                "notes_link": f"[Notes](solutions/{item.name}/notes.md)",
                "folder": item.name
            })

    problems.sort(key=lambda x: x["int_num"])
    return committed_numbers, committed_slugs, problems


def update_readme_stats(problems: Optional[List[Dict]] = None) -> bool:
    """Update the statistics table and problem index in README.md."""
    if problems is None:
        _, _, problems = scan_committed_problems()

    if not README_FILE.exists():
        print(f"{Colors.YELLOW}{WARN} README.md not found at {README_FILE}{Colors.RESET}")
        return False

    total = len(problems)
    easy_count = sum(1 for p in problems if p["difficulty"].lower() == "easy")
    med_count = sum(1 for p in problems if p["difficulty"].lower() == "medium")
    hard_count = sum(1 for p in problems if p["difficulty"].lower() == "hard")

    stats_markdown = f"""<!-- STATS:START -->
### 📊 Practice Overview

| Total Solved | 🟢 Easy | 🟡 Medium | 🔴 Hard |
| :---: | :---: | :---: | :---: |
| **{total}** | **{easy_count}** | **{med_count}** | **{hard_count}** |

---

### 📑 Solved Problems Index

| # | Problem | Difficulty | Solution | Notes | Tags |
| :---: | :--- | :---: | :---: | :---: | :--- |
"""

    if not problems:
        stats_markdown += "| — | *No problems tracked yet. Use `python commit_solution.py` to add your first solution!* | — | — | — | — |\n"
    else:
        for p in problems:
            diff_badge = get_difficulty_badge(p["difficulty"])
            tags_str = ", ".join([f"`{t}`" for t in p["tags"]]) if p["tags"] else "`—`"
            stats_markdown += (
                f"| `{p['number']}` | [{p['title']}]({p['url']}) | "
                f"{diff_badge} | {p['sol_link']} | {p['notes_link']} | {tags_str} |\n"
            )

    stats_markdown += "<!-- STATS:END -->"

    try:
        content = README_FILE.read_text(encoding="utf-8")
        if "<!-- STATS:START -->" in content and "<!-- STATS:END -->" in content:
            new_content = re.sub(
                r"<!-- STATS:START -->.*?<!-- STATS:END -->",
                stats_markdown,
                content,
                flags=re.DOTALL,
            )
        else:
            new_content = content + "\n\n" + stats_markdown

        README_FILE.write_text(new_content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"{Colors.RED}{WARN} Failed to update README.md: {e}{Colors.RESET}")
        return False


def parse_problem_from_file(file_path: Path) -> Dict:
    """Infer problem number, title, difficulty, and metadata from filename and contents."""
    stem = file_path.stem
    ext = file_path.suffix

    # Attempt to extract leading number: "0020_valid_parentheses", "20. Valid Parentheses", "20-valid-parentheses"
    num_str = ""
    title_raw = stem

    num_match = re.match(r"^(\d+)[\s._-]+(.+)$", stem)
    if num_match:
        raw_num = num_match.group(1)
        try:
            num_str = format_problem_num(raw_num)
        except ValueError:
            num_str = ""
        title_raw = num_match.group(2)
    else:
        # Check trailing number e.g. "two_sum_1"
        trail_match = re.match(r"^(.+?)[\s._-]+(\d+)$", stem)
        if trail_match:
            raw_num = trail_match.group(2)
            try:
                num_str = format_problem_num(raw_num)
            except ValueError:
                num_str = ""
            title_raw = trail_match.group(1)

    # Clean title
    clean_title = re.sub(r"[\s._-]+", " ", title_raw).strip()
    clean_title = clean_title.title()
    slug = slugify(clean_title if clean_title else stem)

    # Defaults
    difficulty = "Medium"
    tags = []
    approach = ""
    time_comp = "O(n)"
    space_comp = "O(1)"

    # Inspect file comments for hints
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        diff_m = re.search(r"(?:Difficulty|diff)\s*[:=]\s*(Easy|Medium|Hard)", content, re.IGNORECASE)
        if diff_m:
            difficulty = diff_m.group(1).capitalize()

        tags_m = re.search(r"(?:Tags|topics)\s*[:=]\s*([^\r\n]+)", content, re.IGNORECASE)
        if tags_m:
            tags = [t.strip() for t in tags_m.group(1).split(",") if t.strip()]

        approach_m = re.search(r"(?:Approach|summary)\s*[:=]\s*([^\r\n]+)", content, re.IGNORECASE)
        if approach_m:
            approach = approach_m.group(1).strip()

        time_m = re.search(r"(?:Time|Time Complexity)\s*[:=]\s*([^\r\n]+)", content, re.IGNORECASE)
        if time_m:
            time_comp = time_m.group(1).strip()

        space_m = re.search(r"(?:Space|Space Complexity)\s*[:=]\s*([^\r\n]+)", content, re.IGNORECASE)
        if space_m:
            space_comp = space_m.group(1).strip()
    except Exception:
        pass

    # File timestamps
    mtime = file_path.stat().st_mtime
    ctime = file_path.stat().st_ctime

    return {
        "file_path": file_path,
        "filename": file_path.name,
        "number": num_str,
        "title": clean_title if clean_title else stem,
        "slug": slug,
        "difficulty": difficulty,
        "tags": tags,
        "approach": approach,
        "time": time_comp,
        "space": space_comp,
        "mtime": mtime,
        "ctime": ctime,
    }


def find_backlog_files(backlog_dir: Path) -> List[Path]:
    """Scan backlog folder for solution files excluding hidden files and metadata."""
    if not backlog_dir.exists():
        return []
    valid_exts = {".py", ".cpp", ".cc", ".c", ".java", ".js", ".ts", ".go", ".rs", ".cs", ".kt", ".swift", ".sql"}
    files = []
    for f in backlog_dir.iterdir():
        if f.is_file() and f.suffix.lower() in valid_exts and f.name != ".gitkeep" and not f.name.startswith("."):
            files.append(f)
    return files


def load_solve_order_file(custom_order_path: Optional[Path] = None) -> List[str]:
    """Load ordered lines from solve_order.txt if present."""
    order_file = None
    if custom_order_path and custom_order_path.exists():
        order_file = custom_order_path
    elif SOLVE_ORDER_FILE.exists():
        order_file = SOLVE_ORDER_FILE
    elif BACKLOG_SOLVE_ORDER_FILE.exists():
        order_file = BACKLOG_SOLVE_ORDER_FILE

    if not order_file:
        return []

    lines = []
    try:
        content = order_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                lines.append(line)
    except Exception as e:
        print(f"{Colors.YELLOW}{WARN} Could not read solve order file {order_file}: {e}{Colors.RESET}")
    return lines


def match_solve_order(pending: List[Dict], order_lines: List[str]) -> List[Dict]:
    """Match and sort pending problems according to order_lines."""
    if not order_lines:
        return pending

    ordered: List[Dict] = []
    remaining = list(pending)

    for entry in order_lines:
        clean_entry = entry.lower().strip()
        matched = None
        for item in remaining:
            # Match by 4-digit number, raw integer number, or slug
            if item["number"] and (item["number"] == clean_entry or str(int(item["number"])) == clean_entry):
                matched = item
                break
            if item["slug"] == slugify(clean_entry) or slugify(item["title"]) == slugify(clean_entry):
                matched = item
                break
            if item["filename"].lower() == clean_entry or Path(item["filename"]).stem.lower() == clean_entry:
                matched = item
                break

        if matched:
            ordered.append(matched)
            remaining.remove(matched)

    # Append any remaining pending problems that weren't listed in solve_order.txt
    if remaining:
        # Sort remaining by file modification time
        remaining.sort(key=lambda x: x["mtime"])
        ordered.extend(remaining)

    return ordered


def prompt_user_for_details(item: Dict, index: int, total: int) -> Dict:
    """Prompt user to confirm/fill missing details for a pending problem."""
    print(f"\n{Colors.BOLD}--- [{index}/{total}] Problem Details for '{item['filename']}' ---{Colors.RESET}")

    # Number
    num_val = item["number"]
    while not num_val:
        raw_num = input(f"{Colors.CYAN}Problem Number (e.g. 20, 121): {Colors.RESET}").strip()
        try:
            num_val = format_problem_num(raw_num)
        except ValueError:
            print(f"{Colors.RED}Please enter a valid numeric problem number.{Colors.RESET}")
    item["number"] = num_val

    # Title
    cur_title = item["title"]
    title_in = input(f"{Colors.CYAN}Problem Title [{cur_title}]: {Colors.RESET}").strip()
    if title_in:
        item["title"] = title_in
    item["slug"] = slugify(item["title"])

    # Difficulty
    cur_diff = item["difficulty"]
    diff_in = input(f"{Colors.CYAN}Difficulty (1: Easy, 2: Medium, 3: Hard) [{cur_diff}]: {Colors.RESET}").strip()
    if diff_in in ["1", "E", "Easy", "easy"]:
        item["difficulty"] = "Easy"
    elif diff_in in ["2", "M", "Medium", "medium"]:
        item["difficulty"] = "Medium"
    elif diff_in in ["3", "H", "Hard", "hard"]:
        item["difficulty"] = "Hard"

    # Tags
    cur_tags = ", ".join(item["tags"]) if item["tags"] else "Array"
    tags_in = input(f"{Colors.CYAN}Tags / Topics [{cur_tags}]: {Colors.RESET}").strip()
    if tags_in:
        item["tags"] = [t.strip() for t in tags_in.split(",") if t.strip()]
    elif not item["tags"]:
        item["tags"] = [cur_tags]

    # Approach
    cur_app = item["approach"] if item["approach"] else "Optimal algorithm implementation."
    app_in = input(f"{Colors.CYAN}Approach Summary [{cur_app}]: {Colors.RESET}").strip()
    if app_in:
        item["approach"] = app_in
    else:
        item["approach"] = cur_app

    # Complexity
    cur_time = item["time"]
    time_in = input(f"{Colors.CYAN}Time Complexity [{cur_time}]: {Colors.RESET}").strip()
    if time_in:
        item["time"] = time_in

    cur_space = item["space"]
    space_in = input(f"{Colors.CYAN}Space Complexity [{cur_space}]: {Colors.RESET}").strip()
    if space_in:
        item["space"] = space_in

    return item


def display_detected_order(ordered_items: List[Dict], source_desc: str):
    """Print the detected solve order table."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}🔍 Detected Solve Order ({source_desc}):{Colors.RESET}")
    print(f"{'#':<4} | {'Prob #':<8} | {'Problem Title':<35} | {'Diff':<8} | {'File':<25}")
    print("-" * 88)
    for idx, it in enumerate(ordered_items, 1):
        num_disp = it["number"] if it["number"] else "????"
        title_disp = it["title"][:33]
        diff_disp = it["difficulty"]
        file_disp = it["filename"][:23]
        print(f"{idx:<4} | {num_disp:<8} | {title_disp:<35} | {diff_disp:<8} | {file_disp:<25}")
    print("-" * 88)


def display_date_mapping(ordered_items: List[Dict], date_mappings: List[Tuple[Dict, datetime.date, str]]):
    """Print the date mapping schedule."""
    print(f"\n{Colors.GREEN}{Colors.BOLD}📅 Consecutive Date Mapping Schedule (1 commit/day ending today):{Colors.RESET}")
    print(f"{'Seq':<4} | {'Commit Date':<12} | {'Prob #':<8} | {'Problem Title':<32} | {'Diff':<8} | {'Source File'}")
    print("=" * 95)
    for idx, (it, d, dt_str) in enumerate(date_mappings, 1):
        num_disp = it["number"] if it["number"] else "????"
        title_disp = it["title"][:30]
        diff_disp = it["difficulty"]
        date_disp = d.strftime("%Y-%m-%d")
        print(f"{idx:<4} | {date_disp:<12} | {num_disp:<8} | {title_disp:<32} | {diff_disp:<8} | {it['filename']}")
    print("=" * 95)


def run_backdated_commit(item: Dict, commit_date_str: str) -> bool:
    """Create directory, move file, generate notes, update README, and git commit with backdated timestamp."""
    num_str = item["number"]
    title = item["title"]
    difficulty = item["difficulty"]
    slug = item["slug"]
    folder_name = f"{num_str}-{slug}"
    target_dir = SOLUTIONS_DIR / folder_name

    target_dir.mkdir(parents=True, exist_ok=True)

    # Move source file into solutions/
    source_file = item["file_path"]
    dest_filename = f"solution{source_file.suffix}"
    dest_path = target_dir / dest_filename

    shutil.move(str(source_file), str(dest_path))

    # Generate notes.md
    notes_content = generate_notes_md(
        num_str=num_str,
        title=title,
        difficulty=difficulty,
        tags=item["tags"],
        approach=item["approach"],
        time_comp=item["time"],
        space_comp=item["space"],
        solution_filename=dest_filename,
    )
    (target_dir / "notes.md").write_text(notes_content, encoding="utf-8")

    # Update README stats
    update_readme_stats()

    # Backdated Git Commit
    commit_msg = f"Solve {num_str}: {title} [{difficulty.capitalize()}]"
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = commit_date_str
    env["GIT_COMMITTER_DATE"] = commit_date_str

    try:
        subprocess.run(["git", "add", "."], cwd=REPO_ROOT, check=True, env=env)
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_ROOT, check=True, env=env)
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}{WARN} Git commit failed for {title}: {e}{Colors.RESET}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="LeetCode Backfill & Backdated Commit Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--backlog", help="Custom path to backlog directory", default=str(BACKLOG_DIR))
    parser.add_argument("--order", help="Custom path to solve_order.txt")
    parser.add_argument("--dry-run", action="store_true", help="Preview solve order and date mapping without making changes")
    parser.add_argument("--yes", "-y", action="store_true", help="Auto-confirm prompts with detected/default values")

    args = parser.parse_args()
    print_banner()

    backlog_path = Path(args.backlog).resolve()
    if not backlog_path.exists():
        backlog_path.mkdir(parents=True, exist_ok=True)
        print(f"{Colors.YELLOW}{INFO} Created backlog directory at {backlog_path}{Colors.RESET}")

    # 1. Scan existing committed solutions
    committed_numbers, committed_slugs, _ = scan_committed_problems()
    print(f"{Colors.CYAN}{INFO} Found {len(committed_numbers)} already committed problems in /solutions.{Colors.RESET}")

    # 2. Scan backlog files
    backlog_files = find_backlog_files(backlog_path)
    if not backlog_files:
        print(f"{Colors.YELLOW}{WARN} No solution files found in {backlog_path}!{Colors.RESET}")
        print(f"{Colors.DIM}Drop your solved files into '{backlog_path.name}/' and run this script again.{Colors.RESET}")
        return

    # Parse all backlog files
    parsed_items = [parse_problem_from_file(f) for f in backlog_files]

    # Filter down to uncommitted pending problems
    pending_items: List[Dict] = []
    skipped_count = 0
    for it in parsed_items:
        if it["number"] and it["number"] in committed_numbers:
            skipped_count += 1
            continue
        if it["slug"] in committed_slugs:
            skipped_count += 1
            continue
        pending_items.append(it)

    print(f"{Colors.CYAN}{INFO} Backlog scan results: {len(backlog_files)} total files, {skipped_count} already committed, {Colors.BOLD}{len(pending_items)} pending uncommitted.{Colors.RESET}")

    if not pending_items:
        print(f"{Colors.GREEN}{CHECK} All problems in backlog are already committed! Nothing to process.{Colors.RESET}")
        return

    # 3. Determine Solve Order (Priority: solve_order.txt -> File metadata -> Interactive)
    custom_order_file = Path(args.order).resolve() if args.order else None
    order_lines = load_solve_order_file(custom_order_file)

    if order_lines:
        source_desc = "Loaded from solve_order.txt"
        ordered_items = match_solve_order(pending_items, order_lines)
    else:
        source_desc = "File System Timestamps (Creation/Modified date)"
        ordered_items = sorted(pending_items, key=lambda x: x["mtime"])

    # Display detected order
    display_detected_order(ordered_items, source_desc)

    # Interactive Confirmation / Reordering if not --yes
    if not args.yes:
        confirm = input(f"\n{Colors.BOLD}Is this solve order correct? ([Y]es / [r]eorder / [q]uit): {Colors.RESET}").strip().lower()
        if confirm in ["q", "quit"]:
            print("Operation aborted by user.")
            return
        elif confirm in ["r", "reorder"]:
            print(f"{Colors.CYAN}Enter the new order using comma-separated numbers (e.g. '3, 1, 2'): {Colors.RESET}")
            order_input = input("New order: ").strip()
            try:
                indices = [int(i.strip()) - 1 for i in order_input.split(",") if i.strip()]
                if len(indices) == len(ordered_items) and all(0 <= idx < len(ordered_items) for idx in indices):
                    ordered_items = [ordered_items[idx] for idx in indices]
                    print(f"{Colors.GREEN}{CHECK} Reordered successfully!{Colors.RESET}")
                    display_detected_order(ordered_items, "Custom User Reorder")
                else:
                    print(f"{Colors.RED}{WARN} Invalid index sequence. Keeping previous order.{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}{WARN} Failed to parse reordering: {e}. Keeping previous order.{Colors.RESET}")

    # Fill in missing numbers or titles interactively if needed
    for idx, it in enumerate(ordered_items, 1):
        if not it["number"] or not it["title"] or not args.yes:
            if not args.yes:
                ordered_items[idx - 1] = prompt_user_for_details(it, idx, len(ordered_items))

    # 4. Consecutive Date Mapping (1 commit/day ending today)
    N = len(ordered_items)
    today = datetime.date.today()
    tz_offset = get_local_timezone_offset()

    date_mappings: List[Tuple[Dict, datetime.date, str]] = []
    for i, it in enumerate(ordered_items):
        days_back = N - 1 - i
        assigned_date = today - datetime.timedelta(days=days_back)
        commit_dt_str = f"{assigned_date.strftime('%Y-%m-%d')} 20:00:00 {tz_offset}"
        date_mappings.append((it, assigned_date, commit_dt_str))

    display_date_mapping(ordered_items, date_mappings)

    if args.dry_run:
        print(f"\n{Colors.YELLOW}{INFO} [DRY-RUN MODE] No files were moved and no git commits were created.{Colors.RESET}")
        return

    # Final execution prompt if not --yes
    if not args.yes:
        proceed = input(f"\n{Colors.BOLD}Proceed with creating {N} backdated commits? [Y/n]: {Colors.RESET}").strip().lower()
        if proceed not in ["", "y", "yes"]:
            print("Operation cancelled.")
            return

    # 5. Process Backlog & Create Commits
    print(f"\n{Colors.CYAN}{Colors.BOLD}🚀 Processing backlog and creating backdated commits...{Colors.RESET}")
    success_count = 0
    for idx, (it, assigned_date, commit_dt_str) in enumerate(date_mappings, 1):
        print(f"\n[{idx}/{N}] Committing: {Colors.BOLD}{it['number']} - {it['title']}{Colors.RESET} (Assigned: {assigned_date.strftime('%Y-%m-%d')})")
        if run_backdated_commit(it, commit_dt_str):
            success_count += 1
            print(f"{Colors.GREEN}{CHECK} Committed successfully!{Colors.RESET}")

    print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Successfully created {success_count}/{N} backdated commits!{Colors.RESET}")

    # 6. Review Before Push
    print(f"\n{Colors.CYAN}{Colors.BOLD}📜 Git Commit History Review:{Colors.RESET}")
    print("=" * 80)
    try:
        log_res = subprocess.run(
            ["git", "log", f"-n{N + 3}", "--pretty=format:%h | %ad | %s", "--date=iso"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        print(log_res.stdout)
    except Exception as e:
        print(f"{Colors.YELLOW}Could not print git log: {e}{Colors.RESET}")
    print("=" * 80)

    # 7. Ask before pushing
    push_confirm = input(f"\n{Colors.BOLD}Would you like to push these commits to GitHub now? [y/N]: {Colors.RESET}").strip().lower()
    if push_confirm in ["y", "yes"]:
        print(f"{Colors.CYAN}[...] Pushing commits to GitHub...{Colors.RESET}")
        try:
            res = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_ROOT, capture_output=True, text=True, check=True)
            print(f"{Colors.GREEN}{CHECK} Successfully pushed to GitHub!{Colors.RESET}")
            print(res.stdout)
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}{WARN} Git push failed: {e.stderr.strip()}{Colors.RESET}")
    else:
        print(f"{Colors.DIM}{INFO} Commits remain safely recorded locally. Push anytime via 'git push origin main'.{Colors.RESET}")


if __name__ == "__main__":
    main()
