# Slade360 Python SDK

A Python SDK for interacting with the [Slade360 HealthCloud API](https://healthcloud.sh/api-reference). This SDK provides easy-to-use functions to handle common healthcare workflows such as claim creation, invoice submission, credit note management, and attachment handling.

## Features

- **Claims**: Create and manage medical claims, including submitting attachments.
- **Invoices**: Submit invoices related to claims and attach additional documents.
- **Credit Notes**: Submit credit notes for correcting billing overcharges.
- **Attachments**: Upload supporting documents for claims and invoices.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Authentication](#authentication)
  - [Claims](#claims)
  - [Invoices](#invoices)
  - [Credit Notes](#credit-notes)
- [Contributing](#contributing)
- [License](#license)

## Installation

Install the SDK using `pip`:

```bash
pip install slade360
```

## Usage

### Authentication

All requests require authentication with an access token. The `Authentication` class is the base for all resources and handles API authentication for requests.

Here’s how to initialize the SDK:

```python
from slade360.wrappers import Claim, Invoice, CreditNote

# Initialize with your access token
auth_token = "your-access-token"

# Example: Initialize Claims
claim_instance = Claim(auth_token=auth_token)

# Example: Initialize Invoices
invoice_instance = Invoice(auth_token=auth_token)

# Example: Initialize Credit Notes
credit_note_instance = CreditNote(auth_token=auth_token)
```

### Claims

You can create claims and submit attachments related to them.

#### Create a Claim

```python
claim_data = {
    "payer_code": 1234,
    "payer_name": "Health Insurance Co",
    "patient_name": "John Doe",
    "member_number": "ABC123",
    "scheme_name": "Gold Plan",
    "visit_number": "VN001",
    "visit_start": "2024-09-08T08:00:00Z",
    "visit_end": "2024-09-08T10:00:00Z",
    "icd10_codes": [{"code": "A01", "description": "Typhoid Fever"}],
    "location_code": "001",
    "location_name": "Main Hospital",
}

response = claim_instance.create_claim(**claim_data)
print(response)
```

#### Submit a Claim Attachment

```python
attachment_data = {
    "claim": "claim_id",
    "path_to_attachment": "/path/to/file.pdf",
    "attachment_type": "CLAIM_FORM",
    "description": "Claim form for patient John Doe",
}

response = claim_instance.submit_claim_attachment(**attachment_data)
print(response)
```

### Invoices

You can submit invoices for claims and attach additional documents.

#### Submit an Invoice

```python
invoice_data = {
    "claim": "claim_id",
    "invoice_number": "INV001",
    "invoice_date": "2024-09-08T12:00:00Z",
    "lines": [{"service_code": "SVC001", "description": "Consultation", "amount": 100}],
}

response = invoice_instance.submit_invoices(**invoice_data)
print(response)
```

#### Submit an Invoice Attachment

```python
invoice_attachment_data = {
    "invoice": "invoice_id",
    "path_to_attachment": "/path/to/invoice.pdf",
    "description": "Invoice for consultation",
}

response = invoice_instance.submit_invoice_attachment(**invoice_attachment_data)
print(response)
```

### Credit Notes

Submit credit notes for claim corrections, such as overcharges.

#### Submit a Credit Note

```python
credit_note_data = {
    "claim": "claim_id",
    "invoice_number": "CN001",
    "invoice_date": "2024-09-08T15:00:00Z",
    "lines": [{"service_code": "SVC001", "description": "Overcharge refund", "amount": -50}],
}

response = credit_note_instance.submit_credit_note(**credit_note_data)
print(response)
```

## Contributing

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Notes

1. **Installation**: The installation section includes the command to install your package using `pip`.
2. **Usage**: Covers authentication and step-by-step examples of using each class (`Claim`, `Invoice`, and `CreditNote`) with explanations.
3. **Contributing**: A brief guide on how others can contribute to the project.
4. **License**: The license is mentioned (based on the setup.py file).
