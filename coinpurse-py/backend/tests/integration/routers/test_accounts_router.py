"""
Integration tests for account endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models import Account, AccountType, Institution, TaxTreatmentType


def account_payload(institution_id: int, account_name: str = "Checking") -> dict:
    return {
        "account_name": account_name,
        "institution_id": institution_id,
        "template_id": None,
        "account_type": AccountType.BANKING.value,
        "tax_treatment": TaxTreatmentType.TAXABLE.value,
        "last_4_digits": "1234",
        "tracks_transactions": True,
        "tracks_balances": True,
        "active": True,
        "display_order": 0,
    }


@pytest.fixture
def account_institutions(db_session: Session) -> list[Institution]:
    institutions = [Institution(name="First Bank"), Institution(name="Second Bank")]
    db_session.add_all(institutions)
    db_session.commit()
    for institution in institutions:
        db_session.refresh(institution)
    return institutions


def create_account(
    db_session: Session, institution_id: int, account_name: str = "Checking"
) -> Account:
    account = Account(
        institution_id=institution_id,
        account_name=account_name,
        account_type=AccountType.BANKING,
        tax_treatment=TaxTreatmentType.TAXABLE,
        last_4_digits="1234",
        tracks_transactions=True,
        tracks_balances=True,
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


class TestAccountsRouter:
    def test_create_allows_same_name_for_different_institutions(
        self, client: TestClient, account_institutions: list[Institution]
    ):
        first, second = account_institutions

        first_response = client.post(
            "/api/accounts/", json=account_payload(first.institution_id)
        )
        second_response = client.post(
            "/api/accounts/", json=account_payload(second.institution_id)
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 201
        assert first_response.json()["account_name"] == second_response.json()[
            "account_name"
        ]
        assert first_response.json()["institution_id"] != second_response.json()[
            "institution_id"
        ]

    def test_create_rejects_same_name_for_same_institution(
        self, client: TestClient, account_institutions: list[Institution]
    ):
        institution = account_institutions[0]

        first_response = client.post(
            "/api/accounts/", json=account_payload(institution.institution_id)
        )
        duplicate_response = client.post(
            "/api/accounts/", json=account_payload(institution.institution_id)
        )

        assert first_response.status_code == 201
        assert duplicate_response.status_code == 400
        assert "for this institution" in duplicate_response.json()["detail"]

    def test_update_allows_name_matching_other_institution(
        self,
        client: TestClient,
        db_session: Session,
        account_institutions: list[Institution],
    ):
        first, second = account_institutions
        create_account(db_session, first.institution_id, "Checking")
        account_to_update = create_account(db_session, second.institution_id, "Savings")

        response = client.patch(
            f"/api/accounts/{account_to_update.account_id}",
            json={"account_name": "Checking"},
        )

        assert response.status_code == 200
        assert response.json()["account_name"] == "Checking"
        assert response.json()["institution_id"] == second.institution_id

    def test_update_rejects_institution_change_that_creates_name_conflict(
        self,
        client: TestClient,
        db_session: Session,
        account_institutions: list[Institution],
    ):
        first, second = account_institutions
        create_account(db_session, first.institution_id, "Checking")
        account_to_update = create_account(
            db_session, second.institution_id, "Checking"
        )

        response = client.patch(
            f"/api/accounts/{account_to_update.account_id}",
            json={"institution_id": first.institution_id},
        )

        assert response.status_code == 400
        assert "for this institution" in response.json()["detail"]
