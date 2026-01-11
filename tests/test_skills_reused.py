"""Smoke tests for reused skills."""

import pytest

from app.skills.reused import generate_incident_update, generate_runbook, generate_fcr_content
from app.skills.task_prioritizer import prioritize_tasks
from app.skills.daily_status_summary import generate_daily_summary


class TestIncidentUpdate:
    """Tests for incident update skill."""

    def test_basic_incident_update(self):
        """Test generating a basic incident update."""
        result = generate_incident_update(
            incident_title="Core Router Reboot",
            impact_summary="Users in Building A experiencing intermittent connectivity",
        )
        assert "Core Router Reboot" in result
        assert "Building A" in result
        assert "investigating" in result.lower() or "Investigating" in result

    def test_incident_update_with_evidence(self):
        """Test incident update with evidence provided."""
        result = generate_incident_update(
            incident_title="Firewall Policy Error",
            impact_summary="VPN users cannot access internal resources",
            severity="P1",
            evidence=["Screenshot of deny logs", "User ticket #12345"],
        )
        assert "P1" in result
        assert "Screenshot" in result or "Evidence" in result

    def test_client_audience(self):
        """Test client-facing incident update."""
        result = generate_incident_update(
            incident_title="Service Degradation",
            impact_summary="Slow response times on web portal",
            audience="client",
        )
        assert "Service" in result
        assert "patience" in result.lower() or "update" in result.lower()


class TestRunbookGenerator:
    """Tests for runbook generator skill."""

    def test_firewall_runbook(self):
        """Test generating a firewall runbook."""
        result = generate_runbook(
            domain="firewall",
            symptom_category="high_cpu",
        )
        assert "FIREWALL" in result.upper()
        assert "CPU" in result.upper()
        assert "Diagnostic" in result or "Step" in result
        assert "STOP" in result.upper() or "Escalate" in result

    def test_f5_runbook(self):
        """Test generating an F5 runbook."""
        result = generate_runbook(
            domain="f5",
            symptom_category="pool_down",
        )
        assert "F5" in result.upper() or "Pool" in result
        assert "health" in result.lower()

    def test_invalid_domain(self):
        """Test error on invalid domain."""
        with pytest.raises(ValueError) as exc_info:
            generate_runbook(domain="invalid", symptom_category="test")
        assert "No playbook found" in str(exc_info.value)

    def test_invalid_symptom(self):
        """Test error on invalid symptom."""
        with pytest.raises(ValueError) as exc_info:
            generate_runbook(domain="firewall", symptom_category="invalid")
        assert "Unknown symptom" in str(exc_info.value)


class TestFCRAutofill:
    """Tests for FCR autofill skill."""

    def test_basic_fcr(self):
        """Test generating basic FCR content."""
        result = generate_fcr_content(
            purpose="Allow HTTPS traffic from vendor to internal app server",
        )
        assert "HTTPS" in result or "vendor" in result
        assert "Rollback" in result
        assert "Test" in result

    def test_fcr_with_options(self):
        """Test FCR with all options specified."""
        result = generate_fcr_content(
            purpose="Configure NAT for new DMZ server",
            change_type="nat_change",
            risk_level="medium",
            environment="prod",
        )
        assert "NAT" in result.upper()
        assert "MEDIUM" in result.upper() or "Moderate" in result

    def test_fcr_empty_purpose(self):
        """Test error on empty purpose."""
        with pytest.raises(ValueError) as exc_info:
            generate_fcr_content(purpose="")
        assert "purpose is required" in str(exc_info.value)


class TestTaskPrioritizer:
    """Tests for task prioritizer skill."""

    def test_prioritize_tasks(self):
        """Test prioritizing a list of tasks."""
        tasks = [
            {"title": "Low priority task", "status": "todo", "priority": "low"},
            {"title": "High priority task", "status": "todo", "priority": "high"},
            {"title": "In progress task", "status": "in_progress", "priority": "medium"},
        ]
        result = prioritize_tasks(tasks)
        assert "Priority" in result
        assert "High priority task" in result
        # High priority should come first
        high_pos = result.find("High priority task")
        low_pos = result.find("Low priority task")
        assert high_pos < low_pos

    def test_empty_tasks(self):
        """Test with no tasks."""
        result = prioritize_tasks([])
        assert "No tasks" in result


class TestDailySummary:
    """Tests for daily status summary skill."""

    def test_basic_summary(self):
        """Test generating a basic daily summary."""
        tasks = [
            {"title": "Completed task", "status": "done"},
            {"title": "Working on this", "status": "in_progress"},
            {"title": "Next up", "status": "todo"},
        ]
        result = generate_daily_summary(tasks)
        assert "Completed" in result
        assert "In Progress" in result
        assert "Next" in result

    def test_summary_with_blockers(self):
        """Test summary with blocked tasks."""
        tasks = [
            {"title": "Blocked task", "status": "todo", "blocked": True, "blocker_reason": "Waiting on vendor"},
        ]
        result = generate_daily_summary(tasks)
        assert "Blocked" in result
        assert "vendor" in result

    def test_empty_summary(self):
        """Test summary with no tasks."""
        result = generate_daily_summary([])
        assert "No tasks" in result or "0" in result
