import traceback
from datetime import date

from database import get_session, init_db
from models import (
    Account,
    AccountBalance,
    AccountType,
    Category,
    Institution,
    Transaction,
    TransactionType,
)


def seed_initial_data(session):
    """Create some initial data to work with"""
    print("\n📦 Seeding initial data...")

    # Create institutions
    chase = Institution(name="Chase", is_active=True, display_order=1)
    vanguard = Institution(name="Vanguard", is_active=True, display_order=2)
    session.add_all([chase, vanguard])
    session.commit()

    # Create accounts
    checking = Account(
        institution_id=chase.institution_id,
        account_name="Chase Freedom",
        account_type=AccountType.BANKING,
        last_4_digits="1234",
        tracks_transactions=True,
        tracks_balances=False,
        display_order=1,
    )

    credit_card = Account(
        institution_id=chase.institution_id,
        account_name="Chase Sapphire",
        account_type=AccountType.CREDIT_CARD,
        last_4_digits="5678",
        tracks_transactions=True,
        tracks_balances=False,
        display_order=2,
    )

    roth_ira = Account(
        institution_id=vanguard.institution_id,
        account_name="Roth IRA",
        account_type=AccountType.INVESTMENT,
        last_4_digits="0000",
        tracks_transactions=False,
        tracks_balances=True,
        display_order=3,
    )

    session.add_all([checking, credit_card, roth_ira])
    session.commit()

    # Create categories
    categories_list = [
        "groceries",
        "dining",
        "transportation",
        "utilities",
        "entertainment",
        "shopping",
        "healthcare",
        "income",
        "bills",
    ]
    categories = [Category(name=cat) for cat in categories_list]
    session.add_all(categories)
    session.commit()

    print("✓ Seed data created!")
    return {
        "chase": chase,
        "vanguard": vanguard,
        "checking": checking,
        "credit_card": credit_card,
        "roth_ira": roth_ira,
        "groceries": categories[0],
        "dining": categories[1],
    }


def test_transactions(session, data):
    """Test transaction operations"""
    print("\n💰 Testing Transactions...")

    # Create a transaction
    transaction = Transaction(
        account_id=data["credit_card"].account_id,
        category_id=data["groceries"].category_id,
        transaction_date=date(2025, 10, 20),
        posted_date=date(2025, 10, 21),
        amount=4599,  # $45.99
        description="Whole Foods Market",
        transaction_type=TransactionType.PURCHASE,
        notes="Weekly groceries",
    )
    session.add(transaction)
    session.commit()
    print(f"✓ Created: {transaction}")

    # Query transactions for an account
    transactions = (
        session.query(Transaction)
        .filter(Transaction.account_id == data["credit_card"].account_id)
        .all()
    )
    print(
        f"✓ Found {len(transactions)} transaction(s) for {data['credit_card'].account_name}"
    )

    # Query with joins
    result = (
        session.query(Transaction, Account, Category)
        .join(Transaction.account)
        .join(Transaction.category)
        .first()
    )

    if result:
        trans, account, category = result
        print("✓ Transaction details:")
        print(f"  - Account: {account.account_name}")
        print(f"  - Category: {category.name}")
        print(f"  - Amount: ${trans.amount / 100:.2f}")
        print(f"  - Description: {trans.description}")


def test_balances(session, data):
    """Test balance tracking"""
    print("\n📊 Testing Account Balances...")

    # Create balance snapshots
    balances_data = [
        (date(2025, 10, 1), 125000),  # $1,250.00
        (date(2025, 10, 8), 126500),  # $1,265.00
        (date(2025, 10, 15), 128000),  # $1,280.00
    ]

    for balance_date, balance_amount in balances_data:
        balance = AccountBalance(
            account_id=data["roth_ira"].account_id,
            balance=balance_amount,
            balance_date=balance_date,
            notes="Weekly snapshot",
        )
        session.add(balance)

    session.commit()
    print(f"✓ Created {len(balances_data)} balance snapshots")

    # Query balance history
    balances = (
        session.query(AccountBalance)
        .filter(AccountBalance.account_id == data["roth_ira"].account_id)
        .order_by(AccountBalance.balance_date)
        .all()
    )

    print(f"✓ Balance history for {data['roth_ira'].account_name}:")
    for bal in balances:
        print(f"  - {bal.balance_date}: ${bal.balance / 100:,.2f}")


def test_relationships(session, data):
    """Test relationship navigation"""
    print("\n🔗 Testing Relationships...")

    # Navigate from institution to accounts
    chase = session.query(Institution).filter(Institution.name == "Chase").first()

    print(f"✓ {chase.name} has {len(chase.accounts)} account(s):")
    for acc in chase.accounts:
        print(f"  - {acc.account_name} ({acc.account_type.value})")

    # Navigate from account to transactions
    credit_card = (
        session.query(Account).filter(Account.account_name == "Chase Sapphire").first()
    )

    print(
        f"\n✓ {credit_card.account_name} has {len(credit_card.transactions)} transaction(s)"
    )
    for trans in credit_card.transactions:
        print(f"  - {trans.description}: ${trans.amount / 100:.2f}")


def test_queries(session, data):
    """Test various query patterns"""
    print("\n🔍 Testing Query Patterns...")

    # Get all transaction-tracking accounts
    trans_accounts = (
        session.query(Account).filter(Account.tracks_transactions is True).all()
    )
    print(f"✓ {len(trans_accounts)} account(s) track transactions")

    # Get all balance-tracking accounts
    balance_accounts = (
        session.query(Account).filter(Account.tracks_balances is True).all()
    )
    print(f"✓ {len(balance_accounts)} account(s) track balances")

    # Get accounts by type
    credit_cards = (
        session.query(Account)
        .filter(Account.account_type == AccountType.CREDIT_CARD)
        .all()
    )
    print(f"✓ {len(credit_cards)} credit card account(s)")

    # Get total spending by category
    from sqlalchemy import func

    category_totals = (
        session.query(Category.name, func.sum(Transaction.amount).label("total"))
        .join(Transaction.category)
        .group_by(Category.name)
        .all()
    )

    print("✓ Spending by category:")
    for cat_name, total in category_totals:
        print(f"  - {cat_name}: ${total / 100:.2f}")


def run_all_tests():
    """Run all test functions"""
    session = get_session()

    try:
        # Seed data
        data = seed_initial_data(session)

        # Run tests
        test_transactions(session, data)
        test_balances(session, data)
        test_relationships(session, data)
        test_queries(session, data)

        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    # Create fresh database
    print("=" * 50)
    print("Creating Database Schema")
    print("=" * 50)
    init_db()

    # Run tests
    print("\n" + "=" * 50)
    print("Running Tests")
    print("=" * 50)
    run_all_tests()
