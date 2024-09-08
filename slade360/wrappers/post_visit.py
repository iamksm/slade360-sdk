from typing import Any, Dict

from slade360.wrappers import Authentication


class Remittance(Authentication):
    """
    Remittances are a collection of individual payments for a set of claims.
    A single claim can be associated with multiple remittances and a single remittance
    can be associated with multiple claims.

    https://healthcloud.sh/api-reference#tag/REMITTANCE
    """

    def list_remittances(self) -> Dict[str, Any]:
        """
        Retrieve all remittances for a specific medical provider.

        https://healthcloud.sh/api-reference#tag/REMITTANCE/operation/list_remittances
        """
        url = f"{self.base_edi_url}/v1/remittances"
        return self._make_request(request_method="GET", url=url)

    def get_remittance(self, claim_remittance_id: int) -> Dict[str, Any]:
        """
        Retrieve a specific claim remittance for a specific medical provider.

        :parmam claim_remittance_id (int): claim id referencing the ClaimRemittance
        """
        url = f"{self.base_edi_url}/v1/remittances/claim_remittance"
        payload = {"claim_id": claim_remittance_id}

        return self._make_request(request_method="GET", url=url, json=payload)
