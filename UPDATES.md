# Klevaedge v2.0 - Professional Crypto Broker Platform

## Major Updates

### 1. **Rebranding to Klevaedge**
- Complete rebrand from CryptoBroker to Klevaedge
- Professional dark theme with blue accents (Exness-inspired)
- Sophisticated UI matching top-tier brokers like Binance, Bybit, Exness

### 2. **Copy Trading Feature** ✨ NEW
- View top performing traders with ROI, Win Rate, and Copier stats
- Start/stop copy trading with any trader
- Track active copy trades and profits
- Automated profit tracking system
- Investment management

### 3. **Email Verification** ✨ NEW
- 6-digit verification code sent upon registration
- SMTP email integration (Gmail compatible)
- Secure account verification process
- Verification required before login

### 4. **Professional Dashboard Features**
- Real-time crypto prices (BTC, ETH, USDT, LTC)
- Account overview with balance, profit, deposits, withdrawals
- Trading activity log
- Recent transactions
- Quick actions panel
- Market overview with live price updates
- Copy trading status

### 5. **Dark Theme Design**
- Professional dark background (#0a0e27)
- Blue accent colors for CTAs and highlights
- Gradient effects and subtle animations
- Glass-morphism cards
- Glow effects on interactive elements
- Smooth transitions and hover states

### 6. **Enhanced Database Schema**
- Email verification fields
- Copy trading tables
- Trading activity logging
- Extended user profiles

## Setup Instructions

### Email Configuration

Edit `app.py` lines 9-15 to configure SMTP:

```python
EMAIL_CONFIG = {
    'SMTP_SERVER': 'smtp.gmail.com',  # Your SMTP server
    'SMTP_PORT': 587,
    'EMAIL': 'your-email@gmail.com',  # Your email
    'PASSWORD': 'your-app-password',  # Gmail app password
    'FROM_NAME': 'Klevaedge'
}
```

**For Gmail:**
1. Enable 2-Factor Authentication
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the 16-character app password in EMAIL_CONFIG

### Installation

```bash
pip install Flask requests
python app.py
```

Access at: http://localhost:5000

### Default Admin Credentials
- Email: admin@cryptobroker.com
- Password: admin123

**Change these before production!**

## New Features

### Copy Trading
- Browse top traders with performance metrics
- Invest min $100 to copy any trader
- Admin can update copy trade profits
- Automatic balance calculations
- Start/stop copying anytime

### Email Verification
- All new users must verify email
- 6-digit code sent automatically
- Code displayed in console if email fails (for testing)
- Can be disabled by modifying registration route

### Professional UI Elements
- Gradient borders
- Hover animations
- Glow effects on buttons
- Dark theme with blue accents
- Responsive design
- Mobile-optimized

## File Structure

```
crypto_broker_v2/
├── app.py                          # Main application
├── requirements.txt
├── templates/
│   ├── base.html                  # Dark theme base
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── verify_email.html         # NEW
│   ├── dashboard.html            # Enhanced
│   ├── copy_trading.html         # NEW
│   ├── deposit.html
│   ├── withdraw.html
│   ├── transactions.html
│   ├── support.html
│   ├── contact.html
│   ├── faq.html
│   └── admin/
│       ├── dashboard.html
│       └── edit_user.html
```

## Admin Features

### Managing Copy Trades
1. Go to Admin Dashboard
2. Click "Edit" on any user
3. View their copy trades
4. Update `total_profit` in copy_trades table to simulate earnings
5. User can stop copy trading anytime to get investment + profit back

### Update User Copy Trade Profits

Use SQL or admin panel to update:
```sql
UPDATE copy_trades SET total_profit = 500.00 WHERE id = 1;
```

## Testing Email Verification

### Without Email Server (Testing)
The app will print verification codes to console. Look for:
```
Registration successful but email could not be sent. Code: 123456
```

### With Email Server
Configure EMAIL_CONFIG properly and emails will be sent automatically.

## Color Scheme

- Background: #0a0e27 (Deep Navy)
- Cards: #1a1f3a (Dark Blue)
- Hover: #252b4a (Lighter Blue)
- Primary: #3b82f6 (Bright Blue)
- Accent: #8b5cf6 (Purple)
- Text: #ffffff, #9ca3af (White, Gray)

## Professional Features Checklist

✅ Copy Trading System
✅ Email Verification
✅ Dark Theme (Exness-style)
✅ Real Crypto Prices
✅ Trading Activity Log
✅ Professional Dashboard
✅ Gradient Effects
✅ Glow Animations
✅ Mobile Responsive
✅ Admin Panel
✅ Transaction Management

## Troubleshooting

### Email not sending
- Check SMTP credentials
- Use Gmail app password, not regular password
- Ensure 2FA is enabled on Gmail
- Check firewall/antivirus settings

### Copy Trading not showing
- Refresh database: Delete crypto_broker.db and restart
- Check if copy_trades table exists

### Verification code not working
- Codes expire after 24 hours
- Check email spam folder
- View console output for code

## Production Deployment

1. Update EMAIL_CONFIG with production email
2. Change ADMIN_PASSWORD
3. Use production database (PostgreSQL/MySQL)
4. Enable HTTPS
5. Set secure secret_key
6. Configure proper SMTP server
7. Add rate limiting
8. Enable logging

## Support

For issues, check the README.md or contact support through the platform.
