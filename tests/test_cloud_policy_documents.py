"""Regression checks for all repository film agents, skills and commands."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_every_film_definition_loads_common_policy_and_config():
    definitions = [*ROOT.glob('.opencode/agents/*.md'), *ROOT.glob('.opencode/commands/*.md'), *ROOT.glob('.opencode/skills/*/SKILL.md')]
    assert len(list(ROOT.glob('.opencode/agents/*.md'))) == 15
    assert len(list(ROOT.glob('.opencode/skills/*/SKILL.md'))) == 16
    for path in definitions:
        text = path.read_text(encoding='utf-8')
        assert 'docs/cloud-policy.md' in text, path
        assert 'config/cloud-tiers.yaml' in text, path
        assert text.startswith('---\n'), path
        frontmatter = yaml.safe_load(text.split('---', 2)[1])
        assert frontmatter.get('description'), path
        # Recommendations never pretend to be OpenCode runtime model references.
        assert 'model' not in frontmatter, path


def test_budget_estimate_precedes_screenplay_in_director_and_command():
    for name in ['.opencode/agents/film-director.md', '.opencode/commands/film.md']:
        text = (ROOT / name).read_text(encoding='utf-8')
        pipeline = text.split('story\n', 1)[1]
        assert pipeline.index('budget estimate') < pipeline.index('screenplay')
        assert 'budget/decision.yaml' in text


def test_legacy_dialects_are_explicit_opt_in():
    for name in ['flux-2-klein', 'krea-2', 'qwen-image', 'ltx-2.5', 'minimax-h3', 'qwen3-tts']:
        text = (ROOT / '.opencode/skills' / name / 'SKILL.md').read_text(encoding='utf-8').lower()
        assert 'legacy' in text and 'opt-in' in text, name
