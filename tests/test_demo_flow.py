"""Tests for demo flow logic."""

import pytest

from app.models.task import SkillType
from app.services.skill_service import execute_skill


class TestSkillService:
    """Tests for skill service execution."""

    def test_execute_runbook_skill(self):
        """Test executing runbook skill through service."""
        input_payload = {
            "domain": "firewall",
            "symptom_category": "high_cpu",
            "access_mode": "gui_only",
            "environment": "prod",
        }
        result = execute_skill(SkillType.RUNBOOK, input_payload)

        assert result["skill_type"] == "runbook"
        assert "output" in result
        assert "FIREWALL" in result["output"].upper()
        assert "CPU" in result["output"].upper()

    def test_execute_incident_skill(self):
        """Test executing incident skill through service."""
        input_payload = {
            "incident_title": "Test Incident",
            "impact_summary": "Test impact",
        }
        result = execute_skill(SkillType.INCIDENT, input_payload)

        assert result["skill_type"] == "incident"
        assert "Test Incident" in result["output"]

    def test_execute_fcr_skill(self):
        """Test executing FCR skill through service."""
        input_payload = {
            "purpose": "Test purpose for FCR",
        }
        result = execute_skill(SkillType.FCR, input_payload)

        assert result["skill_type"] == "fcr"
        assert "Test purpose" in result["output"]

    def test_execute_prioritizer_skill(self):
        """Test executing prioritizer skill through service."""
        input_payload = {
            "tasks": [
                {"title": "Task A", "status": "todo", "priority": "high"},
                {"title": "Task B", "status": "done", "priority": "low"},
            ]
        }
        result = execute_skill(SkillType.PRIORITIZER, input_payload)

        assert result["skill_type"] == "prioritizer"
        assert "Task A" in result["output"]

    def test_execute_daily_summary_skill(self):
        """Test executing daily summary skill through service."""
        input_payload = {
            "tasks": [
                {"title": "Done task", "status": "done"},
                {"title": "In progress", "status": "in_progress"},
            ],
            "team_name": "Test Team",
        }
        result = execute_skill(SkillType.DAILY_SUMMARY, input_payload)

        assert result["skill_type"] == "daily_summary"
        assert "Test Team" in result["output"]
        assert "Completed" in result["output"]


class TestDemoIntegration:
    """Integration tests for demo flow."""

    def test_full_skill_pipeline(self):
        """Test the full skill execution pipeline."""
        # Simulate demo flow: create task data, execute skill, capture output
        task_input = {
            "domain": "f5",
            "symptom_category": "ssl_error",
            "access_mode": "gui_only",
            "environment": "prod",
        }

        result = execute_skill(SkillType.RUNBOOK, task_input)

        # Verify output structure
        assert "skill_type" in result
        assert "output" in result
        assert len(result["output"]) > 100  # Meaningful output

        # Verify content quality
        output = result["output"]
        assert "SSL" in output.upper() or "Certificate" in output
        assert "Step" in output or "Diagnostic" in output
