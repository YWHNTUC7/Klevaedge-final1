# Deploying Klevaedge to Render (Free Tier)

## Steps

### 1. Push to GitHub
- Go to github.com and create a free account
- Create a new repository called `klevaedge` (set to Private)
- Upload all these project files to the repository

### 2. Deploy on Render
- Go to render.com and sign up free
- Click **New +** → **Web Service**
- Click **Connect a repository** → connect your GitHub
- Select your `klevaedge` repository
- Render will auto-detect the `render.yaml` file

Confirm settings:
- **Name:** klevaedge
- **Environment:** Python
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app --workers 1 --threads 2 --timeout 60`
- **Plan:** Free

Click **Create Web Service** and wait ~3 minutes for first deploy.

### 3. Your app will be live at:
`https://klevaedge.onrender.com`

---

## ⚠️ Free Tier Limitations

| Issue | What happens |
|-------|-------------|
| **Sleep after 15min inactivity** | First visitor waits ~30-50 seconds for wake-up |
| **Database resets on restart** | User accounts & data lost when app sleeps/redeploys |
| **Uploads lost on restart** | Payment proof images disappear on restart |

## Upgrade Path (when ready for real users)

1. Upgrade to **Starter plan ($7/month)** on Render → app stays always on
2. Add a **Persistent Disk ($1/month)** → set env vars:
   - `DB_PATH` = `/data/crypto_broker.db`
   - `UPLOAD_FOLDER` = `/data/uploads`

This gives you a fully stable platform for ~$8/month (≈ ₦12,000/month).

## Connecting Your WhoGoHost Domain

After deploying:
1. Go to Render dashboard → your service → **Settings** → **Custom Domains**
2. Click **Add Custom Domain** → enter e.g. `klevaedge.com`
3. Render gives you a CNAME value like `klevaedge.onrender.com`
4. Log into WhoGoHost → DNS Management → add:
   - **Type:** CNAME
   - **Name:** www
   - **Value:** klevaedge.onrender.com
5. For the root domain (@), add an A record pointing to Render's IP
6. Wait 10-30 minutes for DNS to propagate

---

## Admin Login
- Email: `admin@cryptobroker.com`
- Password: `admin123`

**Change these immediately after first login via Settings.**
