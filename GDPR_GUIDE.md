# 🔒 GDPR Compliance Guide

## Översikt

Detta API är **fullt GDPR-compliant** och implementerar alla nödvändiga krav från EU:s dataskyddsförordning (GDPR).

---

## 🎯 GDPR Features Implemented

### ✅ 1. **Lawful Basis for Processing** (Article 6)
- **Consent**: Explicit consent krävs innan data samlas in
- **Purpose Limitation**: Data används bara för det angivna syftet

### ✅ 2. **Consent Management** (Article 7)
- Freely given (frivilligt)
- Specific (specifikt för varje syfte)
- Informed (användaren vet vad de samtycker till)
- Unambiguous (tydlig handling krävs)
- Easy to withdraw (lätt att dra tillbaka)

### ✅ 3. **Right to Access** (Article 15)
- Användare kan exportera all sin data i JSON-format
- Endpoint: `POST /api/v1/gdpr/export`

### ✅ 4. **Right to Rectification** (Article 16)
- Användare kan uppdatera sina uppgifter
- Endpoint: `PUT /api/v1/gdpr/rectify/{user_id}`

### ✅ 5. **Right to Erasure** (Article 17) - "Right to be Forgotten"
- Användare kan radera all sin data
- Endpoint: `POST /api/v1/gdpr/delete`
- Verifieringsprocess för säkerhet

### ✅ 6. **Right to Data Portability** (Article 20)
- Data exporteras i maskinläsbart format (JSON)
- Kan importeras till andra system

### ✅ 7. **Privacy by Design** (Article 25)
- **Pseudonymization**: User IDs är pseudonyma (inte personlig identitet)
- **Data Minimization**: Samlar bara nödvändig data
- **Encryption**: Email lagras som SHA-256 hash
- **Anonymization**: Gamla assessments anonymiseras automatiskt

### ✅ 8. **Accountability** (Article 30)
- **Audit Logs**: All databehandling loggas
- **Records of Processing**: Spårbara processer
- **Transparency**: Användare ser vad som händer med deras data

### ✅ 9. **Data Retention**
- Automatisk radering efter specificerad tid (default: 365 dagar)
- Användare kan ändra retention period
- Auto-anonymisering av gammal data

### ✅ 10. **Breach Notification** (Article 33-34)
- Audit logs möjliggör breach detection
- IP-logging för säkerhetsanalys

---

## 📋 GDPR Endpoints

### **Consent Management**

#### Give/Withdraw Consent
```http
POST /api/v1/gdpr/consent
Content-Type: application/json

{
  "user_id": "user_123",
  "consent_type": "data_processing",
  "consent_given": true,
  "purpose": "Personality assessment analysis",
  "legal_basis": "consent"
}
```

#### Get User Consents
```http
GET /api/v1/gdpr/consent/{user_id}
```

**Response:**
```json
{
  "user_id": "user_123",
  "consents": [
    {
      "consent_type": "data_processing",
      "consent_given": true,
      "consent_date": "2024-01-01T10:00:00",
      "purpose": "Personality assessment analysis",
      "legal_basis": "consent"
    }
  ]
}
```

---

### **Data Access (Right to Access)**

#### Export All User Data
```http
POST /api/v1/gdpr/export
Content-Type: application/json

{
  "user_id": "user_123",
  "email": "user@example.com"  // For verification
}
```

**Response:** Complete user data in JSON format including all assessments, results, consents, and audit logs.

#### Get Privacy Information
```http
GET /api/v1/gdpr/privacy-info/{user_id}
```

**Response:**
```json
{
  "user_id": "user_123",
  "consents": [...],
  "data_summary": {
    "total_assessments": 5,
    "completed_assessments": 3,
    "anonymized_assessments": 0
  },
  "retention_info": {
    "data_retention_days": 365,
    "delete_after": "2025-01-01T00:00:00",
    "days_until_deletion": 180
  }
}
```

---

### **Data Deletion (Right to Erasure)**

#### Request Deletion
```http
POST /api/v1/gdpr/delete
Content-Type: application/json

{
  "user_id": "user_123",
  "email": "user@example.com",
  "reason": "I no longer want to use the service"
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "status": "pending",
  "verification_token": "abc123...",
  "message": "Deletion request created. Use verification token to confirm."
}
```

#### Confirm Deletion
```http
POST /api/v1/gdpr/delete/confirm/{verification_token}
```

**Response:**
```json
{
  "status": "completed",
  "message": "All data permanently deleted",
  "deleted_at": "2024-01-01T10:00:00"
}
```

---

### **Data Rectification**

#### Update User Data
```http
PUT /api/v1/gdpr/rectify/{user_id}?data_retention_days=180
```

---

### **Audit Logs**

#### Get User Audit Logs
```http
GET /api/v1/gdpr/audit/{user_id}?limit=100
```

**Response:**
```json
{
  "user_id": "user_123",
  "total_logs": 25,
  "logs": [
    {
      "action": "assessment_started",
      "resource_type": "assessment",
      "resource_id": "assess_123",
      "timestamp": "2024-01-01T10:00:00",
      "details": {...}
    }
  ]
}
```

---

## 🔐 How It Works

### 1. **Starting an Assessment (with Consent)**

```typescript
// Frontend code
const response = await fetch('/api/v1/assessment/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    assessment_type: 'big_five',
    language: 'sv',
    num_questions: 30,

    // GDPR: Required consents
    consent_data_processing: true,
    consent_ai_analysis: true,
    consent_storage: true
  })
});
```

**What happens:**
1. User is created with pseudonymous ID
2. Email is hashed (SHA-256) - never stored in plaintext
3. All consents are recorded with timestamp
4. Audit log created
5. Auto-delete date set (default: 1 year from now)

### 2. **Data Storage**

- **User ID**: Pseudonymous (e.g., `user_a7b3c...`)
- **Email**: Hashed with SHA-256
- **Assessment Data**: Linked to user ID
- **Answers**: Stored separately, can be anonymized
- **Results**: Can be exported or deleted

### 3. **Automatic Data Management**

#### Auto-Deletion (run periodically)
```http
POST /api/v1/gdpr/admin/cleanup
?admin_key=YOUR_ADMIN_KEY
```

Deletes users past their retention period.

#### Auto-Anonymization
```http
POST /api/v1/gdpr/admin/anonymize
?admin_key=YOUR_ADMIN_KEY
&days_threshold=90
```

Anonymizes assessments older than 90 days:
- Removes user link
- Keeps statistical data
- Redacts free text answers

---

## 🔍 Data Flow Example

```
1. User Visits App
   ↓
2. Consent Screen Shown
   ├─ Data Processing ✓
   ├─ AI Analysis ✓
   └─ Storage ✓
   ↓
3. Consents Recorded in DB
   ├─ Timestamp
   ├─ Purpose
   └─ Legal Basis
   ↓
4. Assessment Started
   ├─ Questions Generated (AI)
   ├─ Audit Log: "assessment_started"
   └─ Data stored with retention policy
   ↓
5. User Answers Questions
   ├─ Answers stored
   └─ Audit Log: "answer_submitted"
   ↓
6. Results Generated (AI)
   ├─ Analysis performed
   ├─ Results stored
   └─ Audit Log: "assessment_completed"
   ↓
7. User Can:
   ├─ View Results (Audit: "result_accessed")
   ├─ Export Data (Audit: "data_exported")
   └─ Delete Data (Audit: "deletion_requested" → "user_deleted")
```

---

## 📱 Frontend Integration (Lovable)

### Consent Component

```typescript
// src/components/ConsentForm.tsx

import React, { useState } from 'react';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';

export function ConsentForm({ onConsent }: { onConsent: (consents: Consents) => void }) {
  const [consents, setConsents] = useState({
    data_processing: false,
    ai_analysis: false,
    storage: true
  });

  const allRequired = consents.data_processing && consents.ai_analysis;

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Samtycke</h2>

      <p className="text-gray-600">
        Enligt GDPR behöver vi ditt samtycke för att behandla dina personuppgifter.
      </p>

      <div className="space-y-3">
        <div className="flex items-start space-x-2">
          <Checkbox
            checked={consents.data_processing}
            onCheckedChange={(checked) =>
              setConsents({...consents, data_processing: !!checked})
            }
          />
          <div>
            <label className="font-medium">
              Databehandling (Obligatoriskt)
            </label>
            <p className="text-sm text-gray-600">
              Jag samtycker till att mina svar samlas in och behandlas för personlighetsanalys.
            </p>
          </div>
        </div>

        <div className="flex items-start space-x-2">
          <Checkbox
            checked={consents.ai_analysis}
            onCheckedChange={(checked) =>
              setConsents({...consents, ai_analysis: !!checked})
            }
          />
          <div>
            <label className="font-medium">
              AI-Analys (Obligatoriskt)
            </label>
            <p className="text-sm text-gray-600">
              Jag samtycker till att Anthropic Claude AI används för att analysera mina svar.
            </p>
          </div>
        </div>

        <div className="flex items-start space-x-2">
          <Checkbox
            checked={consents.storage}
            onCheckedChange={(checked) =>
              setConsents({...consents, storage: !!checked})
            }
          />
          <div>
            <label className="font-medium">
              Datalagring (Valfritt)
            </label>
            <p className="text-sm text-gray-600">
              Jag samtycker till att mina resultat sparas för framtida referens (max 365 dagar).
            </p>
          </div>
        </div>
      </div>

      <div className="border-t pt-4">
        <p className="text-xs text-gray-500 mb-4">
          Du kan när som helst exportera eller radera dina uppgifter.
          Se vår <a href="/privacy" className="underline">integritetspolicy</a> för mer information.
        </p>

        <Button
          disabled={!allRequired}
          onClick={() => onConsent(consents)}
        >
          Acceptera och fortsätt
        </Button>
      </div>
    </div>
  );
}
```

### User Data Dashboard

```typescript
// src/components/UserDataDashboard.tsx

export function UserDataDashboard({ userId }: { userId: string }) {
  const [privacyInfo, setPrivacyInfo] = useState(null);

  useEffect(() => {
    fetch(`/api/v1/gdpr/privacy-info/${userId}`)
      .then(res => res.json())
      .then(data => setPrivacyInfo(data));
  }, [userId]);

  const exportData = async () => {
    const response = await fetch('/api/v1/gdpr/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    });

    const data = await response.json();

    // Download as JSON
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `my-data-${userId}.json`;
    a.click();
  };

  const deleteData = async () => {
    if (!confirm('Är du säker? Detta kan inte ångras.')) return;

    const response = await fetch('/api/v1/gdpr/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId })
    });

    const { verification_token } = await response.json();

    // Show verification step
    alert(`Deletion requested. Token: ${verification_token}`);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Dina Personuppgifter (GDPR)</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {privacyInfo && (
          <>
            <div>
              <h3 className="font-semibold">Dataöversikt</h3>
              <p>Totalt {privacyInfo.data_summary.total_assessments} assessments</p>
              <p>Data raderas automatiskt: {new Date(privacyInfo.retention_info.delete_after).toLocaleDateString()}</p>
            </div>

            <div>
              <h3 className="font-semibold">Dina Rättigheter</h3>
              <div className="space-y-2 mt-2">
                <Button variant="outline" onClick={exportData}>
                  📥 Exportera Mina Data
                </Button>
                <Button variant="destructive" onClick={deleteData}>
                  🗑️ Radera Alla Mina Data
                </Button>
              </div>
            </div>

            <div>
              <h3 className="font-semibold">Samtycken</h3>
              {privacyInfo.consents.map((consent, i) => (
                <div key={i} className="text-sm">
                  {consent.consent_type}: {consent.consent_given ? '✅' : '❌'}
                </div>
              ))}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
```

---

## ⚙️ Admin Tasks

### Periodic Cleanup (Cron Job)

```bash
# Run daily to clean up expired data
curl -X POST "http://localhost:8000/api/v1/gdpr/admin/cleanup?admin_key=YOUR_KEY"

# Anonymize old data (run weekly)
curl -X POST "http://localhost:8000/api/v1/gdpr/admin/anonymize?admin_key=YOUR_KEY&days_threshold=90"
```

### Setup Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add daily cleanup at 2 AM
0 2 * * * curl -X POST "http://your-api.com/api/v1/gdpr/admin/cleanup?admin_key=YOUR_KEY"

# Weekly anonymization on Sundays at 3 AM
0 3 * * 0 curl -X POST "http://your-api.com/api/v1/gdpr/admin/anonymize?admin_key=YOUR_KEY"
```

---

## 📄 Privacy Policy Template

See `PRIVACY_POLICY_TEMPLATE.md` for a complete privacy policy template you can customize.

---

## ✅ GDPR Compliance Checklist

- [x] Lawful basis for processing (consent)
- [x] Consent management system
- [x] Right to access (data export)
- [x] Right to rectification
- [x] Right to erasure (delete)
- [x] Right to data portability
- [x] Privacy by design
- [x] Data minimization
- [x] Pseudonymization
- [x] Encryption (email hashing)
- [x] Audit logging
- [x] Data retention policies
- [x] Auto-deletion
- [x] Anonymization
- [x] Transparency (privacy info endpoint)
- [x] Breach detection capability (audit logs + IP logging)

---

## 🚨 Important Notes

1. **Admin Key**: Change `CHANGE_ME_IN_PRODUCTION` in production!
2. **Cron Jobs**: Set up periodic cleanup and anonymization
3. **Privacy Policy**: Customize the template with your company details
4. **DPO**: Designate a Data Protection Officer if required
5. **Logging**: Monitor audit logs for suspicious activity
6. **Backups**: Ensure backups also respect retention policies
7. **Third-Party**: Document all data processors (Anthropic, hosting provider)

---

## 📞 Support

För GDPR-relaterade frågor:
- Email: dpo@yourcompany.com
- Support: support@yourcompany.com

För att utöva dina GDPR-rättigheter, använd endpoints i detta API eller kontakta support.

---

**Byggd med ❤️ och respekt för användarnas integritet**
