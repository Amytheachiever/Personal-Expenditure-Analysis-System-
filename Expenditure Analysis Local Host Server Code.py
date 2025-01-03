import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, request, send_file
import os

# Initialize Flask app
app = Flask(__name__)

# Ensure uploads directory exists
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Step 1: Load the Expense Data
def load_data(file_path):
    try:
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        return data
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

# Step 2: Clean and Prepare the Data
def clean_data(data):
    data.columns = [col.strip().upper().replace('.', '') for col in data.columns]
    data = data.drop(columns=['CHQNO', 'VALUEDATE', ''], errors='ignore')
    data.rename(columns={
        'ACCOUNT NO': 'ACCOUNT_NO',
        'DATE': 'DATE',
        'TRANSACTION DETAILS': 'TRANSACTION_DETAILS',
        'WITHDRAWAL AMT': 'WITHDRAWAL_AMT',
        'DEPOSIT AMT': 'DEPOSIT_AMT',
        'BALANCE AMT': 'BALANCE_AMT'
    }, inplace=True)
    data['DATE'] = pd.to_datetime(data['DATE'], errors='coerce')
    data[['WITHDRAWAL_AMT', 'DEPOSIT_AMT']] = data[['WITHDRAWAL_AMT', 'DEPOSIT_AMT']].fillna(0)
    data['NET_AMOUNT'] = data['DEPOSIT_AMT'] - data['WITHDRAWAL_AMT']
    return data

# Step 3: Categorize Expenses
def categorize_expenses(data):
    expense_data = data[data['WITHDRAWAL_AMT'] > 0].copy()
    category_summary = expense_data.groupby('TRANSACTION_DETAILS')['WITHDRAWAL_AMT'].sum().reset_index()
    category_summary.sort_values(by='WITHDRAWAL_AMT', ascending=False, inplace=True)
    return category_summary

# Step 4: Analyze Monthly Expenses
def analyze_monthly_expenses(data):
    data['MONTH'] = data['DATE'].dt.to_period('M')
    monthly_summary = data.groupby('MONTH')['WITHDRAWAL_AMT'].sum().reset_index()
    return monthly_summary

# Step 5: Plot and Save the Graphs
def plot_category_expenses(category_summary):
    plt.figure(figsize=(10, 6))
    sns.barplot(x='WITHDRAWAL_AMT', y='TRANSACTION_DETAILS', data=category_summary.head(10), palette='viridis')
    plt.title('Top 10 Expense Categories')
    plt.xlabel('Total Withdrawal Amount')
    plt.ylabel('Transaction Details')
    plt.savefig('static/category_expenses.png')
    plt.close()

def plot_monthly_expenses(monthly_summary):
    monthly_summary['MONTH'] = monthly_summary['MONTH'].astype(str)
    plt.figure(figsize=(12, 6))
    sns.lineplot(x='MONTH', y='WITHDRAWAL_AMT', data=monthly_summary, marker='o', color='b')
    plt.title('Monthly Expense Trend')
    plt.xlabel('Month')
    plt.ylabel('Total Withdrawal Amount')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.savefig('static/monthly_expenses.png')
    plt.close()

def plot_pie_chart(category_summary):
    plt.figure(figsize=(8, 8))
    category_summary.set_index('TRANSACTION_DETAILS')['WITHDRAWAL_AMT'].head(10).plot.pie(autopct='%1.1f%%', startangle=140, colormap='tab20')
    plt.title('Expense Distribution by Top Categories')
    plt.savefig('static/expense_distribution.png')
    plt.close()

# Step 6: Actionable Insights
def actionable_insights(category_summary, monthly_summary, data):
    total_expense = category_summary['WITHDRAWAL_AMT'].sum()
    total_income = data['DEPOSIT_AMT'].sum()
    insights = []

    if total_expense > total_income * 0.8:
        insights.append("Your expenses exceed 80% of your income. Review your budgeting.")
    
    monthly_high_expense = monthly_summary['WITHDRAWAL_AMT'].max()
    insights.append(f"Your highest monthly expense is {monthly_high_expense}.")

    return insights

# Flask route to render the index page
@app.route('/')
def index():
    return render_template('index.html')

# Flask route to handle file upload and analysis
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        # Process the data
        data = load_data(file_path)
        if data is not None:
            data = clean_data(data)
            category_summary = categorize_expenses(data)
            monthly_summary = analyze_monthly_expenses(data)

            # Generate insights and graphs
            actionable = actionable_insights(category_summary, monthly_summary, data)
            plot_category_expenses(category_summary)
            plot_monthly_expenses(monthly_summary)
            plot_pie_chart(category_summary)

            return render_template('result.html', actionable=actionable)
    return "File not found or invalid"

# Run the app
if __name__ == "__main__":
    app.run(debug=True)


