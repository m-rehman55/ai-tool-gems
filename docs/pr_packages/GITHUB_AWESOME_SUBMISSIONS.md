# Curated GitHub Awesome Lists PR Submission Packages
**Project:** AI Tool Gems (`https://aitoolgems.tech`)  
**Objective:** Earn authoritative, white-hat developer backlinks and repository citations from top starred GitHub Awesome AI lists.  
**Compliance Standard:** Strict adherence to each repository's `CONTRIBUTING.md` (proper alphabetical ordering, concise non-marketing descriptions, clean Markdown links).

---

## Submission 1: `eudk/awesome-ai-tools` (Stars: 10,000+)

* **Repository:** `https://github.com/eudk/awesome-ai-tools`
* **Target File:** `README.md`
* **Target Section:** `## AI Tool Directories & Resources`
* **Status in Tracker:** Staged (`submitted_pending_review`)

### PR Title:
```text
Add AI Tool Gems to AI Tool Directories & Resources
```

### Git Branch & Commit Message:
```bash
git checkout -b add-aitoolgems-directory
git commit -m "docs: add AI Tool Gems to AI Tool Directories & Resources"
```

### Exact Markdown Line to Add:
```markdown
- [AI Tool Gems](https://aitoolgems.tech/) - Curated directory of 65+ AI tools with a downloadable PKR & USD pricing index, localized buyer guides, and machine-readable llms.txt coverage.
```

### PR Description:
```markdown
### Summary
This PR adds [AI Tool Gems](https://aitoolgems.tech/) to the `AI Tool Directories & Resources` section.

### Details
- **Website:** https://aitoolgems.tech/
- **Open Dataset:** https://aitoolgems.tech/prices/
- **Description:** Curates 65+ AI tools with detailed buyer guides, transparent pricing tables (PKR and USD), and downloadable open datasets (`ai-tools-pricing-pakistan.csv` / `ai-tools-pricing-pakistan.json`).
- Adheres to repository formatting guidelines and alphabetical ordering.
```

---

## Submission 2: `steven2358/awesome-generative-ai` (Stars: 14,000+)

* **Repository:** `https://github.com/steven2358/awesome-generative-ai`
* **Target File:** `README.md`
* **Target Section:** `## Aggregators & Directories`

### PR Title:
```text
docs: add AI Tool Gems directory and pricing index
```

### Exact Markdown Line to Add:
```markdown
- [AI Tool Gems](https://aitoolgems.tech/) - Directory tracking generative AI tools, foundation model comparisons, and an open machine-readable pricing index.
```

### PR Description:
```markdown
### What does this PR do?
Adds **AI Tool Gems** to the list of Generative AI aggregators and directories.

- URL: https://aitoolgems.tech/
- Open machine-readable data: https://aitoolgems.tech/prices/
- Clean non-promotional description matching the repository style guide.
```

---

## Submission 3: `mahseema/awesome-ai-tools` (Stars: 5,000+)

* **Repository:** `https://github.com/mahseema/awesome-ai-tools`
* **Target File:** `README.md`
* **Target Section:** `## Directories & Indexes`

### PR Title:
```text
Add AI Tool Gems to Directories
```

### Exact Markdown Line to Add:
```markdown
- [AI Tool Gems](https://aitoolgems.tech/) - Comprehensive AI software directory featuring detailed feature reviews, pricing comparisons, and open-source datasets.
```

---

## Local Git CLI Command Sequence to Submit Any Awesome List PR:

```bash
# 1. Fork target repository on GitHub Web UI
# 2. Clone your fork locally
git clone https://github.com/m-rehman55/awesome-ai-tools.git
cd awesome-ai-tools

# 3. Create clean feature branch
git checkout -b add-aitoolgems

# 4. Insert Markdown entry in alphabetical order in README.md
# (Edit README.md)

# 5. Commit and push
git commit -am "docs: add AI Tool Gems to AI Directories"
git push origin add-aitoolgems

# 6. Open Pull Request using GitHub CLI
gh pr create --title "Add AI Tool Gems to AI Tool Directories" --body "Adds AI Tool Gems (https://aitoolgems.tech/) to AI Directories list."
```
