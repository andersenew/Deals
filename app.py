from flask import Flask
import pandas as pd
import os

app = Flask(__name__)

def read_deals_from_google_sheets(sheet_url):
    """Read deals data from Google Sheets"""
    try:
        # Convert Google Sheets sharing URL to CSV export URL
        if '/edit' in sheet_url:
            # Extract the sheet ID from the URL
            sheet_id = sheet_url.split('/d/')[1].split('/')[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        else:
            csv_url = sheet_url
        
        print(f"Trying to read from: {csv_url}")
        
        # Read the Google Sheet as CSV
        df = pd.read_csv(csv_url)
        
        # Convert DataFrame to list of dictionaries
        deals_data = []
        for index, row in df.iterrows():
            deal = {
                "title": str(row['title']) if pd.notna(row['title']) else "No Title",
                "store": str(row['store']) if pd.notna(row['store']) else "Unknown Store",
                "current_price": float(row['current_price']) if pd.notna(row['current_price']) else 0.0,
                "original_price": float(row['original_price']) if pd.notna(row['original_price']) else 0.0,
                "deal_url": str(row['deal_url']) if pd.notna(row['deal_url']) else "#"
            }
            deals_data.append(deal)
        
        print(f"Successfully loaded {len(deals_data)} deals from Google Sheets")
        return deals_data
        
    except Exception as e:
        print(f"Error reading Google Sheets: {e}")
        return []

# Google Sheets URL - CHANGE THIS TO YOUR SHEET URL
google_sheet_url = "https://docs.google.com/spreadsheets/d/1uaBi90r1B1ON6YZtf74zGrwbwAAYwiDCQS769ReEdjI/edit#gid=0"

# Try to load deals from Google Sheets
deals_data = read_deals_from_google_sheets(google_sheet_url)

def calculate_discount(current_price, original_price):
    """Calculate discount percentage"""
    return round(((original_price - current_price) / original_price) * 100)

def create_deals_html(deals_list):
    """Generate HTML for all deals"""
    deals_html = ""
    
    for deal in deals_list:
        discount = calculate_discount(deal['current_price'], deal['original_price'])
        
        deal_html = f"""
    <div class="deal">
        <div class="deal-title">{deal['title']}</div>
        <div class="store">{deal['store']}</div>
        <div class="price">
            <span class="current-price">${deal['current_price']:.2f}</span>
            <span class="original-price">${deal['original_price']:.2f}</span>
            <span class="discount">{discount}% OFF</span>
        </div>
        <a href="{deal['deal_url']}" class="deal-link">View Deal</a>
    </div>"""
        
        deals_html += deal_html
    
    return deals_html

@app.route('/')
def home():
    # Reload deals from Google Sheets each time (so you get live updates)
    current_deals = read_deals_from_google_sheets(google_sheet_url)
    
    if not current_deals:
        # Show error message if no deals loaded
        error_html = """
        <div style="text-align: center; padding: 50px;">
            <h2>No deals found!</h2>
            <p>Make sure your Google Sheets URL is correct and the sheet is public</p>
            <p>The Google Sheet should have columns: title, store, current_price, original_price, deal_url</p>
            <br>
            <h3>How to set up Google Sheets:</h3>
            <ol style="text-align: left; display: inline-block;">
                <li>Create a Google Sheet with the required columns</li>
                <li>Click "Share" and set to "Anyone with the link can view"</li>
                <li>Copy the sharing URL and paste it in the Python code</li>
            </ol>
        </div>
        """
        
        html_page = f"""
        <!DOCTYPE html>
        <html><head><title>Deals List</title>
        <style>body{{font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;}}</style>
        </head>
        <body>{error_html}</body></html>
        """
        return html_page
    
    deals_html = create_deals_html(current_deals)
    
    html_page = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Deals List</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 20px auto;
                padding: 20px;
                background-color: #fff;
            }}

            h1 {{
                text-align: center;
                margin-bottom: 30px;
            }}

            .deal {{
                border: 1px solid #ccc;
                padding: 15px;
                margin-bottom: 15px;
                background-color: #f9f9f9;
            }}

            .deal-title {{
                font-weight: bold;
                font-size: 18px;
                margin-bottom: 5px;
            }}

            .store {{
                color: #666;
                margin-bottom: 8px;
            }}

            .price {{
                margin-bottom: 10px;
            }}

            .current-price {{
                font-size: 20px;
                font-weight: bold;
                color: #d9534f;
            }}

            .original-price {{
                text-decoration: line-through;
                color: #999;
                margin-left: 10px;
            }}

            .discount {{
                background-color: #d9534f;
                color: white;
                padding: 3px 8px;
                margin-left: 10px;
                font-size: 14px;
            }}

            .deal-link {{
                color: #337ab7;
                text-decoration: none;
            }}

            .deal-link:hover {{
                text-decoration: underline;
            }}

            .deals-count {{
                text-align: center;
                color: #666;
                margin-bottom: 20px;
            }}

            .refresh-note {{
                text-align: center;
                color: #666;
                font-size: 12px;
                margin-top: 20px;
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <h1>Today's Deals</h1>
        <div class="deals-count">Showing {len(current_deals)} deals from Google Sheets</div>
        {deals_html}
        <div class="refresh-note">Data updates automatically when you refresh the page</div>
    </body>
    </html>
    """
    
    return html_page

if __name__ == '__main__':
    print("Starting Flask app...")
    print("Visit: http://127.0.0.1:5000")
    app.run(debug=True)
