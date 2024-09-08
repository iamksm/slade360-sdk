import os
from typing import Any, Dict, List, Literal, Optional, Union

from slade360.wrappers import Authentication


class Claim(Authentication):
    """
    Handles medical claim creation and attachment submission processes.

    Provides functionality to create claims, upload claim attachments, and interact with
    claim-related resources.

    https://healthcloud.sh/api-reference#tag/CLAIMS
    """

    def create_claim(
        self,
        payer_code: int,
        payer_name: str,
        patient_name: str,
        member_number: str,
        scheme_name: str,
        visit_number: str,
        visit_start: str,
        visit_end: str,
        icd10_codes: List[Dict[str, str]],
        location_code: Optional[str] = None,
        location_name: Optional[str] = None,
        scheme_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a medical claim for a member.

        :param payer_code (int): Unique payer identifier on Slade360.
        :param payer_name (str): Name of the payer.
        :param patient_name (str): The patient's name as recorded by the provider.
        :param member_number (str): The member's number or auth_token retrieved during authorization.
        :param scheme_name (str): The member's insurance scheme name.
        :param visit_number (str): A unique identifier for the medical visit.
        :param visit_start (str): ISO 8601 timestamp of visit start time.
        :param visit_end (str): ISO 8601 timestamp of visit end time.
        :param icd10_codes (List[Dict[str, str]]): List of diagnoses in ICD-10 format.
        :param location_code (Optional[str]): Provider location code. Defaults to None.
        :param location_name (Optional[str]): Provider location name. Defaults to None.
        :param scheme_code (Optional[str]): Member scheme code. Defaults to None.
        :return (Dict[str, Any]): JSON response containing the created claim details.
        """
        url = f"{self.base_is_url}/v1/claims/"
        payload = {
            "payer_code": payer_code,
            "payer_name": payer_name,
            "patient_name": patient_name,
            "member_number": member_number,
            "scheme_name": scheme_name,
            "visit_number": visit_number,
            "visit_start": visit_start,
            "visit_end": visit_end,
            "icd10_codes": icd10_codes,
            "location_code": location_code,
            "location_name": location_name,
            "scheme_code": scheme_code,
        }

        return self._make_request(request_method="POST", url=url, json=payload)

    def submit_claim_attachment(
        self,
        claim: str,
        path_to_attachment: str,
        attachment_type: Literal[
            "CLAIM_FORM",
            "PREAUTH_FORM",
            "PRESCRIPTION",
            "LAB_ORDER",
            "IMAGING_ORDER",
            "OTHER",
        ],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submit an attachment for a specific claim.

        :param claim (str): The claim's unique identifier, obtained from `create_claim`.
        :param path_to_attachment (str): Path to the file to be uploaded.
        :param attachment_type (Literal): Type of attachment to be uploaded.
        :param description (Optional[str]): Optional description for the attachment.
        :return (Dict[str, Any]): JSON response containing attachment details.
        """
        resource_url = "/v1/claim_attachments/upload_attachment/"
        url = f"{self.base_is_url}{resource_url}"

        if not os.path.exists(path_to_attachment):
            raise FileNotFoundError(
                f"Attachment file '{path_to_attachment}' not found."
            )

        with open(path_to_attachment, "rb") as attachment:
            files = {"attachment": attachment}
            payload = {
                "claim": claim,
                "attachment_type": attachment_type,
                "description": description,
            }

            return self._make_request(
                request_method="POST", url=url, files=files, json=payload
            )


class Invoice(Authentication):
    """
    Handles invoice creation, submission, and attachments for claims.

    https://healthcloud.sh/api-reference#tag/INVOICES
    """

    def submit_invoices(
        self,
        claim: str,
        invoice_number: str,
        invoice_date: str,
        lines: List[Dict[str, Any]],
        copays: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Submit an invoice for a medical claim.

        :param claim (str): Unique identifier for a previously created claim.
        :param invoice_number (str): Provider's invoice number.
        :param invoice_date (str): ISO 8601 date of invoice creation.
        :param lines (List[Dict[str, Any]]): Line items representing specific billable services/products.
        :param copays (Optional[List[Dict[str, Any]]]): Optional list of copay details. Defaults to None.
        :return (Dict[str, Any]): JSON response containing the submitted invoice details.
        """
        url = f"{self.base_is_url}/v1/invoices"
        payload = {
            "claim": claim,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "lines": lines,
            "copays": copays or [],  # Use an empty list if copays is None
        }

        return self._make_request(request_method="POST", url=url, json=payload)

    def submit_invoice_attachment(
        self, invoice: str, path_to_attachment: str, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Submit an attachment for a specific invoice.

        :param invoice (str): Unique identifier for the invoice.
        :param path_to_attachment (str): Path to the file to be uploaded.
        :param description (Optional[str]): Optional description for the attachment.
        :return (Dict[str, Any]): JSON response containing attachment details.
        """
        resource_url = "/v1/invoice_attachments/upload_attachment/"
        url = f"{self.base_is_url}{resource_url}"

        if not os.path.exists(path_to_attachment):
            raise FileNotFoundError(
                f"Attachment file '{path_to_attachment}' not found."
            )

        with open(path_to_attachment, "rb") as attachment:
            files = {"attachment": attachment}
            payload = {
                "invoice": invoice,
                "description": description,
            }

            return self._make_request(
                request_method="POST", url=url, files=files, json=payload
            )


class CreditNote(Authentication):
    """
    Handles submission of credit notes to correct overcharges for claims.

    https://healthcloud.sh/api-reference#tag/CREDIT_NOTES
    """

    def submit_credit_note(
        self,
        claim: str,
        invoice_number: str,
        invoice_date: str,
        lines: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Submit a credit note to correct an overcharge on a claim.

        :param claim (str): Unique identifier for a previously created claim.
        :param invoice_number (str): Provider's credit note reference number.
        :param invoice_date (str): ISO 8601 date of the credit note.
        :param lines (List[Dict[str, Any]]): Specific billable line items for correction.
        :return (Dict[str, Any]): JSON response containing the submitted credit note details.
        """
        url = f"{self.base_is_url}/v1/invoices"
        payload = {
            "invoice_type": "CREDIT_NOTE",
            "claim": claim,
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "lines": lines,
        }

        return self._make_request(request_method="POST", url=url, json=payload)
