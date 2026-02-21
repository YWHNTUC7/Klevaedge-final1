# Quick Start Guide - CryptoBroker

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
pip install Flask requests
```

### Step 2: Run the Application
```bash
python app.py
```

### Step 3: Open Your Browser
Navigate to: `http://localhost:5000`

## 🔑 Login Credentials

### Admin Access
- **Email:** admin@cryptobroker.com
- **Password:** admin123

### Test It Out

1. **Register a New User:**
   - Click "Get Started"
   - Fill in: Name, Email, Password, Confirm Password
   - Click "Create Account"

2. **Login:**
   - Use the email and password you just created
   - Or login as admin to manage users

3. **Make a Deposit:**
   - Go to "Deposit" page
   - Enter amount and select crypto
   - Copy the wallet address shown

4. **Admin: Approve the Deposit:**
   - Logout and login as admin
   - Click "Edit" on your user
   - Find the pending transaction
   - Click "Approve Transaction"

5. **Check Your Balance:**
   - Logout and login as the user again
   - Your balance is now updated!

## 📝 Important: Update Before Production

1. **Change Admin Password** (in app.py, lines 36-37):
   ```python
   ADMIN_EMAIL = 'your_email@example.com'
   ADMIN_PASSWORD = hashlib.sha256('your_secure_password'.encode()).hexdigest()
   ```

2. **Update Wallet Addresses** (in app.py, lines 28-33):
   ```python
   WALLET_ADDRESSES = {
       'bitcoin': 'YOUR_ACTUAL_BTC_ADDRESS',
       'ethereum': 'YOUR_ACTUAL_ETH_ADDRESS',
       'usdt': 'YOUR_ACTUAL_USDT_ADDRESS',
       'litecoin': 'YOUR_ACTUAL_LTC_ADDRESS'
   }
   ```

## 🎯 Key Features

✅ Real-time crypto prices from CoinGecko API
✅ User registration with password confirmation
✅ Deposit & Withdrawal system
✅ Admin panel to manage users
✅ Update user balances, profits, deposits, withdrawals
✅ Transaction approval system
✅ Proper logout functionality
✅ All support links working (Support, Contact, FAQ)
✅ Built with Tailwind CSS

## 🛠️ Admin Features

As admin, you can:
- View all registered users
- Edit user balances
- Update total profits
- Modify deposit/withdrawal totals
- Approve or manage transactions
- View transaction history

## 💡 Tips

- Prices update every 30 seconds automatically
- Click the logo when logged in to logout
- Minimum deposit/withdrawal: $10
- All transactions start as "Pending" until admin approves

## ❓ Need Help?

Check the full README.md for detailed documentation!
