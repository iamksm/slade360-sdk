from datetime import datetime, timedelta
from typing import Any, Dict

import requests


class Authentication:
    """
    Handles OAuth 2.0-based authentication for accessing APIs on the HealthCloud platform.

    This class is responsible for retrieving and managing the access token required
    to authorize API requests. The token is automatically refreshed when it expires.

    https://healthcloud.sh/api-reference#tag/API_AUTHORIZATION
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        base_auth_url: str,
        base_edi_url: str,
        base_is_url: str,
        grant_type: str = "password",
    ) -> None:
        """
        Initializes the authentication class by setting up necessary credentials
        and making the initial authentication request to retrieve the access token.

        :param client_id: The client application's unique identifier for the authorization server.
        :param client_secret: The application's secret key for the authorization server.
        :param username: The registered user's email address for authentication.
        :param password: The registered user's password for authentication.
        :param base_auth_url: The base URL of the authorization server.
        :param base_edi_url: The base URL of the EDI system.
        :param base_is_url: The base URL of the Integration Services system.
        :param grant_type: The OAuth grant type for requesting an access token (default is "password").
        """
        self.base_auth_url = base_auth_url
        self.base_edi_url = base_edi_url
        self.base_is_url = base_is_url
        self.session = requests.Session()
        self.token_url = f"{self.base_auth_url}/oauth2/token/"
        self.auth_payload = {
            "grant_type": grant_type,
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password,
        }
        self.authenticate()

    def authenticate(self) -> None:
        """
        Authenticates with the authorization server to retrieve an access token.

        This method sends the OAuth 2.0 authentication request using the client credentials
        and updates the session headers with the retrieved access token.

        https://healthcloud.sh/api-reference#tag/API_AUTHORIZATION/operation/get_access_token
        """
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = self.session.post(
            self.token_url, data=self.auth_payload, headers=headers
        )
        response.raise_for_status()

        # Parse response and extract token and expiration time
        response_content = response.json()
        expires_in = response_content.get(
            "expires_in", 3600
        )  # Default to 1 hour if not provided
        self.session_expiry = datetime.now() + timedelta(seconds=expires_in)

        # Update session headers to include the access token
        new_headers = {
            "Authorization": f"Bearer {response_content['access_token']}",
            "Accept": "*/*",
            "Content-Type": "application/json",
        }
        self.session.headers.update(new_headers)

    def _make_request(self, request_method: str, **kwargs) -> Dict[str, Any]:
        """
        Makes an authenticated API request using the provided HTTP method.

        Automatically refreshes the access token if it has expired.

        :param request_method: The HTTP method to use (e.g., "GET", "POST" etc.).
        :param kwargs: Additional arguments to pass to the `requests.request` method.
        :return: The JSON response from the API.
        :raises HTTPError: If the API request fails.
        """
        # Refresh token if expired
        if datetime.now() > self.session_expiry:
            self.authenticate()

        # Make the API request
        response: requests.Response = self.session.request(
            method=request_method, **kwargs
        )
        response.raise_for_status()
        return response.json()
