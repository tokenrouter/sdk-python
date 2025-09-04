"""
Client-side encryption utilities for inline provider keys.

Format matches API expectations (RSA-OAEP-256 + AES-256-GCM):
- Input: dict {provider_name: api_key}
- Output header value: base64url(JSON({alg, enc, ek, iv, ct, tag}))
"""

from __future__ import annotations

import base64
import json
import os
from typing import Dict

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _b64url_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def encrypt_provider_keys_header(provider_keys: Dict[str, str], public_key_pem: str) -> str:
    # Normalize provider names
    norm: Dict[str, str] = {}
    for k, v in provider_keys.items():
        if not v:
            continue
        key = k.strip().lower()
        if key == "gemini":
            key = "google"
        elif key == "llama":
            key = "meta"
        norm[key] = v
    # Serialize payload
    plaintext = json.dumps(norm, separators=(",", ":")).encode()

    # Load public key
    pub = serialization.load_pem_public_key(public_key_pem.encode())

    # Generate AES-256-GCM key and nonce
    aes_key = AESGCM.generate_key(bit_length=256)
    iv = os.urandom(12)
    aesgcm = AESGCM(aes_key)
    ciphertext = aesgcm.encrypt(iv, plaintext, associated_data=None)
    ct, tag = ciphertext[:-16], ciphertext[-16:]

    # Encrypt AES key with RSA-OAEP-256
    ek = pub.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # Build wrapper and base64url-encode whole JSON for header safety
    wrapper = {
        "alg": "RSA-OAEP-256",
        "enc": "A256GCM",
        "ek": _b64url_encode(ek),
        "iv": _b64url_encode(iv),
        "ct": _b64url_encode(ct),
        "tag": _b64url_encode(tag),
    }
    wrapper_json = json.dumps(wrapper, separators=(",", ":")).encode()
    return _b64url_encode(wrapper_json)

