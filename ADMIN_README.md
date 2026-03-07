# 🎛️ Persona Admin Panel

Komplett administrativ miljö för att hantera Persona som en tjänst.

## 🔐 Åtkomst

**URL:** `https://your-domain.vercel.app/admin`

**Standard-lösenord:** `admin123`

⚠️ **VIKTIGT:** Byt lösenord i produktion!

## 🔑 Ändra Admin-lösenord

1. Generera SHA-256 hash av ditt nya lösenord:
   ```bash
   echo -n "ditt_nya_lösenord" | sha256sum
   ```

2. Lägg till hashen i Vercel Environment Variables:
   ```
   Nyckel: ADMIN_PASSWORD_HASH
   Värde: [din_genererade_hash]
   ```

3. Redeploya projektet

## 📊 Funktioner

### Dashboard
- **Totala assessments** - Antal genomförda tester
- **Unika användare** - Registrerade användare
- **Senaste 24h** - Nya assessments senaste dygnet
- **Chat-meddelanden** - Totalt antal AI-konversationer
- **Dimensionsanalys** - Genomsnittliga Big Five-scores över alla användare

### Användarhantering
- Lista alla användare
- Se användaraktivitet och antal assessments
- **Exportera användardata** (GDPR-compliance)
- **Radera användardata** (GDPR-compliance)

### Assessments
- Lista alla genomförda assessments
- Se detaljer om varje test
- Filtrera efter datum, användare, språk

### Konfiguration
- API-status (Anthropic API-nyckel konfigurerad?)
- Chat-funktion aktiverad/inaktiverad
- AI-rapporter aktiverade/inaktiverade
- GDPR-läge
- Token-limits för chat och rapporter
- Tjänstestatus

## 🛡️ GDPR-verktyg

### Exportera användardata
```
GET /api/admin/users/{user_id}/export
```
Returnerar all användardata i JSON-format:
- Användarprofil
- Alla assessments
- Chat-profil och konversationer

### Radera användardata
```
DELETE /api/admin/users/{user_id}
```
Raderar **permanent**:
- Användarprofil
- Alla assessments
- Chat-profil
- Samtycken (consents)

⚠️ Denna åtgärd går **inte** att ångra!

## 📡 API-endpoints

Alla admin-endpoints kräver autentisering:
```
Authorization: Bearer {admin_token}
```

### Autentisering
- `POST /api/admin/login` - Logga in
- `POST /api/admin/logout` - Logga ut

### Statistik
- `GET /api/admin/dashboard` - Dashboard-statistik
- `GET /api/admin/users` - Lista användare
- `GET /api/admin/assessments` - Lista assessments
- `GET /api/admin/config` - Hämta konfiguration
- `GET /api/admin/health` - Hälsokontroll

### GDPR
- `GET /api/admin/users/{user_id}/export` - Exportera användardata
- `DELETE /api/admin/users/{user_id}` - Radera användardata

## 🔒 Säkerhet

### Nuvarande implementation
- SHA-256 password hashing
- Token-based autentisering
- 8 timmars session timeout
- In-memory session storage

### Rekommendationer för produktion
1. **Använd JWT-tokens** istället för simple tokens
2. **Implementera rate limiting** på login-endpoint
3. **Lägg till 2FA** (two-factor authentication)
4. **Använd HTTPS-only cookies** för token storage
5. **Aktivera IP-whitelist** för admin-panel
6. **Logga all admin-aktivitet** till extern logg-tjänst
7. **Sätt upp varningar** för misstänkt aktivitet

## 📈 Skalning

### Begränsningar i nuvarande version
- **In-memory storage** - Data försvinner vid omstart
- **Single-instance** - Fungerar inte med load balancing
- **Ingen databas** - Begränsad historik

### Upgrade till produktionsskala
1. **Lägg till PostgreSQL/MongoDB** för persistent storage
2. **Implementera Redis** för session management
3. **Aktivera databas-backup** automatiskt
4. **Sätt upp monitoring** (Sentry, Datadog, etc.)
5. **Implementera analytics** (Mixpanel, Amplitude)

## 🎨 Anpassning

Admin-panelen kan enkelt anpassas:

### Färgschema
Ändra i `admin.html`:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Lägg till nya statistik-kort
```html
<div class="stat-card">
    <h3>Din metrik</h3>
    <div class="value" id="myMetric">-</div>
    <div class="label">Beskrivning</div>
</div>
```

### Lägg till nya admin-endpoints
Se `api_admin.py` för exempel på hur endpoints implementeras.

## 📝 Licens

MIT License - Se LICENSE-filen för detaljer

## 🆘 Support

Vid problem, kontakta:
- GitHub Issues: https://github.com/your-repo/issues
- Email: admin@your-domain.com

---

**Skapad med ❤️ av Claude Code**
