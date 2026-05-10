from playwright.sync_api import sync_playwright


def run_basic_website_test(url: str):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, timeout=30000)

            title = page.title()

            results.append({
                "test": "Page loads successfully",
                "status": "passed",
                "details": f"Page title: {title}"
            })

            screenshot_path = "reports/page_screenshot.png"
            page.screenshot(path=screenshot_path, full_page=True)

            results.append({
                "test": "Screenshot captured",
                "status": "passed",
                "details": screenshot_path
            })

        except Exception as error:
            results.append({
                "test": "Website test failed",
                "status": "failed",
                "details": str(error)
            })

        finally:
            browser.close()

    return results