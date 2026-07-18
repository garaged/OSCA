from osca.security.api import AuthorizationContext, Capability


def local_authorization_context() -> AuthorizationContext:
    """Trusted M1 local profile context backed by the operating-system user boundary."""

    return AuthorizationContext(
        actor="local-os-user",
        authentication_method="operating-system-user-boundary",
        capabilities=frozenset(Capability),
    )
