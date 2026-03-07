# Admin Panel - Quick Start Guide
## DISC Integration Features

### 🚀 Quick Access

**Admin Panel URL:** `http://your-domain/admin.html`

**Login:** Use your admin password configured in `ADMIN_PASSWORD_HASH`

---

## 📊 Dashboard Overview

### New Statistics Cards

1. **Big Five Count** - Total Big Five assessments completed
2. **DISC Count** - Total DISC assessments completed
3. **Most Popular** - Which assessment type is most used

### Score Displays

**Big Five Dimensions:**
- E (Extraversion)
- A (Agreeableness)
- C (Conscientiousness)
- N (Neuroticism)
- O (Openness)

**DISC Dimensions:**
- D (Dominance) - Red
- I (Influence) - Orange
- S (Steadiness) - Green
- C (Conscientiousness) - Blue

**Top DISC Profiles:**
- Shows most common profiles (D, I, S, C, Di, DC, etc.)
- Displays count and percentage

---

## 👥 Users Tab

### Filter Users
Use dropdown to filter by assessment type:
- **All** - Show all users
- **Big Five** - Only users with Big Five assessments
- **DISC** - Only users with DISC assessments

### Table Columns
- **User ID** - Unique identifier
- **Total** - Total assessments across all types
- **Big Five** - Number of Big Five assessments
- **DISC** - Number of DISC assessments
- **Last Type** - Most recent assessment type taken
- **Last Activity** - Last interaction timestamp
- **Chat Profile** - Whether user has chat enabled
- **Actions** - Export/Delete buttons

### Export User Data
Click **Exportera** to download user data as JSON:
```json
{
  "user_id": "user_123",
  "assessments": {
    "big_five": {
      "count": 2,
      "data": [...]
    },
    "disc": {
      "count": 1,
      "data": [...]
    }
  }
}
```

---

## 📝 Assessments Tab

### Filter Assessments
Use dropdown to filter by type:
- **All** - Show all assessments
- **Big Five** - Only Big Five assessments
- **DISC** - Only DISC assessments

### Table Columns
- **Assessment ID** - Unique identifier
- **User ID** - User who completed it
- **Type** - Assessment type (color-coded badge)
  - Blue = Big Five
  - Orange = DISC
- **Completed** - Timestamp
- **Language** - sv/en
- **Actions** - View button

---

## 📈 Analytics Tab (NEW!)

### 1. Big Five vs DISC Comparison
Visual comparison showing percentage split:
```
Big Five: 45%    |    DISC: 55%
```

### 2. User Preferences
- Total users
- Users preferring Big Five
- Users preferring DISC
- Users with both types

### 3. Completion Rates
Success rates for each assessment type:
- Big Five: 95.2%
- DISC: 94.8%

### 4. Last 7 Days Activity
Quick summary of recent assessments:
- Big Five: 12 assessments
- DISC: 15 assessments
- Total: 27

### 5. Time Series Table
Daily breakdown for last 10 days:
```
Date        | Big Five | DISC | Total
2026-03-07  |    2     |  3   |   5
2026-03-06  |    1     |  2   |   3
...
```

---

## 🔌 API Endpoints

### New Analytics Endpoints

#### Get Big Five Stats
```bash
GET /api/admin/stats/big-five
Authorization: Bearer {token}
```

**Response:**
```json
{
  "total": 25,
  "avg_scores": {
    "E": 68.3,
    "A": 65.0,
    "C": 73.3,
    "N": 50.0,
    "O": 72.3
  },
  "score_distribution": {...},
  "completion_rate": 95.0
}
```

#### Get DISC Stats
```bash
GET /api/admin/stats/disc
Authorization: Bearer {token}
```

**Response:**
```json
{
  "total": 30,
  "avg_scores": {
    "D": 55.0,
    "I": 56.2,
    "S": 50.0,
    "C": 55.0
  },
  "profile_distribution": {
    "D": 8,
    "I": 6,
    "Di": 5,
    "S": 4,
    "SC": 3,
    "C": 4
  },
  "dominant_profiles": [
    {"profile": "D", "count": 8, "percentage": 26.7},
    {"profile": "I", "count": 6, "percentage": 20.0}
  ]
}
```

#### Compare Assessment Types
```bash
GET /api/admin/stats/comparison
Authorization: Bearer {token}
```

#### Time Series Data
```bash
GET /api/admin/stats/time-series?days=30
Authorization: Bearer {token}
```

#### User Demographics
```bash
GET /api/admin/stats/users/demographics
Authorization: Bearer {token}
```

#### Conversion Funnel
```bash
GET /api/admin/stats/conversion-funnel
Authorization: Bearer {token}
```

#### Comprehensive Report
```bash
GET /api/admin/analytics/comprehensive
Authorization: Bearer {token}
```

**Response:** Complete analytics report with all data

---

## 🎯 Common Tasks

### Task 1: View DISC Assessment Distribution
1. Go to **Dashboard** tab
2. Scroll to "Genomsnittliga DISC-scores"
3. Check "Top DISC-profiler" section

### Task 2: Find Users by Assessment Type
1. Go to **Users** tab
2. Select filter: "Big Five" or "DISC"
3. View filtered results

### Task 3: Export DISC Data Only
1. Go to **Users** tab
2. Find user with DISC assessments
3. Click **Exportera**
4. JSON will include separate DISC section

### Task 4: Compare Assessment Popularity
1. Go to **Analytics** tab
2. View "Big Five vs DISC Comparison"
3. Check percentages

### Task 5: See Recent Trends
1. Go to **Analytics** tab
2. Scroll to "Tidsserie" table
3. View last 10 days breakdown

---

## 🔍 DISC Profile Types

### Single Profiles
- **D** - Dominance (direct, results-oriented)
- **I** - Influence (enthusiastic, persuasive)
- **S** - Steadiness (stable, patient)
- **C** - Conscientiousness (analytical, precise)

### Combination Profiles
- **Di** - Dominance + Influence
- **DC** - Dominance + Conscientiousness
- **ID** - Influence + Dominance
- **IS** - Influence + Steadiness
- **SC** - Steadiness + Conscientiousness
- **SI** - Steadiness + Influence

**Detection Logic:**
- If one dimension is 10+ points higher → Single profile
- If two dimensions are close → Combination profile

---

## 🐛 Troubleshooting

### Problem: DISC stats showing 0
**Solution:** No DISC assessments in database yet. Complete at least one DISC assessment.

### Problem: Filters not working
**Solution:** Check that assessments have `assessment_type` field. Older assessments may default to "unknown".

### Problem: Analytics tab empty
**Solution:**
1. Check browser console for errors
2. Verify API endpoints are accessible
3. Ensure admin token is valid

### Problem: 401 Unauthorized
**Solution:** Admin session expired. Refresh page and login again.

### Problem: Charts not updating
**Solution:** Refresh the page or switch tabs to reload data.

---

## 💡 Tips & Best Practices

### Performance
- Analytics data is calculated on-demand
- For large datasets (10k+ assessments), consider caching
- Time series limited to requested days (default 30)

### Security
- Always logout when finished
- Session expires after 15 minutes of inactivity
- All analytics endpoints require authentication

### Data Export
- Export data regularly for backup
- Use comprehensive analytics endpoint for full reports
- Filter exports by type to reduce file size

### Monitoring
- Check "Most Popular" to understand user preferences
- Monitor completion rates to identify issues
- Review time series for usage trends

---

## 📚 Related Documentation

- **ADMIN_DISC_UPDATE.md** - Complete technical documentation
- **ADMIN_CHANGES_SUMMARY.txt** - Summary of all changes
- **test_admin_analytics.py** - Test examples and validation

---

## 🆘 Support

### Run Tests
```bash
python test_admin_analytics.py
```

### Verify Integration
```bash
./verify_admin_disc_integration.sh
```

### Check Logs
Look for errors in browser console (F12) or server logs.

### Common API Errors
- **401** - Authentication required/expired
- **404** - Endpoint not found (check URL)
- **500** - Server error (check logs)

---

**Version:** 1.0
**Last Updated:** 2026-03-07
**Status:** Production Ready ✅
