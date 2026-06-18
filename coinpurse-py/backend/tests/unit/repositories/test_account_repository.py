"""
Unit tests for AccountRepository.
"""

from sqlalchemy.orm import Session

from models import Account, AccountType, Institution, TaxTreatmentType
from repositories.account_repository import AccountRepository


def create_account(
    db_session: Session, institution_id: int, account_name: str = "Checking"
) -> Account:
    account = Account(
        institution_id=institution_id,
        account_name=account_name,
        account_type=AccountType.BANKING,
        tax_treatment=TaxTreatmentType.TAXABLE,
        last_4_digits="1234",
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


def test_name_exists_is_scoped_to_institution(db_session: Session):
    first = Institution(name="First Bank")
    second = Institution(name="Second Bank")
    db_session.add_all([first, second])
    db_session.commit()

    create_account(db_session, first.institution_id, "Checking")

    repo = AccountRepository(db_session)

    assert repo.name_exists("Checking", first.institution_id) is True
    assert repo.name_exists("Checking", second.institution_id) is False


def test_name_exists_honors_exclude_id(db_session: Session):
    institution = Institution(name="Test Bank")
    db_session.add(institution)
    db_session.commit()
    account = create_account(db_session, institution.institution_id, "Checking")

    repo = AccountRepository(db_session)

    assert (
        repo.name_exists(
            "Checking",
            institution.institution_id,
            exclude_id=account.account_id,
        )
        is False
    )
