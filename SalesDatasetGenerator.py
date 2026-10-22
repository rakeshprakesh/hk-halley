import argparse
import os
import random
import time
from datetime import datetime
import pandas as pd
from faker import Faker
import pyodbc
from sqlalchemy import create_engine, text

# --- Configuration & Credentials ---
DB_SERVER = ".\\SQLEXPRESS"  # Local SQLEXPRESS notation
DB_NAME = "ecommerce-sales"

# Connection configurations incorporating local authentication overrides
MASTER_CONN_STR = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={DB_SERVER};"
    f"DATABASE=master;"
    f"Trusted_Connection=yes;"
    f"Encrypt=yes;"
    f"TrustServerCertificate=yes;"
)

ENGINE_URL = (
    f"mssql+pyodbc://{DB_SERVER}/{DB_NAME}?"
    f"driver=ODBC+Driver+17+for+SQL+Server&"
    f"Trusted_Connection=yes&"
    f"Encrypt=yes&"
    f"TrustServerCertificate=yes"
)

# Initialize Faker with Indian locale
fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

# --- Whitelists ---
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
]

PRODUCT_CATEGORIES = [
    "Apparel", "Appliances", "Arts & Crafts", "Automotive", "Baby Care", "Bakery",
    "Bakeware", "Bath & Body", "Bedding", "Beverages", "Board Games", "Books",
    "Building Materials", "Camping Gear", "Canned Goods", "Car Electronics",
    "Cell Phones", "Cleaning Supplies", "Cookware", "Cosmetics", "Cycling", "Dairy",
    "Desk Organizers", "Dinnerware", "Dolls", "Educational Toys", "Electrical Supplies",
    "Ethernet Cables", "Exercise Equipment", "Fine Jewelry", "Fitness Trackers",
    "Flooring", "Footwear", "Frozen Foods", "Fruits", "Gardening Tools", "Gift Cards",
    "Grains", "Hand Tools", "Headphones", "Health Supplements", "Heating & Cooling",
    "Home Decor", "Home Security", "Hunting Gear", "Intimate Apparel", "Kitchen Gadgets",
    "Kitchen Storage", "Laptop Accessories", "Laptops", "Laundry Supplies", "Light Fixtures",
    "Live Plants", "Luggage", "Makeup", "Maternity", "Meat & Poultry", "Medical Supplies",
    "Motorcycle Gear", "Musical Instruments", "Office Electronics", "Office Furniture",
    "Outerwear", "Packaging Supplies", "Painting Supplies", "Paper Products", "Party Supplies",
    "Pet Food", "Pet Toys", "Photography Equipment", "Plumbing", "Power Tools", "Printers",
    "Relishes & Sauces", "Running Gear", "Salad Dressings", "School Supplies", "Seafood",
    "Smart Home Devices", "Smartwatches", "Snack Foods", "Souvenirs", "Space Heaters",
    "Specialty Teas", "Sporting Goods", "Storage Solutions", "Studio Monitors", "Sunglasses",
    "Tablets", "Televisions", "Travel Accessories", "Umbrellas", "Undergarments", "Vegetables",
    "Video Games", "Wall Art", "Wallets", "Watches", "Water Bottles", "Window Treatments"
]

CATEGORY_MODIFIERS = {
    "Electronics": ["Pro", "Max", "Wireless", "Ultra", "HD", "Smart"],
    "Food/Consumables": ["Organic", "Premium", "Fresh", "Classic", "Diet", "Natural"],
    "Apparel/Wearables": ["Slim Fit", "Cotton", "Designer", "Casual", "Sports", "Luxury"],
    "Default": ["Premium Edition", "Classic Model", "Standard pack", "Pro Series", "Eco Choice"]
}

def get_current_timestamps():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return now_str, now_str

def get_subproduct_name(cat_name):
    if cat_name in ["Apparel", "Footwear", "Outerwear", "Undergarments", "Maternity"]:
        modifier = random.choice(CATEGORY_MODIFIERS["Apparel/Wearables"])
    elif cat_name in ["Beverages", "Bakery", "Dairy", "Frozen Foods", "Fruits", "Vegetables", "Snack Foods"]:
        modifier = random.choice(CATEGORY_MODIFIERS["Food/Consumables"])
    elif cat_name in ["Laptops", "Televisions", "Cell Phones", "Smartwatches", "Headphones", "Printers"]:
        modifier = random.choice(CATEGORY_MODIFIERS["Electronics"])
    else:
        modifier = random.choice(CATEGORY_MODIFIERS["Default"])
    return f"{modifier} {cat_name}"

def ensure_database_and_tables():
    print("Checking SQL Server for target database...")
    conn = pyodbc.connect(MASTER_CONN_STR, autocommit=True)
    cursor = conn.cursor()
    cursor.execute(f"SELECT database_id FROM sys.databases WHERE name = '{DB_NAME}'")
    row = cursor.fetchone()
    if not row:
        print(f"Database '{DB_NAME}' not found. Creating database...")
        cursor.execute(f"CREATE DATABASE [{DB_NAME}]")
        print("Database created successfully.")
    else:
        print(f"Database '{DB_NAME}' ready.")
    cursor.close()
    conn.close()

def initialize_dimension_tables(engine):
    print("Initializing Unchanging Dimension Master Tables directly into SQL Server...")

    # 1. dim_store
    store_data = []
    for i in range(1, 201):
        entry, modified = get_current_timestamps()
        est_date = fake.date_between(start_date=datetime(1991, 1, 1), end_date=datetime(2022, 12, 31)).strftime("%d-%m-%Y")
        store_data.append({
            "ID": f"STR{i:03d}",
            "State": random.choice(INDIAN_STATES),
            "Estd Date": est_date,
            "Row Entry timestamp": entry,
            "Last Modified Timestamp": modified
        })
    pd.DataFrame(store_data).to_sql("dim_store", engine, if_exists="replace", index=False)

    # 2. dim_category
    category_data = []
    for i, cat_name in enumerate(PRODUCT_CATEGORIES[:100], start=1):
        entry, modified = get_current_timestamps()
        category_data.append({
            "Category ID": f"CATR{i:03d}",
            "Category Name": cat_name,
            "Row Entry timestamp": entry,
            "Last Modified Timestamp": modified
        })
    df_cat = pd.DataFrame(category_data)
    df_cat.to_sql("dim_category", engine, if_exists="replace", index=False)

    # 3. dim_product
    product_data = []
    cat_records = df_cat[["Category ID", "Category Name"]].to_dict(orient="records")
    for i in range(1, 3001):
        entry, modified = get_current_timestamps()
        chosen_cat = random.choice(cat_records)
        product_data.append({
            "Product ID": f"PRD{i:05d}",
            "Product Name": get_subproduct_name(chosen_cat["Category Name"]),
            "Category ID": chosen_cat["Category ID"],
            "Price": round(random.uniform(99.00, 85000.00), 2),
            "Row Entry timestamp": entry,
            "Last Modified Timestamp": modified
        })
    pd.DataFrame(product_data).to_sql("dim_product", engine, if_exists="replace", index=False)

    # 4. dim_user
    user_data = []
    for i in range(1, 1501):
        entry, modified = get_current_timestamps()
        first_name = fake.first_name()
        last_name = fake.last_name()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=75).strftime("%d-%m-%Y")
        signup_date = fake.date_between(start_date=datetime(2025, 2, 1), end_date=datetime(2026, 6, 1)).strftime("%d-%m-%Y")
        
        user_data.append({
            "User ID": f"USR{i:03d}",
            "FirstName": first_name,
            "LastName": last_name,
            "PhoneNumber": str(fake.phone_number().replace(" ", "")),
            "State": random.choice(INDIAN_STATES),
            "Date of Birth": dob,
            "Sign-up date": signup_date,
            "Email ID": f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}",
            "Credit card Number": fake.numerify("####-####-####-####"),
            "CVV Number": fake.numerify("###"),
            "Expiry Date": fake.credit_card_expire(date_format="%d-%m-%Y"),
            "Row Entry timestamp": entry,
            "Last Modified Timestamp": modified
        })
    pd.DataFrame(user_data).to_sql("dim_user", engine, if_exists="replace", index=False)
    print("Dimension tables created and loaded successfully into SQL Server!\n")

def append_sales_fact_data(engine, num_records=5000):
    print(f"Reading dimension keys from SQL Server to assemble {num_records} sales logs...")

    df_store = pd.read_sql_table("dim_store", engine)
    df_user = pd.read_sql_table("dim_user", engine)
    df_product = pd.read_sql_table("dim_product", engine)

    store_ids = df_store["ID"].tolist()
    user_ids = df_user["User ID"].tolist()
    product_price_map = dict(zip(df_product["Product ID"], df_product["Price"]))
    payment_types = ["CreditCard", "DebitCard", "InternetBanking", "Cash", "UPI"]

    start_idx = 1
    with engine.connect() as conn:
        table_exists = engine.dialect.has_table(conn, "fact_sales")
        if table_exists:
            res = conn.execute(text("SELECT COUNT(*) FROM fact_sales")).scalar()
            start_idx = res + 1
            print(f"Existing fact data found. Appending starting from ID index: TXN{start_idx:010d}")

    sales_batch = []
    for i in range(start_idx, start_idx + num_records):
        entry, modified = get_current_timestamps()
        
        # Calculate Base Price information dynamically for accurate mathematical tracking
        chosen_prod = random.choice(list(product_price_map.keys()))
        quantity = random.randint(1, 8)
        total_amount = round(product_price_map[chosen_prod] * quantity, 2)
        
        txn_date = fake.date_between(start_date=datetime(2025, 1, 1), end_date=datetime(2025, 12, 31)).strftime("%d-%m-%Y")

        # Core Relational Attributes
        u_id = random.choice(user_ids)
        p_type = random.choice(payment_types)
        s_id = random.choice(store_ids)
        p_id = chosen_prod

        # Target Nullable Logic Check: 10% probability of dropping single column fields
        # Guards against all four values settling to None simultaneously
        null_choices = ["User ID", "Payment Type", "Store ID", "Product ID"]
        random.shuffle(null_choices)
        
        # We allow up to 3 columns to drop randomly to guarantee at least 1 remains non-NULL
        num_nulls_to_apply = random.choices([0, 1, 2, 3], weights=[70, 15, 10, 5], k=1)[0]
        cols_to_nullify = null_choices[:num_nulls_to_apply]

        if "User ID" in cols_to_nullify:
            u_id = None
        if "Payment Type" in cols_to_nullify:
            p_type = None
        if "Store ID" in cols_to_nullify:
            s_id = None
        if "Product ID" in cols_to_nullify:
            p_id = None

        sales_batch.append({
            "Transaction ID": f"TXN{i:010d}",
            "Transaction Date": txn_date,
            "Product ID": p_id,
            "Store ID": s_id,
            "User ID": u_id,
            "Quantity": quantity,
            "Total Amount": total_amount,
            "Payment Type": p_type,
            "Row Entry timestamp": entry,
            "Last Modified Timestamp": modified
        })

    df_new_sales = pd.DataFrame(sales_batch)
    df_new_sales.to_sql("fact_sales", engine, if_exists="append", index=False)
    print(f"Successfully processed and appended {num_records} transaction records to SQL Server table 'fact_sales'.\n")

def modify_single_user(engine, user_id):
    with engine.connect() as conn:
        if not engine.dialect.has_table(conn, "dim_user"):
            print("Error: dim_user table does not exist in the database.")
            return

    df_user = pd.read_sql_table("dim_user", engine)

    if user_id not in df_user["User ID"].values:
        print(f"Error: User ID '{user_id}' not found in database table 'dim_user'.")
        return

    print(f"Modifying target attributes for User '{user_id}' inside MS SQL Server...")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_phone = fake.phone_number().replace(" ", "")
    new_dob = fake.date_of_birth(minimum_age=18, maximum_age=75).strftime("%d-%m-%Y")
    new_cc = fake.numerify("####-####-####-####")
    new_cvv = fake.numerify("###")
    new_expiry = fake.credit_card_expire(date_format="%d-%m-%Y")

    idx = df_user[df_user["User ID"] == user_id].index[0]
    df_user.at[idx, "PhoneNumber"] = str(new_phone)
    df_user.at[idx, "Date of Birth"] = str(new_dob)
    df_user.at[idx, "Credit card Number"] = str(new_cc)
    df_user.at[idx, "CVV Number"] = str(new_cvv)
    df_user.at[idx, "Expiry Date"] = str(new_expiry)
    df_user.at[idx, "Last Modified Timestamp"] = now_str

    df_user.to_sql("dim_user", engine, if_exists="replace", index=False)
    print(f"Success! User '{user_id}' updated in SQL Server database. Last Modified Timestamp bumped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Relational SQL Server E-commerce pipeline generator.")
    parser.add_argument(
        "--modifyuser", 
        type=str, 
        metavar="USER_ID",
        help="Specify a valid User ID string (e.g. USR001) to update records and trigger SCD delta logic."
    )
    args = parser.parse_args()

    ensure_database_and_tables()
    engine = create_engine(ENGINE_URL)

    if args.modifyuser:
        dynamic_seed = int(time.time())
        fake.seed_instance(dynamic_seed)
        random.seed(dynamic_seed)
        
        modify_single_user(engine, args.modifyuser)
    else:
        with engine.connect() as conn:
            dimensions_deployed = engine.dialect.has_table(conn, "dim_user")
            
        if not dimensions_deployed:
            initialize_dimension_tables(engine)
            
        append_sales_fact_data(engine, num_records=500000)