import pandas as pd
import streamlit as st
import math
import re
from rapidfuzz import process, fuzz
import os
import sys

# For Excel reading (now directly integrated)
import openpyxl

# --- Streamlit Page Configuration and Custom CSS (MUST BE FIRST) ---
st.set_page_config(layout="wide", page_title="Autobake Machine Match")

st.markdown(
    """
    <style>
    /* Overall Body Background and crucial overflow fix */
    html, body {
        background-color: #F2DBBB; /* Overall body background except specified areas */
        color: #333333; /* Default text color */
        overflow-x: hidden; /* PREVENTS HORIZONTAL SHIFTING ON MOBILE/SMALL SCREENS */
    }

    /* Streamlit Main App Container - Removed flexbox for stability */
    /*
    [data-testid="stAppViewContainer"] {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
    }
    */

    /* Streamlit Main Content Area - Reverted to simpler background */
    .stApp {
        background-color: #F2DBBB; /* Overall body background for Streamlit app */
        /* Removed flex-grow: 1; for stability */
    }

    /* Custom styles for the main title 'Autobake Machine Match' block */
    .header-section {
        background-color: #FFE8C2; /* Background for the heading part */
        padding: 20px 0; /* Add some padding around the title background */
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Soft shadow for header */

        /* REVERTED: Full width hack that's more stable for Streamlit */
        margin-top: -20px; /* Adjust to remove default Streamlit top margin */
        margin-left: -3rem; /* Compensate for Streamlit's default left/right padding */
        margin-right: -3rem; /* Compensate for Streamlit's default left/right padding */
        width: calc(100% + 6rem); /* Make it span full width including Streamlit's padding */
        box-sizing: border-box; /* Crucial for padding/borders not to add to width */
    }
    .header-section h1 {
        display: inline;
        font-weight: 900; /* Make 'Autobake' bolder */
        margin: 0; /* Remove default h1 margins */
        padding: 0; /* Remove default h1 padding */
    }
    .header-section h1 span.auto {
        color: #66382B; /* 'Auto' in Autobake */
    }
    .header-section h1 span.bake {
        color: #545B37; /* 'bake' in Autobake */
    }
    .header-section h2 {
        display: inline;
        color: #8D5A46; /* Lighter shade for 'Machine Match' */
        font-weight: bold; /* Make 'Machine Match' bold */
        margin: 0; /* Remove default h2 margins */
        padding: 0; /* Remove default h2 padding */
    }

    /* Headings for stages, criteria, etc. */
    h2:not(.header-section h2), h3, h4, h5, h6 { /* Exclude the main H2 in the header */
        color: #66382B; /* Color for other heading text like Stage, Machines meeting criteria, etc */
        font-weight: bold; /* Make these headings bold */
        margin-top: 1.5rem; /* Add some space above headings */
        margin-bottom: 0.5rem; /* Add some space below headings */
    }

    /* Buttons Styling */
    .stButton > button {
        background-color: #4A5022; /* Background for buttons */
        color: #FEFEFE; /* Text for buttons (white) */
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.2s ease;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2); /* Soft shadow for buttons */
    }
    .stButton > button:hover {
        background-color: #3b3f1b; /* Slightly darker green on hover */
        box-shadow: 1px 1px 3px rgba(0,0,0,0.2); /* Smaller shadow on hover */
    }

    /* Dropdown/Selectbox Background */
    /* Target the main container of the selectbox */
    .stSelectbox > div:first-child {
        background-color: #FFD183; /* Dropdown background */
        border: 1px solid #FFD183; /* Match border to background */
        border-radius: 5px;
        box-shadow: inset 1px 1px 3px rgba(0,0,0,0.1); /* Subtle inner shadow for depth */
    }
    /* Target the input/selected value area */
    .stSelectbox > div > div > div > div > div:first-child {
        padding: 8px 10px; /* Adjust padding to ensure text fits */
        height: auto; /* Allow height to adjust */
        line-height: 1.5; /* Ensure text fits on a single line */
        white-space: nowrap; /* Prevent wrapping for selected item */
        background-color: #FFD183; /* Ensure this specific part also has the background */
        color: #333333; /* Default text color for dropdown */
    }
    /* For the list of options in the dropdown */
    div[data-baseweb="popover"] > div > div {
        background-color: #FFD183 !important; /* Background for dropdown options */
        color: #333333 !important;
        border: 1px solid #FFD183; /* Match border for dropdown options */
        border-radius: 5px; /* Rounded corners for the dropdown list */
        box-shadow: 0 4px 8px rgba(0,0,0,0.15); /* Soft shadow for the dropdown list */
    }
    div[data-baseweb="popover"] > div > div div[role="option"]:hover {
        background-color: #f2c77d !important; /* Slightly darker on hover */
    }


    /* Text Input Styling */
    .stTextInput > div > div > input {
        background-color: #FFFFFF; /* White background for text inputs */
        color: #333333; /* Default text color */
        border: 1px solid #DDDDDD; /* Light gray border */
        border-radius: 5px;
        padding: 8px 10px;
        box-shadow: inset 1px 1px 3px rgba(0,0,0,0.1); /* Subtle inner shadow */
    }
    /* Text Area Styling */
    .stTextArea > div > div > textarea {
        background-color: #FFFFFF; /* White background for text areas */
        color: #333333; /* Default text color */
        border: 1px solid #DDDDDD; /* Light gray border */
        border-radius: 5px;
        padding: 8px 10px;
        box-shadow: inset 1px 1px 3px rgba(0,0,0,0.1); /* Subtle inner shadow */
    }


    /* Dataframe Styling */
    .stDataFrame {
        overflow-x: auto; /* Enable horizontal scroll for the entire dataframe */
        border: 1px solid #DDDDDD; /* Light border around the table */
        border-radius: 5px;
        background-color: #FFEED4; /* Background for tables */
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* Soft shadow for tables */
    }
    .stDataFrame table {
        width: 100% !important; /* Ensure table takes full width of its container */
        border-collapse: collapse;
        font-size: 14px;
        color: #545B37; /* Text color for machine results in table */
    }
    .stDataFrame thead th {
        background-color: #FFEED4; /* Header background for table */
        color: #66382B; /* Header text color for table */
        padding: 10px 15px;
        text-align: left;
        border-bottom: 1px solid #DDDDDD;
        font-weight: bold; /* Make table headers bold */
    }
    .stDataFrame tbody tr {
        background-color: #FFFFFF; /* White rows by default for contrast */
    }
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #FFF8E6; /* Slightly different shade for even rows, light cream */
    }
    .stDataFrame tbody td {
        padding: 10px 15px;
        border-bottom: 1px solid #EEEEEE; /* Lighter border between rows */
        white-space: normal; /* Allow text to wrap within cells */
    }
    /* Specific width for 'Key Features' to suggest a minimum, combined with wrap */
    .stDataFrame tbody td:nth-child(6) { /* Assuming 'Key Features' is the 6th column due to S. No. */
        min-width: 250px;
    }
    /* If 'Units Req.' and 'Total Cap.' are present, adjust their column width */
    .stDataFrame tbody td:nth-child(5), /* Units Req. */
    .stDataFrame tbody td:nth-child(6) { /* Total Cap. (if present before original 6th) */
        min-width: 80px; /* Smaller width for numeric columns */
        text-align: center; /* Center align these numbers */
    }


    /* Other Streamlit elements */
    .stMarkdown, .stText {
        color: #333333; /* Default text color for markdown/write */
    }

    /* Adjust padding for main content area to align with background */
    /* No changes needed here, as the full-width elements handle their own margins */


    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #FFEED4 !important; /* Sidebar background */
        color: #333333; /* Text color for sidebar */
    }
    [data-testid="stSidebarContent"] {
        background-color: #FFEED4 !important; /* Ensure content area also matches */
        padding-top: 2rem; /* Add some padding at the top of the sidebar content */
        /* NO min-height: 100vh here, which often causes scrolling issues */
    }
    [data-testid="stSidebar"] .st-emotion-cache-1kyxreq h2, /* Specific targeting for selectbox label in sidebar */
    [data-testid="stSidebar"] h2 {
        color: #66382B !important; /* Ensure sidebar headings match other headings */
    }
    /* Adjust button background within sidebar if needed, though global .stButton should apply */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #4A5022;
        color: #FEFEFE;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #3b3f1b;
    }

    /* Copyright Footer Styling */
    .footer {
        font-size: 0.8rem;
        color: #66382B; /* Darker brown from palette for text */
        background-color: transparent; /* Removed background */
        text-align: center;
        margin-top: 50px; /* Space above the footer - REVERTED to fixed margin */
        padding: 20px 0; /* Padding inside the footer div */
        border-top: 1px solid #DDDDDD; /* A subtle line above it */

        /* REVERTED: Full width hack that's more stable for Streamlit */
        width: calc(100% + 6rem); /* Ensure it spans full width including Streamlit's padding */
        box-sizing: border-box; /* Include padding and border in the width */
        margin-left: -3rem; /* Compensate for Streamlit's default left/right padding */
        margin-right: -3rem; /* Compensate for Streamlit's default left/right padding */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Excel to CSV Sync Function (Integrated) ---
def excel_to_csv_sync(excel_file_path, csv_file_path):
    # These messages will now go to the terminal/console, not the app UI.
    print(f"🔄 Running Excel to CSV sync from '{excel_file_path}' to '{csv_file_path}'...")
    try:
        if not os.path.exists(excel_file_path):
            print(f"ERROR: Source Excel file '{excel_file_path}' not found for sync.")
            st.error(f"❌ Error: Source Excel file '{excel_file_path}' not found.")
            st.stop()

        # Read the Excel file, specifying the sheet name and reading all as strings initially
        df = pd.read_excel(excel_file_path, sheet_name="Raw Data", dtype=str)

        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('').astype(str).str.strip()

        df.to_csv(csv_file_path, index=False, encoding="utf-8")
        print(f"✅ Sync completed: '{excel_file_path}' synced to '{csv_file_path}'.")
        return True
    except Exception as e:
        print(f"❌ ERROR during Excel to CSV sync: {e}")
        st.error(f"❌ Error during Excel to CSV sync. Details in terminal/console: {e}")
        st.error("Please ensure 'Autobake_Machines_Data.xlsx' is correct and accessible, and that the sheet name ('Raw Data') is accurate.")
        return False

# --- Data Sync and Loading ---
EXCEL_FILE = "Autobake_Machines_Data.xlsx"
CSV_FILE = "Raw_Data.csv"

if excel_to_csv_sync(EXCEL_FILE, CSV_FILE):
    try:
        df_raw = pd.read_csv(CSV_FILE, encoding="utf-8")

        # Create numeric columns for calculations, keeping original string columns for display
        df_raw["_Numeric_Dough Min (g)"] = pd.to_numeric(df_raw["Dough Min (g)"], errors="coerce")
        df_raw["_Numeric_Dough Max (g)"] = pd.to_numeric(df_raw["Dough Max (g)"], errors="coerce")
        df_raw["_Numeric_Production Capacity (pcs/hr)"] = pd.to_numeric(df_raw["Production Capacity (pcs/hr)"], errors="coerce")

    except FileNotFoundError:
        print(f"ERROR: '{CSV_FILE}' not found AFTER sync, or could not be loaded by pandas.")
        st.error(f"❌ Error: '{CSV_FILE}' not found AFTER sync. This indicates an issue with the sync script or file permissions.")
        st.stop()
    except Exception as e:
        print(f"ERROR: Exception loading '{CSV_FILE}' into DataFrame: {e}")
        st.error(f"❌ Error loading '{CSV_FILE}' into DataFrame: {e}")
        st.stop()
else:
    print("DEBUG: excel_to_csv_sync returned False. Stopping app.")
    st.stop()

# --- Preprocess Raw Data ---
if "Products" not in df_raw.columns:
    st.warning("⚠️ Warning: 'Products' column not found in `Raw_Data.csv`. Please ensure your Excel data has a column named 'Products' (case-sensitive) for proper matching.", icon="⚠️")
    df_raw["Products"] = ""
df_raw.dropna(subset=["Products"], inplace=True)
df_raw["Products"] = df_raw["Products"].astype(str).str.lower()

df_combined = df_raw.copy()
df_combined.drop_duplicates(inplace=True)

# --- Product normalization dictionary ---
product_normalization = {
    "bread": "bread", "bred": "bread", "brown bred": "brown bread", "brown bread": "brown bread",
    "white bread": "white bread", "sour dough bread": "sourdough bread", "sourdough bread": "sourdough bread",
    "bun": "bun", "buns": "bun", "roll": "roll", "rolls": "roll",
    "doughnut": "donut", "doughnuts": "donut", "donut": "donut", "donuts": "donut",
    "hotdog": "hot dog", "hot dog": "hot dog",
    "cake": "cake", "cakes": "cake", "cupcake": "cup cake", "cupcakes": "cup cake",
    "pastry": "pastry", "pastries": "pastry",
    "pizza base": "pizza base", "pizza bases": "pizza base",
    "naan": "naan", "naans": "naan",
    "chapati": "chapati", "chapatis": "chapati",
    "biscuit": "biscuit", "biscuits": "biscuit",
    "cookie": "cookie", "cookies": "cookie", "cooky": "cookie",
    "rusk": "rusk", "rusks": "rusk",
    "muffin": "muffin", "muffins": "muffin",
    "croissant": "croissant", "croissants": "croissant",
    "toast": "toast", "toasts": "toast",
    "puff": "puff pastry", "puffs": "puff pastry",
    "baguette": "baguette", "baguettes": "baguette",
    "brioche": "brioche", "brioches": "brioche",
    "kulcha": "kulcha", "kulchas": "kulcha",
    "swiss roll": "swiss roll", "swiss rolls": "swiss roll",
    "eclair": "eclair", "eclairs": "eclair",
    "macaron": "macaron", "macarons": "macaron",
    "creme roll": "cream roll", "cream roll": "cream roll", # Consistent spelling
    "pizza": "pizza base" # Alias for "pizza base"
}

def normalize_product(product_str):
    p = str(product_str).strip().lower()
    normalized = product_normalization.get(p, None)
    if normalized:
        return normalized
    if p.endswith("s") and not p.endswith("ss"):
        return p.rstrip("s")
    return p

def extract_and_normalize_products_from_df(product_series):
    all_products = set()
    for entry in product_series:
        for p in str(entry).split(","):
            normalized = normalize_product(p)
            if normalized and normalized not in ["nan", "n/a", ""]:
                all_products.add(normalized)
    return sorted(list(all_products))

product_set = extract_and_normalize_products_from_df(df_combined["Products"])

# --- Define Mappings for Production Line Logic ---
machine_stage_mapping = {
    "Spiral Mixer": "Mixing", "Reinforced Spiral Mixer with Fixed Bowl": "Mixing",
    "Hydraulic Bowl Lifter": "Mixing", "Spiral Mixer (Fixed Bowl)": "Mixing",
    "Spiral Mixer with Hydraulic Lifter": "Mixing", "Mixer": "Mixing",
    "Planetary Mixer": "Mixing", "Dough Mixer": "Mixing",

    "Automatic divider & rounder": "Dividing", "Automatic Divider and Moulder": "Dividing",
    "Dough Divider": "Dividing", "Dough Rounder": "Dividing",

    "Automatic Cream Roll Forming": "Forming", "Cookie Dropping Machine": "Forming",
    "Wire Cut Cookie Machine": "Forming", "Rotary Moulder": "Forming",
    "Dough Moulder": "Forming", "Sheeter": "Forming", "Laminator": "Forming",
    "Depositor": "Depositing", "Dough Former": "Forming", "Extruder": "Forming",

    "Confectionery depositor": "Depositing", "Automatic Confectionery Depositer": "Depositing",
    "Inline Depositing & Decorating": "Depositing",

    "Depositing & Icing": "Finishing", "Depositing Injecting & Icing": "Finishing",
    "Depositing & Injecting": "Filling", "Filling": "Filling", # Corrected typo in key to match value

    "Convection oven": "Baking", "Fryer": "Baking",
    "Cyclothermic Deck Oven": "Baking", "Rotary Rack Oven": "Baking",
    "Rotary Convection Oven": "Baking", "Electric Deck Oven": "Baking",
    "Tunnel Oven": "Baking", "Industrial Oven": "Baking",

    "Vacuum Cooler": "Cooling", "Cooling Conveyor": "Cooling", "Cooling Tunnel": "Cooling",

    "Slicing": "Slicing", "Slicing & Packing Line": "Slicing",
    "Bread Slicer": "Slicing", "Automatic Commercial Bread Slicer": "Slicing",
    "Automatic Bread Slicer": "Slicing", "Cake Slicer": "Slicing",

    "Sourdough Fermenter": "Fermentation", "Proofer": "Proofing",
    "Intermediate Proofer": "Proofing",

    "Packing Machine": "Packing", "Flow Wrap Machine": "Packing",
    "Vertical Form Fill Seal Machine": "Packing", "Horizontal Flow Wrapper": "Packing",
    "Packaging Machine": "Packing",

    "Syrup Spraying": "Finishing", "Glazer": "Finishing",
    "Decorating Machine": "Finishing", "Enrober": "Finishing",

    "Automatic Cake Line": "Complete Line", "Integrated Bread Line": "Complete Line",
    "Integrated Bun Line": "Complete Line", "Integrated Cookie Line": "Complete Line",
    "Integrated Donut Line": "Complete Line", "Integrated Pastry Line": "Complete Line",
    "General Purpose": "General Processing", "Industrial Line": "Complete Line"
}


# Helper function for fuzzy matching categories
def get_stage_from_category(category_name, mapping=machine_stage_mapping, threshold=85):
    if pd.isna(category_name) or not isinstance(category_name, str):
        return "N/A"
    best_match = process.extractOne(category_name, mapping.keys(), scorer=fuzz.token_sort_ratio)
    if best_match and best_match[1] >= threshold:
        return mapping[best_match[0]]
    return "N/A"

product_to_group_mapping = {
    "bun": "Bun & Pav Line", "long bun": "Bun & Pav Line", "ladi pav": "Bun & Pav Line",
    "fruit bun": "Bun & Pav Line", "hamburger bun": "Bun & Pav Line",
    "dinner roll": "Bun & Pav Line", "hot dog": "Bun & Pav Line",
    "burger bun": "Bun & Pav Line", "pav": "Bun & Pav Line",

    "bread loaf": "Bread Line", "white bread": "Bread Line",
    "tin bread": "Bread Line", "brown bread": "Bread Line",
    "sandwich bread": "Bread Line",

    "atta cookie": "Cookie Line", "butter cookie": "Cookie Line",
    "choco-filled cookie": "Cookie Line", "checkered cookie": "Cookie Line",
    "coconut biscuit": "Cookie Line", "danish cookie": "Cookie Line",
    "drop cookie": "Cookie Line", "date bar cookie": "Cookie Line",
    "long drop cookie": "Cookie Line", "rotary cookie": "Cookie Line",
    "shortbread cookie": "Cookie Line", "neapolitan cookie": "Cookie Line",
    "viennese whirl": "Cookie Line", "wirecut cookie": "Cookie Line",
    "jeera butter": "Biscuit & Snack Line",

    "banana cake": "Cake Line", "barni cake": "Cake Line",
    "battenberg cake": "Cake Line", "carrot cake": "Cake Line",
    "cup cake": "Cake Line", "muffin": "Cake Line",
    "rainbow muffin": "Cake Line", "plum cake": "Cake Line",
    "slice cake": "Cake Line", "sponge cake": "Cake Line",
    "sponge sheet": "Cake Line", "finger cake": "Cake Line",
    "pound cake": "Cake Line", "bar cake": "Cake Line",

    "cream filled muffin": "Confectionery & Filled Line",
    "swiss roll": "Confectionery & Filled Line",
    "swiss roll sheet": "Confectionery & Filled Line",
    "jam roll": "Confectionery & Filled Line",

    "croissant": "Puff & Croissant Line", "puff pastry": "Puff & Croissant Line",
    "khari": "Puff & Croissant Line", "danish pastry": "Puff & Croissant Line",

    "fruit rusk": "Rusk & Toast Line", "jeera rusk": "Rusk & Toast Line",
    "rusk": "Rusk & Toast Line", "toast": "Rusk & Toast Line",
    "milk rusk": "Rusk & Toast Line",

    "sour dough": "Specialty Bread Line", "sourdough bread": "Specialty Bread Line",
    "brioche": "Specialty Bread Line", "baguette": "baguette", # Corrected typo "Baguelte"
    "kulcha": "General Products", # Assigning to General Products as no specific group found
    "focaccia": "Specialty Bread Line", "ciabatta": "Specialty Bread Line",

    "cream roll": "Confectionery & Filled Line",
    "eclair": "Confectionery & Filled Line",

    "pizza base": "Pizza Base Line",
    "macaron": "Macaron Line",
    "donut": "Donut Line",
    "doughnut": "Donut Line",

    "biscuit": "Biscuit & Snack Line",
    "cracker": "Biscuit & Snack Line",
    "namkeen": "Biscuit & Snack Line",
    "wafer": "Biscuit & Snack Line",
    "cookies": "Cookie Line",
}

for p in product_set:
    if p not in product_to_group_mapping:
        product_to_group_mapping[p] = "General Products"

group_wise_production_lines = {
    "Bun & Pav Line": [
        "Mixing", "Dividing", "Forming", "Proofing", "Baking", "Cooling", "Slicing", "Packing"
    ],
    "Bread Line": [
        "Mixing", "Dividing", "Forming", "Fermentation", "Baking", "Cooling", "Slicing", "Packing"
    ],
    "Cookie Line": [
        "Mixing", "Forming", "Depositing", "Baking", "Cooling", "Packing"
    ],
    "Cake Line": [
        "Mixing", "Depositing", "Baking", "Cooling", "Finishing", "Packing"
    ],
    "Puff & Croissant Line": [
        "Mixing", "Sheeting", "Forming", "Proofing", "Baking", "Cooling", "Packing"
    ],
    "Rusk & Toast Line": [
        "Mixing", "Dividing", "Forming", "Baking", "Cooling", "Slicing", "Re-Baking", "Packing"
    ],
    "Specialty Bread Line": [
        "Mixing", "Fermentation", "Dividing", "Forming", "Proofing", "Baking", "Cooling", "Packing"
    ],
    "Confectionery & Filled Line": [
        "Mixing", "Depositing", "Forming", "Baking", "Cooling", "Filling", "Finishing", "Packing"
    ],
    "Pizza Base Line": [
        "Mixing", "Dividing", "Forming", "Proofing", "Baking", "Cooling", "Packing"
    ],
    "Biscuit & Snack Line": [
        "Mixing", "Forming", "Baking", "Cooling", "Packing"
    ],
    "Macaron Line": [
        "Mixing", "Depositing", "Baking", "Cooling", "Packing"
    ],
    "Donut Line": [
        "Mixing", "Forming", "Proofing", "Baking", "Finishing", "Slicing"
    ],
    "General Products": [
        "Mixing", "General Processing", "Packing"
    ]
}

# --- Parse user prompt ---
def parse_input(prompt_text):
    prompt_text = prompt_text.lower()

    capacity_match = re.search(r"(\d{2,6})\s*(pcs|pieces|per hour|/hr|units)?", prompt_text)
    capacity = int(capacity_match.group(1)) if capacity_match else None

    dough_match = re.search(r"(dough\s*weight\s*(of)?\s*)?(\d{1,4})\s*(g|grams|gram)\b", prompt_text)
    dough_weight = float(dough_match.group(3)) if dough_match else None

    words = prompt_text.split()
    candidates = []
    for i in range(len(words)):
        for j in range(1, 4):
            phrase = " ".join(words[i:i + j])
            if len(phrase.split()) == j:
                candidates.append(phrase)

    best_match = None
    best_score = 0
    candidates.append(prompt_text)

    non_product_terms = ["line", "per hour", "capacity", "dough", "weight", "needed", "make", "produce", "for", "machine"]
    filtered_candidates = [c for c in candidates if not any(term in c for term in non_product_terms)]
    if not filtered_candidates:
        filtered_candidates = candidates

    for phrase in filtered_candidates:
        normalized_phrase = normalize_product(phrase)
        match_result = process.extractOne(normalized_phrase, product_set, scorer=fuzz.token_sort_ratio)
        if match_result and match_result[1] > best_score:
            best_match = match_result[0]
            best_score = match_result[1]

    product = best_match if best_score >= 80 else None

    return product, dough_weight, capacity

# --- Helper to display values (preserving original strings for non-numeric data) ---
def get_display_value(value):
    """
    Returns the string representation of a value, handling NaN or empty strings.
    If truly empty or NaN, returns a dash. Otherwise, returns the exact string.
    """
    s_value = str(value).strip()
    if s_value.lower() in ["nan", "n/a", ""]:
        return "-"
    return s_value

# --- Helper to generate DataFrame for display with 1-indexed S. No. ---
def generate_display_dataframe(df_machines, min_capacity_provided):
    # Add 'S. No.' column
    df_machines_copy = df_machines.copy() # Work on a copy to avoid SettingWithCopyWarning
    df_machines_copy.insert(0, 'S. No.', range(1, 1 + len(df_machines_copy)))

    table_headers = ["S. No.", "Machine Name", "Company", "Capacity (pcs/hr)", "Dough (g)", "Key Features"]
    if isinstance(min_capacity_provided, (int, float)):
        # Adjusting insertion points for "Units Req." and "Total Cap." based on your desired order
        table_headers.insert(4, "Units Req.") # Insert after "Capacity (pcs/hr)"
        table_headers.insert(5, "Total Cap.") # Insert after "Units Req."

    table_rows = []
    for _, machine_row in df_machines_copy.iterrows(): # Iterate over the copy with S. No.
        s_no = str(machine_row.get("S. No.", "N/A"))
        machine_name = get_display_value(machine_row.get("Machine Name", "N/A"))
        company = get_display_value(machine_row.get("Company Name", "N/A"))

        # Display original string for Production Capacity
        prod_capacity = get_display_value(machine_row.get("Production Capacity (pcs/hr)", "N/A"))

        # Display original strings for Dough Min/Max
        dough_min_str = get_display_value(machine_row.get("Dough Min (g)", "N/A"))
        dough_max_str = get_display_value(machine_row.get("Dough Max (g)", "N/A"))

        dough_info = "-"
        if dough_min_str != "-" and dough_max_str != "-":
            dough_info = f"{dough_min_str}-{dough_max_str}g"
        elif dough_min_str != "-":
            dough_info = f"Min {dough_min_str}g"
        elif dough_max_str != "-":
            dough_info = f"Max {dough_max_str}g"

        key_features = get_display_value(machine_row.get("Key Features / Notes", "N/A"))
        # Replace newlines with spaces for better table display
        key_features = key_features.replace('\n', ' ').strip()


        row_data = [
            s_no,
            machine_name,
            company,
            prod_capacity,
            dough_info,
            key_features
        ]

        if isinstance(min_capacity_provided, (int, float)):
            units_required = machine_row.get("Calculated Units Required", None)
            total_capacity_val = machine_row.get("Calculated Total Capacity", None)

            units_req_str = "-"
            total_cap_str = "-"

            if pd.notna(units_required) and units_required != float('inf'):
                units_req_str = str(int(units_required))
            elif units_required == float('inf'):
                units_req_str = "N/A (Cap. 0)"

            if pd.notna(total_capacity_val):
                total_cap_str = str(int(total_capacity_val))

            row_data.insert(4, units_req_str) # Insert at position 4 (after Capacity)
            row_data.insert(5, total_cap_str) # Insert at position 5 (after Units Req)

        table_rows.append(row_data)

    if not table_rows:
        return pd.DataFrame()

    display_df = pd.DataFrame(table_rows, columns=table_headers)
    return display_df


# --- Main matching function ---
def match_from_inputs(prompt, selected_product, dough_weight_input, capacity_input):
    product, dough_weight, min_capacity = None, None, None

    # Determine input source
    if prompt.strip():
        product, dough_weight, min_capacity = parse_input(prompt)
    else:
        product = normalize_product(selected_product) if selected_product else None
        try:
            dough_weight = None if dough_weight_input in ("", "-", None) else float(dough_weight_input)
        except ValueError:
            st.error("Invalid Dough Weight. Please enter a number or '-'")
            return
        try:
            min_capacity = None if capacity_input in ("", "-", None) else int(capacity_input)
        except ValueError:
            st.error("Invalid Capacity. Please enter a whole number or '-'")
            return

    if not product:
        st.error("❌ Couldn't identify a valid product from your input or selection. Please refine your input.")
        return

    product_group = product_to_group_mapping.get(product, "General Products")
    production_line_stages = group_wise_production_lines.get(product_group, ["General Processing"])

    st.markdown(f"## 📦 **Product:** `{product.title()}`")
    st.markdown(f"## 🔄 **Production Line:** `{ ' → '.join(production_line_stages) }`")
    st.markdown("---")

    eligible_df_product_filtered = df_combined[
        df_combined["Products"].apply(lambda x: product in [normalize_product(p) for p in str(x).split(",")])
    ].copy()

    if eligible_df_product_filtered.empty:
        st.warning(f"❌ No machines found in the database that are specified for **{product.title()}**.")
        return

    for stage in production_line_stages:
        st.markdown(f"### **Stage: {stage}**")

        stage_eligible_machines = eligible_df_product_filtered[
            eligible_df_product_filtered["Category"].apply(
                lambda x: get_stage_from_category(str(x)) == stage
            )
        ].copy()

        if stage_eligible_machines.empty:
            st.info("    _No specific machines found for this stage matching the product._")
            continue

        # Use the numeric columns for calculations
        dough_match_mask = pd.Series(True, index=stage_eligible_machines.index)
        capacity_match_mask = pd.Series(True, index=stage_eligible_machines.index)

        if isinstance(dough_weight, (int, float)):
            dough_match_mask = (stage_eligible_machines["_Numeric_Dough Min (g)"].isna() | (stage_eligible_machines["_Numeric_Dough Min (g)"] <= dough_weight)) & \
                               (stage_eligible_machines["_Numeric_Dough Max (g)"].isna() | (stage_eligible_machines["_Numeric_Dough Max (g)"] >= dough_weight))

        if isinstance(min_capacity, (int, float)):
            stage_eligible_machines["Calculated Units Required"] = stage_eligible_machines["_Numeric_Production Capacity (pcs/hr)"].apply(
                lambda x: math.ceil(min_capacity / x) if pd.notna(x) and x > 0 else (None if pd.isna(x) or x == 0 else float('inf'))
            )
            stage_eligible_machines["Calculated Total Capacity"] = stage_eligible_machines.apply(
                lambda row: row["Calculated Units Required"] * row["_Numeric_Production Capacity (pcs/hr)"]
                if pd.notna(row["Calculated Units Required"]) and pd.notna(row["_Numeric_Production Capacity (pcs/hr)"])
                and row["Calculated Units Required"] != float('inf') # Exclude inf units from total capacity calculation
                else None, axis=1
            )
            capacity_match_mask = (stage_eligible_machines["_Numeric_Production Capacity (pcs/hr)"].notna()) & \
                                  (stage_eligible_machines["_Numeric_Production Capacity (pcs/hr)"] > 0) & \
                                  (stage_eligible_machines["Calculated Total Capacity"].fillna(0) >= min_capacity) # Fillna 0 for comparison

        else:
            stage_eligible_machines["Calculated Units Required"] = None
            stage_eligible_machines["Calculated Total Capacity"] = None


        tier1_machines = stage_eligible_machines[dough_match_mask & capacity_match_mask].sort_values(by="Company Name").copy()
        tier2_machines = stage_eligible_machines[~(dough_match_mask & capacity_match_mask)].sort_values(by="Company Name").copy()

        if not tier1_machines.empty:
            st.markdown("#### ✅ Machines meeting all criteria:")
            st.dataframe(generate_display_dataframe(tier1_machines, min_capacity), hide_index=True) # hide_index hides pandas default 0-index
        elif tier2_machines.empty:
            st.info("    _No machines perfectly meet all specified criteria for this stage, and no other relevant machines were found._")


        if not tier2_machines.empty:
            st.markdown("#### ℹ️ Other relevant machines (may not meet all numeric criteria or have missing data):")
            st.dataframe(generate_display_dataframe(tier2_machines, min_capacity), hide_index=True) # hide_index hides pandas default 0-index
        elif tier1_machines.empty:
            st.info("    _No other relevant machines found for this stage._")


        st.markdown("\n")

# --- Streamlit UI Elements ---
# Using markdown to create the custom title with specific colors and line break
st.markdown(
    """
    <div class="header-section">
        <h1><span class="auto">Auto</span><span class="bake">bake</span></h1><br>
        <h2>Machine Match</h2>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")
st.write("Enter your bakery production needs below. You can describe your requirement in natural language, or use the dropdowns and numeric fields for precise input. Use '-' to skip optional numeric fields.")

# Use a placeholder for messages or results that might be shown before actual results
results_placeholder = st.empty()

# Move the form to the sidebar
with st.sidebar: # This places the content in the sidebar
    st.header("Search Criteria")
    with st.form("machine_matcher_form_sidebar"): # Give it a unique key for the sidebar
        prompt_input = st.text_area(
            "🧠 Describe your requirement (optional)",
            placeholder="e.g., 'I need a line for 5000 donuts per hour with 50g dough weight'",
            height=80
        )
        selected_product = st.selectbox(
            "📦 Select Product (optional, overrides prompt if present)",
            options=[""] + product_set,
            index=0
        )

        dough_weight_input = st.text_input(
            "⚖️ Dough Weight (grams, optional — use '-' to skip)",
            placeholder="e.g., 100 or -",
            value="-"
        )
        capacity_input = st.text_input(
            "📈 Production Capacity Needed (per hour, optional — use '-' to skip)",
            placeholder="e.g., 10000 or -",
            value="-"
        )

        submitted = st.form_submit_button("Find Machines")

# Display results in the main area
if submitted:
    results_placeholder.empty()
    with results_placeholder.container(): # Use the placeholder to display dynamic content
        with st.spinner("Searching for machines..."):
            match_from_inputs(prompt_input, selected_product, dough_weight_input, capacity_input)

# --- Copyright Footer ---
st.markdown(
    """
    <div class="footer">
        &copy; Designed and developed by Mohammed Udaipurwala
    </div>
    """,
    unsafe_allow_html=True
)
