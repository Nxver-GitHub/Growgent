# User Profile System Implementation

## Overview

A comprehensive user profile system has been implemented to store user information, farm data, and preferences that agents use for decision-making. This system enables personalized agent behavior based on user settings.

## Components Created

### 1. Database Models

#### User Model (`app/models/user.py`)
- **Fields**: email, full_name, phone, role, is_active, is_verified, notes
- **Relationships**: One-to-many with Farm, One-to-one with UserPreferences
- **Purpose**: Stores user account information

#### Farm Model (`app/models/farm.py`)
- **Fields**: name, farm_id (legacy string), location_geom (PostGIS), address, city, state, zip_code, country, contact_email, contact_phone, notes
- **Relationships**: Many-to-one with User (owner), One-to-many with Field
- **Purpose**: Represents farms owned by users with location and contact information

#### UserPreferences Model (`app/models/user_preferences.py`)
- **Notification Preferences**: email_notifications_enabled, sms_notifications_enabled, push_notifications_enabled
- **Alert Preferences**: alert_severity_minimum, psps_alerts_enabled, water_milestone_alerts_enabled, fire_risk_alerts_enabled
- **Irrigation Preferences**: water_cost_per_liter_usd, typical_irrigation_schedule, irrigation_automation_enabled
- **Water Efficiency Preferences**: water_savings_milestone_liters, efficiency_goal_percent
- **PSPS Preferences**: psps_pre_irrigation_hours, psps_auto_pre_irrigate
- **Locale**: timezone, locale
- **Purpose**: Stores user-specific settings that agents use for decision-making

#### Field Model Updates (`app/models/field.py`)
- Added `farm_uuid` foreign key to Farm model (optional, for backward compatibility)
- Kept `farm_id` string field for legacy support
- Added relationship to Farm model

### 2. Pydantic Schemas

- **User Schemas** (`app/schemas/user.py`): UserCreate, UserUpdate, UserResponse, UserProfileResponse
- **Farm Schemas** (`app/schemas/farm.py`): FarmCreate, FarmUpdate, FarmResponse
- **UserPreferences Schemas** (`app/schemas/user_preferences.py`): UserPreferencesCreate, UserPreferencesUpdate, UserPreferencesResponse

### 3. Services

#### UserService (`app/services/user.py`)
- `create_user()`: Create user with default preferences
- `get_user()`: Get user by ID
- `get_user_by_email()`: Get user by email
- `update_user()`: Update user information
- `list_users()`: List users with filtering
- `get_user_preferences()`: Get user preferences

#### FarmService (`app/services/farm.py`)
- `create_farm()`: Create farm with location geometry
- `get_farm()`: Get farm by UUID
- `get_farm_by_farm_id()`: Get farm by legacy farm_id string
- `update_farm()`: Update farm information
- `list_farms_by_owner()`: List farms owned by a user
- `get_farm_with_field_count()`: Get farm with field count

### 4. API Endpoints

#### User Endpoints (`/api/users`)
- `POST /api/users` - Create user
- `GET /api/users/{user_id}` - Get user by ID
- `GET /api/users/email/{email}` - Get user by email
- `PUT /api/users/{user_id}` - Update user
- `GET /api/users` - List users

#### Farm Endpoints (`/api/farms`)
- `POST /api/farms` - Create farm
- `GET /api/farms/{farm_id}` - Get farm by UUID
- `GET /api/farms/farm-id/{farm_id_str}` - Get farm by legacy farm_id
- `PUT /api/farms/{farm_id}` - Update farm
- `GET /api/farms/owner/{owner_id}` - List farms by owner

#### User Preferences Endpoints (`/api/users/{user_id}/preferences`)
- `POST /api/users/{user_id}/preferences` - Create preferences
- `GET /api/users/{user_id}/preferences` - Get preferences
- `PUT /api/users/{user_id}/preferences` - Update preferences

## How Agents Use User Profile Data

### Water Efficiency Agent
- Uses `water_cost_per_liter_usd` from UserPreferences for cost savings calculations
- Uses `water_savings_milestone_liters` to determine when to send milestone alerts
- Uses `water_milestone_alerts_enabled` to check if alerts should be sent

### PSPS Anticipation Agent
- Uses `psps_alerts_enabled` to check if PSPS alerts should be generated
- Uses `psps_pre_irrigation_hours` to determine when to recommend pre-irrigation
- Uses `psps_auto_pre_irrigate` to determine if pre-irrigation should be automatic
- Uses Farm location (`location_geom`) to match PSPS events to farms

### Alert Orchestration
- Uses `alert_severity_minimum` to filter alerts by severity
- Uses notification preferences (`email_notifications_enabled`, `sms_notifications_enabled`, `push_notifications_enabled`) to determine delivery channels
- Uses alert type preferences (`psps_alerts_enabled`, `water_milestone_alerts_enabled`, `fire_risk_alerts_enabled`) to filter alerts

### Fire-Adaptive Irrigation Agent
- Can use `typical_irrigation_schedule` from UserPreferences for baseline comparison
- Can use `irrigation_automation_enabled` to determine if recommendations should be auto-applied
- Uses Farm location for spatial queries

## Database Migration

The new tables will be automatically created when the application starts via `init_db()` in `app/database.py`. The `Base.metadata.create_all()` call will create:
- `users` table
- `farms` table
- `user_preferences` table
- Updated `fields` table with `farm_uuid` column

## Example Usage

### Creating a User Profile

```python
# 1. Create user
POST /api/users
{
  "email": "farmer@example.com",
  "full_name": "John Doe",
  "phone": "+1-555-123-4567",
  "role": "owner"
}

# 2. Create farm
POST /api/farms
{
  "owner_id": "<user_id>",
  "name": "Sunny Dale Farm",
  "farm_id": "farm-001",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "address": "123 Farm Road",
  "city": "Fresno",
  "state": "CA",
  "zip_code": "93710"
}

# 3. Update preferences (optional - defaults are created automatically)
PUT /api/users/{user_id}/preferences
{
  "water_cost_per_liter_usd": 0.0015,
  "water_savings_milestone_liters": 2000,
  "psps_pre_irrigation_hours": 48,
  "alert_severity_minimum": "WARNING"
}
```

## Next Steps

1. **Update Agents**: Modify agents to fetch and use UserPreferences when making decisions
2. **Update MetricsService**: Use `water_cost_per_liter_usd` from UserPreferences instead of hardcoded value
3. **Add Tests**: Create integration tests for user/farm/preferences CRUD operations
4. **Frontend Integration**: Connect frontend Settings component to these API endpoints
5. **Authentication**: Add authentication/authorization middleware to protect user endpoints

## Notes

- The `farm_id` string field is kept for backward compatibility with existing code
- The `farm_uuid` foreign key is optional to allow gradual migration
- User preferences are automatically created with sensible defaults when a user is created
- All models include timestamps (`created_at`, `updated_at`) for audit trails

