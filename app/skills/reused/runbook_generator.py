"""Safe Troubleshooting Runbook Generator.

This skill generates SAFE, reusable troubleshooting steps for recurring network issues.

Key features:
- Only 2 required selections (domain, symptom_category)
- All steps are SAFE by default (gui_only mode)
- Auto-generates evidence checklists
- Includes STOP conditions for escalation
- NO disruptive actions allowed by default

Reused from PI-300 with imports adapted for standalone operation.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


# Inline helper functions
def get_current_timestamp() -> str:
    """Get current timestamp in standard format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def format_bullet_list(items: list[str]) -> str:
    """Format a list of items as markdown bullets."""
    if not items:
        return ""
    return "\n".join(f"- {item}" for item in items)


# Inline playbook data (adapted from playbooks/*.yaml)
PLAYBOOKS = {
    "firewall": {
        "name": "Firewall Troubleshooting",
        "escalation_path": "Contact Firewall Team Lead or Security Operations",
        "symptoms": {
            "high_cpu": {
                "explanation": "Firewall CPU utilization exceeds normal thresholds, potentially impacting traffic inspection.",
                "diagnostic_steps": [
                    {"step": "Check CPU utilization in dashboard", "mode": "gui_only"},
                    {"step": "Review active connections count", "mode": "gui_only"},
                    {"step": "Check for unusual traffic patterns in logs", "mode": "gui_only"},
                    {"step": "Verify NAT session counts", "mode": "gui_only"},
                    {"step": "Review recent policy changes", "mode": "gui_only"},
                ],
                "evidence_checklist": [
                    "Screenshot of CPU utilization graph (last 24h)",
                    "Active connection count",
                    "Top talkers report",
                    "Recent policy change log",
                ],
                "stop_conditions": [
                    "CPU exceeds 95% for more than 5 minutes",
                    "Packet drops reported",
                    "Management interface unresponsive",
                ],
            },
            "connectivity_loss": {
                "explanation": "Traffic is not passing through the firewall as expected.",
                "diagnostic_steps": [
                    {"step": "Verify interface status in dashboard", "mode": "gui_only"},
                    {"step": "Check policy rules for the affected traffic", "mode": "gui_only"},
                    {"step": "Review deny logs for blocked traffic", "mode": "gui_only"},
                    {"step": "Verify NAT rules if applicable", "mode": "gui_only"},
                    {"step": "Check routing table entries", "mode": "gui_only"},
                ],
                "evidence_checklist": [
                    "Interface status screenshot",
                    "Relevant policy rules screenshot",
                    "Deny log entries for affected source/destination",
                    "NAT configuration if applicable",
                ],
                "stop_conditions": [
                    "Multiple zones affected",
                    "Unable to identify blocking rule",
                    "Suspected security incident",
                ],
            },
        },
    },
    "f5": {
        "name": "F5 Load Balancer Troubleshooting",
        "escalation_path": "Contact F5 Team Lead or Application Delivery",
        "symptoms": {
            "pool_down": {
                "explanation": "One or more pool members are marked down, affecting load balancing.",
                "diagnostic_steps": [
                    {"step": "Check pool member status in GUI", "mode": "gui_only"},
                    {"step": "Review health monitor results", "mode": "gui_only"},
                    {"step": "Verify backend server connectivity", "mode": "gui_only"},
                    {"step": "Check for SSL certificate issues", "mode": "gui_only"},
                    {"step": "Review pool statistics for error patterns", "mode": "gui_only"},
                ],
                "evidence_checklist": [
                    "Pool status screenshot",
                    "Health monitor configuration",
                    "Recent pool statistics",
                    "Backend server health check results",
                ],
                "stop_conditions": [
                    "All pool members down",
                    "SSL handshake failures increasing",
                    "Application team reports service outage",
                ],
            },
            "ssl_error": {
                "explanation": "SSL/TLS termination issues affecting client connections.",
                "diagnostic_steps": [
                    {"step": "Check SSL profile configuration", "mode": "gui_only"},
                    {"step": "Verify certificate validity and chain", "mode": "gui_only"},
                    {"step": "Review cipher suite settings", "mode": "gui_only"},
                    {"step": "Check client-side SSL logs", "mode": "gui_only"},
                    {"step": "Verify SNI configuration if applicable", "mode": "gui_only"},
                ],
                "evidence_checklist": [
                    "Certificate details screenshot",
                    "SSL profile configuration",
                    "Error log entries",
                    "Cipher suite list",
                ],
                "stop_conditions": [
                    "Certificate expired",
                    "Certificate chain incomplete",
                    "Multiple applications affected",
                ],
            },
        },
    },
    "circuit": {
        "name": "Circuit/WAN Troubleshooting",
        "escalation_path": "Contact Network Operations or Carrier Support",
        "symptoms": {
            "latency": {
                "explanation": "Network latency exceeds acceptable thresholds for the circuit.",
                "diagnostic_steps": [
                    {"step": "Check interface error counters", "mode": "gui_only"},
                    {"step": "Review bandwidth utilization graphs", "mode": "gui_only"},
                    {"step": "Verify QoS policy application", "mode": "gui_only"},
                    {"step": "Check for packet drops at interface", "mode": "gui_only"},
                    {"step": "Review carrier SLA metrics if available", "mode": "gui_only"},
                ],
                "evidence_checklist": [
                    "Latency graph (last 24h)",
                    "Bandwidth utilization graph",
                    "Interface error counters",
                    "QoS policy screenshot",
                ],
                "stop_conditions": [
                    "Latency exceeds SLA threshold",
                    "Packet loss detected",
                    "Circuit errors increasing",
                ],
            },
            "flapping": {
                "explanation": "Circuit or interface is repeatedly going up and down.",
                "diagnostic_steps": [
                    {"step": "Check interface status history", "mode": "gui_only"},
                    {"step": "Review optical power levels if fiber", "mode": "gui_only"},
                    {"step": "Check for physical layer errors", "mode": "gui_only"},
                    {"step": "Verify both ends report same status", "mode": "gui_only"},
                    {"step": "Review recent changes at physical layer", "mode": "gui_only"},
                ],
                "evidence_checklist": [
                    "Interface state change log",
                    "Optical power readings",
                    "Physical layer error counters",
                    "Both-end status comparison",
                ],
                "stop_conditions": [
                    "Flapping continues after 15 minutes",
                    "Multiple circuits affected",
                    "Physical layer errors increasing",
                ],
            },
        },
    },
}


@dataclass
class RunbookInput:
    """Schema for runbook generator input."""

    domain: str
    symptom_category: str
    access_mode: str = "gui_only"
    environment: str = "prod"

    def validate(self) -> list[str]:
        """Validate required fields. Returns list of errors."""
        errors = []
        if not self.domain or not self.domain.strip():
            errors.append("domain is required")
        if not self.symptom_category or not self.symptom_category.strip():
            errors.append("symptom_category is required")
        return errors


def get_available_domains() -> list[str]:
    """Get list of available domains."""
    return list(PLAYBOOKS.keys())


def get_symptoms_for_domain(domain: str) -> list[str]:
    """Get available symptoms for a domain."""
    playbook = PLAYBOOKS.get(domain, {})
    symptoms = playbook.get("symptoms", {})
    return list(symptoms.keys())


def render_runbook_template(context: dict[str, Any]) -> str:
    """Render runbook template."""
    lines = [
        f"# Troubleshooting Runbook: {context['domain'].upper()} - {context['symptom_category'].replace('_', ' ').title()}",
        "",
        f"**Environment:** {context['environment'].upper()} | **Access Mode:** {context['access_mode']}",
        f"**Generated:** {context['timestamp']}",
        "",
        "## Symptom Explanation",
        context["symptom_explanation"],
        "",
        "## Safe Diagnostic Steps",
    ]

    for i, step in enumerate(context["diagnostic_steps"], 1):
        step_text = step.get("step", step) if isinstance(step, dict) else step
        lines.append(f"{i}. {step_text}")

    lines.extend([
        "",
        "## Evidence Checklist",
    ])
    for item in context["evidence_checklist"]:
        lines.append(f"- [ ] {item}")

    lines.extend([
        "",
        "## STOP Conditions (Escalate Immediately)",
    ])
    for item in context["stop_conditions"]:
        lines.append(f"- {item}")

    lines.extend([
        "",
        f"**Escalation Path:** {context['escalation_path']}",
    ])

    return "\n".join(lines)


def generate_runbook(
    domain: str,
    symptom_category: str,
    access_mode: str = "gui_only",
    environment: str = "prod",
) -> str:
    """Generate a safe troubleshooting runbook.

    Args:
        domain: Network domain (firewall, f5, circuit)
        symptom_category: Type of symptom (high_cpu, connectivity_loss, etc.)
        access_mode: Access level (gui_only, cli_read_only, cli_full)
        environment: Target environment (prod, uat, dev)

    Returns:
        Formatted runbook string
    """
    input_data = RunbookInput(
        domain=domain,
        symptom_category=symptom_category,
        access_mode=access_mode,
        environment=environment,
    )

    errors = input_data.validate()
    if errors:
        raise ValueError(f"Invalid input: {', '.join(errors)}")

    # Load playbook for domain
    playbook = PLAYBOOKS.get(domain)
    if not playbook:
        available = list(PLAYBOOKS.keys())
        raise ValueError(f"No playbook found for domain: {domain}. Available: {available}")

    # Get symptom data
    symptoms = playbook.get("symptoms", {})
    symptom_data = symptoms.get(symptom_category)
    if not symptom_data:
        available = list(symptoms.keys())
        raise ValueError(
            f"Unknown symptom '{symptom_category}' for domain '{domain}'. "
            f"Available: {available}"
        )

    # Build context for template
    context = {
        "domain": domain,
        "symptom_category": symptom_category,
        "access_mode": access_mode,
        "environment": environment,
        "symptom_explanation": symptom_data.get("explanation", ""),
        "diagnostic_steps": symptom_data.get("diagnostic_steps", []),
        "evidence_checklist": symptom_data.get("evidence_checklist", []),
        "stop_conditions": symptom_data.get("stop_conditions", []),
        "escalation_path": playbook.get("escalation_path", "Contact Tier 2 support"),
        "timestamp": get_current_timestamp(),
    }

    return render_runbook_template(context)


def generate_from_dict(data: dict[str, Any]) -> str:
    """Generate runbook from dictionary input."""
    return generate_runbook(
        domain=data.get("domain", ""),
        symptom_category=data.get("symptom_category", ""),
        access_mode=data.get("access_mode", "gui_only"),
        environment=data.get("environment", "prod"),
    )
