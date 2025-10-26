from database import get_session, init_db
from models import Institution, Account

def test_basic_operations():
    """Test creating and querying data"""
    
    # Get a database session
    session = get_session()
    
    try:
        # 1. CREATE: Add an institution
        print("\n1. Creating institution...")
        chase = Institution(
            name="Chase",
            display_order=1,
            is_active=True
        )
        session.add(chase)
        session.commit()
        print(f"✓ Created: {chase}")
        
        # 2. CREATE: Add an account
        print("\n2. Creating account...")
        checking = Account(
            institution_id=chase.institution_id,
            account_name="Chase Freedom",
            account_type="checking",
            display_order=1,
            is_active=True
        )
        session.add(checking)
        session.commit()
        print(f"✓ Created: {checking}")
        
        # 3. READ: Query all institutions
        print("\n3. Querying all institutions...")
        institutions = session.query(Institution).all()
        for inst in institutions:
            print(f"  - {inst.name}")
        
        # 4. READ: Query with relationship (accounts for Chase)
        print("\n4. Querying accounts for Chase...")
        chase_accounts = session.query(Account)\
            .filter(Account.institution_id == chase.institution_id)\
            .all()
        for acc in chase_accounts:
            print(f"  - {acc.account_name} (type: {acc.account_type})")
        
        # 5. READ: Using relationship navigation
        print("\n5. Using relationship navigation...")
        chase_reloaded = session.query(Institution)\
            .filter(Institution.name == "Chase")\
            .first()
        print(f"Institution: {chase_reloaded.name}")
        print(f"Accounts:")
        for acc in chase_reloaded.accounts:
            print(f"  - {acc.account_name}")
        
        # 6. UPDATE: Change account name
        print("\n6. Updating account name...")
        checking.account_name = "Chase Freedom Unlimited"
        session.commit()
        print(f"✓ Updated: {checking}")
        
        # 7. DELETE: Remove the account
        print("\n7. Deleting account...")
        session.delete(checking)
        session.commit()
        print("✓ Account deleted")
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    # Create tables first
    init_db()
    
    # Run tests
    print("\n" + "="*50)
    print("Testing Database Operations")
    print("="*50)
    test_basic_operations()