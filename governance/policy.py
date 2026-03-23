import re

class GovernancePolicy:
    def __init__(self):
        # Basic patterns for financial PII
        self.pii_patterns = {
            "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
            "social_security": r"\b\d{3}-\d{2}-\d{4}\b",
            "bank_account": r"\b\d{8,17}\b"
        }

    def validate_query(self, query):
        """
        Validate queries against data governance policies (e.g., no PII in queries).
        """
        violations = []
        for pii_type, pattern in self.pii_patterns.items():
            if re.search(pattern, query):
                violations.append(pii_type)
        
        if violations:
            return False, f"Policy Violation: PII detected ({', '.join(violations)})"
        return True, "Safe"

    def apply_masking(self, text):
        """
        Apply simple masking to detected PII.
        """
        masked_text = text
        for pii_type, pattern in self.pii_patterns.items():
            masked_text = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", masked_text)
        return masked_text

    def log_governance_event(self, event_type, status, detail):
        """
        Log governance decisions for audit trails.
        """
        # In a real app, this would write to a secure database or ELK stack
        print(f"[GOVERNANCE AUDIT] Type: {event_type} | Status: {status} | Detail: {detail}")
