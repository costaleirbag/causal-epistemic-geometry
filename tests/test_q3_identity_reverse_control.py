"""Software fixtures only; never load a model or scientific dataset."""
import ast
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'src')]
import q3_identity_reverse_control as control
from epistemic_geometry.research.durable_journal import SingleWriterJournal


def mock_journal(tmp_path, copy_reverse=False):
    m = control.verified_manifest()
    refs = json.loads((control.REVIEW / 'REFERENCES.json').read_text())
    identity = {'software_test_only': True}
    control.write(tmp_path / 'PREOPEN.json', identity)
    with SingleWriterJournal(tmp_path / 'journal.jsonl', identity=identity, key_fields=control.KEYS) as journal:
        for i, row in enumerate(m['schedule']):
            value = refs[row['family_id']]
            if copy_reverse and row['condition'] == 'REVERSE':
                value = repr(next(f['input']['text'] for f in m['fixtures'] if f['fixture_id'] == row['family_id']))
            journal.append({**row, 'schedule_index': i, 'raw_output': f'FINAL: {value}',
                            'generated_token_count': 10, 'elapsed_seconds': 0.1,
                            'terminal_reason': 'eos', 'runtime_error': None, 'truncated': False})
        journal.seal(tmp_path / 'COLLECTION_COMPLETE_SEAL.json', m['schedule'], lambda rows: {
            'status': 'COLLECTION_COMPLETE_RAW_UNSCORED', 'correctness_inspected': False,
            'semantic_scoring': 'NOT_RUN', 'manifest_sha256': control.sha(control.REVIEW / 'MANIFEST.json')})


def test_panel_pairs_and_reference_isolation():
    m = control.verified_manifest()
    refs = json.loads((control.REVIEW / 'REFERENCES.json').read_text())
    assert len(m['fixtures']) == 12 and len(m['schedule']) == 24
    for pair in range(6):
        f = [f for f in m['fixtures'] if f['pair_id'] == pair]
        assert f[0]['input'] == f[1]['input']
        assert f[0]['source'].replace('data["text"]', 'data["text"][::-1]') == f[1]['source']
        text = f[0]['input']['text']
        assert text.isascii() and text != text[::-1]
        assert ast.literal_eval(refs[f[1]['fixture_id']]) == text[::-1]
        assert 'reference' not in f[0] and 'reference' not in f[1]
        for rollout in (0, 1):
            rows = [r for r in m['schedule'] if r['pair_id'] == pair and r['rollout_index'] == rollout]
            assert len(rows) == 2 and rows[0]['seed'] == rows[1]['seed']


@pytest.mark.parametrize('copy_reverse,correct_pairs', [(False, 12), (True, 0)])
def test_exact_pair_scoring_not_arbitrary_change(tmp_path, copy_reverse, correct_pairs):
    mock_journal(tmp_path, copy_reverse)
    control.score(tmp_path)
    r = json.loads((tmp_path / 'RESULT.json').read_text())
    assert r['pairs_both_correct'] == correct_pairs
    assert r['conditions']['IDENTITY']['correct'] == 12
    assert r['reverse_returned_original_input'] == (12 if copy_reverse else 0)


def test_mutated_raw_rejected_before_scoring(tmp_path):
    mock_journal(tmp_path)
    with (tmp_path / 'journal.jsonl').open('ab') as f:
        f.write(b'\n')
    with pytest.raises(AssertionError):
        control.score(tmp_path)
    assert not (tmp_path / 'SCORES.json').exists()
