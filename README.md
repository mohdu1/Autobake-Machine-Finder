Autobake Machine Match App 🍞✨

This Streamlit application helps users quickly find suitable bakery machines based on their specific product, dough weight, and production capacity requirements. It streamlines the process of matching production needs with available machinery, presenting results by stages of the baking process.

Features 🚀

Intelligent Search: Describe your machine needs in natural language (e.g., "I need a line for 5000 donuts per hour with 50g dough weight").

Detailed Filtering: Optionally refine your search using dedicated dropdowns for product selection, and input fields for specific dough weight and production capacity.

Production Line Breakdown: Results are organized by the typical stages of a baking production line relevant to your selected product (e.g., Mixing, Forming, Baking, Packing).

Tiered Results: Machines are presented in two tiers: those that meet all specified criteria, and other relevant machines that might have missing data or slightly different specifications.

Dynamic Data Sync: Automatically syncs machine data from an Excel file (Autobake_Machines_Data.xlsx) to a CSV (Raw_Data.csv) on startup, ensuring the app always uses the latest information.

Custom Theme: Features a custom, user-friendly theme with colors inspired by bakery aesthetics for an enhanced visual experience.

Usage Guide 📋

Input Your Requirements:

Use the "Describe your requirement" text box for a natural language query.

Alternatively, or to refine your prompt, use the "Select Product" dropdown, and the "Dough Weight (grams)" and "Production Capacity Needed (per hour)" input fields. Use - in numeric fields if they are not applicable to your search.

Find Machines: Click the "Find Machines" button.

View Results: The app will display a loading spinner, then present matching machines categorized by their stage in the production line.
