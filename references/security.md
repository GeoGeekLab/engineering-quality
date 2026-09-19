# Security

Security review begins at trust boundaries.

## Identify trust boundaries

Treat user-controlled input, request metadata, files and paths, external service responses, messages, serialized objects, and operator-supplied configuration as untrusted unless the system establishes otherwise.

Normalize and validate at the boundary before domain logic relies on stronger invariants.

## Authorization before action

Authentication establishes identity; authorization establishes permitted action. Verify authorization at the server-side boundary where the protected action occurs.

Pay particular attention to object-level authorization when identifiers are externally controlled.

## Injection and command execution

Prefer structured APIs and parameterization for SQL, shell commands, templates, directory queries, URLs, and filesystem paths. Avoid constructing executable syntax through string concatenation.

## Secrets and sensitive data

Do not place secrets in source, logs, errors, test fixtures, snapshots, or generated artifacts. Keep diagnostics useful without exposing credentials, tokens, personal data, or confidential payloads.

## Cryptography

Use maintained, well-reviewed platform libraries and established constructions. Do not design custom cryptographic primitives or protocols.

## Deserialization and parsing

Reject unsupported or ambiguous input rather than guessing. Apply size, depth, count, and resource limits where hostile input can cause excessive work.

## Network and file access

Consider server-side request forgery, path traversal, symlinks, local-network access, redirects, archive extraction, unsafe file types, and resource exhaustion.

## Dependencies

Evaluate direct and transitive dependencies for provenance, maintenance, known vulnerabilities, and unnecessary runtime capability.

## Security standards

For web applications and services, use the current OWASP Application Security Verification Standard as a structured source of security requirements. Apply requirements according to the application's risk and architecture.
