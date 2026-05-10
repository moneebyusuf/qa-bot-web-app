import gradio as gr
from app.automation.page_analyzer import analyze_page
from app.automation.playwright_runner import run_basic_website_test
from app.automation.page_analyzer import analyze_page, save_analysis_report


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


def format_page_analysis(url):
    if not url:
        return "Please enter a website URL."

    analysis = analyze_page(url)

    if "error" in analysis:
        return f"Error while analyzing page:\n\n{analysis['error']}"

    score, issues = calculate_qa_score(analysis)

    output = "# Smart Page Analysis Report\n\n"

    output += "## Summary\n\n"
    output += f"**URL:** {analysis['url']}\n\n"
    output += f"**Page Title:** {analysis['title']}\n\n"
    output += f"**QA Score:** {score}/100\n\n"
    output += f"**Forms Found:** {analysis['forms_count']}\n\n"
    output += f"**Inputs Found:** {len(analysis['inputs'])}\n\n"
    output += f"**Buttons Found:** {len(analysis['buttons'])}\n\n"
    output += f"**Links Found:** {len(analysis['links'])}\n\n"
    output += f"**Working Links:** {len(analysis.get('working_links', []))}\n\n"
    output += f"**Broken Links:** {len(analysis.get('broken_links', []))}\n\n"
    output += f"**Images Missing Alt Text:** {len(analysis['images_without_alt'])}\n\n"

    output += "## Detected Issues\n\n"

    if analysis.get("issues"):
        for issue in analysis["issues"]:
            output += f"### {issue['severity']} - {issue['category']}\n"
            output += f"**Issue:** {issue['issue']}\n\n"
            output += f"**Recommendation:** {issue['recommendation']}\n\n"
    else:
        output += "No major issues detected.\n"

    output += "\n## Inputs Found\n\n"
    if analysis["inputs"]:
        for input_item in analysis["inputs"]:
            output += (
                f"- Type: `{input_item['type']}`, "
                f"Name: `{input_item['name']}`, "
                f"Placeholder: `{input_item['placeholder']}`\n"
            )
    else:
        output += "No inputs found.\n"

    output += "\n## Buttons Found\n\n"
    if analysis["buttons"]:
        for button in analysis["buttons"]:
            output += f"- {button}\n"
    else:
        output += "No buttons found.\n"
        output += "\n## Broken Links\n\n"
    if analysis.get("broken_links"):
        for link in analysis["broken_links"]:
            output += f"- {link['url']} "
            if "status_code" in link:
                output += f"(Status: {link['status_code']})\n"
            else:
                output += f"(Error: {link['error']})\n"
    else:
        output += "No broken links detected.\n"
    output += "\n## Accessibility Issues\n\n"
    output += f"- Images without alt text: {len(analysis['images_without_alt'])}\n"

    output += "\n## Auto-Generated QA Test Cases\n\n"
    for index, test_case in enumerate(analysis["generated_test_cases"], start=1):
        output += f"### {index}. {test_case['title']}\n"
        output += f"**Priority:** {test_case['priority']}\n\n"

        output += "**Steps:**\n"
        for step in test_case["steps"]:
            output += f"- {step}\n"

        output += f"\n**Expected Result:** {test_case['expected_result']}\n\n"

    output += "## Recommendation\n\n"

    if score >= 90:
        output += "The page looks good from a basic QA perspective.\n"
    elif score >= 70:
        output += "The page is acceptable, but some improvements are recommended.\n"
    else:
        output += "The page needs QA improvements before release.\n"

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
        return "Please enter a website URL.", None

    analysis = analyze_page(url)

    if "error" in analysis:
        return f"Error while analyzing page:\n\n{analysis['error']}", None

    report_text = format_page_analysis(url)
    file_path = save_analysis_report(analysis)

    return report_text, file_path

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

            report_file = gr.File(label="Download JSON Report")

            analyze_button.click(
                fn=analyze_page_and_export,
                inputs=analyzer_url_input,
                outputs=[analysis_output, report_file]
            )

    return demo