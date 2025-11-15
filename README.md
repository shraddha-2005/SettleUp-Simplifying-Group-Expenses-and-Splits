SettleUp-Simplifying Group Expenses and Splits 
This project is an expense management application designed to track and settle shared expenses within groups. The application utilizes Django framework with SQLite database for data storage. It supports single and multiple payer scenarios with flexible splitting options, automatically calculates balances, and includes a dummy payment feature to simulate settlements.

Features
•	Integration with Django framework and SQLite database
•	Manual group and member creation with persistent data storage
•	Flexible expense splitting options (equal and unequal splits)
•	Support for single and multiple payer expense entries
•	Greedy algorithm implementation for optimal debt settlement 
•	Automated balance calculation with real-time updates
•	Dynamic "Who Owes Whom" settlement summary generation
•	Dummy payment simulation to mark expenses as settled
•	Responsive UI for testing and managing expenses

How to Run
Installation Steps
1. Clone the Repository
git clone https://github.com/yourusername/SettleUp-Simplifying-Group-Expenses-and-Splits.git
cd settleup
2. Create Virtual Environment
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
4. Apply Migrations
python manage.py makemigrations
python manage.py migrate
5. Run Development Server
python manage.py runserver
6. Access the Application
•	Open your browser and navigate to: http://localhost:8000
