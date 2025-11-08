"""
Integration tests for User and Farm API endpoints.

Tests the full API flow for user profile management.
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.models.user import User, UserRole
from app.models.farm import Farm
from app.models.user_preferences import UserPreferences


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.mark.integration
class TestUserAPI:
    """Integration tests for User API endpoints."""

    @pytest.mark.asyncio
    async def test_create_user_api(
        self, db_session, client: TestClient
    ) -> None:
        """Test POST /api/users creates a user."""
        user_data = {
            "email": f"apitest{uuid4().hex[:8]}@example.com",
            "full_name": "API Test User",
            "phone": "+1-555-123-4567",
            "role": "owner",
        }

        response = client.post("/api/users", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == user_data["email"]
        assert data["data"]["full_name"] == user_data["full_name"]
        assert "id" in data["data"]

    @pytest.mark.asyncio
    async def test_get_user_api(
        self, db_session, client: TestClient
    ) -> None:
        """Test GET /api/users/{user_id} returns user."""
        from app.services.user import UserService
        from app.schemas.user import UserCreate

        # Create user
        user_data = UserCreate(
            email=f"getuser{uuid4().hex[:8]}@example.com",
            full_name="Get User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        response = client.get(f"/api/users/{user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == str(user.id)
        assert data["data"]["email"] == user.email

    @pytest.mark.asyncio
    async def test_get_user_by_email_api(
        self, db_session, client: TestClient
    ) -> None:
        """Test GET /api/users/email/{email} returns user."""
        from app.services.user import UserService
        from app.schemas.user import UserCreate

        email = f"emailuser{uuid4().hex[:8]}@example.com"
        user_data = UserCreate(
            email=email,
            full_name="Email User",
            role=UserRole.OWNER,
        )
        await UserService.create_user(db_session, user_data)

        response = client.get(f"/api/users/email/{email}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == email

    @pytest.mark.asyncio
    async def test_update_user_api(
        self, db_session, client: TestClient
    ) -> None:
        """Test PUT /api/users/{user_id} updates user."""
        from app.services.user import UserService
        from app.schemas.user import UserCreate

        user_data = UserCreate(
            email=f"updateuser{uuid4().hex[:8]}@example.com",
            full_name="Update User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        update_data = {
            "full_name": "Updated Name",
            "phone": "+1-555-999-9999",
        }

        response = client.put(f"/api/users/{user.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["full_name"] == "Updated Name"
        assert data["data"]["phone"] == "+1-555-999-9999"

    @pytest.mark.asyncio
    async def test_list_users_api(
        self, db_session, client: TestClient
    ) -> None:
        """Test GET /api/users returns list of users."""
        response = client.get("/api/users?skip=0&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)


@pytest.mark.integration
class TestFarmAPI:
    """Integration tests for Farm API endpoints."""

    @pytest.mark.asyncio
    async def test_create_farm_api(
        self, db_session, client: TestClient
    ) -> None:
        """Test POST /api/farms creates a farm."""
        from app.services.user import UserService
        from app.schemas.user import UserCreate

        user_data = UserCreate(
            email=f"farmowner{uuid4().hex[:8]}@example.com",
            full_name="Farm Owner",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        farm_data = {
            "owner_id": str(user.id),
            "name": "API Test Farm",
            "farm_id": f"api-farm-{uuid4().hex[:8]}",
            "address": "123 Farm Road",
            "city": "Fresno",
            "state": "CA",
            "zip_code": "93710",
            "latitude": 36.7378,
            "longitude": -119.7871,
        }

        response = client.post("/api/farms", json=farm_data)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == farm_data["name"]
        assert data["data"]["farm_id"] == farm_data["farm_id"]

    @pytest.mark.asyncio
    async def test_get_farm_api(
        self, db_session, client: TestClient
    ) -> None:
        """Test GET /api/farms/{farm_id} returns farm."""
        from app.services.user import UserService
        from app.services.farm import FarmService
        from app.schemas.user import UserCreate
        from app.schemas.farm import FarmCreate

        user_data = UserCreate(
            email=f"farmget{uuid4().hex[:8]}@example.com",
            full_name="Farm Get User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        farm_data = FarmCreate(
            owner_id=user.id,
            name="Get Farm",
            farm_id=f"get-farm-{uuid4().hex[:8]}",
        )
        farm = await FarmService.create_farm(db_session, farm_data)

        response = client.get(f"/api/farms/{farm.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == str(farm.id)

    @pytest.mark.asyncio
    async def test_list_farms_by_owner_api(
        self, db_session, client: TestClient
    ) -> None:
        """Test GET /api/farms/owner/{owner_id} returns farms."""
        from app.services.user import UserService
        from app.services.farm import FarmService
        from app.schemas.user import UserCreate
        from app.schemas.farm import FarmCreate

        user_data = UserCreate(
            email=f"farmlist{uuid4().hex[:8]}@example.com",
            full_name="Farm List User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        # Create farms
        for i in range(2):
            farm_data = FarmCreate(
                owner_id=user.id,
                name=f"Farm {i}",
                farm_id=f"list-farm-{uuid4().hex[:8]}",
            )
            await FarmService.create_farm(db_session, farm_data)

        response = client.get(f"/api/farms/owner/{user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) >= 2


@pytest.mark.integration
class TestUserPreferencesAPI:
    """Integration tests for User Preferences API endpoints."""

    @pytest.mark.asyncio
    async def test_get_user_preferences_api(
        self, db_session, client: TestClient
    ) -> None:
        """Test GET /api/users/{user_id}/preferences returns preferences."""
        from app.services.user import UserService
        from app.schemas.user import UserCreate

        user_data = UserCreate(
            email=f"prefsget{uuid4().hex[:8]}@example.com",
            full_name="Prefs Get User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        response = client.get(f"/api/users/{user.id}/preferences")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["user_id"] == str(user.id)
        assert "email_notifications_enabled" in data["data"]

    @pytest.mark.asyncio
    async def test_update_user_preferences_api(
        self, db_session, client: TestClient
    ) -> None:
        """Test PUT /api/users/{user_id}/preferences updates preferences."""
        from app.services.user import UserService
        from app.schemas.user import UserCreate

        user_data = UserCreate(
            email=f"prefsupdate{uuid4().hex[:8]}@example.com",
            full_name="Prefs Update User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        update_data = {
            "water_cost_per_liter_usd": 0.0015,
            "water_savings_milestone_liters": 2000,
            "psps_pre_irrigation_hours": 48,
            "email_notifications_enabled": False,
        }

        response = client.put(
            f"/api/users/{user.id}/preferences", json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["water_cost_per_liter_usd"] == 0.0015
        assert data["data"]["water_savings_milestone_liters"] == 2000
        assert data["data"]["psps_pre_irrigation_hours"] == 48
        assert data["data"]["email_notifications_enabled"] is False

