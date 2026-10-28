"""Risk catalog: the single source for which risk flags exist, how they're named,
and what to do about them. The LLM may only raise these flags (see scoring.py)."""

RISKS = {
    "customer_data_shared": {
        "label": "Shared customer data with an AI tool",
        "team_action": "Approve one AI tool for customer work and run a 15-minute session on "
                       "removing names, emails and order numbers before pasting.",
        "your_action": "Before pasting, replace customer names, emails and IDs with placeholders, "
                       "and only use the company-approved tool.",
    },
    "confidential_data_shared": {
        "label": "Shared confidential company data with an AI tool",
        "team_action": "Publish a one-page list of what must never go into AI tools (contracts, "
                       "financials, credentials) and which tools are approved for internal data.",
        "your_action": "Don't paste contracts, financials or internal documents into AI tools "
                       "unless the tool is approved for internal data.",
    },
    "unreviewed_output": {
        "label": "Used AI output without reviewing it",
        "team_action": "Add a review step for AI-assisted work (e.g. a second read before "
                       "anything goes to a customer) and share examples of AI mistakes.",
        "your_action": "Check facts, numbers and names in AI output before you use or send it.",
    },
    "policy_unaware": {
        "label": "Not aware of the company AI policy",
        "team_action": "Walk the team through the AI policy in the next team meeting and pin it "
                       "where people work.",
        "your_action": "Read the company AI policy and ask your manager which tools you may use.",
    },
}


def for_employee(flag: str) -> dict:
    r = RISKS.get(flag, {})
    return {"risk": flag, "label": r.get("label", flag), "action": r.get("your_action")}
