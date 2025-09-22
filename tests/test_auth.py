import pytest
from fastapi import status

class TestAuthentication:
    
    def test_register_user_success(self, client, test_user_data):
        """Test successful user registration"""
        response = client.post("/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password

    def test_register_duplicate_username(self, client, test_user_data):
        """Test registration with duplicate username"""
        # First registration
        client.post("/register", json=test_user_data)
        
        # Second registration with same username
        response = client.post("/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()

    def test_login_success(self, client, test_user_data):
        """Test successful login"""
        # Register user first
        client.post("/register", json=test_user_data)
        
        # Login
        response = client.post("/login", json=test_user_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, test_user_data):
        """Test login with invalid credentials"""
        # Register user first
        client.post("/register", json=test_user_data)
        
        # Login with wrong password
        invalid_data = test_user_data.copy()
        invalid_data["password"] = "wrongpassword"
        
        response = client.post("/login", json=invalid_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post("/login", json={
            "username": "nonexistent",
            "password": "password"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get("/expenses")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/expenses", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED