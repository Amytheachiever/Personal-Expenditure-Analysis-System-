import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Load the Expense Data
def load_data(file_path):
    """
    Load the expense data from an Excel file.
    """
    try:
        data = pd.read_excel(file_path, sheet_name='Sheet1')
        return data
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

# Step 2: Clean and Prepare the Data
def clean_data(data):
    """
    Clean and preprocess the expense data.
    """
    # Standardize column names
    data.columns = [col.strip().upper().replace('.', '') for col in data.columns]

    # Drop unnecessary columns
    data = data.drop(columns=['CHQNO', 'VALUEDATE', ''], errors='ignore')

    # Rename columns for clarity
    data.rename(columns={
        'ACCOUNT NO': 'ACCOUNT_NO',
        'DATE': 'DATE',
        'TRANSACTION DETAILS': 'TRANSACTION_DETAILS',
        'WITHDRAWAL AMT': 'WITHDRAWAL_AMT',
        'DEPOSIT AMT': 'DEPOSIT_AMT',
        'BALANCE AMT': 'BALANCE_AMT'
    }, inplace=True)

    # Convert date columns to datetime
    data['DATE'] = pd.to_datetime(data['DATE'], errors='coerce')

    # Fill missing values in numerical columns with 0
    data[['WITHDRAWAL_AMT', 'DEPOSIT_AMT']] = data[['WITHDRAWAL_AMT', 'DEPOSIT_AMT']].fillna(0)

    # Create a net amount column (-ve for withdrawals, +ve for deposits)
    data['NET_AMOUNT'] = data['DEPOSIT_AMT'] - data['WITHDRAWAL_AMT']

    return data

# Step 3: Categorize Expenses
def categorize_expenses(data):
    """
    Aggregate expenses by transaction details.
    """
    expense_data = data[data['WITHDRAWAL_AMT'] > 0].copy()
    category_summary = expense_data.groupby('TRANSACTION_DETAILS')['WITHDRAWAL_AMT'].sum().reset_index()
    category_summary.sort_values(by='WITHDRAWAL_AMT', ascending=False, inplace=True)
    return category_summary

# Step 4: Analyze Monthly Expenses
def analyze_monthly_expenses(data):
    """
    Aggregate expenses by month.
    """
    data['MONTH'] = data['DATE'].dt.to_period('M')
    monthly_summary = data.groupby('MONTH')['WITHDRAWAL_AMT'].sum().reset_index()
    return monthly_summary

# Step 5: Visualize Insights
def plot_category_expenses(category_summary):
    """
    Plot the expense distribution by transaction details.
    """
    plt.figure(figsize=(10, 6))
    sns.barplot(x='WITHDRAWAL_AMT', y='TRANSACTION_DETAILS', data=category_summary.head(10), palette='viridis')
    plt.title('Top 10 Expense Categories')
    plt.xlabel('Total Withdrawal Amount')
    plt.ylabel('Transaction Details')
    plt.show()

def plot_monthly_expenses(monthly_summary):
    """
    Plot the expense trend over months.
    """
    # Convert the MONTH column to a string for compatibility
    monthly_summary['MONTH'] = monthly_summary['MONTH'].astype(str)
    
    plt.figure(figsize=(12, 6))
    sns.lineplot(x='MONTH', y='WITHDRAWAL_AMT', data=monthly_summary, marker='o', color='b')
    plt.title('Monthly Expense Trend')
    plt.xlabel('Month')
    plt.ylabel('Total Withdrawal Amount')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()

def plot_pie_chart(category_summary):
    """
    Plot a pie chart of expense distribution by category.
    """
    plt.figure(figsize=(8, 8))
    category_summary.set_index('TRANSACTION_DETAILS')['WITHDRAWAL_AMT'].head(10).plot.pie(autopct='%1.1f%%', startangle=140, colormap='tab20')
    plt.title('Expense Distribution by Top Categories')
    plt.ylabel('')
    plt.show()

# Step 6: Actionable Insights
def actionable_insights(category_summary, monthly_summary, data):
    """
    Provide actionable insights into spending habits.
    """
    insights = []

    # Highlight the top expense category
    top_category = category_summary.iloc[0]
    insights.append(
        f"Your top expense category is '{top_category['TRANSACTION_DETAILS']}' with a total expenditure of {top_category['WITHDRAWAL_AMT']:.2f}. "
        "Consider reviewing these expenses to identify potential savings."
    )

    # Identify months with unusually high expenses
    average_monthly_expense = monthly_summary['WITHDRAWAL_AMT'].mean()
    high_expense_months = monthly_summary[monthly_summary['WITHDRAWAL_AMT'] > 1.5 * average_monthly_expense]
    if not high_expense_months.empty:
        months = ", ".join(high_expense_months['MONTH'].astype(str).tolist())
        insights.append(
            f"Your spending in the months {months} is significantly higher than average. "
            "Evaluate your expenses during these periods."
        )

    # Suggest diversification if one category dominates
    top_10_total = category_summary['WITHDRAWAL_AMT'].head(10).sum()
    overall_total = category_summary['WITHDRAWAL_AMT'].sum()
    if top_10_total / overall_total > 0.8:
        insights.append(
            "More than 80% of your expenses are concentrated in the top 10 categories. "
            "Consider diversifying your spending or optimizing these key areas."
        )

    # Suggest savings if income is sufficient
    total_expense = category_summary['WITHDRAWAL_AMT'].sum()
    total_income = data['DEPOSIT_AMT'].sum()  # Assuming total deposits represent income
    if total_expense > total_income * 0.8:
        insights.append(
            "Your expenses exceed 80% of your income. It might be time to review your budgeting and consider cutting down on non-essential spending."
        )

    # Provide advice for emergency funds and budgeting
    if total_expense > total_income:
        insights.append(
            "Your expenses exceed your income. Consider setting up an emergency fund and reviewing your spending habits."
        )

    # Print the insights without the Rupee symbol
    print("\n=== Actionable Insights ===")
    for insight in insights:
        print("- " + insight)




















# Step 7: Save Insights
def save_insights(category_summary, monthly_summary):
    """
    Save the insights into separate CSV files.
    """
    category_summary.to_csv('category_summary.csv', index=False)
    monthly_summary.to_csv('monthly_summary.csv', index=False)
    print("Insights saved as 'category_summary.csv' and 'monthly_summary.csv'.")

def main():
    file_path = r"C:\Users\user\OneDrive\Desktop\PROJECT\bank.xlsx"
    data = load_data(file_path)
    if data is not None:
        print("Data loaded successfully!")

        data = clean_data(data)
        print("Data cleaned and preprocessed.")

        category_summary = categorize_expenses(data)
        print("Expense summary by category:")
        print(category_summary.head(10))

        monthly_summary = analyze_monthly_expenses(data)
        print("Expense trend by month:")
        print(monthly_summary)

        plot_category_expenses(category_summary)
        plot_monthly_expenses(monthly_summary)
        plot_pie_chart(category_summary)

        # Pass 'data' as the third argument to actionable_insights
        actionable_insights(category_summary, monthly_summary, data)

        save_insights(category_summary, monthly_summary)

if __name__ == "__main__":
    main()


