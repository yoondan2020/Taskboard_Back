from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_BCRYPT_BYTES = 72

def _ensure_bcrypt_len(plain: str) -> str:
    # bcrypt는 입력이 72바이트를 넘으면 에러가 나므로 사전에 막는다.
    if plain is None:
        raise ValueError("password is required")
    if len(plain.encode("utf-8")) > MAX_BCRYPT_BYTES:
        raise ValueError("password too long (bcrypt max 72 bytes)")
    return plain

def verify_password(plain: str, hashed: str) -> bool:
    plain = _ensure_bcrypt_len(plain)
    return pwd_context.verify(plain, hashed)

def hash_password(plain: str) -> str:
    plain = _ensure_bcrypt_len(plain)
    return pwd_context.hash(plain)
