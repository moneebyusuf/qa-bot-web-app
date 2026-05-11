from datetime import datetime
import json
import os
from urllib.parse import urljoin

import requests
from playwright.sync_api import sync_playwright


def run_smart_tests(url: str):
    results = {
        "url": url,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
        },
        "tests": [],
        "screenshot_path": "",
        "report_path": "",
    }

    if not url:
        add_test_result(
            results,
            name="Validate URL input",
            status="failed",
            severity="High",
            details="No URL was provided.",
            recommendation="Enter a valid website URL.",
        )
        finalize_summary(results)
        return results

    os.makedirs("reports", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = f"reports/smart_test_screenshot_{timestamp}.png"
    report_path = f"reports/smart_test_report_{timestamp}.json"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1200})

            response = page.goto(url, timeout=30000, wait_until="domcontentloaded")

            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass

            status_code = response.status if response else None

            if status_code and status_code < 400:
                add_test_result(
                    results,
                    name="Page loads successfully",
                    status="passed",
                    severity="High",
                    details=f"Page loaded with status code {status_code}.",
                    recommendation="No action needed.",
                )
            else:
                add_test_result(
                    results,
                    name="Page loads successfully",
                    status="failed",
                    severity="High",
                    details=f"Page returned status code {status_code}.",
                    recommendation="Check website availability and server response.",
                )

            title = page.title()

            if title:
                add_test_result(
                    results,
                    name="Page title exists",
                    status="passed",
                    severity="Medium",
                    details=f"Page title found: {title}",
                    recommendation="No action needed.",
                )
            else:
                add_test_result(
                    results,
                    name="Page title exists",
                    status="failed",
                    severity="Medium",
                    details="No page title was found.",
                    recommendation="Add a descriptive page title for SEO and usability.",
                )

            forms_count = page.locator("form").count()
            inputs_count = page.locator("input, textarea, select").count()
            buttons_count = page.locator("button, input[type='button'], input[type='submit']").count()
            links_count = page.locator("a[href]").count()
            missing_alt_count = page.locator("img:not([alt]), img[alt='']").count()

            if buttons_count > 0:
                add_test_result(
                    results,
                    name="Buttons are present",
                    status="passed",
                    severity="Medium",
                    details=f"{buttons_count} button(s) found.",
                    recommendation="No action needed.",
                )
            else:
                add_test_result(
                    results,
                    name="Buttons are present",
                    status="warning",
                    severity="Low",
                    details="No buttons were found on the page.",
                    recommendation="Verify whether the page needs user action buttons.",
                )

            if links_count > 0:
                add_test_result(
                    results,
                    name="Navigation links are present",
                    status="passed",
                    severity="Medium",
                    details=f"{links_count} link(s) found.",
                    recommendation="No action needed.",
                )
            else:
                add_test_result(
                    results,
                    name="Navigation links are present",
                    status="warning",
                    severity="Medium",
                    details="No links were found on the page.",
                    recommendation="Verify navigation and user flow.",
                )

            if forms_count > 0:
                if inputs_count > 0:
                    add_test_result(
                        results,
                        name="Forms have input fields",
                        status="passed",
                        severity="High",
                        details=f"{forms_count} form(s) and {inputs_count} input field(s) found.",
                        recommendation="No action needed.",
                    )
                else:
                    add_test_result(
                        results,
                        name="Forms have input fields",
                        status="failed",
                        severity="High",
                        details=f"{forms_count} form(s) found but no inputs detected.",
                        recommendation="Check whether form fields are rendered correctly.",
                    )
            else:
                add_test_result(
                    results,
                    name="Forms have input fields",
                    status="warning",
                    severity="Low",
                    details="No forms were found on the page.",
                    recommendation="This is fine for static pages. For interactive pages, verify forms exist.",
                )

            if missing_alt_count == 0:
                add_test_result(
                    results,
                    name="Images have alt text",
                    status="passed",
                    severity="Medium",
                    details="No images missing alt text were detected.",
                    recommendation="No action needed.",
                )
            else:
                add_test_result(
                    results,
                    name="Images have alt text",
                    status="failed",
                    severity="Medium",
                    details=f"{missing_alt_count} image(s) are missing alt text.",
                    recommendation="Add meaningful alt text to important images.",
                )

            link_check_result = check_sample_links(page, url)

            if link_check_result["broken_count"] == 0:
                add_test_result(
                    results,
                    name="Sample links are reachable",
                    status="passed",
                    severity="High",
                    details=(
                        f"Checked {link_check_result['checked_count']} sample link(s). "
                        f"No broken links detected."
                    ),
                    recommendation="No action needed.",
                )
            else:
                add_test_result(
                    results,
                    name="Sample links are reachable",
                    status="failed",
                    severity="High",
                    details=(
                        f"Checked {link_check_result['checked_count']} sample link(s). "
                        f"{link_check_result['broken_count']} broken link(s) detected."
                    ),
                    recommendation="Review and fix broken links.",
                )

            page.screenshot(path=screenshot_path, full_page=True)
            results["screenshot_path"] = screenshot_path

            browser.close()

    except Exception as error:
        add_test_result(
            results,
            name="Smart test runner execution",
            status="failed",
            severity="High",
            details=str(error),
            recommendation="Check the URL, network access, and Playwright browser installation.",
        )

    finalize_summary(results)

    with open(report_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)

    results["report_path"] = report_path

    return results


def add_test_result(results, name, status, severity, details, recommendation):
    results["tests"].append({
        "name": name,
        "status": status,
        "severity": severity,
        "details": details,
        "recommendation": recommendation,
    })


def finalize_summary(results):
    tests = results.get("tests", [])

    results["summary"]["total"] = len(tests)
    results["summary"]["passed"] = len([test for test in tests if test["status"] == "passed"])
    results["summary"]["failed"] = len([test for test in tests if test["status"] == "failed"])
    results["summary"]["warnings"] = len([test for test in tests if test["status"] == "warning"])


def check_sample_links(page, base_url, max_links=10):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    raw_links = page.locator("a[href]").evaluate_all(
        """links => links.map(a => a.getAttribute('href')).filter(Boolean)"""
    )

    unique_links = []
    seen = set()

    for href in raw_links:
        if href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:") or href.startswith("tel:"):
            continue

        full_url = urljoin(base_url, href)

        if full_url not in seen:
            seen.add(full_url)
            unique_links.append(full_url)

        if len(unique_links) >= max_links:
            break

    checked_count = 0
    broken_count = 0

    for link in unique_links:
        try:
            response = requests.head(
                link,
                timeout=8,
                allow_redirects=True,
                headers=headers,
            )

            if response.status_code in [400, 401, 403, 405, 429]:
                response = requests.get(
                    link,
                    timeout=12,
                    allow_redirects=True,
                    headers=headers,
                )

            checked_count += 1

            if response.status_code >= 400 and response.status_code not in [401, 403, 429]:
                broken_count += 1

        except Exception:
            checked_count += 1
            broken_count += 1

    return {
        "checked_count": checked_count,
        "broken_count": broken_count,
    }