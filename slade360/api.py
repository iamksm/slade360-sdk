import logging
import os
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Thread
from typing import Any, Callable, Deque, Dict, List, Tuple

from slade360.wrappers.post_visit import Remittance
from slade360.wrappers.start_visits import Visit
from slade360.wrappers.submit_visits import Claim, CreditNote, Invoice

DEFAULT_NUM_OF_WORKERS = os.cpu_count() or 4
LOGGER = logging.getLogger(__name__)


class Slade360(Visit, Claim, Invoice, CreditNote, Remittance):
    """
    A class that handles the API interactions with Slade360 (edi.slade360.co.ke)
    for claims, invoices, credit notes, and remittances.
    """

    def send_claims_in_bulk(
        self,
        bundled_claims: List[Dict[str, Any]],
        num_of_workers=DEFAULT_NUM_OF_WORKERS,
    ):
        """
        Sends claims, invoices, and related attachments in bulk.

        :param bundled_claims: A list of claims, where each claim includes
            associated invoices, credit notes, and attachments.
        :param num_of_workers: Number of concurrent workers for sending claims
            in parallel (default: set by DEFAULT_NUM_OF_WORKERS).

        Example structure of `bundled_claims`:
        - claim: Details about the claim, including payer, patient, visit, ICD codes, and scheme info.
        - invoices: A list of invoices linked to the claim.
        - credit_notes: A list of credit notes linked to the claim.
        - claim_attachments: Attachments related to the claim (e.g., prescription, preauth form).

        Usage:
        >>> self.send_claims_in_bulk(bundled_claims)
        """
        with ThreadPoolExecutor(max_workers=num_of_workers) as executor:
            executor.map(self.send_a_claim_and_its_children, bundled_claims)

    def _worker(self, queue: Queue) -> None:
        while True:
            task = queue.get()
            if task is None:
                break

            func, args = task
            try:
                func(*args)
            except Exception as e:
                LOGGER.error(f"Error processing task: {e}")
            finally:
                queue.task_done()

    def _process_tasks(
        self, tasks: Deque[Tuple[Callable, Tuple]], num_workers=DEFAULT_NUM_OF_WORKERS
    ) -> None:
        queue = Queue()
        threads: List[Thread] = []

        for _ in range(num_workers):
            t = Thread(target=self._worker, args=(queue,))
            t.start()
            threads.append(t)

        for task in tasks:
            queue.put(task)

        queue.join()

        for _ in range(num_workers):
            queue.put(None)

        for t in threads:
            t.join()

    def _process_claim_attachments(
        self, claim_attachments: List[Dict[str, Any]], tasks: Deque, claim_id: str
    ) -> None:
        for attachment in claim_attachments:
            tasks.append(
                (
                    self.submit_claim_attachment,
                    (
                        claim_id,
                        attachment["path_to_attachment"],
                        attachment["attachment_type"],
                        attachment.get("description"),
                    ),
                )
            )

    def _process_invoices(
        self, invoices: List[Dict[str, Any]], tasks: Deque, claim_id: str
    ) -> None:
        for invoice in invoices:
            inv_response = self.submit_invoices(claim=claim_id, **invoice)
            inv_id = inv_response["id"]
            for inv_attachment in invoice.get("invoice_attachments", []):
                tasks.append(
                    (
                        self.submit_invoice_attachment,
                        (
                            inv_id,
                            inv_attachment["path_to_attachment"],
                            inv_attachment.get("description", ""),
                        ),
                    )
                )

    def _process_credit_notes(
        self, credit_notes: List[Dict[str, Any]], tasks: Deque, claim_id: str
    ) -> None:
        for crn in credit_notes:
            crn_response = self.submit_credit_note(claim_id, **crn)
            crn_id = crn_response["id"]
            for crn_attachment in crn.get("crn_attachments", []):
                tasks.append(
                    (
                        self.submit_invoice_attachment,
                        (
                            crn_id,
                            crn_attachment["path_to_attachment"],
                            crn_attachment.get("description", ""),
                        ),
                    )
                )

    def send_a_claim_and_its_children(self, bundled_claim: Dict[str, Any]) -> None:
        """
        Sends an individual claim, along with its invoices, credit notes, and attachments.
        :param bundled_claim: A dictionary containing the claim,
            its invoices, credit notes, and related attachments.
        """
        invoices: List[Dict[str, Any]] = bundled_claim.pop("invoices", [])
        claim_attachments: List[Dict[str, Any]] = bundled_claim.pop(
            "claim_attachments", []
        )
        credit_notes: List[Dict[str, Any]] = bundled_claim.pop("credit_notes", [])

        claim_resp = self.create_claim(**bundled_claim)
        claim_id = claim_resp["id"]

        tasks = deque()

        self._process_claim_attachments(claim_attachments, tasks, claim_id)
        self._process_invoices(invoices, tasks, claim_id)
        self._process_credit_notes(credit_notes, tasks, claim_id)

        self._process_tasks(tasks)
