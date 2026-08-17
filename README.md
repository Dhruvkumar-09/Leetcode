<div align="center">

# 🧠 LeetCode Practice & Solution Tracker

Personal repository for structured LeetCode practice, solutions, approach notes, and complexity analysis with fully automated folder scaffolding, Git committing, and stats tracking.

<p align="center">
  <img src="https://img.shields.io/badge/LeetCode-Practice-FFA116?style=for-the-badge&logo=leetcode&logoColor=black" alt="LeetCode" />
  <img src="https://img.shields.io/badge/Language-Python_3-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3" />
  <img src="https://img.shields.io/badge/Automation-CLI_Script-00C7B7?style=for-the-badge&logo=gnubash&logoColor=white" alt="Automation" />
</p>

</div>

---

## 📂 Repository Structure

The repository is organized cleanly with zero-padded problem numbers and slugified titles for optimal sorting and searchability:

```text
leetcode/
├── inbox/                        # Drop zone for incoming raw solution files
│   └── .gitkeep
├── solutions/                    # Scaffolding for all solved problems
│   ├── 0001-two-sum/
│   │   ├── notes.md              # Problem link, approach, complexity, tags
│   │   └── solution.py           # Clean, tested solution implementation
│   └── 0217-contains-duplicate/
│       ├── notes.md
│       └── solution.py
├── .gitignore                    # Python cache, OS files, and temp ignores
├── commit_solution.py            # Local automation & tracker script
└── README.md                     # Overview, documentation, and live stats table
```

### 🏷️ Naming Conventions
- **Folder Format**: `solutions/<4-digit-number>-<slugified-title>/` (e.g., `solutions/0001-two-sum/`)
- **Solution File**: `solution.py` (or `solution.cpp`, `solution.java`, `solution.ts` based on language)
- **Notes File**: `notes.md` containing formatted difficulty badges, LeetCode URLs, topic tags, time/space complexity analysis, and approach breakdowns.

---

<!-- STATS:START -->
### 📊 Practice Overview

| Total Solved | 🟢 Easy | 🟡 Medium | 🔴 Hard |
| :---: | :---: | :---: | :---: |
| **4** | **4** | **0** | **0** |

---

### 📑 Solved Problems Index

| # | Problem | Difficulty | Solution | Notes | Tags |
| :---: | :--- | :---: | :---: | :---: | :--- |
| `0001` | [Two Sum](https://leetcode.com/problems/two-sum/) | 🟢 `Easy` | [Python](solutions/0001-two-sum/solution.py) | [Notes](solutions/0001-two-sum/notes.md) | `Array`, `Hash Table` |
| `0121` | [Best Time To Buy And Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | 🟢 `Easy` | [Python](solutions/0121-best-time-to-buy-and-sell-stock/solution.py) | [Notes](solutions/0121-best-time-to-buy-and-sell-stock/notes.md) | `Array`, `Dynamic Programming` |
| `0217` | [Contains Duplicate](https://leetcode.com/problems/contains-duplicate/) | 🟢 `Easy` | [Python](solutions/0217-contains-duplicate/solution.py) | [Notes](solutions/0217-contains-duplicate/notes.md) | `Array`, `Hash Table`, `Sorting` |
| `0242` | [Valid Anagram](https://leetcode.com/problems/valid-anagram/) | 🟢 `Easy` | [Python](solutions/0242-valid-anagram/solution.py) | [Notes](solutions/0242-valid-anagram/notes.md) | `Hash Table`, `String`, `Sorting` |
<!-- STATS:END -->

---

## ⚡ Automation Script (`commit_solution.py`)

The repository includes a comprehensive Python automation tool that completely eliminates manual folder creation, documentation formatting, and git commands.

### 🌟 Key Capabilities
1. **Inbox Detection**: Automatically detects solution files dropped into `inbox/` or lets you select one interactively.
2. **Auto-Formatting & Slugs**: Automatically pads problem numbers (e.g. `1` ➔ `0001`) and converts titles to URL-safe slugs (e.g. `Two Sum` ➔ `two-sum`).
3. **Structured Notes**: Generates complete `notes.md` with problem URLs, complexity tables, and topic tags.
4. **Live README Sync**: Dynamically updates the statistics overview table and solved problem index above.
5. **Git Workflow**: Automatically stages changes, creates standardized commit messages (e.g. `Solve 0001: Two Sum [Easy]`), and pushes to your remote repository.

---

## 🚀 How to Use the Automation

### 1. Interactive Mode (Recommended)
Simply drop your solution file into the `inbox/` directory and run:

```bash
python commit_solution.py
```

The script will guide you step-by-step:
```text
╔══════════════════════════════════════════════════════════════╗
║             ⚡ LEETCODE SOLUTION AUTOMATOR ⚡                ║
╚══════════════════════════════════════════════════════════════╝

Found solution file in inbox: 'solution.py'. Use it? [Y/n]: y
[✓] Using solution file: solution.py

1. Problem Number (e.g. 1, 217): 1
2. Problem Title (e.g. 'Two Sum'): Two Sum
3. Difficulty ([1] Easy, [2] Medium, [3] Hard): 1
4. Tags / Topics (comma-separated): Array, Hash Table
5. Approach Summary: Hash map one-pass complement lookup.
6. Time Complexity [Default: O(n)]: O(n)
7. Space Complexity [Default: O(1)]: O(n)

[✓] Scaffolded directory: solutions/0001-two-sum/
[✓] Moved inbox file -> solutions/0001-two-sum/solution.py
[✓] Generated notes.md template!
[✓] README.md statistics successfully updated!
[✓] git add .
[✓] git commit -m "Solve 0001: Two Sum [Easy]"
[✓] git push successful!
```

---

### 2. Single-Line Command Mode
For fast-paced workflows, pass all arguments directly via CLI:

```bash
python commit_solution.py \
  --file inbox/my_solution.py \
  --number 704 \
  --title "Binary Search" \
  --difficulty Easy \
  --tags "Array, Binary Search" \
  --approach "Standard two-pointer binary search on sorted array." \
  --time "O(log n)" \
  --space "O(1)"
```

#### Available CLI Options:
| Flag | Short | Description | Example |
| :--- | :---: | :--- | :--- |
| `--file` | `-f` | Path to the source solution file | `-f inbox/two_sum.py` |
| `--number` | `-n` | LeetCode problem number | `-n 1` |
| `--title` | `-t` | Problem title | `-t "Two Sum"` |
| `--difficulty` | `-d` | Problem difficulty (`Easy`, `Medium`, `Hard`) | `-d Easy` |
| `--tags` | — | Comma-separated topic tags | `--tags "Array, Hash Table"` |
| `--approach` | — | Brief summary of the algorithm/approach | `--approach "Hash map lookup"` |
| `--time` | — | Time complexity (default: `O(n)`) | `--time "O(n)"` |
| `--space` | — | Space complexity (default: `O(1)`) | `--space "O(n)"` |
| `--no-push` | — | Stage and commit locally without pushing | `--no-push` |
| `--update-readme` | — | Re-scan `solutions/` and refresh README stats | `--update-readme` |

---

### 3. Re-Sync Statistics Only
If you ever manually edit problem notes or add files outside the script, refresh the README tables instantly:

```bash
python commit_solution.py --update-readme
```

---

## ⏳ Backfilling Existing Problems (`backfill_solutions.py`)

If you have a batch of already-solved problems stored locally and want to commit them to GitHub with a **chronologically backdated commit history (exactly 1 commit per day ending today)**:

### How it works:
1. **Solve Order Detection**:
   - Reads `solve_order.txt` (or `backlog/solve_order.txt`) containing problem numbers or slugs in the order you solved them on LeetCode.
   - If not found, falls back to local file timestamps.
   - Interactive prompt lets you verify or re-order before proceeding.
2. **Dynamic Uncommitted Detection**:
   - Automatically compares `backlog/` against `/solutions` and identifies all pending problems.
3. **Consecutive Date Mapping**:
   - Maps $N$ pending problems to $N$ consecutive calendar days ($Today - (N-1)$ to $Today$) at 8:00 PM local time.
4. **Local Commits & Safe Review**:
   - Generates notes, moves files, updates README stats, and creates backdated git commits locally.
   - Shows the full `git log` with timestamps and **waits for your confirmation** before pushing to GitHub.

### Backfill Commands:
```bash
# 1. Preview solve order and date assignments without making changes
python backfill_solutions.py --dry-run

# 2. Run interactive backfill
python backfill_solutions.py

# 3. Non-interactive run (uses detected solve order & date mapping)
python backfill_solutions.py --yes
```

---

## 🛠️ Setup & Git Configuration

### 1. Prerequisites
- **Python 3.8+** installed (`python --version`)
- **Git** installed (`git --version`)

### 2. Connect to your Remote GitHub Repository
If you created a new empty public repository on GitHub (e.g. `https://github.com/<your-username>/leetcode.git`):

```bash
# Navigate to the repo folder
cd leetcode

# Link to your remote GitHub repository
git remote add origin https://github.com/<your-username>/leetcode.git

# Set default branch to main and push initial files
git branch -M main
git push -u origin main
```

### 3. Git Credentials Setup (If not already configured)
Ensure Git knows your commit identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

For seamless authenticated pushes on Windows:
```bash
git config --global credential.helper manager
```

---

## 🔮 Future Enhancements
- [x] Auto-updating stats summary and difficulty breakdown in README.
- [ ] LeetCode GraphQL API integration to auto-fetch problem title, difficulty, and description given only the problem number.
- [ ] Automated solution test runner (`pytest`) integration for inbox verification before committing.
- [ ] Multi-language solution comparisons (e.g. Python vs C++ benchmarks).

---

<div align="center">
  <b>Happy Coding & Algorithm Practice! 🚀</b>
</div>
