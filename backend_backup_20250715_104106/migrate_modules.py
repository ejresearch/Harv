# Create a new file: backend/migrate_modules.py
from sqlalchemy import create_engine, text
from app.database import DATABASE_URL

def migrate_modules():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Add new columns to modules table
        try:
            connection.execute(text("ALTER TABLE modules ADD COLUMN module_prompt TEXT"))
            print("Added module_prompt column")
        except Exception as e:
            print(f"module_prompt column might already exist: {e}")
        
        try:
            connection.execute(text("ALTER TABLE modules ADD COLUMN system_corpus TEXT"))
            print("Added system_corpus column")
        except Exception as e:
            print(f"system_corpus column might already exist: {e}")
        
        try:
            connection.execute(text("ALTER TABLE modules ADD COLUMN module_corpus TEXT"))
            print("Added module_corpus column")
        except Exception as e:
            print(f"module_corpus column might already exist: {e}")
        
        try:
            connection.execute(text("ALTER TABLE modules ADD COLUMN dynamic_corpus TEXT"))
            print("Added dynamic_corpus column")
        except Exception as e:
            print(f"dynamic_corpus column might already exist: {e}")
        
        try:
            connection.execute(text("ALTER TABLE modules ADD COLUMN api_endpoint VARCHAR DEFAULT 'https://api.openai.com/v1/chat/completions'"))
            print("Added api_endpoint column")
        except Exception as e:
            print(f"api_endpoint column might already exist: {e}")
        
        connection.commit()
        print("Migration completed!")

if __name__ == "__main__":
    migrate_modules()
