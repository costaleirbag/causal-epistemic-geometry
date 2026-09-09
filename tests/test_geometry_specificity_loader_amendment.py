import json
import sys

sys.path.insert(0, "scripts")
import geometry_specificity_loader_amendment as adapter


def test_exact_pinned_panel_content_and_calibration_fallback(tmp_path, monkeypatch):
    panel = tmp_path / adapter.runner.PANEL
    panel.parent.mkdir(parents=True)
    panel.write_text(
        json.dumps(
            {
                "dataset_revision": "fixed",
                "items": [{"item_id": "new", "prompt": "frozen prompt", "reference_answer": "42"}],
            }
        )
    )
    monkeypatch.setattr(adapter.runner, "ROOT", tmp_path)
    sentinel = object()
    calls = []

    def old(path, ids):
        calls.append(ids)
        return {"cal": sentinel}

    monkeypatch.setattr(adapter, "ORIGINAL_LOAD_ITEMS", old)
    result = adapter.load_items(tmp_path / "official", ["new", "cal"])
    assert result["new"].prompt == "frozen prompt"
    assert result["new"].reference_answer == "42"
    assert result["cal"] is sentinel
    assert calls == [{"cal"}]
