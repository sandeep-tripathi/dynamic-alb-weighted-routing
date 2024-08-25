import unittest
from unittest.mock import patch, MagicMock
from oidc_boto_authentication import AWSOIDCAuth


class TestOIDCAuth(unittest.TestCase):

    @patch('oidc_boto_authentication.boto3.Session')
    @patch('oidc_boto_authentication.boto3.client')
    def test_get_boto3_client_with_oidc(self, mock_boto_client, mock_boto_session):
        """Test the initialization and return of a boto3 client using OIDC authentication."""

        # Setup the mock session and client
        mock_session = MagicMock()
        mock_boto_session.return_value = mock_session
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client

        # Create an instance of AWSOIDCAuth and initialize the client
        oidc_auth = AWSOIDCAuth()
        service_client = oidc_auth.get_boto3_client_with_oidc('s3')

        # Assertions to ensure the session and client are being created
        mock_boto_session.assert_called_once_with()
        mock_boto_client.assert_called_once_with('s3', aws_session_token=mock_session.get_credentials().token)

        # Check if the returned client is the mocked client
        self.assertEqual(service_client, mock_client)

    @patch('oidc_boto_authentication.boto3.Session')
    def test_get_session_with_oidc(self, mock_boto_session):
        """Test the creation of a boto3 session with OIDC authentication."""
        
        # Setup the mock session
        mock_session = MagicMock()
        mock_boto_session.return_value = mock_session

        # Create an instance of AWSOIDCAuth and initialize the session
        oidc_auth = AWSOIDCAuth()
        session = oidc_auth.get_session_with_oidc()

        # Assertions to ensure the session is being created
        mock_boto_session.assert_called_once_with()
        
        # Check if the returned session is the mocked session
        self.assertEqual(session, mock_session)


if __name__ == '__main__':
    unittest.main()

