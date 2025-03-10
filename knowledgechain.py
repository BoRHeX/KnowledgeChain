import hashlib
import json
import time

class KnowledgeBlock:
    def __init__(self, index, previous_hash, timestamp, data, merkle_root, validator, proof):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data  # Stored knowledge
        self.merkle_root = merkle_root
        self.validator = validator  # Proof of Knowledge Validator
        self.proof = proof  # PoK (Proof of Knowledge)
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_contents = f"{self.index}{self.previous_hash}{self.timestamp}{json.dumps(self.data)}{self.merkle_root}{self.validator}{self.proof}"
        return hashlib.sha256(block_contents.encode()).hexdigest()

class KnowledgeChain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return KnowledgeBlock(
            index=0,
            previous_hash="0",
            timestamp=time.time(),
            data={"message": "KBC Exists - Genesis Block"},
            merkle_root="0x2c1f7d9e8a3b45f1d6e7c890ab12cd34ef56fa7890bcde1234567890fedcba98",
            validator="Master Boyan",
            proof="0x00000000000000000000000000000000"
        )

    def add_block(self, data, validator, proof):
        previous_block = self.chain[-1]
        new_block = KnowledgeBlock(
            index=len(self.chain),
            previous_hash=previous_block.hash,
            timestamp=time.time(),
            data=data,
            merkle_root=hashlib.sha256(json.dumps(data).encode()).hexdigest(),
            validator=validator,
            proof=proof
        )
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.previous_hash != previous_block.hash:
                return False
            if current_block.hash != current_block.calculate_hash():
                return False
        return True
