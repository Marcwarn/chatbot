# 🚀 Vercel Deployment Guide - Chatbot Persona

## Snabbstart (Rekommenderat)

### Via Vercel Dashboard (Enklast)

1. **Gå till:** https://vercel.com/new
2. **Import:** Välj `Marcwarn/chatbot` från GitHub
3. **Konfigurera Environment Variables:**
   ```
   ANTHROPIC_API_KEY = sk-ant-...
   VERCEL_TOKEN = din-vercel-token
   DATABASE_URL = postgresql://... (om du har)
   ALLOWED_ORIGINS = https://ditt-projekt.vercel.app
   ```
4. **Klicka Deploy** 🚀

---

## Via CLI (Mer Kontroll)

### 1. Logga in
```bash
vercel login
```

### 2. Länka projektet
```bash
cd /home/user/chatbot
vercel link
```
Välj:
- Scope: Ditt Vercel team/konto
- Link to existing project: Ja (om det finns) eller Nej (skapa nytt)
- Project name: `chatbot` eller vad du vill

### 3. Sätt Environment Variables
```bash
# Anthropic API Key
vercel env add ANTHROPIC_API_KEY

# Vercel Token (för deployment monitoring)
vercel env add VERCEL_TOKEN

# Allowed Origins (uppdatera efter deployment)
vercel env add ALLOWED_ORIGINS
```

För varje variabel:
- **Environment:** Välj `Production`, `Preview`, och `Development` (alla tre)
- **Value:** Klistra in värdet

### 4. Deploya till Preview
```bash
vercel
```

### 5. Deploya till Production
```bash
vercel --prod
```

---

## Eller använd scriptet
```bash
./DEPLOY.sh
```

---

## 🎯 Vad du ska se efter deployment

### Landing Page (`/`)
- Modern gradient hero section
- Big Five och DISC presentation
- Pricing cards (299 kr / 499 kr)
- Security badges
- Gratis provversion sektion

### Admin Panel (`/admin`)
**Login:**
- Admin token required (sätt i environment)

**Dashboard Tab:**
- 📊 Totalt antal assessments
- 📈 Big Five & DISC stats
- 💬 Chat-meddelanden
- 🚀 **Deployment Status** (NYA!)
  - Environment badge
  - Live URL
  - Commit info
  - Branch
  - Vercel connection status

**Användare Tab:**
- Lista alla users
- Export user data (GDPR)
- Delete user data

**Assessments Tab:**
- Alla assessments
- Filter Big Five / DISC
- View detaljer

**Analytics Tab:**
- Genomsnittliga Big Five scores
- DISC profiler
- Tidsserier (30 dagar)

**Konfiguration Tab:**
- API-nyckel status
- Chat aktiverad
- AI-rapporter
- **Vercel Token status** (NYA!)
- **Deployment ID** (NYA!)

---

## 🔧 Efter Första Deployment

### 1. Uppdatera ALLOWED_ORIGINS

Efter deployment får du en URL typ:
```
https://chatbot-abc123.vercel.app
```

Uppdatera då:
```bash
vercel env add ALLOWED_ORIGINS
# Värde: https://chatbot-abc123.vercel.app,https://www.dindomain.se
```

Eller via Dashboard:
1. Project Settings → Environment Variables
2. Uppdatera `ALLOWED_ORIGINS`
3. Redeploy

### 2. Testa Endpoints

```bash
# Health check
curl https://ditt-projekt.vercel.app/api/v1/health

# Deployment info (NYA!)
curl https://ditt-projekt.vercel.app/api/v1/deployment/info

# Deployment status
curl https://ditt-projekt.vercel.app/api/v1/deployment/status
```

### 3. Admin Login

Gå till:
```
https://ditt-projekt.vercel.app/admin
```

Token: Din admin token (sätt ADMIN_PASSWORD env var)

### 4. Testa Assessments

**Big Five:**
```
https://ditt-projekt.vercel.app/big-five-demo.html
```

**DISC:**
```
https://ditt-projekt.vercel.app/disc-assessment.html
```

---

## 📊 Deployment Monitoring

Med `VERCEL_TOKEN` konfigurerad får du:

✅ **Live deployment URL** i admin
✅ **Senaste commit info** i admin
✅ **Environment badge** (Production/Preview)
✅ **Health metrics** via `/api/v1/deployment/health`:
   - Success rate %
   - Genomsnittlig build-tid
   - Failed deployments
   - Warnings/Issues

---

## 🐛 Troubleshooting

### "CORS error när jag testar"
→ Uppdatera `ALLOWED_ORIGINS` med din Vercel URL

### "Chat fungerar inte"
→ Kolla att `ANTHROPIC_API_KEY` är satt i Vercel env vars

### "Database errors"
→ Lägg till `DATABASE_URL` (PostgreSQL) i environment variables

### "Deployment monitoring visar inte data"
→ Kolla att `VERCEL_TOKEN` är satt och giltig

### "Admin login fungerar inte"
→ Sätt `ADMIN_PASSWORD` environment variable

---

## 🎉 Production Checklist

- [ ] Vercel project skapad
- [ ] GitHub repo kopplad
- [ ] Environment variables satta:
  - [ ] `ANTHROPIC_API_KEY`
  - [ ] `VERCEL_TOKEN`
  - [ ] `ALLOWED_ORIGINS`
  - [ ] `DATABASE_URL` (optional)
  - [ ] `ADMIN_PASSWORD`
- [ ] Första deployment lyckad
- [ ] Landing page fungerar (`/`)
- [ ] Admin panel fungerar (`/admin`)
- [ ] Big Five assessment fungerar
- [ ] DISC assessment fungerar
- [ ] Deployment monitoring visar data
- [ ] CORS konfigurerad korrekt
- [ ] Health endpoints svarar

---

## 📝 Vercel Dashboard URLs

- **Project:** https://vercel.com/dashboard
- **Deployments:** https://vercel.com/DITT-TEAM/chatbot/deployments
- **Settings:** https://vercel.com/DITT-TEAM/chatbot/settings
- **Environment Variables:** https://vercel.com/DITT-TEAM/chatbot/settings/environment-variables

---

**Lycka till med deploymentet! 🚀**

Om något inte fungerar - kolla Vercel deployment logs:
https://vercel.com/DITT-TEAM/chatbot/deployments → Välj deployment → Klicka "View Build Logs"
