# Threat Model

Axezent AI CTR assumes the AI agent output is untrusted.

The checker is designed to catch deterministic receipt violations such as:

- undeclared file modifications
- forbidden path access
- failed tests presented as successful
- malformed SHA-256 evidence hashes
- disallowed network access
- non-monotonic trace step IDs
- missing required test evidence

Out of scope:

- hidden model reasoning
- semantic truth of every natural-language statement
- complete AI alignment
- future behavior guarantees
- proof that an external simulator or agent is globally correct
