# 🚀 Production Deployment Guide - Persona Assessment Service

Complete guide för att sätta upp Persona som en produktionsklar tjänst på Vercel.

---

## 📋 Pre-Deployment Checklist

- [ ] Anthropic API-nyckel (https://console.anthropic.com)
- [ ] Vercel account (https://vercel.com)
- [ ] Sentry account (https://sentry.io) - För monitoring
- [ ] Vercel Postgres Database - För persistent storage
- [ ] (Valfritt) AWS S3 - För backups

---

## 🗄️ Step 1: Sätt upp Vercel Postgres Database

### 1.1 Skapa databas

1. Gå till ditt Vercel-projekt
2. Klicka på **Storage** tab
3. Klicka **Create Database**
4. Välj **Postgres**
5. Välj region (välj närmaste dina användare, t.ex. Stockholm)
6. Klicka **Create**

### 1.2 Koppla database till projekt

Vercel lägger automatiskt till environment variables:
```
POSTGRES_URL
POSTGRES_PRISMA_URL
POSTGRES_URL_NON_POOLING
```

Din app använder automatiskt `DATABASE_URL` (som Vercel sätter från `POSTGRES_URL`).

### 1.3 Verifiera database

Efter deployment, kör:
```bash
# Från Vercel CLI
vercel env pull .env.local
python database.py  # Skapar tabeller
```

---

## 🔐 Step 2: Sätt upp Environment Variables

Gå till **Project Settings → Environment Variables** i Vercel.

### Obligatoriska variabler:

```bash
# Claude AI API (KRITISKT)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Admin Password (BYT DETTA!)
# Generera: echo -n "ditt_lösenord" | sha256sum
ADMIN_PASSWORD_HASH=<din_sha256_hash>

# Environment
ENVIRONMENT=production
```

### Monitoring (Rekommenderat):

```bash
# Sentry Error Tracking
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx

# Vercel sätter automatiskt:
VERCEL_GIT_COMMIT_SHA=<commit_hash>
```

### Backup (Valfritt):

```bash
# AWS S3 för automated backups
AWS_ACCESS_KEY_ID=<aws_key>
AWS_SECRET_ACCESS_KEY=<aws_secret>
AWS_REGION=eu-north-1
BACKUP_S3_BUCKET=persona-backups
```

---

## 📊 Step 3: Sätt upp Sentry Monitoring

### 3.1 Skapa Sentry-projekt

1. Gå till https://sentry.io
2. Skapa nytt projekt
3. Välj **FastAPI** som plattform
4. Kopiera DSN-nyckeln

### 3.2 Lägg till i Vercel

```bash
SENTRY_DSN=https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
```

### 3.3 Verifiera

Efter deployment:
1. Besök `/api/v1/health`
2. Gå till Sentry dashboard
3. Se att errors loggas

---

## 🔒 Step 4: Säkerhetskonfiguration

### 4.1 Byt Admin-lösenord

**KRITISKT: Byt från standard "admin123"!**

Generera nytt lösenord:
```bash
# På din dator
echo -n "ditt_starka_lösenord_123!" | sha256sum
```

Kopiera hash och lägg till i Vercel:
```
ADMIN_PASSWORD_HASH=<din_genererade_hash>
```

### 4.2 Rate Limiting

✅ Redan konfigurerat!

Limits:
- Admin login: 5 försök / 5 min
- Chat: 20 meddelanden / minut
- Assessment start: 10 tester / timme
- Default: 100 requests / minut

För att ändra, uppdatera `monitoring.py`.

### 4.3 CORS (om du har custom domain)

Uppdatera i `api_main_gdpr.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Specifik domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 💾 Step 5: Automated Backups

### 5.1 Lokala backups (basic)

Lägg till i Vercel Cron (vercel.json):
```json
{
  "crons": [
    {
      "path": "/api/admin/backup",
      "schedule": "0 2 * * *"
    }
  ]
}
```

### 5.2 S3 Cloud Backups (rekommenderat)

1. Skapa S3 bucket på AWS
2. Skapa IAM user med S3 write permissions
3. Lägg till credentials i Vercel env vars
4. Backups körs automatiskt dagligen kl 02:00 UTC

Manuell backup:
```bash
python backup.py
```

### 5.3 Backup retention

Standard: 30 dagar

Ändra i `backup.py`:
```python
manager.cleanup_old_backups(keep_days=90)  # 90 dagar
```

---

## 📈 Step 6: Deploy till Production

### 6.1 Git Push

```bash
git add .
git commit -m "Production-ready deployment"
git push origin main
```

### 6.2 Vercel Auto-Deploy

Vercel deployer automatiskt från `main` branch.

Verifiera deployment:
1. Se deployment logs i Vercel dashboard
2. Besök `https://your-project.vercel.app/api/v1/health`
3. Testa admin-panelen: `https://your-project.vercel.app/admin`

### 6.3 Custom Domain (valfritt)

1. Gå till **Project Settings → Domains**
2. Lägg till din domain
3. Följ DNS-instruktionerna
4. Vercel aktiverar automatiskt SSL/HTTPS

---

## ✅ Step 7: Post-Deployment Verification

### 7.1 Health Checks

```bash
# API Health
curl https://your-domain.vercel.app/api/v1/health

# Admin Health
curl https://your-domain.vercel.app/api/admin/health \
  -H "Authorization: Bearer <token>"
```

### 7.2 Test Assessment Flow

1. Gå till `https://your-domain.vercel.app`
2. Starta nytt test
3. Fyll i samtycken
4. Genomför testet
5. Verifiera resultat och AI-rapport
6. Testa chat-funktionen

### 7.3 Test Admin Panel

1. Gå till `https://your-domain.vercel.app/admin`
2. Logga in med ditt nya lösenord
3. Verifiera dashboard-statistik
4. Testa exportera användardata
5. Verifiera att Sentry loggar events

---

## 🔧 Step 8: Ongoing Maintenance

### Dagliga uppgifter
- ✅ Automatiska backups (S3)
- ✅ Rate limiting aktiv
- ✅ Error tracking (Sentry)

### Veckovisa uppgifter
- [ ] Kontrollera Sentry för errors
- [ ] Granska API usage logs
- [ ] Verifiera backup status

### Månatliga uppgifter
- [ ] Granska användningsstatistik
- [ ] Uppdatera dependencies (`pip list --outdated`)
- [ ] Testa backup restore procedure
- [ ] Granska GDPR compliance (data retention)

### Auto-cleanup (redan konfigurerat)
- Expired user data: Auto-delete efter 365 dagar
- Old assessments: Anonymisering efter 90 dagar
- Backups: Auto-delete efter 30 dagar

---

## 📊 Monitoring Dashboard

### Sentry (Errors & Performance)
- URL: https://sentry.io/organizations/your-org/projects/
- Se errors, stack traces, user context
- Performance monitoring (10% sampling)

### Vercel Analytics
- URL: https://vercel.com/your-project/analytics
- Se requests, latency, status codes
- Bandwidth usage

### Admin Panel
- URL: https://your-domain.vercel.app/admin
- Real-time statistik
- User management
- GDPR tools

---

## 🚨 Troubleshooting

### Problem: Database connection error

**Lösning:**
```bash
# Verifiera DATABASE_URL är satt
vercel env ls

# Test connection
python -c "from database import db; db.create_tables(); print('OK')"
```

### Problem: Chat returnerar fallback-svar

**Lösning:**
- Verifiera `ANTHROPIC_API_KEY` är korrekt satt
- Kolla Sentry för API errors
- Verifiera API quota: https://console.anthropic.com

### Problem: Admin login fungerar inte

**Lösning:**
- Verifiera `ADMIN_PASSWORD_HASH` är korrekt
- Testa hash lokalt:
  ```bash
  echo -n "ditt_lösenord" | sha256sum
  ```
- Kolla browser console för errors

### Problem: Rate limit triggad

**Lösning:**
- Vänta 5 minuter (för login)
- Eller uppdatera limits i `monitoring.py`

---

## 🎯 Performance Optimization

### Database Indexing

Lägg till index för snabbare queries:
```sql
CREATE INDEX idx_user_last_active ON users(last_active);
CREATE INDEX idx_assessment_completed ON assessments(completed_at);
CREATE INDEX idx_assessment_user ON assessments(user_id);
```

### Caching (future)

För high-traffic scenarios:
- Implementera Redis för session storage
- Cache AI-genererade rapporter (samma profil)
- CDN för statiska assets

---

## 📜 GDPR Compliance Checklist

- [x] **Data Minimization**: Samlar bara nödvändig data
- [x] **Consent Management**: Explicit consent tracking
- [x] **Right to Access**: Export user data via `/api/admin/users/{id}/export`
- [x] **Right to Erasure**: Delete user data via `/api/admin/users/{id}` (DELETE)
- [x] **Data Retention**: Auto-delete after 365 days
- [x] **Anonymization**: Old assessments anonymized after 90 days
- [x] **Audit Logging**: All GDPR actions logged
- [x] **Breach Notification**: Sentry alerts för security issues

---

## 🔗 Useful Links

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Sentry Dashboard**: https://sentry.io
- **Anthropic Console**: https://console.anthropic.com
- **Admin Panel**: https://your-domain.vercel.app/admin
- **API Docs**: https://your-domain.vercel.app/docs (om aktiverat)

---

## 🆘 Support & Updates

### Get Help
- GitHub Issues: https://github.com/your-repo/issues
- Vercel Support: https://vercel.com/support
- Sentry Support: https://sentry.io/support

### Stay Updated
- Watch repository for updates
- Follow Vercel blog for platform updates
- Monitor Anthropic API changelog

---

**🎉 Grattis! Din Persona Assessment Service är nu produktionsklar!**

För frågor eller support, kontakta admin@your-domain.com

---

*Senast uppdaterad: 2026-03-07*
*Version: 3.0.0*
