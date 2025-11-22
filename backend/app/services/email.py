import resend

from app.config import settings

resend.api_key = settings.resend_api_key


def send_followup_email(
    to_emails: list[str],
    subject: str,
    meeting_title: str,
    summary_text: str,
    action_items: list[dict],
    decisions: list[str],
    additional_message: str | None = None
) -> dict:
    action_items_html = ""
    if action_items:
        items = "".join([
            f"<li><strong>{item.get('task', '')}</strong>"
            f"{' - ' + item.get('assignee', '') if item.get('assignee') else ''}"
            f"{' (Due: ' + item.get('deadline', '') + ')' if item.get('deadline') else ''}"
            f"</li>"
            for item in action_items
        ])
        action_items_html = f"<h3>Action Items</h3><ul>{items}</ul>"

    decisions_html = ""
    if decisions:
        items = "".join([f"<li>{d}</li>" for d in decisions])
        decisions_html = f"<h3>Key Decisions</h3><ul>{items}</ul>"

    additional_html = ""
    if additional_message:
        additional_html = f"<p>{additional_message}</p><hr>"

    html_content = f"""
    <html>
    <body>
        <h2>Meeting Summary: {meeting_title}</h2>
        {additional_html}
        <h3>Summary</h3>
        <p>{summary_text}</p>
        {action_items_html}
        {decisions_html}
        <hr>
        <p><em>This summary was automatically generated.</em></p>
    </body>
    </html>
    """

    params: resend.Emails.SendParams = {
        "from": settings.email_from,
        "to": to_emails,
        "subject": subject,
        "html": html_content,
    }

    result = resend.Emails.send(params)
    return result
