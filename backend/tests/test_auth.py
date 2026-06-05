"""Tests for authentication module."""
import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock entire heavy dependency chain before any app imports fire.
# The app.core.__init__ pulls in tools → rag → ChromaDB + langchain.
sys.modules['langchain_chroma'] = MagicMock()
sys.modules['chromadb'] = MagicMock()
# Also mock app.rag so its __init__.py doesn't try to import a non-existent
# 'vectorstore' name from vectorstore.py (latent bug in vectorstore module:
# only get_vectorstore() exists, no module-level 'vectorstore').
sys.modules['app.rag'] = MagicMock()
sys.modules['app.rag.retriever'] = MagicMock()
sys.modules['app.rag.vectorstore'] = MagicMock()
sys.modules['app.rag.embeddings'] = MagicMock()
sys.modules['app.rag.splitter'] = MagicMock()
sys.modules['app.rag.loader'] = MagicMock()

from app.core.security import (  # noqa: E402
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "SecureP@ss123"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_wrong_password(self):
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_hash_is_stable(self):
        pw = "same_password"
        h1 = hash_password(pw)
        h2 = hash_password(pw)
        assert h1 != h2
        assert verify_password(pw, h1)
        assert verify_password(pw, h2)


class TestJWT:
    def test_create_and_decode_token(self):
        token = create_access_token(user_id="user_abc123")
        assert isinstance(token, str)
        payload = decode_token(token)
        assert payload["sub"] == "user_abc123"

    def test_decode_invalid_token(self):
        import pytest
        with pytest.raises(Exception):
            decode_token("not.a.valid.jwt.token")

    def test_token_has_expiry(self):
        token = create_access_token(user_id="user_test")
        payload = decode_token(token)
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload
