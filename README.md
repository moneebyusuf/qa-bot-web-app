# Smart QA Automation Platform

A free, local, rule-based QA automation platform built with **Python**, **Gradio**, and **Playwright**.

This project started as a simple QA bot and evolved into a lightweight Smart QA Automation Platform that can analyze websites, generate QA reports, run automated checks, capture screenshots, and export ready-to-run Pytest test files.

No paid AI APIs are required.

---

## Features

### 1. Smart Page Analyzer

Analyze any public website URL and generate a QA report.

The analyzer can detect:

- Page title
- Forms
- Input fields
- Buttons
- Links
- Working links
- Broken links
- Images missing alt text
- Accessibility issues
- Validation-related issues
- Auto-generated QA test cases
- QA score
- Screenshot path

Exports:

- JSON report
- HTML report
- Screenshot

---

### 2. Smart Test Runner

Run real automated checks against a website using Playwright.

Current checks include:

- Page loads successfully
- Page title exists
- Buttons are present
- Navigation links are present
- Forms have input fields if forms exist
- Images have alt text
- Sample links are reachable

The runner returns:

- Total tests
- Passed tests
- Failed tests
- Warnings
- Detailed recommendation per check
- JSON report
- Screenshot

---

### 3. Pytest Export

Generate a ready-to-run Playwright Pytest file from the Smart Test Runner.

Example generated test file:

```bash
reports/test_generated_example_com_20260511_134717.py

Run it with:

```bash
pytest reports/test_generated_example_com_20260511_134717.py
```

Example result:

```bash
5 passed in 2.70s
```

---

### 4. Rule-Based Test Case Generator

Generate basic QA test cases from a feature description without using paid AI APIs.

Example input:

```text
Login page with email and password
```

Generated cases include:

- Happy path test
- Required fields validation
- Invalid input test
- Boundary value test
- Accessibility test
- Basic security test

---

### 5. Website Tester

Run a basic website smoke test and capture a screenshot.

Current checks:

- Page loads successfully
- Screenshot captured

---

## Project Structure

```text
qa-bot-web-app/
│
├── app/
│   ├── ai/
│   │   └── llm_service.py
│   │
│   ├── automation/
│   │   ├── page_analyzer.py
│   │   ├── playwright_runner.py
│   │   └── smart_test_runner.py
│   │
│   ├── rag/
│   │
│   ├── ui/
│   │   └── gradio_app.py
│   │
│   └── main.py
│
├── reports/
│   ├── qa_report_*.json
│   ├── qa_report_*.html
│   ├── screenshot_*.png
│   ├── smart_test_report_*.json
│   └── test_generated_*.py
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Tech Stack

- Python
- Gradio
- Playwright
- Pytest
- Requests
- LangChain packages prepared for future local/RAG features

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/moneebyusuf/qa-bot-web-app.git
cd qa-bot-web-app
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

Linux / WSL / macOS:

```bash
source venv/bin/activate
```

Windows PowerShell:

```bash
venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Install Playwright browser

```bash
python3 -m playwright install chromium
```

---

## Run the App

From the project root:

```bash
python3 -m app.ui.gradio_app
```

Or:

```bash
python3 -m app.main
```

Then open the local Gradio URL shown in the terminal:

```text
http://127.0.0.1:7860
```

---

## Usage

### Smart Page Analyzer

1. Open the app.
2. Go to the **Smart Page Analyzer** tab.
3. Enter a website URL, for example:

```text
https://example.com
```

4. Click **Analyze Page & Generate Tests**.

The app will generate:

- Markdown report in the UI
- JSON report
- HTML report
- Page screenshot

---

### Smart Test Runner

1. Go to the **Smart Test Runner** tab.
2. Enter a website URL.
3. Click **Run Smart Tests**.

The app will generate:

- Pass/fail/warning report
- JSON report
- Screenshot
- Generated Pytest file

---

### Run Generated Pytest File

After generating a Pytest file, run:

```bash
pytest reports/test_generated_example_com_*.py
```

Example output:

```bash
5 passed in 2.70s
```

---

## Example Smart Page Analyzer Output

Example URL:

```text
https://example.com
```

Example result:

```text
QA Score: 95/100

Forms Found: 0
Inputs Found: 0
Buttons Found: 0
Links Found: 1
Working Links: 1
Broken Links: 0
Images Missing Alt Text: 0
```

---

## Example Smart Test Runner Output

```text
Total Tests: 7
Passed: 5
Failed: 0
Warnings: 2
```

Example checks:

```text
PASS - Page loads successfully
PASS - Page title exists
WARNING - Buttons are present
PASS - Navigation links are present
WARNING - Forms have input fields
PASS - Images have alt text
PASS - Sample links are reachable
```

---

## Reports

Generated reports are saved inside:

```text
reports/
```

Supported report types:

| Type | Example |
|---|---|
| JSON QA Report | `qa_report_20260511_132803.json` |
| HTML QA Report | `qa_report_20260511_132803.html` |
| Screenshot | `screenshot_20260511_133340.png` |
| Smart Test JSON | `smart_test_report_20260511_134222.json` |
| Generated Pytest | `test_generated_example_com_20260511_134717.py` |

---

## Current Limitations

- The platform currently focuses on public web pages.
- Some websites may block automated link checks.
- Some accessibility checks are basic and rule-based.
- The system does not rely on paid AI APIs.
- Generated tests are starter automation tests and may need customization for complex applications.

---

## Roadmap

Planned improvements:

- Add HTML report styling improvements
- Add PDF report export
- Add advanced accessibility checks
- Add login/signup/search form detection
- Add generated Pytest fixtures
- Add selectable test templates
- Add local AI/RAG support without paid APIs
- Add dashboard for previous reports
- Add CI/CD GitHub Actions example

---

## Why This Project?

Many QA automation tools require complex setup or paid services.

This project aims to provide a simple, free, local-first QA automation assistant that helps testers and developers quickly:

- Analyze websites
- Generate test ideas
- Run basic automated checks
- Export reports
- Generate starter Pytest automation code

---

## License

This project is currently for learning and experimentation.

You can add an open-source license later, such as MIT, Apache 2.0, or GPL.

---

## Author

Created by [@moneebyusuf](https://github.com/moneebyusuf)