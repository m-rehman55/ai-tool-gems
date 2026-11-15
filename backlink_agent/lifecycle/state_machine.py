"""Acquisition State Machine enforcing transition invariants and evidence gates."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

from .models import (
    LifecycleState,
    LifecycleTransitionRecord,
    VALID_TRANSITION_GRAPH,
)
from .store import LocalSQLiteLifecycleStore

logger = logging.getLogger(__name__)


class StateMachineTransitionError(Exception):
    """Raised when an invalid or ungrounded lifecycle transition is attempted."""
    pass


class AcquisitionStateMachine:
    """Manages strictly validated, evidence-gated transitions in the backlink lifecycle."""

    def __init__(self, store: Optional[LocalSQLiteLifecycleStore] = None):
        self.store = store or LocalSQLiteLifecycleStore()

    def transition(
        self,
        prospect_id: str,
        to_state: str,
        actor: str,
        reason: str,
        evidence_data: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Tuple[bool, Optional[str], Optional[LifecycleTransitionRecord]]:
        evidence = evidence_data or {}
        prospect = self.store.get_prospect(prospect_id)
        if not prospect:
            return (False, f"Prospect '{prospect_id}' not found in lifecycle database", None)

        from_state = prospect["current_state"]

        # 1. State machine graph check
        valid_next_states = VALID_TRANSITION_GRAPH.get(from_state, set())
        if to_state not in valid_next_states:
            err = (
                f"Invalid lifecycle transition for {prospect_id}: '{from_state}' -> '{to_state}'. "
                f"Valid next states: {sorted(list(valid_next_states))}"
            )
            return (False, err, None)

        # 2. Invariant Check: Never infer publication without publication URL/evidence
        if to_state == LifecycleState.PUBLISHED:
            pub_url = evidence.get("publication_url") or prospect.get("publication_url")
            if not pub_url:
                err = "Cannot transition to 'published': Publication URL or verification proof required"
                return (False, err, None)

        # 3. Invariant Check: Never infer backlink verification without independent DOM anchor evidence
        if to_state == LifecycleState.BACKLINK_VERIFIED:
            if not evidence.get("anchor_verified") or not evidence.get("target_url_matched"):
                err = "Cannot transition to 'backlink_verified': Independent DOM anchor verification evidence required"
                return (False, err, None)

        # 4. Invariant Check: Owner approval requires matching draft hash
        if to_state == LifecycleState.OWNER_APPROVED:
            inbound_hash = evidence.get("draft_hash")
            stored_hash = prospect.get("draft_hash")
            if stored_hash and inbound_hash and inbound_hash != stored_hash:
                err = f"Draft hash mismatch on approval: expected '{stored_hash}', got '{inbound_hash}'"
                return (False, err, None)

        record = LifecycleTransitionRecord(
            prospect_id=prospect_id,
            from_state=from_state,
            to_state=to_state,
            actor=actor,
            reason=reason,
            evidence_data=evidence,
            idempotency_key=idempotency_key,
        )

        success = self.store.record_transition(record)
        if not success:
            return (False, "Atomic transition failed (state conflict or duplicate idempotency key)", None)

        return (True, None, record)
