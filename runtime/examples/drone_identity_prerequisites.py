"""Current drone identity prerequisites.

The current repository evidence is intentionally incomplete, so this example must
remain NOT_READY and must not fabricate missing identity or provenance.
"""

from __future__ import annotations

from runtime.identity_prerequisites import (
    CANONICAL_IDENTITY_SOURCES,
    IdentityPrerequisiteEvidence,
    qualify_identity_prerequisites,
)


DRONE_IDENTITY_PREREQUISITE_EVIDENCE = IdentityPrerequisiteEvidence(
    source_refs=CANONICAL_IDENTITY_SOURCES,
    schema_compatibility_qualified=False,
)

DRONE_IDENTITY_PREREQUISITE_QUALIFICATION = qualify_identity_prerequisites(
    DRONE_IDENTITY_PREREQUISITE_EVIDENCE
)
