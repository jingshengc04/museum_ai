"""Offline smoke test: builds every stage's input and schema without calling the API. Run before spending tokens.

    uv run python smoke.py
"""
from __future__ import annotations

import agent
import checks
import images
import run  # noqa: F401  (syntax and import errors in the runner show up here)
import view  # noqa: F401
import schemas
import seedance  # noqa: F401  (import errors show up here)
import timing    # noqa: F401


def main() -> None:
    for model in (schemas.Identification, schemas.Research, schemas.MaterialSheet, schemas.AssetPlan,
                  schemas.ConceptSet, schemas.Script, schemas.Review, schemas.KeywordBatch):
        agent.strict_schema(model)
    for e in agent.exhibits():
        photo = agent.HERE / e["test_photo"] if e.get("test_photo") else None
        blocks = agent.photo_blocks(photo) + agent.asset_blocks(e["id"])
        agent._content_for_key(blocks)
        agent.pack(e["id"])
        print(f"{e['id']}: {sum(1 for b in blocks if b['type'] == 'image')} images, prompts and schemas OK")
    for stage in ("s0_identify", "s0b_research", "s1_digest", "s1b_assets", "s2_concept", "s3_script", "s4_review", "keywords"):
        assert agent.prompt_file(stage).exists(), stage
    assert checks.keywords([{"text": "x"}], "x") is not None
    assert images.total([]) == 0
    print("smoke OK")


if __name__ == "__main__":
    main()
