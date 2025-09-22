import pytest
from fastapi import status

class TestIntegration:
    
    def test_full_user_journey(self, client):
        """Test complete user journey from registration to expense management"""
        user_data = {"username": "journeyuser", "password": "journey123"}
        
        # 1. Register
        register_response = client.post("/register", json=user_data)
        assert register_response.status_code == status.HTTP_200_OK
        
        # 2. Login
        login_response = client.post("/login", json=user_data)
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Create multiple expenses
        expenses_data = [
            {"description": "Groceries", "amount": 50.25},
            {"description": "Gas", "amount": 30.00},
            {"description": "Coffee", "amount": 5.50}
        ]
        
        for expense in expenses_data:
            response = client.post("/expenses", json=expense, headers=headers)
            assert response.status_code == status.HTTP_200_OK
        
        # 4. Get all expenses
        response = client.get("/expenses", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        user_expenses = response.json()
        assert len(user_expenses) == 3
        
        # 5. Verify total amount
        total_amount = sum(expense["amount"] for expense in user_expenses)
        expected_total = sum(expense["amount"] for expense in expenses_data)
        assert total_amount == expected_total

    def test_concurrent_users(self, client):
        """Test multiple users creating expenses concurrently"""
        users_data = [
            {"username": "concurrent1", "password": "pass123"},
            {"username": "concurrent2", "password": "pass123"},
            {"username": "concurrent3", "password": "pass123"}
        ]
        
        tokens = []
        
        # Register and login all users
        for user_data in users_data:
            client.post("/register", json=user_data)
            login_response = client.post("/login", json=user_data)
            tokens.append(login_response.json()["access_token"])
        
        # Each user creates expenses
        for i, token in enumerate(tokens):
            headers = {"Authorization": f"Bearer {token}"}
            expense_data = {
                "description": f"User {i+1} expense",
                "amount": (i + 1) * 10.0
            }
            response = client.post("/expenses", json=expense_data, headers=headers)
            assert response.status_code == status.HTTP_200_OK
        
        # Verify each user sees only their expenses
        for i, token in enumerate(tokens):
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/expenses", headers=headers)
            expenses = response.json()
            assert len(expenses) == 1
            assert expenses[0]["description"] == f"User {i+1} expense"