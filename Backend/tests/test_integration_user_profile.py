"""
Integration tests for User and Farm services.

Tests user creation, farm management, and user preferences.
"""

import pytest
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.user import UserService
from app.services.farm import FarmService
from app.models.user import User, UserRole
from app.models.farm import Farm
from app.models.user_preferences import UserPreferences
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.farm import FarmCreate, FarmUpdate


@pytest.mark.integration
class TestUserServiceIntegration:
    """Integration tests for UserService."""

    @pytest.mark.asyncio
    async def test_create_user_with_default_preferences(
        self, db_session: AsyncSession
    ) -> None:
        """Test creating a user automatically creates default preferences."""
        user_data = UserCreate(
            email="test@example.com",
            full_name="Test User",
            phone="+1-555-123-4567",
            role=UserRole.OWNER,
        )

        user = await UserService.create_user(db_session, user_data)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.role == UserRole.OWNER
        assert user.is_active is True
        assert user.is_verified is False

        # Check that preferences were created
        preferences = await UserService.get_user_preferences(db_session, user.id)
        assert preferences is not None
        assert preferences.user_id == user.id
        assert preferences.email_notifications_enabled is True
        assert preferences.psps_alerts_enabled is True

    @pytest.mark.asyncio
    async def test_get_user_by_email(
        self, db_session: AsyncSession
    ) -> None:
        """Test getting user by email."""
        user_data = UserCreate(
            email="getbyemail@example.com",
            full_name="Get By Email User",
            role=UserRole.OWNER,
        )
        created_user = await UserService.create_user(db_session, user_data)

        user = await UserService.get_user_by_email(
            db_session, "getbyemail@example.com"
        )

        assert user is not None
        assert user.id == created_user.id
        assert user.email == "getbyemail@example.com"

    @pytest.mark.asyncio
    async def test_update_user(
        self, db_session: AsyncSession
    ) -> None:
        """Test updating user information."""
        user_data = UserCreate(
            email="update@example.com",
            full_name="Update User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        update_data = UserUpdate(
            full_name="Updated Name",
            phone="+1-555-999-9999",
            is_verified=True,
        )

        updated_user = await UserService.update_user(
            db_session, user.id, update_data
        )

        assert updated_user is not None
        assert updated_user.full_name == "Updated Name"
        assert updated_user.phone == "+1-555-999-9999"
        assert updated_user.is_verified is True

    @pytest.mark.asyncio
    async def test_list_users(
        self, db_session: AsyncSession
    ) -> None:
        """Test listing users with filtering."""
        # Create multiple users
        for i in range(3):
            user_data = UserCreate(
                email=f"listuser{i}@example.com",
                full_name=f"List User {i}",
                role=UserRole.OWNER,
            )
            await UserService.create_user(db_session, user_data)

        users = await UserService.list_users(db_session, skip=0, limit=10)

        assert len(users) >= 3
        assert all(isinstance(user, User) for user in users)

    @pytest.mark.asyncio
    async def test_get_user_preferences(
        self, db_session: AsyncSession
    ) -> None:
        """Test getting user preferences."""
        user_data = UserCreate(
            email="prefs@example.com",
            full_name="Prefs User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        preferences = await UserService.get_user_preferences(db_session, user.id)

        assert preferences is not None
        assert preferences.user_id == user.id


@pytest.mark.integration
class TestFarmServiceIntegration:
    """Integration tests for FarmService."""

    @pytest.mark.asyncio
    async def test_create_farm(
        self, db_session: AsyncSession
    ) -> None:
        """Test creating a farm."""
        # Create user first
        user_data = UserCreate(
            email="farmowner@example.com",
            full_name="Farm Owner",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        farm_data = FarmCreate(
            owner_id=user.id,
            name="Test Farm",
            farm_id="test-farm-001",
            address="123 Farm Road",
            city="Fresno",
            state="CA",
            zip_code="93710",
            latitude=36.7378,
            longitude=-119.7871,
        )

        farm = await FarmService.create_farm(db_session, farm_data)

        assert farm.id is not None
        assert farm.name == "Test Farm"
        assert farm.farm_id == "test-farm-001"
        assert farm.owner_id == user.id
        assert farm.location_geom is not None

    @pytest.mark.asyncio
    async def test_get_farm_by_farm_id(
        self, db_session: AsyncSession
    ) -> None:
        """Test getting farm by legacy farm_id string."""
        user_data = UserCreate(
            email="farmget@example.com",
            full_name="Farm Get User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        farm_data = FarmCreate(
            owner_id=user.id,
            name="Get Farm",
            farm_id="get-farm-001",
        )
        created_farm = await FarmService.create_farm(db_session, farm_data)

        farm = await FarmService.get_farm_by_farm_id(
            db_session, "get-farm-001"
        )

        assert farm is not None
        assert farm.id == created_farm.id
        assert farm.farm_id == "get-farm-001"

    @pytest.mark.asyncio
    async def test_update_farm(
        self, db_session: AsyncSession
    ) -> None:
        """Test updating farm information."""
        user_data = UserCreate(
            email="farmupdate@example.com",
            full_name="Farm Update User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        farm_data = FarmCreate(
            owner_id=user.id,
            name="Update Farm",
            farm_id="update-farm-001",
        )
        farm = await FarmService.create_farm(db_session, farm_data)

        update_data = FarmUpdate(
            name="Updated Farm Name",
            city="Sacramento",
            state="CA",
        )

        updated_farm = await FarmService.update_farm(
            db_session, farm.id, update_data
        )

        assert updated_farm is not None
        assert updated_farm.name == "Updated Farm Name"
        assert updated_farm.city == "Sacramento"
        assert updated_farm.state == "CA"

    @pytest.mark.asyncio
    async def test_list_farms_by_owner(
        self, db_session: AsyncSession
    ) -> None:
        """Test listing farms owned by a user."""
        user_data = UserCreate(
            email="farmlist@example.com",
            full_name="Farm List User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        # Create multiple farms
        for i in range(2):
            farm_data = FarmCreate(
                owner_id=user.id,
                name=f"Farm {i}",
                farm_id=f"list-farm-{i:03d}",
            )
            await FarmService.create_farm(db_session, farm_data)

        farms = await FarmService.list_farms_by_owner(
            db_session, user.id, skip=0, limit=10
        )

        assert len(farms) >= 2
        assert all(farm.owner_id == user.id for farm in farms)

    @pytest.mark.asyncio
    async def test_get_farm_with_field_count(
        self, db_session: AsyncSession
    ) -> None:
        """Test getting farm with field count."""
        user_data = UserCreate(
            email="farmcount@example.com",
            full_name="Farm Count User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        farm_data = FarmCreate(
            owner_id=user.id,
            name="Count Farm",
            farm_id="count-farm-001",
        )
        farm = await FarmService.create_farm(db_session, farm_data)

        # Create fields for this farm
        from app.models.field import Field
        for i in range(2):
            field = Field(
                farm_id=farm.farm_id,
                farm_uuid=farm.id,
                name=f"Field {i}",
                crop_type="tomato",
                area_hectares=10.0,
            )
            db_session.add(field)
        await db_session.commit()

        result = await FarmService.get_farm_with_field_count(
            db_session, farm.id
        )

        assert result is not None
        assert result["fields_count"] == 2

