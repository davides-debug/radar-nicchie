import os
import pytest
from storage import db_manager
from report import generate_dashboard as dashboard_module

def test_generate_dashboard_creates_file(tmp_path, monkeypatch):
    """Testa che la dashboard venga creata quando il DB contiene dati, usando file temporanei isolati."""
    db_path = str(tmp_path / "niches.db")
    output_html = str(tmp_path / "dashboard.html")

    monkeypatch.setattr(db_manager, "DB_PATH", db_path)
    monkeypatch.setattr(dashboard_module, "DB_PATH", db_path)
    monkeypatch.setattr(dashboard_module, "OUTPUT_HTML", output_html)

    db_manager.init_db()
    db_manager.save_niche_data("test niche", "google_trends", 1.0, 42.0)

    dashboard_module.generate_dashboard()

    assert os.path.exists(output_html)
    assert os.path.getsize(output_html) > 0
