import gradio as gr

from app.automation.page_analyzer import analyze_page, save_analysis_report, save_html_report
from app.automation.playwright_runner import run_basic_website_test

def format_test_results(url):
    if not url:
        return "Please enter a website URL."

    results = run_basic_website_test(url)

    output = "# Website Test Report\n\n"
    output += f"**URL:** {url}\n\n"

    for result in results:
        icon = "✅" if result["status"] == "passed" else "❌"
        output += f"## {icon} {result['test']}\n"
        output += f"**Status:** {result['status']}\n\n"
        output += f"**Details:** {result['details']}\n\n"

    return output

def calculate_qa_score(analysis):
    score = 100
    issues = []

    if analysis["forms_count"] > 0 and len(analysis["inputs"]) == 0:
        score -= 15
        issues.append("Forms found but no input fields detected.")

    if len(analysis["images_without_alt"]) > 0:
        score -= min(20, len(analysis["images_without_alt"]) * 5)
        issues.append("Some images are missing alt text.")

    if len(analysis["buttons"]) == 0:
        score -= 5
        issues.append("No buttons detected on the page.")

    if len(analysis["links"]) == 0:
        score -= 10
        issues.append("No links detected on the page.")

    if not analysis["title"]:
        score -= 10
        issues.append("Page title is missing.")

    score = max(score, 0)

    return score, issues


def format_page_analysis(url, analysis=None):
    if not url:
        return "Please enter a website URL."

    if analysis is None:
        analysis = analyze_page(url)

    if "error" in analysis:
        return f"Error while analyzing page:\n\n{analysis['error']}"

    score, score_issues = calculate_qa_score(analysis)

    forms_count = analysis.get("forms_count", 0)
    inputs = analysis.get("inputs", [])
    buttons = analysis.get("buttons", [])
    links = analysis.get("links", [])
    working_links = analysis.get("working_links", [])
    broken_links = analysis.get("broken_links", [])
    images_without_alt = analysis.get("images_without_alt", [])
    issues = analysis.get("issues", [])
    generated_test_cases = analysis.get("generated_test_cases", [])

    output = "# Smart QA Page Analysis Report\n\n"

    output += "## Page Info\n\n"
    output += f"**URL:** {analysis.get('url', url)}\n\n"
    output += f"**Title:** {analysis.get('title', 'N/A')}\n\n"
    output += f"**QA Score:** {score}/100\n\n"

    output += "---\n\n"

    output += "## Summary\n\n"
    output += "| Metric | Count |\n"
    output += "|---|---:|\n"
    output += f"| Forms Found | {forms_count} |\n"
    output += f"| Inputs Found | {len(inputs)} |\n"
    output += f"| Buttons Found | {len(buttons)} |\n"
    output += f"| Links Found | {len(links)} |\n"
    output += f"| Working Links | {len(working_links)} |\n"
    output += f"| Broken Links | {len(broken_links)} |\n"
    output += f"| Images Missing Alt Text | {len(images_without_alt)} |\n\n"

    output += "---\n\n"

    output += "## Broken Links\n\n"

    if broken_links:
        for link in broken_links:
            link_url = link.get("url", "N/A")
            status_code = link.get("status_code")
            error = link.get("error")

            if status_code:
                output += f"- {link_url} | Status: {status_code}\n"
            elif error:
                output += f"- {link_url} | Error: {error}\n"
            else:
                output += f"- {link_url}\n"
    else:
        output += "No broken links detected.\n"

    output += "\n---\n\n"

    output += "## Accessibility Issues\n\n"

    accessibility_issues = [
        issue for issue in issues
        if issue.get("category") == "Accessibility"
    ]

    if accessibility_issues:
        for issue in accessibility_issues:
            output += f"### {issue.get('category', 'Accessibility')} - {issue.get('severity', 'Info')}\n\n"
            output += f"**Issue:** {issue.get('issue', '')}\n\n"
            output += f"**Recommendation:** {issue.get('recommendation', '')}\n\n"
    elif images_without_alt:
        output += f"- {len(images_without_alt)} images are missing alt text.\n"
    else:
        output += "No accessibility issues detected.\n"

    output += "\n---\n\n"

    output += "## Detected Issues\n\n"

    if issues:
        for issue in issues:
            output += f"### {issue.get('severity', 'Info')} - {issue.get('category', 'General')}\n\n"
            output += f"**Issue:** {issue.get('issue', '')}\n\n"
            output += f"**Recommendation:** {issue.get('recommendation', '')}\n\n"
    elif score_issues:
        for issue in score_issues:
            output += f"- {issue}\n"
    else:
        output += "No major issues detected.\n"

    output += "\n---\n\n"

    output += "## Inputs Found\n\n"

    if inputs:
        for input_item in inputs:
            output += (
                f"- Type: `{input_item.get('type', '')}`, "
                f"Name: `{input_item.get('name', '')}`, "
                f"Placeholder: `{input_item.get('placeholder', '')}`\n"
            )
    else:
        output += "No inputs found.\n"

    output += "\n---\n\n"

    output += "## Buttons Found\n\n"

    if buttons:
        for button in buttons:
            output += f"- {button}\n"
    else:
        output += "No buttons found.\n"

    output += "\n---\n\n"

    output += "## Auto-Generated QA Test Cases\n\n"

    if generated_test_cases:
        for index, test_case in enumerate(generated_test_cases, start=1):
            output += f"### {index}. {test_case.get('title', 'Untitled Test Case')}\n\n"
            output += f"**Priority:** {test_case.get('priority', 'Medium')}\n\n"

            output += "**Steps:**\n"
            for step in test_case.get("steps", []):
                output += f"- {step}\n"

            output += f"\n**Expected Result:** {test_case.get('expected_result', '')}\n\n"
    else:
        output += "No test cases generated.\n"

    output += "\n---\n\n"

    output += "## Recommendation\n\n"

    if score >= 90:
        output += "The page looks good from a basic QA perspective.\n"
    elif score >= 70:
        output += "The page is acceptable, but some improvements are recommended.\n"
    else:
        output += "The page needs QA improvements before release.\n"

    output += "\n\nRecommended next actions:\n\n"
    output += "- Fix broken links first.\n"
    output += "- Add alt text to images that are missing accessibility text.\n"
    output += "- Test forms with valid and invalid data.\n"
    output += "- Re-run the analyzer after making fixes.\n"

    return output

def generate_test_cases(provider, feature_description):
    if not feature_description:
        return "Please describe the feature you want to test."

    output = "# Rule-Based Test Cases\n\n"
    output += f"**Feature:** {feature_description}\n\n"

    output += "## 1. Happy Path Test\n"
    output += "**Priority:** High\n\n"
    output += "**Steps:**\n"
    output += "- Open the application\n"
    output += "- Navigate to the target feature\n"
    output += "- Enter valid data\n"
    output += "- Complete the main user action\n\n"
    output += "**Expected Result:** The feature should work successfully without errors.\n\n"

    output += "## 2. Required Fields Validation\n"
    output += "**Priority:** High\n\n"
    output += "**Steps:**\n"
    output += "- Open the feature page\n"
    output += "- Leave required fields empty\n"
    output += "- Submit the form or action\n\n"
    output += "**Expected Result:** Clear validation messages should be displayed.\n\n"

    output += "## 3. Invalid Input Test\n"
    output += "**Priority:** High\n\n"
    output += "**Steps:**\n"
    output += "- Enter invalid data\n"
    output += "- Submit the form or action\n\n"
    output += "**Expected Result:** The system should reject invalid input and show a helpful error message.\n\n"

    output += "## 4. Boundary Value Test\n"
    output += "**Priority:** Medium\n\n"
    output += "**Steps:**\n"
    output += "- Enter minimum allowed values\n"
    output += "- Enter maximum allowed values\n"
    output += "- Submit the form or action\n\n"
    output += "**Expected Result:** The system should handle boundary values correctly.\n\n"

    output += "## 5. Accessibility Test\n"
    output += "**Priority:** Medium\n\n"
    output += "**Steps:**\n"
    output += "- Navigate using only the keyboard\n"
    output += "- Check focus order\n"
    output += "- Activate buttons using Enter or Space\n\n"
    output += "**Expected Result:** The feature should be usable with keyboard only.\n\n"

    output += "## 6. Basic Security Test\n"
    output += "**Priority:** High\n\n"
    output += "**Steps:**\n"
    output += "- Enter `<script>alert('xss')</script>` into text fields\n"
    output += "- Submit the form\n\n"
    output += "**Expected Result:** The script should not execute and input should be safely handled.\n\n"

    return output

def analyze_page_and_export(url):
    if not url:
        return "Please enter a website URL.", None, None, None

    analysis = analyze_page(url)

    if "error" in analysis:
        return f"Error while analyzing page:\n\n{analysis['error']}", None, None, None

    report_text = format_page_analysis(url, analysis)
    json_file_path = save_analysis_report(analysis)
    html_file_path = save_html_report(analysis)
    screenshot_path = analysis.get("screenshot_path")

    return report_text, json_file_path, html_file_path, screenshot_path

def create_app():
    with gr.Blocks(title="AI QA Automation Platform") as demo:
        gr.Markdown("# AI QA Automation Platform")
        gr.Markdown("AI assistant for PDF QA, test case generation, and website automation.")

        with gr.Tab("AI Test Case Generator"):
            provider = gr.Dropdown(
                choices=["Rule-Based Engine"],
                value="Rule-Based Engine",
                label="Test Generation Engine"
            )

            feature_input = gr.Textbox(
                label="Feature Description",
                placeholder="Example: Login page with email and password",
                lines=5
            )

            generate_button = gr.Button("Generate Test Cases")

            test_cases_output = gr.Markdown(label="Generated Test Cases")

            generate_button.click(
                fn=generate_test_cases,
                inputs=[provider, feature_input],
                outputs=test_cases_output
            )

        with gr.Tab("Website Tester"):
            url_input = gr.Textbox(
                label="Website URL",
                placeholder="https://example.com"
            )

            test_button = gr.Button("Run Website Test")

            result_output = gr.Markdown(label="Test Results")

            test_button.click(
                fn=format_test_results,
                inputs=url_input,
                outputs=result_output
            )
        with gr.Tab("Smart Page Analyzer"):
            analyzer_url_input = gr.Textbox(
                label="Website URL",
                placeholder="https://example.com"
            )

            analyze_button = gr.Button("Analyze Page & Generate Tests")

            analysis_output = gr.Markdown(label="Analysis Result")

            json_report_file = gr.File(label="Download JSON Report")
            html_report_file = gr.File(label="Download HTML Report")

            screenshot_output = gr.Image(
                label="Page Screenshot",
                type="filepath"
            )

            analyze_button.click(
                fn=analyze_page_and_export,
                inputs=analyzer_url_input,
                outputs=[
                    analysis_output,
                    json_report_file,
                    html_report_file,
                    screenshot_output
                ]
            )

    return demo

if __name__ == "__main__":
    demo = create_app()
    demo.launch()