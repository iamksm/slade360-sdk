from typing import Any, Dict, List, Literal, Optional, Union

from slade360.wrappers import Authentication


class Visit(Authentication):
    """
    The Visit class handles various visit-related functionalities for
    interacting with member insurance details, starting a visit, and managing
    authorizations via the HealthCloud API.
    """

    def get_member_eligibility(
        self,
        member_number: str,
        payer_slade_code: int,
    ) -> Dict[str, Any]:
        """
        Retrieve medical cover details for a specific member under a given insurer/payer.

        :param member_number: Member number printed on the insurance card.
        :param payer_slade_code: The insurer's identifier on Slade.

        :return: A dictionary containing member eligibility details.

        https://healthcloud.sh/api-reference#tag/MEMBER_ELIGIBILITY
        """
        eligibility_params = {
            "member_number": member_number,
            "payer_slade_code": payer_slade_code,
        }
        eligibility_resource = "/v1/beneficiaries/member_eligibility"

        return self._make_request(
            request_method="GET", url=eligibility_resource, params=eligibility_params
        )

    def request_otp(self, contact_id: int) -> None:
        """
        Request an OTP to be sent to the member's registered phone number.

        :param contact_id: The ID of one of the member's verified contact
            objects returned by `get_member_eligibility`.

        https://healthcloud.sh/api-reference#tag/MEMBER_AUTHENTICATION
        """
        resource = f"/v1/beneficiaries/beneficiary_contacts/{contact_id}/send_otp/"
        otp_url = f"{self.base_edi_url}{resource}"

        self._make_request(request_method="POST", url=otp_url)

    def start_visit_via_otp(
        self,
        beneficiary_id: int,
        factors: List[str],
        benefit_type: str,
        benefit_code: str,
        policy_number: str,
        policy_effective_date: str,
        otp: int,
        beneficiary_contact: str,
        scheme_name: Optional[str] = "",
        scheme_code: Optional[str] = "",
    ) -> Dict[str, Any]:
        """
        Create a medical visit for an insured member authenticated via OTP.

        :param beneficiary_id: The member's ID from the `get_member_eligibility` response.
        :param factors: Methods used to authenticate the member (e.g., ["OTP"]).
        :param benefit_type: The benefit type from the `get_member_eligibility` response.
        :param benefit_code: The benefit code from the `get_member_eligibility` response.
        :param policy_number: The policy number from the `get_member_eligibility` response.
        :param policy_effective_date: The effective date of the policy from the `get_member_eligibility` response.
        :param otp: OTP sent to the member's registered phone.
        :param beneficiary_contact: The phone number used when requesting the OTP.
        :param scheme_name: Optional name of the member's scheme.
        :param scheme_code: Optional code of the member's scheme.

        :return: A dictionary containing visit start details.

        https://healthcloud.sh/api-reference#tag/START_VISIT/operation/start_visit_via_otp
        """
        url = f"{self.base_is_url}/v1/authorizations/start_visit/"
        payload = {
            "beneficiary_id": beneficiary_id,
            "factors": factors,
            "benefit_type": benefit_type,
            "benefit_code": benefit_code,
            "policy_number": policy_number,
            "policy_effective_date": policy_effective_date,
            "otp": otp,
            "beneficiary_contact": beneficiary_contact,
            "scheme_name": scheme_name,
            "scheme_code": scheme_code,
        }
        return self._make_request(request_method="POST", url=url, json=payload)

    def validate_authorization_token(
        self,
        first_name: str,
        last_name: str,
        other_names: str,
        member_number: str,
        auth_token: str,
        visit_type: Optional[Literal["OUTPATIENT", "INPATIENT", ""]] = "",
        scheme_code: Optional[str] = "",
        scheme_name: Optional[str] = "",
        payer_code: Optional[str] = "",
    ) -> Dict[str, Any]:
        """
        Validate an authorization token for a member's visit.

        :param first_name: The member's first name.
        :param last_name: The member's last name.
        :param other_names: The member's other names.
        :param member_number: The member's number printed on the insurance card.
        :param auth_token: The token retrieved after a successful visit start.
        :param visit_type: The visit type, either "OUTPATIENT" or "INPATIENT".
        :param scheme_code: The member's scheme code (optional).
        :param scheme_name: The member's scheme name (optional).
        :param payer_code: The member's payer code (optional).

        :return: A dictionary containing the validation result.

        https://healthcloud.sh/api-reference#tag/START_VISIT/operation/validate_authorization_token
        """
        url = f"{self.base_is_url}/v1/authorizations/validate_authorization_token/"
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "other_names": other_names,
            "member_number": member_number,
            "auth_token": auth_token,
            "visit_type": visit_type,
            "scheme_code": scheme_code,
            "scheme_name": scheme_name,
            "payer_code": payer_code,
        }
        return self._make_request(request_method="POST", url=url, json=payload)

    def create_balance_reservation(
        self, authorization: str, invoice_number: str, amount: Union[int, float]
    ) -> Dict[str, Any]:
        """
        Create a balance reservation from a member's benefit balance.

        :param authorization: The `edi_auth_guid` returned from the start visit response.
        :param invoice_number: The invoice number for the anticipated bill.
        :param amount: The amount to be reserved from the member's benefit balance.

        :return: A dictionary containing balance reservation details.

        https://healthcloud.sh/api-reference#tag/BALANCE_RESERVATION/operation/create_balance_reservation
        """
        url = (
            f"{self.base_edi_url}/v1/balances/reservations/reserve_from_authorization/"
        )
        payload = {
            "authorization": authorization,
            "invoice_number": invoice_number,
            "amount": amount,
        }

        return self._make_request(request_method="POST", url=url, json=payload)
