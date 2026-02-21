# CryptoBroker - Crypto Trading Platform

A modern cryptocurrency broker platform with real-time prices, user authentication, and admin management.

## Features

✅ **Real Crypto Prices** - Live prices from CoinGecko API for Bitcoin, Ethereum, Tether, and Litecoin
✅ **Working Links** - All navigation links including Support, Contact, and FAQ pages are functional
✅ **Tailwind CSS** - Modern, responsive design using Tailwind CSS
✅ **Simple Authentication** - Register with name, email, and password (with confirmation)
✅ **SQLite Database** - Lightweight database for user data and transactions
✅ **Admin Panel** - Update user balances, profits, deposits, withdrawals, and transaction history
✅ **Proper Logout** - Functional logout from dashboard and logo click
✅ **Real-time Updates** - Dashboard shows live crypto prices that update every 30 seconds

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Wallet Addresses

Edit `app.py` and update your wallet addresses (lines 28-33):

```python
WALLET_ADDRESSES = {
    'bitcoin': 'YOUR_BITCOIN_ADDRESS',
    'ethereum': 'YOUR_ETHEREUM_ADDRESS',
    'usdt': 'YOUR_USDT_ADDRESS',
    'litecoin': 'YOUR_LITECOIN_ADDRESS'
}
```

### 3. Change Admin Credentials

Edit `app.py` (lines 36-37):

```python
ADMIN_EMAIL = 'your_admin@email.com'
ADMIN_PASSWORD = hashlib.sha256('your_secure_password'.encode()).hexdigest()
```

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Default Credentials

**Admin Login:**
- Email: `admin@cryptobroker.com`
- Password: `admin123`

⚠️ **IMPORTANT:** Change these credentials before deploying to production!

## Admin Features

The admin panel allows you to:

1. **View All Users** - See all registered users and their account details
2. **Edit User Data** - Update:
   - Balance
   - Total Profit
   - Total Deposits
   - Total Withdrawals
3. **Manage Transactions** - View and approve pending deposits/withdrawals
4. **Transaction Approval** - When you approve a transaction:
   - Deposits: User's balance and total_deposit increase
   - Withdrawals: User's balance decreases, total_withdrawal increases

## Admin Usage Guide

### Updating User Balance

1. Login as admin (`admin@cryptobroker.com / admin123`)
2. Click on any user's "Edit" button
3. Update the fields:
   - **Balance**: Current account balance
   - **Profit**: Total profit earned
   - **Total Deposits**: Cumulative deposit amount
   - **Total Withdrawals**: Cumulative withdrawal amount
4. Click "Update User Data"

### Approving Transactions

1. Go to a user's edit page
2. Scroll to "User Transactions"
3. Click "Approve Transaction" on pending transactions
4. The user's balance will be automatically updated

## User Features

### For Regular Users:

1. **Register** - Create account with name, email, and password
2. **Deposit** - Request deposits in BTC, ETH, USDT, or LTC
3. **Withdraw** - Request withdrawals to your crypto wallet
4. **Dashboard** - View:
   - Account balance
   - Total profit
   - Total deposits/withdrawals
   - Real-time crypto prices
   - Recent transactions
5. **Transaction History** - View all deposits and withdrawals

## Logout Functionality

- **From Dashboard**: Click the "Logout" button in the navigation
- **Logo Click**: When logged in, clicking the logo logs you out and returns to homepage

## File Structure

```
crypto_broker_v2/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── crypto_broker.db               # SQLite database (auto-created)
└── templates/
    ├── base.html                  # Base template with navigation
    ├── index.html                 # Landing page
    ├── login.html                 # Login page
    ├── register.html              # Registration page
    ├── dashboard.html             # User dashboard
    ├── deposit.html               # Deposit page
    ├── withdraw.html              # Withdrawal page
    ├── transactions.html          # Transaction history
    ├── support.html               # Support page
    ├── contact.html               # Contact page
    ├── faq.html                   # FAQ page
    └── admin/
        ├── dashboard.html         # Admin user list
        └── edit_user.html         # Admin user editor
```

## Database Schema

### Users Table
- id (Primary Key)
- name
- email (Unique)
- password (Hashed)
- balance
- profit
- total_deposit
- total_withdrawal
- created_at

### Transactions Table
- id (Primary Key)
- user_id (Foreign Key)
- type (Deposit/Withdrawal)
- amount
- crypto
- status (Pending/Completed/Failed)
- wallet_address
- created_at

## Security Notes

1. ⚠️ Change admin credentials before deployment
2. ⚠️ Update the secret_key in app.py for production
3. ⚠️ Use HTTPS in production
4. ⚠️ Consider adding two-factor authentication
5. ⚠️ Implement rate limiting for login attempts
6. ⚠️ Use environment variables for sensitive data

## API Integration

The platform uses the **CoinGecko API** (free tier) for real-time cryptocurrency prices. No API key required.

Supported cryptocurrencies:
- Bitcoin (BTC)
- Ethereum (ETH)
- Tether (USDT)
- Litecoin (LTC)

## Troubleshooting

**Issue: Crypto prices not loading**
- Check internet connection
- CoinGecko API may be rate-limited (free tier has limits)
- Wait 30 seconds for auto-refresh

**Issue: Can't login as admin**
- Verify you've updated the admin credentials correctly
- Password must be hashed using sha256

**Issue: Database errors**
- Delete `crypto_broker.db` and restart the app to recreate
- Check file permissions

## Production Deployment

For production deployment:

1. Use a production-ready database (PostgreSQL, MySQL)
2. Set up proper environment variables
3. Use a WSGI server (Gunicorn, uWSGI)
4. Enable HTTPS
5. Set up proper logging
6. Implement backup strategies
7. Add rate limiting and security headers

## Support

For issues or questions:
- Email: support@cryptobroker.com
- WhatsApp: +1 (234) 567-890
- Telegram: @cryptobrokersupport

## License

This project is for educational purposes. Ensure you comply with all applicable laws and regulations when operating a cryptocurrency platform.
