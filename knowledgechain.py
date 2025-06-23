import hashlib
import json
import time
import uuid
from typing import Dict, List


class KnowledgeBlock:
    """Represents a single block in the KnowledgeChain."""

    def __init__(self, index: int, previous_hash: str, timestamp: float, data, *,
                 merkle_root: str, validator: str, proof: str,
                 knowledge_id: str = None, author_id: str = "",
                 evidence=None, kbc_score: float = 0.0,
                 validator_signatures: List[Dict] = None, validated: bool = False):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.merkle_root = merkle_root
        self.validator = validator
        self.proof = proof
        self.knowledge_id = knowledge_id or str(uuid.uuid4())
        self.author_id = author_id
        self.evidence = evidence if evidence is not None else []
        self.kbc_score = kbc_score
        self.validator_signatures = validator_signatures if validator_signatures is not None else []
        self.validated = validated
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_contents = json.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "merkle_root": self.merkle_root,
            "validator": self.validator,
            "proof": self.proof,
            "knowledge_id": self.knowledge_id,
            "author_id": self.author_id,
            "evidence": self.evidence,
            "kbc_score": self.kbc_score,
            "validator_signatures": self.validator_signatures,
            "validated": self.validated
        }, sort_keys=True)
        return hashlib.sha256(block_contents.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "data": self.data,
            "merkle_root": self.merkle_root,
            "validator": self.validator,
            "proof": self.proof,
            "knowledge_id": self.knowledge_id,
            "author_id": self.author_id,
            "evidence": self.evidence,
            "kbc_score": self.kbc_score,
            "validator_signatures": self.validator_signatures,
            "validated": self.validated,
            "hash": self.hash
        }


class User:
    """Represents a participant in the KnowledgeChain."""

    def __init__(self, user_id: str, name: str, is_ai: bool = False, total_kbc_earned: float = 0.0):
        self.id = user_id
        self.name = name
        self.is_ai = is_ai
        self.total_kbc_earned = total_kbc_earned

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "is_ai": self.is_ai,
            "total_kbc_earned": self.total_kbc_earned,
        }


class KnowledgeChain:
    def __init__(self):
        self.chain: List[KnowledgeBlock] = [self.create_genesis_block()]

    def create_genesis_block(self) -> KnowledgeBlock:
        return KnowledgeBlock(
            index=0,
            previous_hash="0" * 64,
            timestamp=time.time(),
            data="Genesis Block - KBC Exists",
            merkle_root="GENESIS",
            validator="KBC_Oracle",
            proof="0x1",
            author_id="KBC_Oracle",
        )

    def add_block(self, data, validator: str, proof: str, author_id: str, evidence=None) -> KnowledgeBlock:
        previous_block = self.chain[-1]
        new_block = KnowledgeBlock(
            index=len(self.chain),
            previous_hash=previous_block.hash,
            timestamp=time.time(),
            data=data,
            merkle_root=hashlib.sha256(json.dumps(data).encode()).hexdigest(),
            validator=validator,
            proof=proof,
            author_id=author_id,
            evidence=evidence or [],
        )
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.previous_hash != previous_block.hash:
                return False
            if current_block.hash != current_block.calculate_hash():
                return False
        return True


# user management -----------------------------------------------------------

USERS_FILE = "users.json"


def load_users() -> Dict[str, User]:
    try:
        with open(USERS_FILE, "r") as f:
            data = json.load(f)
            return {u["id"]: User(**u) for u in data}
    except FileNotFoundError:
        return {}


def save_users(users: Dict[str, User]):
    with open(USERS_FILE, "w") as f:
        json.dump([u.to_dict() for u in users.values()], f, indent=4)


users: Dict[str, User] = load_users()
knowledge_chain = KnowledgeChain()


def save_block_to_file(block: KnowledgeBlock):
    with open(f"block_{block.index}.json", "w") as f:
        json.dump(block.to_dict(), f, indent=4)
    print(f"\n✅ Block {block.index} saved to 'block_{block.index}.json'")


# validation and scoring ---------------------------------------------------


def validate_block(block: KnowledgeBlock, validator_id: str, validation_score: float):
    signature = {"validator_id": validator_id, "validation_score": validation_score}
    block.validator_signatures.append(signature)

    ai_validations = 0
    human_validations = 0
    for s in block.validator_signatures:
        user = users.get(s["validator_id"])
        if user and user.is_ai:
            ai_validations += 1
        else:
            human_validations += 1

    if not block.validated and ai_validations >= 1 and human_validations >= 2:
        block.validated = True
        average = sum(s["validation_score"] for s in block.validator_signatures) / len(block.validator_signatures)
        block.kbc_score = average
        author = users.get(block.author_id)
        if author:
            author.total_kbc_earned += average
            save_users(users)
        print(f"Block {block.index} validated with score {average}")


# CLI ---------------------------------------------------------------------

def ensure_user_exists(user_id: str) -> User:
    if user_id in users:
        return users[user_id]
    name = input("Enter user name: ")
    is_ai = input("Is this user AI? (y/n): ").lower().startswith("y")
    user = User(user_id, name, is_ai)
    users[user_id] = user
    save_users(users)
    return user


def submit_knowledge():
    author_id = input("Author ID: ")
    ensure_user_exists(author_id)
    data = input("Knowledge content: ")
    evidence_raw = input("Evidence (comma separated): ")
    evidence = [e.strip() for e in evidence_raw.split(',')] if evidence_raw else []
    block = knowledge_chain.add_block(
        data=data,
        validator=author_id,
        proof="submitted",
        author_id=author_id,
        evidence=evidence,
    )
    save_block_to_file(block)
    print(f"Knowledge submitted in block {block.index}")


def validate_knowledge():
    validator_id = input("Validator ID: ")
    ensure_user_exists(validator_id)
    try:
        block_index = int(input("Block index to validate: "))
        block = knowledge_chain.chain[block_index]
    except (ValueError, IndexError):
        print("Invalid block index")
        return
    try:
        score = float(input("Validation score (0-1): "))
    except ValueError:
        print("Invalid score")
        return
    validate_block(block, validator_id, score)
    save_block_to_file(block)


def view_chain():
    for block in knowledge_chain.chain:
        print(json.dumps(block.to_dict(), indent=4))


def view_user_stats():
    for user in users.values():
        print(f"{user.id} | {user.name} | AI: {user.is_ai} | KBC: {user.total_kbc_earned}")


def main_cli():
    while True:
        print("\nKnowledgeChain CLI")
        print("1) Submit Knowledge")
        print("2) Validate Knowledge")
        print("3) View Chain")
        print("4) View User Stats")
        print("5) Exit")
        choice = input("Select option: ")
        if choice == "1":
            submit_knowledge()
        elif choice == "2":
            validate_knowledge()
        elif choice == "3":
            view_chain()
        elif choice == "4":
            view_user_stats()
        elif choice == "5":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main_cli()
