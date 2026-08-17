#!/usr/bin/env python3
"""
LeetCode Solution Automation & Tracker
---------------------------------------
Automates organizing, documenting, tracking, and committing LeetCode solutions.

Usage:
    python commit_solution.py                     # Interactive mode (checks inbox/ or prompts)
    python commit_solution.py --file solution.py  # Specify file
    python commit_solution.py --update-readme     # Refresh README stats only
    python commit_solution.py --help              # View all options
"""

import os
import sys
import re
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Base repository root (directory containing this script)
REPO_ROOT = Path(__file__).resolve().parent
SOLUTIONS_DIR = REPO_ROOT / "solutions"
INBOX_DIR = REPO_ROOT / "inbox"
README_FILE = REPO_ROOT / "README.md"

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

# ANSI Colors for clean terminal output
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
    print("             LEETCODE SOLUTION AUTOMATOR & TRACKER              ")
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
    """Return markdown badge/formatted tag for difficulty."""
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
    """Generate rich notes.md markdown content."""
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


def scan_solutions() -> List[Dict]:
    """Scan the solutions directory and parse metadata from existing problem folders."""
    if not SOLUTIONS_DIR.exists():
        return []

    problems = []
    for item in sorted(SOLUTIONS_DIR.iterdir()):
        if item.is_dir() and re.match(r"^\d{4}-", item.name):
            num_str = item.name[:4]
            slug = item.name[5:]
            title_guess = slug.replace("-", " ").title()
            notes_file = item / "notes.md"
            difficulty = "Medium"
            tags = []
            problem_url = f"https://leetcode.com/problems/{slug}/"

            # Check for solution file
            solution_files = [f for f in item.iterdir() if f.is_file() and f.name != "notes.md"]
            sol_link = ""
            sol_lang = "Solution"
            if solution_files:
                sol_file = solution_files[0]
                sol_lang = get_language_from_ext(sol_file.suffix)
                sol_link = f"[{sol_lang}](solutions/{item.name}/{sol_file.name})"
            else:
                sol_link = "—"

            # Parse notes.md if available
            if notes_file.exists():
                try:
                    text = notes_file.read_text(encoding="utf-8")
                    # Extract title
                    title_match = re.search(r"^#\s+\d+\.\s+(.+)$", text, re.MULTILINE)
                    if title_match:
                        title_guess = title_match.group(1).strip()

                    # Extract difficulty
                    if "Easy" in text:
                        difficulty = "Easy"
                    elif "Hard" in text:
                        difficulty = "Hard"
                    elif "Medium" in text:
                        difficulty = "Medium"

                    # Extract tags
                    tags_match = re.search(r"## 🏷️ Topics / Tags\s*\n([^\n]+)", text)
                    if tags_match:
                        raw_tags = tags_match.group(1)
                        tags = [t.strip("` ") for t in raw_tags.split(",") if t.strip()]

                    # Extract url
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
    return problems


def update_readme_stats(problems: Optional[List[Dict]] = None) -> bool:
    """Update the statistics table and problem index in README.md."""
    if problems is None:
        problems = scan_solutions()

    if not README_FILE.exists():
        print(f"{Colors.YELLOW}[!] README.md not found at {README_FILE}{Colors.RESET}")
        return False

    total = len(problems)
    easy_count = sum(1 for p in problems if p["difficulty"].lower() == "easy")
    med_count = sum(1 for p in problems if p["difficulty"].lower() == "medium")
    hard_count = sum(1 for p in problems if p["difficulty"].lower() == "hard")

    # Generate Stats Block
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
        print(f"{Colors.GREEN}{CHECK} README.md statistics successfully updated! (Total: {total}){Colors.RESET}")
        return True
    except Exception as e:
        print(f"{Colors.RED}{WARN} Failed to update README.md: {e}{Colors.RESET}")
        return False


def run_git_commands(problem_num: str, title: str, difficulty: str, no_push: bool = False):
    """Execute git add, commit, and push."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}--> Running Git Automation...{Colors.RESET}")
    commit_msg = f"Solve {problem_num}: {title} [{difficulty.capitalize()}]"

    # Git Add
    try:
        subprocess.run(["git", "add", "."], cwd=REPO_ROOT, check=True)
        print(f"{Colors.GREEN}{CHECK} git add .{Colors.RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}{WARN} git add failed: {e}{Colors.RESET}")
        return False

    # Git Commit
    try:
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_ROOT, check=True)
        print(f"{Colors.GREEN}{CHECK} git commit -m \"{commit_msg}\"{Colors.RESET}")
    except subprocess.CalledProcessError:
        # Check if working tree clean
        print(f"{Colors.YELLOW}{INFO} No new changes to commit.{Colors.RESET}")

    # Git Push
    if no_push:
        print(f"{Colors.DIM}{INFO} Skipped git push (--no-push flag active){Colors.RESET}")
        return True

    print(f"{Colors.CYAN}[...] Attempting git push...{Colors.RESET}")
    try:
        result = subprocess.run(
            ["git", "push"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            print(f"{Colors.GREEN}{CHECK} git push successful!{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}{WARN} git push did not complete: {result.stderr.strip()}{Colors.RESET}")
            print(f"{Colors.DIM}    Hint: If remote origin is not configured yet, connect it via:{Colors.RESET}")
            print(f"{Colors.DIM}    git remote add origin https://github.com/<username>/leetcode.git{Colors.RESET}")
            print(f"{Colors.DIM}    git push -u origin main{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.YELLOW}{WARN} git push skipped or timed out: {e}{Colors.RESET}")

    return True


def find_inbox_files() -> List[Path]:
    """Find files inside the inbox directory excluding .gitkeep."""
    if not INBOX_DIR.exists():
        INBOX_DIR.mkdir(parents=True, exist_ok=True)
        return []
    return [
        f for f in INBOX_DIR.iterdir()
        if f.is_file() and f.name != ".gitkeep" and not f.name.startswith(".")
    ]


def interactive_prompt(args_file: Optional[str] = None) -> Tuple[Path, str, str, str, List[str], str, str, str]:
    """Interactively prompt user for problem details."""
    print_banner()

    # 1. Determine solution file
    source_file: Optional[Path] = None
    if args_file:
        source_file = Path(args_file).resolve()
        if not source_file.exists():
            print(f"{Colors.RED}{WARN} Specified file does not exist: {source_file}{Colors.RESET}")
            sys.exit(1)
    else:
        inbox_files = find_inbox_files()
        if len(inbox_files) == 1:
            choice = input(f"{Colors.CYAN}Found solution file in inbox: '{inbox_files[0].name}'. Use it? [Y/n]: {Colors.RESET}").strip().lower()
            if choice in ("", "y", "yes"):
                source_file = inbox_files[0]
        elif len(inbox_files) > 1:
            print(f"{Colors.CYAN}Multiple files found in inbox:{Colors.RESET}")
            for idx, f in enumerate(inbox_files, 1):
                print(f"  [{idx}] {f.name}")
            sel = input(f"{Colors.CYAN}Select file number (1-{len(inbox_files)}) or enter custom path: {Colors.RESET}").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(inbox_files):
                source_file = inbox_files[int(sel) - 1]

        while not source_file:
            path_str = input(f"{Colors.BOLD}Enter path to solution file (or drop into inbox/ and press Enter): {Colors.RESET}").strip().strip('"\'')
            if not path_str:
                inbox_files = find_inbox_files()
                if inbox_files:
                    source_file = inbox_files[0]
                    break
                print(f"{Colors.YELLOW}No files found in inbox. Please specify a file path.{Colors.RESET}")
                continue
            cand = Path(path_str).resolve()
            if cand.exists() and cand.is_file():
                source_file = cand
                break
            else:
                print(f"{Colors.RED}File not found: {cand}. Please try again.{Colors.RESET}")

    print(f"\n{Colors.GREEN}{CHECK} Using solution file: {Colors.BOLD}{source_file.name}{Colors.RESET}")

    # 2. Problem Number
    num_input = ""
    while not num_input:
        raw_num = input(f"\n{Colors.BOLD}1. Problem Number (e.g. 1, 217): {Colors.RESET}").strip()
        try:
            num_input = format_problem_num(raw_num)
        except ValueError:
            print(f"{Colors.RED}Please enter a valid numeric problem number.{Colors.RESET}")

    # 3. Problem Title
    title_input = ""
    while not title_input:
        title_input = input(f"{Colors.BOLD}2. Problem Title (e.g. 'Two Sum', 'Contains Duplicate'): {Colors.RESET}").strip()
        if not title_input:
            print(f"{Colors.RED}Title cannot be empty.{Colors.RESET}")

    # 4. Difficulty
    diff_input = ""
    while diff_input not in ["Easy", "Medium", "Hard"]:
        raw_diff = input(f"{Colors.BOLD}3. Difficulty ([1] Easy, [2] Medium, [3] Hard): {Colors.RESET}").strip().capitalize()
        if raw_diff in ["1", "E", "Easy"]:
            diff_input = "Easy"
        elif raw_diff in ["2", "M", "Med", "Medium"]:
            diff_input = "Medium"
        elif raw_diff in ["3", "H", "Hard"]:
            diff_input = "Hard"
        else:
            print(f"{Colors.RED}Invalid selection. Choose 1 (Easy), 2 (Medium), or 3 (Hard).{Colors.RESET}")

    # 5. Tags / Topics
    tags_raw = input(f"{Colors.BOLD}4. Tags / Topics (comma-separated, e.g. Array, Hash Table, DP): {Colors.RESET}").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    # 6. Approach Summary
    approach = input(f"{Colors.BOLD}5. Approach Summary (brief 1-2 line explanation): {Colors.RESET}").strip()

    # 7. Time & Space Complexity
    time_comp = input(f"{Colors.BOLD}6. Time Complexity [Default: O(n)]: {Colors.RESET}").strip() or "O(n)"
    space_comp = input(f"{Colors.BOLD}7. Space Complexity [Default: O(1)]: {Colors.RESET}").strip() or "O(1)"

    return source_file, num_input, title_input, diff_input, tags, approach, time_comp, space_comp


def process_solution(
    source_file: Path,
    num_str: str,
    title: str,
    difficulty: str,
    tags: List[str],
    approach: str,
    time_comp: str,
    space_comp: str,
    no_push: bool = False,
):
    """Create problem directory, move solution file, generate notes.md, update README, and git commit."""
    slug = slugify(title)
    folder_name = f"{num_str}-{slug}"
    target_dir = SOLUTIONS_DIR / folder_name

    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n{Colors.GREEN}{CHECK} Scaffolded directory: solutions/{folder_name}/{Colors.RESET}")

    # Move or copy solution file
    dest_filename = f"solution{source_file.suffix}"
    dest_path = target_dir / dest_filename

    # If source is in inbox, move it; otherwise copy it
    if INBOX_DIR in source_file.parents or source_file.parent == INBOX_DIR:
        shutil.move(str(source_file), str(dest_path))
        print(f"{Colors.GREEN}{CHECK} Moved inbox file -> solutions/{folder_name}/{dest_filename}{Colors.RESET}")
    else:
        shutil.copy2(str(source_file), str(dest_path))
        print(f"{Colors.GREEN}{CHECK} Copied file -> solutions/{folder_name}/{dest_filename}{Colors.RESET}")

    # Generate notes.md
    notes_content = generate_notes_md(
        num_str=num_str,
        title=title,
        difficulty=difficulty,
        tags=tags,
        approach=approach,
        time_comp=time_comp,
        space_comp=space_comp,
        solution_filename=dest_filename,
    )
    notes_path = target_dir / "notes.md"
    notes_path.write_text(notes_content, encoding="utf-8")
    print(f"{Colors.GREEN}{CHECK} Generated notes.md template!{Colors.RESET}")

    # Update README.md stats
    update_readme_stats()

    # Git commit and push
    run_git_commands(num_str, title, difficulty, no_push=no_push)

    print(f"\n{Colors.CYAN}{Colors.BOLD}*** Successfully tracked LeetCode #{int(num_str)}: {title}! ***{Colors.RESET}\n")



def main():
    parser = argparse.ArgumentParser(
        description="LeetCode Solution Automator & Repository Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-f", "--file", help="Path to the solution file")
    parser.add_argument("-n", "--number", help="LeetCode problem number (e.g. 1, 217)")
    parser.add_argument("-t", "--title", help="LeetCode problem title (e.g. 'Two Sum')")
    parser.add_argument("-d", "--difficulty", choices=["Easy", "Medium", "Hard", "easy", "medium", "hard"], help="Difficulty level")
    parser.add_argument("--tags", help="Comma-separated topic tags (e.g. 'Array, Hash Table')")
    parser.add_argument("--approach", default="", help="Brief approach explanation")
    parser.add_argument("--time", default="O(n)", help="Time complexity (default: O(n))")
    parser.add_argument("--space", default="O(1)", help="Space complexity (default: O(1))")
    parser.add_argument("--no-push", action="store_true", help="Skip git push")
    parser.add_argument("--update-readme", action="store_true", help="Only refresh README statistics and exit")

    args = parser.parse_args()

    # If only updating README
    if args.update_readme:
        print_banner()
        update_readme_stats()
        return

    # Check if all required CLI parameters are provided
    if args.file and args.number and args.title and args.difficulty:
        source_file = Path(args.file).resolve()
        if not source_file.exists():
            print(f"{Colors.RED}[!] Solution file not found: {source_file}{Colors.RESET}")
            sys.exit(1)
        num_str = format_problem_num(args.number)
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        difficulty = args.difficulty.capitalize()
        process_solution(
            source_file=source_file,
            num_str=num_str,
            title=args.title,
            difficulty=difficulty,
            tags=tags,
            approach=args.approach,
            time_comp=args.time,
            space_comp=args.space,
            no_push=args.no_push,
        )
    else:
        # Launch Interactive Prompt
        (
            source_file,
            num_str,
            title,
            difficulty,
            tags,
            approach,
            time_comp,
            space_comp,
        ) = interactive_prompt(args.file)

        process_solution(
            source_file=source_file,
            num_str=num_str,
            title=title,
            difficulty=difficulty,
            tags=tags,
            approach=approach,
            time_comp=time_comp,
            space_comp=space_comp,
            no_push=args.no_push,
        )


if __name__ == "__main__":
    main()
