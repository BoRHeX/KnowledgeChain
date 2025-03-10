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
            previous_hash="0" * 64,  # No previous block
            timestamp=time.time(),
            data="Genesis Block - KBC Exists",
            merkle_root="GENESIS",
            validator="KBC_Oracle",
            proof="0x1"
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

# Initialize KnowledgeChain
knowledge_chain = KnowledgeChain()

def save_block_to_file(block):
    block_data = {
        "index": block.index,
        "timestamp": block.timestamp,
        "data": block.data,
        "previous_hash": block.previous_hash,
        "merkle_root": block.merkle_root,
        "validator": block.validator,
        "proof": block.proof,
        "hash": block.hash
    }
    with open(f"block_{block.index}.json", "w") as f:
        json.dump(block_data, f, indent=4)
    print(f"\n✅ Block {block.index} saved to 'block_{block.index}.json'")

# Test Adding a Block
if __name__ == "__main__":
    print("KnowledgeChain is running!")
    
    # Create and display the Genesis Block
    genesis_block = knowledge_chain.chain[0]
    print("\nGenesis Block:")
    print(f"Index: {genesis_block.index}")
    print(f"Timestamp: {genesis_block.timestamp}")
    print(f"Data: {genesis_block.data}")
    print(f"Previous Hash: {genesis_block.previous_hash}")
    print(f"Merkle Root: {genesis_block.merkle_root}")
    print(f"Validator: {genesis_block.validator}")
    print(f"Proof: {genesis_block.proof}")
    print(f"Hash: {genesis_block.hash}")
    
    # Adding a new knowledge block
    new_data = "Master Boyan submits the first Knowledge Contribution"
    new_block = knowledge_chain.add_block(new_data, "Master Boyan", "0x2")
    save_block_to_file(new_block)
    
    print("\n✅ New Block Added!")
    print(f"Index: {new_block.index}")
    print(f"Timestamp: {new_block.timestamp}")
    print(f"Data: {new_block.data}")
    print(f"Previous Hash: {new_block.previous_hash}")
    print(f"Merkle Root: {new_block.merkle_root}")
    print(f"Validator: {new_block.validator}")
    print(f"Proof: {new_block.proof}")
    print(f"Hash: {new_block.hash}")
    
    # Validate Chain
    if knowledge_chain.is_chain_valid():
        print("\n✅ KnowledgeChain Integrity Verified: VALID")
    else:
        print("\n❌ KnowledgeChain Integrity Check: FAILED")
