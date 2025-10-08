from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier, StaticTokenVerifier

# === Option A: JWKS / asymmetric verification (PROD-friendly) ===
# verifier = JWTVerifier(
#     jwks_uri="https://auth.example.com/.well-known/jwks.json",
#     issuer="https://auth.example.com",
#     audience="mcp-production-api",
# )
#
# === Option B: HMAC / symmetric shared secret (internal) ===
# verifier = JWTVerifier(
#     public_key="your-32+char-shared-secret",
#     issuer="internal-auth",
#     audience="mcp-internal-api",
#     algorithm="HS256",   # HS256 / HS384 / HS512
# )
#
# === Option C: Static public key (dev/test) ===
# verifier = JWTVerifier(
#     public_key="""-----BEGIN PUBLIC KEY-----
# YOUR_PEM_KEY
# -----END PUBLIC KEY-----""",
#     issuer="https://auth.example.com",
#     audience="mcp-dev-api",
# )

# === Option D: Static tokens (DEV-ONLY) ===
verifier = StaticTokenVerifier(
    tokens={
        "dev-alice-token": {"client_id": "alice@company.com", "scopes": ["read:data", "write:data"]},
        "dev-guest-token": {"client_id": "guest", "scopes": ["read:data"]},
    },
    required_scopes=["read:data"],
)

mcp = FastMCP(name="Protected Server (Token Verification)", auth=verifier)

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run(transport='streamable-http')  # Run SSE/HTTP; include Authorization: Bearer <token> from your client
