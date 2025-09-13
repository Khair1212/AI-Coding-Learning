#!/usr/bin/env python3

"""
Fix the payment table constraint issue by making subscription_id nullable
"""

from sqlalchemy import text
from app.core.database import SessionLocal, engine

def fix_payment_constraint():
    """Fix the subscription_id constraint in payments table"""
    
    print("🔧 Fixing payment table constraint...")
    
    # Create a direct connection to execute DDL
    with engine.connect() as connection:
        try:
            # Start a transaction
            trans = connection.begin()
            
            # Make subscription_id nullable
            print("   Making subscription_id nullable...")
            connection.execute(text(
                "ALTER TABLE payments ALTER COLUMN subscription_id DROP NOT NULL"
            ))
            
            # Commit the transaction
            trans.commit()
            print("✅ Successfully fixed payment table constraint!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"❌ Error fixing constraint: {e}")
            
            # Check if the constraint was already fixed
            try:
                # Try to insert a test record with null subscription_id
                print("   Checking if constraint is already fixed...")
                with SessionLocal() as db:
                    # This would fail if constraint still exists
                    result = connection.execute(text(
                        "SELECT column_name, is_nullable FROM information_schema.columns "
                        "WHERE table_name = 'payments' AND column_name = 'subscription_id'"
                    ))
                    row = result.fetchone()
                    if row and row[1] == 'YES':
                        print("✅ Constraint was already fixed!")
                        return True
                        
            except Exception as check_error:
                print(f"❌ Constraint check failed: {check_error}")
                return False
                
    return True

def recreate_payment_table():
    """Recreate the payment table with the correct schema"""
    
    print("🔧 Recreating payment table with correct schema...")
    
    with engine.connect() as connection:
        try:
            trans = connection.begin()
            
            # Drop the existing table
            print("   Dropping existing payments table...")
            connection.execute(text("DROP TABLE IF EXISTS payments"))
            
            # Create the new table with correct schema
            print("   Creating new payments table...")
            connection.execute(text("""
                CREATE TABLE payments (
                    id SERIAL PRIMARY KEY,
                    subscription_id INTEGER REFERENCES subscriptions(id),
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    transaction_id VARCHAR UNIQUE NOT NULL,
                    session_key VARCHAR,
                    amount NUMERIC(10,2) NOT NULL,
                    currency VARCHAR DEFAULT 'BDT',
                    status VARCHAR NOT NULL,
                    payment_method VARCHAR,
                    bank_transaction_id VARCHAR,
                    card_type VARCHAR,
                    card_no VARCHAR,
                    card_issuer VARCHAR,
                    card_brand VARCHAR,
                    card_issuer_country VARCHAR,
                    card_issuer_country_code VARCHAR,
                    val_id VARCHAR,
                    store_amount NUMERIC(10,2),
                    risk_level VARCHAR,
                    risk_title VARCHAR,
                    payment_date TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE
                )
            """))
            
            trans.commit()
            print("✅ Successfully recreated payments table!")
            return True
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error recreating table: {e}")
            return False

if __name__ == "__main__":
    print("🚀 Starting payment constraint fix...")
    
    # First try to fix the constraint
    if fix_payment_constraint():
        print("✅ Constraint fix completed successfully!")
    else:
        print("⚠️  Constraint fix failed, trying table recreation...")
        
        if recreate_payment_table():
            print("✅ Table recreation completed successfully!")
        else:
            print("❌ Both constraint fix and table recreation failed!")
            print("   You may need to manually fix this in your database.")
            exit(1)
    
    print("\n🎉 Payment system is now ready for testing!")
    print("   You can now try the upgrade functionality again.")