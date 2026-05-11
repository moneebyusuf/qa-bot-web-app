import json
import os
from datetime import datetime
from urllib.parse import urljoin

import requests
from playwright.sync_api import sync_playwright


def analyze_page(url: str):
    analysis = {
        "url": url,
        "title": "",
        "screenshot_path": "",
        "inputs": [],
        "buttons": [],
        "links": [],
        "images_without_alt": [],
        "forms_count": 0,
        "generated_test_cases": [],
        "issues": [],
        "broken_links": [],
        "review_links": [],
        "working_links": [],
        "qa_score": 100,
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)

            analysis["title"] = page.title()
            os.makedirs("reports", exist_ok=True)

            screenshot_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"reports/screenshot_{screenshot_timestamp}.png"

            page.screenshot(path=screenshot_path, full_page=True)

            analysis["screenshot_path"] = screenshot_path

            inputs = page.locator("input").all()
            buttons = page.locator("button").all()
            links = page.locator("a").all()
            forms = page.locator("form").all()
            images = page.locator("img").all()

            analysis["forms_count"] = len(forms)

            for input_element in inputs:
                input_type = input_element.get_attribute("type") or "text"
                input_name = input_element.get_attribute("name") or ""
                input_placeholder = input_element.get_attribute("placeholder") or ""

                analysis["inputs"].append({
                    "type": input_type,
                    "name": input_name,
                    "placeholder": input_placeholder
                })

            for button in buttons:
                text = button.inner_text().strip()
                analysis["buttons"].append(text if text else "Unnamed button")

            for link in links[:20]:
                text = link.inner_text().strip()
                href = link.get_attribute("href") or ""
                analysis["links"].append({
                    "text": text,
                    "href": href
                })

            for image in images:
                alt = image.get_attribute("alt")
                src = image.get_attribute("src") or ""

                if not alt:
                    analysis["images_without_alt"].append(src)
            check_links_status(analysis)
            
            
            analysis["qa_score"] = calculate_qa_score(analysis)        
            analysis["issues"] = detect_issues(analysis)
            analysis["generated_test_cases"] = generate_test_cases_from_analysis(analysis)

        except Exception as error:
            analysis["error"] = str(error)

        finally:
            browser.close()

    return analysis


def generate_test_cases_from_analysis(analysis):
    test_cases = []

    test_cases.append({
        "title": "Verify page loads successfully",
        "priority": "High",
        "steps": [
            f"Open {analysis['url']}",
            "Wait for the page to load"
        ],
        "expected_result": "Page should load without errors"
    })

    if analysis["title"]:
        test_cases.append({
            "title": "Verify page title is displayed",
            "priority": "Medium",
            "steps": [
                "Open the page",
                "Check the browser page title"
            ],
            "expected_result": f"Page title should be: {analysis['title']}"
        })

    input_types = [item["type"] for item in analysis["inputs"]]

    if "email" in input_types:
        test_cases.append({
            "title": "Validate email input field",
            "priority": "High",
            "steps": [
                "Enter invalid email format",
                "Submit the form"
            ],
            "expected_result": "System should show email validation error"
        })

    if "password" in input_types:
        test_cases.append({
            "title": "Validate password field behavior",
            "priority": "High",
            "steps": [
                "Enter text in the password field",
                "Verify the characters are masked"
            ],
            "expected_result": "Password should not be visible as plain text"
        })

        test_cases.append({
            "title": "Test empty password validation",
            "priority": "High",
            "steps": [
                "Leave password field empty",
                "Submit the form"
            ],
            "expected_result": "System should show password required validation"
        })

    if analysis["forms_count"] > 0:
        test_cases.append({
            "title": "Submit form with empty required fields",
            "priority": "High",
            "steps": [
                "Open the page",
                "Leave all required fields empty",
                "Click submit button"
            ],
            "expected_result": "Validation messages should be displayed"
        })

    if len(analysis["buttons"]) > 0:
        test_cases.append({
            "title": "Verify all buttons are clickable",
            "priority": "Medium",
            "steps": [
                "Open the page",
                "Check each visible button",
                "Verify button is enabled and clickable"
            ],
            "expected_result": "All important buttons should be clickable"
        })

    if len(analysis["images_without_alt"]) > 0:
        test_cases.append({
            "title": "Check image accessibility alt text",
            "priority": "Medium",
            "steps": [
                "Scan all images on the page",
                "Check if each image has alt text"
            ],
            "expected_result": "All meaningful images should have alt text"
        })

    if len(analysis["links"]) > 0:
        test_cases.append({
            "title": "Verify navigation links",
            "priority": "Medium",
            "steps": [
                "Open the page",
                "Click important navigation links",
                "Verify links redirect correctly"
            ],
            "expected_result": "Links should navigate to the correct pages"
        })

    return test_cases

def calculate_qa_score(analysis):
    score = 100

    if not analysis.get("title"):
        score -= 10

    if len(analysis.get("broken_links", [])) > 0:
        score -= min(30, len(analysis.get("broken_links", [])) * 10)

    if len(analysis.get("images_without_alt", [])) > 0:
        score -= min(20, len(analysis.get("images_without_alt", [])) * 5)

    if analysis.get("forms_count", 0) > 0 and len(analysis.get("inputs", [])) == 0:
        score -= 15

    if len(analysis.get("buttons", [])) == 0:
        score -= 5

    if len(analysis.get("links", [])) == 0:
        score -= 10

    return max(score, 0)

def detect_issues(analysis):
    issues = []

    if not analysis["title"]:
        issues.append({
            "category": "SEO / Usability",
            "severity": "Medium",
            "issue": "Page title is missing",
            "recommendation": "Add a clear and descriptive page title."
        })
        
    if len(analysis.get("broken_links", [])) > 0:
        issues.append({
            "category": "Navigation",
            "severity": "High",
            "issue": f"{len(analysis['broken_links'])} broken links detected",
            "recommendation": "Fix or update broken links to improve navigation and SEO."
        })

    if len(analysis["images_without_alt"]) > 0:
        issues.append({
            "category": "Accessibility",
            "severity": "Medium",
            "issue": f"{len(analysis['images_without_alt'])} images are missing alt text",
            "recommendation": "Add descriptive alt text to meaningful images. Decorative images can use empty alt text intentionally."
        })

    if analysis["forms_count"] > 0 and len(analysis["inputs"]) == 0:
        issues.append({
            "category": "Forms",
            "severity": "High",
            "issue": "Forms exist but no input fields were detected",
            "recommendation": "Check if form fields are rendered correctly and accessible to automation tools."
        })

    if len(analysis["buttons"]) == 0:
        issues.append({
            "category": "UI",
            "severity": "Low",
            "issue": "No buttons detected on the page",
            "recommendation": "Verify whether the page should include user actions or call-to-action buttons."
        })

    email_inputs = [
        item for item in analysis["inputs"]
        if item["type"] == "email"
    ]

    if len(email_inputs) > 0:
        issues.append({
            "category": "Validation",
            "severity": "Medium",
            "issue": f"{len(email_inputs)} email input fields detected",
            "recommendation": "Test invalid email format, empty email, long email, and domain-specific validation."
        })

    password_inputs = [
        item for item in analysis["inputs"]
        if item["type"] == "password"
    ]

    if len(password_inputs) > 0:
        issues.append({
            "category": "Security",
            "severity": "High",
            "issue": f"{len(password_inputs)} password fields detected",
            "recommendation": "Verify masking, password strength rules, empty password validation, and autocomplete behavior."
        })

    return issues

def save_analysis_report(analysis):
    os.makedirs("reports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"reports/qa_report_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(analysis, file, indent=4, ensure_ascii=False)

    return file_path

def check_links_status(analysis):
    base_url = analysis["url"]

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    for link in analysis["links"]:
        href = link.get("href", "")

        if (
            not href
            or href.startswith("#")
            or href.startswith("javascript:")
            or href.startswith("mailto:")
            or href.startswith("tel:")
        ):
            continue

        full_url = urljoin(base_url, href)

        try:
            method_used = "HEAD"

            response = requests.head(
                full_url,
                timeout=8,
                allow_redirects=True,
                headers=headers
            )

            if response.status_code in [400, 401, 403, 405, 429]:
                method_used = "GET"

                response = requests.get(
                    full_url,
                    timeout=12,
                    allow_redirects=True,
                    headers=headers
                )

            result = {
                "url": full_url,
                "status_code": response.status_code,
                "method": method_used
            }

            if response.status_code in [401, 403, 429]:
                result["note"] = "Blocked by website, not necessarily broken"
                analysis["working_links"].append(result)

            elif response.status_code == 400 and method_used == "GET":
                result["note"] = "Automated check returned 400; manual review recommended"
                analysis["working_links"].append(result)

            elif response.status_code >= 400:
                analysis["broken_links"].append(result)

            else:
                analysis["working_links"].append(result)

        except Exception as error:
            analysis["broken_links"].append({
                "url": full_url,
                "error": str(error)
            })
            
def save_html_report(analysis):
    os.makedirs("reports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"reports/qa_report_{timestamp}.html"

    title = analysis.get("title", "N/A")
    url = analysis.get("url", "N/A")
    forms_count = analysis.get("forms_count", 0)
    inputs = analysis.get("inputs", [])
    buttons = analysis.get("buttons", [])
    links = analysis.get("links", [])
    working_links = analysis.get("working_links", [])
    broken_links = analysis.get("broken_links", [])
    images_without_alt = analysis.get("images_without_alt", [])
    issues = analysis.get("issues", [])
    test_cases = analysis.get("generated_test_cases", [])
    screenshot_path = analysis.get("screenshot_path", "")

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Smart QA Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background: #f6f8fa;
            color: #24292f;
        }}
        .container {{
            max-width: 1100px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.08);
        }}
        h1, h2, h3 {{
            color: #0969da;
        }}
        .score {{
            font-size: 28px;
            font-weight: bold;
            padding: 15px;
            background: #ddf4ff;
            border-left: 6px solid #0969da;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #d0d7de;
            padding: 10px;
            text-align: left;
        }}
        th {{
            background: #f6f8fa;
        }}
        .issue {{
            border-left: 5px solid #d1242f;
            padding: 12px;
            background: #fff1f1;
            margin-bottom: 12px;
        }}
        .test-case {{
            border-left: 5px solid #1a7f37;
            padding: 12px;
            background: #dafbe1;
            margin-bottom: 12px;
        }}
        .screenshot {{
            max-width: 100%;
            border: 1px solid #d0d7de;
            border-radius: 8px;
            margin-top: 15px;
        }}
        code {{
            background: #f6f8fa;
            padding: 2px 5px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
<div class="container">
    <h1>Smart QA Page Analysis Report</h1>

    <h2>Page Info</h2>
    <p><strong>URL:</strong> {url}</p>
    <p><strong>Title:</strong> {title}</p>

    <div class="score">QA Score: {analysis.get("qa_score", "Calculated in UI")}/100</div>

    <h2>Summary</h2>
    <table>
        <tr><th>Metric</th><th>Count</th></tr>
        <tr><td>Forms Found</td><td>{forms_count}</td></tr>
        <tr><td>Inputs Found</td><td>{len(inputs)}</td></tr>
        <tr><td>Buttons Found</td><td>{len(buttons)}</td></tr>
        <tr><td>Links Found</td><td>{len(links)}</td></tr>
        <tr><td>Working Links</td><td>{len(working_links)}</td></tr>
        <tr><td>Broken Links</td><td>{len(broken_links)}</td></tr>
        <tr><td>Images Missing Alt Text</td><td>{len(images_without_alt)}</td></tr>
    </table>

    <h2>Broken Links</h2>
"""

    if broken_links:
        html += "<ul>"
        for link in broken_links:
            html += f"<li>{link.get('url')} - Status: {link.get('status_code', link.get('error', 'N/A'))}</li>"
        html += "</ul>"
    else:
        html += "<p>No broken links detected.</p>"

    html += """
    <h2>Detected Issues</h2>
"""

    if issues:
        for issue in issues:
            html += f"""
            <div class="issue">
                <h3>{issue.get('severity', 'Info')} - {issue.get('category', 'General')}</h3>
                <p><strong>Issue:</strong> {issue.get('issue', '')}</p>
                <p><strong>Recommendation:</strong> {issue.get('recommendation', '')}</p>
            </div>
            """
    else:
        html += "<p>No major issues detected.</p>"

    html += """
    <h2>Auto-Generated QA Test Cases</h2>
"""

    if test_cases:
        for index, test_case in enumerate(test_cases, start=1):
            html += f"""
            <div class="test-case">
                <h3>{index}. {test_case.get('title', 'Untitled Test Case')}</h3>
                <p><strong>Priority:</strong> {test_case.get('priority', 'Medium')}</p>
                <p><strong>Steps:</strong></p>
                <ol>
            """

            for step in test_case.get("steps", []):
                html += f"<li>{step}</li>"

            html += f"""
                </ol>
                <p><strong>Expected Result:</strong> {test_case.get('expected_result', '')}</p>
            </div>
            """
    else:
        html += "<p>No test cases generated.</p>"

    if screenshot_path:
        html += f"""
        <h2>Page Screenshot</h2>
        <p><code>{screenshot_path}</code></p>
        <img class="screenshot" src="../{screenshot_path}" alt="Page screenshot">
        """

    html += """
    <h2>Recommendation</h2>
    <ul>
        <li>Fix broken links first.</li>
        <li>Add alt text to images that are missing accessibility text.</li>
        <li>Test forms with valid and invalid data.</li>
        <li>Re-run the analyzer after making fixes.</li>
    </ul>
</div>
</body>
</html>
"""

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html)

    return file_path