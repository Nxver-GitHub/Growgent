# Agent User Preferences Integration

## Overview

All agents have been updated to fetch and use UserPreferences when making decisions. This enables personalized agent behavior based on user settings stored in their profile.

## Changes Made

### 1. Helper Function Created

**File**: `Backend/app/agents/user_preferences_helper.py`

Created utility functions to fetch user preferences:
- `get_user_preferences_for_field()` - Gets preferences by traversing Field -> Farm -> User -> Preferences
- `get_user_preferences_for_farm()` - Gets preferences directly from Farm -> User -> Preferences

These functions handle the relationship traversal and gracefully return `None` if preferences don't exist.

### 2. MetricsService Updated

**File**: `Backend/app/services/metrics.py`

- Updated `_calculate_cost_saved()` to accept optional `water_cost_per_liter_usd` parameter
- Updated `calculate_water_saved()` to:
  - Accept optional `water_cost_per_liter_usd` parameter
  - Automatically fetch user's water cost from preferences if not provided
  - Use user's water cost for cost savings calculations

### 3. Water Efficiency Agent Updated

**File**: `Backend/app/agents/water_efficiency.py`

**Changes**:
- Fetches user preferences at the start of processing
- Passes `water_cost_per_liter_usd` from preferences to MetricsService
- Uses `water_milestone_alerts_enabled` to check if milestone alerts should be sent
- Uses `water_savings_milestone_liters` from preferences as the custom milestone threshold
- Falls back to default milestones (1000L, 5000L, 10000L, 25000L) if preferences not set

**Behavior**:
- If `water_milestone_alerts_enabled` is `False`, no milestone alerts are created
- Custom milestone threshold from preferences is used for the first milestone check
- Standard milestones (5K, 10K, 25K) are still checked regardless of custom threshold

### 4. PSPS Anticipation Agent Updated

**File**: `Backend/app/agents/psps.py`

**Changes**:
- Checks `psps_alerts_enabled` before creating alerts
- Uses `psps_pre_irrigation_hours` from preferences instead of hardcoded 36 hours
- Uses `psps_auto_pre_irrigate` flag (stored but not yet implemented in recommendation creation)

**Behavior**:
- If `psps_alerts_enabled` is `False`, PSPS alerts are skipped for that user's fields
- Pre-irrigation recommendations use the user's preferred timing window
- Falls back to default 36 hours if preferences not set

### 5. Fire-Adaptive Irrigation Agent

**Status**: Not updated yet (Agent 1's responsibility)

**Future Integration Points**:
- `typical_irrigation_schedule` - Could be used for baseline comparison
- `irrigation_automation_enabled` - Could determine if recommendations should be auto-applied

## How It Works

### Flow Diagram

```
Agent Process
    ↓
Get Field
    ↓
Get UserPreferences via Helper
    ↓
Use Preferences for Decision-Making
    ↓
Fallback to Defaults if Not Set
```

### Example: Water Efficiency Agent

1. Agent receives `field_id`
2. Calls `get_user_preferences_for_field(db, field_id)`
3. Helper function:
   - Fetches Field with Farm relationship
   - Traverses to Farm.owner
   - Returns User.preferences
4. Agent uses preferences:
   - `water_cost_per_liter_usd` → Passed to MetricsService
   - `water_milestone_alerts_enabled` → Checked before creating alerts
   - `water_savings_milestone_liters` → Used as custom milestone threshold
5. Falls back to defaults if preferences not found

### Example: PSPS Agent

1. Agent finds affected fields
2. For each field, calls `get_user_preferences_for_field(db, field.id)`
3. Checks `psps_alerts_enabled` → Skips alert if disabled
4. Uses `psps_pre_irrigation_hours` → Custom timing window
5. Falls back to defaults if preferences not found

## Benefits

1. **Personalization**: Each user gets agent behavior tailored to their preferences
2. **Flexibility**: Users can customize alert thresholds, timing, and costs
3. **Backward Compatibility**: Defaults ensure agents work even without preferences
4. **Performance**: Preferences are fetched once per field and cached in the agent state
5. **Graceful Degradation**: If preferences don't exist, agents use sensible defaults

## Testing Recommendations

1. **Test with preferences set**: Verify agents use user preferences correctly
2. **Test without preferences**: Verify agents fall back to defaults
3. **Test preference updates**: Verify agents pick up preference changes
4. **Test multiple users**: Verify preferences are correctly isolated per user

## Future Enhancements

1. **Caching**: Cache preferences in memory to reduce database queries
2. **Batch Fetching**: Fetch preferences for multiple fields in one query
3. **Preference Validation**: Ensure preference values are within valid ranges
4. **Preference Change Notifications**: Notify agents when preferences change
5. **Fire-Adaptive Agent Integration**: Add preference support to irrigation agent

