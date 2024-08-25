import boto3
from typing import Any

class OIDCAuthenticator:
    def __init__(self, token: str) -> None:
        self.token = token

    def authenticate(self) -> Any:
        """Authenticate with AWS using OIDC."""
        return boto3.client('sts', region_name='eu-central-1').assume_role_with_web_identity(
            RoleArn='arn:aws:iam::account-id:role/role-name',
            RoleSessionName='session-name',
            WebIdentityToken=self.token
        )
