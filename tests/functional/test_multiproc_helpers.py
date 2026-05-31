from kryptos.pipeline.attack_generator import AttackSpec
from kryptos.provenance.attack_log import AttackParameters

class AttackGenTestHelper:
    def generate_comprehensive_queue(self, ciphertext, max_total):
        _ = ciphertext
        _ = max_total
        return [
            AttackSpec(
                parameters=AttackParameters(cipher_type="vigenere", key_or_params={"key_length": 4}),
                priority=1.0,
                source="test",
                rationale="r",
                tags=["a"],
            ),
            AttackSpec(
                parameters=AttackParameters(cipher_type="transposition", key_or_params={"period": 5, "method": "simulated_annealing"}),
                priority=0.9,
                source="test",
                rationale="r",
                tags=["b"],
            ),
        ]
