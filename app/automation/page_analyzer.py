from playwright.sync_api import sync_playwright
import json
from datetime import datetime
import requests
from urllib.parse import urljoin

def analyze_page(url: str):
    analysis = {
        "url": url,
        "title": "",
        "inputs": [],
        "buttons": [],
        "links": [],
        "images_without_alt": [],
        "forms_count": 0,
        "generated_test_cases": [],
        "issues": [],
        "broken_links": [],
        "working_links": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, timeout=30000)

            analysis["title"] = page.title()

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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"reports/qa_report_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(analysis, file, indent=4, ensure_ascii=False)

    return file_path

def check_links_status(analysis):
    base_url = analysis["url"]

    headers = {
        "User-Agent": "Mozilla/5.0 QA-Bot-Link-Checker"
    }

    for link in analysis["links"]:
        href = link.get("href", "")

        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue

        full_url = urljoin(base_url, href)

        try:
            response = requests.head(
                full_url,
                timeout=5,
                allow_redirects=True,
                headers=headers
            )

            if response.status_code in [400, 403, 405]:
                response = requests.get(
                    full_url,
                    timeout=8,
                    allow_redirects=True,
                    headers=headers
                )

            if response.status_code >= 400:
                analysis["broken_links"].append({
                    "url": full_url,
                    "status_code": response.status_code
                })
            else:
                analysis["working_links"].append({
                    "url": full_url,
                    "status_code": response.status_code
                })

        except Exception as error:
            analysis["broken_links"].append({
                "url": full_url,
                "error": str(error)
            })