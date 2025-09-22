import pytest
from fastapi import status

class TestExpenses:
    
    def test_create_expense_success(self, client, authenticated_user, test_expense_data):
        """Test successful expense creation"""
        response = client.post(
            "/expenses", 
            json=test_expense_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == test_expense_data["description"]
        assert data["amount"] == test_expense_data["amount"]
        assert "id" in data
        assert "user_id" in data

    def test_create_expense_invalid_data(self, client, authenticated_user):
        """Test expense creation with invalid data"""
        invalid_data = {
            "description": "",  # Empty description
            "amount": -10.50    # Negative amount
        }
        
        response = client.post(
            "/expenses", 
            json=invalid_data,
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_expenses_success(self, client, authenticated_user, test_expense_data):
        """Test getting user's expenses"""
        # Create an expense first
        client.post(
            "/expenses", 
            json=test_expense_data,
            headers=authenticated_user["headers"]
        )
        
        # Get expenses
        response = client.get("/expenses", headers=authenticated_user["headers"])
        
        assert response.status_code == status.HTTP_200_OK
        expenses = response.json()
        assert len(expenses) == 1
        assert expenses[0]["description"] == test_expense_data["description"]

    def test_get_expenses_empty_list(self, client, authenticated_user):
        """Test getting expenses when user has none"""
        response = client.get("/expenses", headers=authenticated_user["headers"])
        
        assert response.status_code == status.HTTP_200_OK
        expenses = response.json()
        assert len(expenses) == 0

    def test_user_isolation(self, client, test_user_data, test_expense_data):
        """Test that users can only see their own expenses"""
        # Create first user and expense
        user1_data = {"username": "user1", "password": "pass123"}
        client.post("/register", json=user1_data)
        login1_response = client.post("/login", json=user1_data)
        user1_token = login1_response.json()["access_token"]
        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        
        client.post("/expenses", json=test_expense_data, headers=user1_headers)
        
        # Create second user
        user2_data = {"username": "user2", "password": "pass123"}
        client.post("/register", json=user2_data)
        login2_response = client.post("/login", json=user2_data)
        user2_token = login2_response.json()["access_token"]
        user2_headers = {"Authorization": f"Bearer {user2_token}"}
        
        # User2 should not see User1's expenses
        response = client.get("/expenses", headers=user2_headers)
        assert response.status_code == status.HTTP_200_OK
        expenses = response.json()
        assert len(expenses) == 0