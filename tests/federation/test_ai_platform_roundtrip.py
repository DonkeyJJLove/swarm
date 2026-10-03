from dataclasses import replace
from hashlib import sha256
import unittest
from federation.ai_platform_runtime_adapter import AiPlatformRuntimeProjection,FederationRuntimeAdapterError,SwarmAdapterPolicy,adapt_to_swarm_request,adapter_evidence
from runtime.admission import evaluate_runtime_admission
from runtime.contracts import AdmissionDecision,AdmissionReason,AdmissionValidationContext,RuntimeRole

H=lambda s:sha256(s.encode()).hexdigest()
def projection():
 return AiPlatformRuntimeProjection(
  "proposal:1","mission:1","workload:1","subject:1","runtime:1","sandbox:1","workspace:1",
  H("attestation"),H("executor"),"effect:1","policy:1",H("lineage"),"read","observe","repo:fixture",
  H("payload"),"HEALTHY",H("ai-identity"),H("ai-effect"))
def policy():
 return SwarmAdapterPolicy(RuntimeRole.AGENT_WORKLOAD,"LOCAL",H("artifact"),"current:1","repository.observe",
  ("repo:fixture",),("read",),"corr:1",("runtime.observe",),H("action"),"pdp:1",H("proposal"),
  ("repo:fixture",),("read",),("runtime.observe",),"nonce:1")
class RoundTripTests(unittest.TestCase):
 def test_exact_projection_round_trip_admits_only_declared_subset(self):
  p=projection();r=adapt_to_swarm_request(p,policy())
  d=evaluate_runtime_admission(r,AdmissionValidationContext(frozenset()))
  self.assertEqual((d.decision,d.reason),(AdmissionDecision.ADMIT,AdmissionReason.ADMITTED))
  ev=adapter_evidence(p,r);self.assertEqual((ev["authority_effect"],ev["execution_effect"]),("NONE","NONE"))
  self.assertEqual(ev["ai_platform_runtime_identity_digest"],H("ai-identity"))
 def test_identity_substitution_is_denied_by_existing_admission(self):
  r=adapt_to_swarm_request(projection(),policy())
  r=replace(r,runtime_identity=replace(r.runtime_identity,runtime_id="runtime:other"))
  d=evaluate_runtime_admission(r,AdmissionValidationContext(frozenset()))
  self.assertEqual((d.decision,d.reason),(AdmissionDecision.DENY,AdmissionReason.RUNTIME_IDENTITY_MISMATCH))
 def test_capability_widening_is_denied(self):
  r=adapt_to_swarm_request(projection(),policy())
  r=replace(r,requested_effect=replace(r.requested_effect,requested_capabilities=("runtime.observe","workload.execute")))
  d=evaluate_runtime_admission(r,AdmissionValidationContext(frozenset()))
  self.assertEqual((d.decision,d.reason),(AdmissionDecision.DENY,AdmissionReason.CAPABILITY_WIDENING))
 def test_projection_has_no_grant_or_executor_creation(self):
  self.assertNotIn("authority_grant",projection().__dict__)
  self.assertNotIn("credential",projection().__dict__)
 def test_open_projection_fields_fail_closed(self):
  x=projection().__dict__.copy();x["extra"]="x"
  with self.assertRaises(FederationRuntimeAdapterError):AiPlatformRuntimeProjection.from_mapping(x)
if __name__=="__main__":unittest.main()
