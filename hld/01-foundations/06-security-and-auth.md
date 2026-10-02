# 🔐 Security, Authentication & Zero-Trust Architecture

Security is a primary non-functional requirement in high-level system design interviews. You must protect data in transit, data at rest, and authenticate/authorize microservice traffic.

---

## 1. Authentication & Authorization Patterns

```mermaid
flowchart LR
    Client([Client App]) -->|1. Authenticate with credentials / OAuth2| IdP[Identity Provider / Auth0 / Keycloak]
    IdP -- 2. Returns Signed JWT Token --> Client
    Client -->|3. Request + Bearer JWT| APIGW[API Gateway]
    APIGW -->|4. Cryptographic Signature Verification (JWKS Public Key)| APIGW
    APIGW -->|5. Forward with Claims & User-ID| ServiceA[Microservice A]
    ServiceA -->|6. mTLS / Service Mesh| ServiceB[Microservice B]
```

### Authentication vs. Authorization
* **Authentication (AuthN)**: *Who are you?* (e.g., Username/Password, MFA, Passkeys/WebAuthn, SAML/OIDC).
* **Authorization (AuthZ)**: *What are you allowed to do?* (e.g., RBAC, ABAC).

---

## 2. Token-Based Auth (JWT) vs. Server-Side Sessions

| Feature | Server-Side Sessions | Stateless JWT (JSON Web Tokens) |
|---|---|---|
| **Storage** | Redis / Database session store | Encoded & signed in client storage (Cookie / LocalStorage) |
| **Verification** | Must query Redis on every request | Verified locally using the public key (JWKS) with zero DB lookups |
| **Revocation** | Instant: Delete session ID from Redis | Harder: Must maintain a token revocation blocklist in Redis until expiration |
| **Scalability** | Requires scaling central session cache | Infinitely scalable across distributed microservices |
| **Payload Size** | Tiny cookie (Session ID $\approx 32$ bytes) | Larger header/payload/signature ($500 - 1500$ bytes) |

### Best-Practice Hybrid Token Pattern:
* **Access Token**: Short-lived (5 - 15 minutes), stateless JWT containing user claims and roles.
* **Refresh Token**: Long-lived (7 - 30 days), stored securely in HttpOnly, SameSite, Secure cookie, tracked in database with rotation to enable instant revocation.

---

## 3. OAuth 2.0 & OpenID Connect (OIDC)

* **OAuth 2.0**: Framework for **delegated authorization** (e.g., "Allow app X to access my Google Drive files").
* **OpenID Connect (OIDC)**: Identity layer on top of OAuth 2.0 providing **authentication** and returning an `id_token` in addition to `access_token`.

### Authorization Code Flow with PKCE (Proof Key for Code Exchange)
MANDATORY standard for SPAs, mobile apps, and modern web apps:
1. Client generates a cryptographic `code_verifier` and derives `code_challenge = SHA256(code_verifier)`.
2. Client redirects user to Auth server with `code_challenge`.
3. User logs in; Auth server returns temporary `authorization_code`.
4. Client exchanges `authorization_code` + original `code_verifier` for tokens.
5. Auth server verifies that `SHA256(code_verifier) == code_challenge`, thwarting code interception attacks.

---

## 4. Zero-Trust & Service-to-Service Security

1. **Mutual TLS (mTLS)**:
   - In a microservices cluster, every pod/container has an X.509 certificate managed by a service mesh (e.g. Istio, Linkerd).
   - Both client and server verify each other's identity and encrypt communication, defeating man-in-the-middle attacks within the VPC.
2. **Secrets Management**:
   - Never commit API keys or database passwords to git.
   - Use HashiCorp Vault, AWS Secrets Manager, or Google Cloud Secret Manager with automated dynamic credential rotation.
3. **Data Protection**:
   - **In Transit**: TLS 1.3 with Perfect Forward Secrecy (PFS).
   - **At Rest**: AES-256 encryption on database disks, backups, and S3 buckets with customer-managed keys (KMS).
   - **Sensitive Fields**: Column-level encryption or pseudonymization for PII/PCI/HIPAA compliance (Hashing with salt + pepper for passwords using Argon2id or bcrypt).
