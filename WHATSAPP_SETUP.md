# WhatsApp Integration Setup Guide

This guide will walk you through setting up WhatsApp communication for your plumber agents using Meta's official WhatsApp Cloud API.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start (CLI Debug Mode)](#quick-start-cli-debug-mode)
3. [WhatsApp Setup (Production)](#whatsapp-setup-production)
4. [Running the System](#running-the-system)ngro
5. [Troubleshooting](#troubleshooting)

---

## Overview

The plumber agents support two communication modes:

| Mode | Use Case | Setup Required |
|------|----------|----------------|
| **CLI** | Local development & debugging | None - works out of the box |
| **WhatsApp** | Production use with real technicians | Meta developer account & WhatsApp Business API |

Both agents (Field Service & Office) can communicate with humans via:
- **Field Service Agent** ↔ Technician (WhatsApp/CLI)
- **Office Agent** ↔ Office Staff (WhatsApp/CLI)

Agent-to-agent communication (Field → Office) continues to use HTTP regardless of mode.

---

## Quick Start (CLI Debug Mode)

No setup required! Just run the agents:

```bash
# 1. Install dependencies
pip install -r shared/requirements.txt
pip install -r field_service_agent/requirements.txt
pip install -r office_agent/requirements.txt

# 2. Set your Gemini API key
export GEMINI_API_KEY=your_gemini_api_key

# 3. Run in CLI mode (default)
export COMMUNICATION_MODE=cli

# 4. Start office agent (in one terminal)
cd office_agent && python main.py

# 5. Start field service agent (in another terminal)
cd field_service_agent && python main.py
```

You'll see formatted messages in the terminal and can respond via keyboard input.

---

## WhatsApp Setup (Production)

### Prerequisites

- Meta (Facebook) developer account
- WhatsApp Business account
- A phone number for WhatsApp Business (can be different from your personal number)
- A publicly accessible server or ngrok for webhooks

### Step 1: Create Meta App

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click **My Apps** → **Create App**
3. Select **Business** as app type
4. Fill in app details and click **Create App**

### Step 2: Add WhatsApp Product

1. In your app dashboard, click **Add Product**
2. Find **WhatsApp** and click **Set Up**
3. You'll be taken to the WhatsApp setup page

### Step 3: Get API Credentials

In the WhatsApp setup page, note down these values:

#### A. Temporary Access Token
- Location: **API Setup** section
- Copy the **Temporary access token** (valid for 24 hours)
- ⚠️ For production, generate a **permanent token**:
  - Go to **Settings** → **Business settings** → **System users**
  - Create system user → Assign WhatsApp permissions
  - Generate permanent token

#### B. Phone Number ID
- Location: **API Setup** section under **From**
- Copy the **Phone Number ID** (not the phone number itself!)

#### C. WhatsApp Business Account ID
- Location: Top of the page or in **API Setup**
- Copy the **WhatsApp Business Account ID**

#### D. App Secret
- Go to **Settings** → **Basic**
- Click **Show** next to **App Secret**
- Copy the value

### Step 4: Configure Test Phone Number

1. In the WhatsApp setup page, scroll to **To**
2. Click **Add phone number**
3. Enter your phone number (the one you'll use for testing)
4. You'll receive a verification code via WhatsApp
5. Enter the code to verify

### Step 5: Set Up Webhook

#### A. Expose Your Server

**Option 1: ngrok (for testing)**
```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8010

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

**Option 2: Production server**
- Use your actual domain with HTTPS (required by Meta)
- Example: `https://your-domain.com`

#### B. Start Webhook Server

```bash
# Set up environment
cp .env.example .env
# Edit .env and set WHATSAPP_VERIFY_TOKEN (any random string you choose)

# Start webhook server
python -m shared.communication.webhook_server
# Or: uvicorn shared.communication.webhook_server:app --host 0.0.0.0 --port 8010
```

#### C. Configure Webhook in Meta

1. In WhatsApp setup page, go to **Configuration** → **Webhook**
2. Click **Edit**
3. Enter your webhook URL: `https://your-domain.com/whatsapp/webhook`
4. Enter **Verify Token**: Same value as `WHATSAPP_VERIFY_TOKEN` in your `.env`
5. Click **Verify and Save**
6. Subscribe to **messages** webhook field

✅ You should see "Webhook verified successfully" in your terminal

### Step 6: Configure Environment Variables

Edit your `.env` file:

```bash
# Communication mode
COMMUNICATION_MODE=whatsapp

# WhatsApp credentials (from Step 3)
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id_here
WHATSAPP_APP_SECRET=your_app_secret_here
WHATSAPP_VERIFY_TOKEN=your_verify_token_here

# Contact phone numbers (format: country_code + number, no + or spaces)
# Example: US +1 234-567-8900 → 12345678900
# Example: Germany +49 123 456789 → 49123456789
FIELD_TECHNICIAN_PHONE=12345678900
OFFICE_STAFF_PHONE=10987654321

# Gemini API
GEMINI_API_KEY=your_gemini_api_key
```

### Step 7: Request Production Access (Optional)

The free tier allows:
- 1,000 free conversations per month
- Testing with up to 5 phone numbers

For production:
1. In Meta App Dashboard, go to **WhatsApp** → **Getting Started**
2. Complete **Business Verification**
3. Request **Access to WhatsApp Business API**

---

## Running the System

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     WhatsApp Cloud API (Meta)                    │
└────────────────────┬──────────────────────┬─────────────────────┘
                     │                      │
              (webhook)              (send messages)
                     │                      │
                     ▼                      │
         ┌──────────────────────┐          │
         │  Webhook Server      │          │
         │  (Port 8010)         │          │
         │  - Receives messages │          │
         │  - Stores in queue   │          │
         └──────────────────────┘          │
                     │                      │
         ┌───────────┴──────────────────────┴───────────────┐
         │                                                   │
         ▼                                                   ▼
┌────────────────────┐                           ┌────────────────────┐
│ Field Service Agent│                           │   Office Agent     │
│  - Reads queue     │─────────(HTTP)───────────▶│   (Port 8001)      │
│  - Sends messages  │                           │                    │
└────────────────────┘                           └────────────────────┘
         │                                                   │
         ▼                                                   ▼
  Technician (WhatsApp)                         Office Staff (WhatsApp)
```

### Running in WhatsApp Mode

```bash
# Terminal 1: Start webhook server (must be first!)
python -m shared.communication.webhook_server

# Terminal 2: Start office agent
cd office_agent && python main.py

# Terminal 3: Start field service agent
cd field_service_agent && python main.py

# Now interact via WhatsApp!
# Send message to your WhatsApp Business number from your verified phone
```

### Running in CLI Debug Mode

```bash
# Set mode
export COMMUNICATION_MODE=cli

# Terminal 1: Office agent
cd office_agent && python main.py

# Terminal 2: Field service agent
cd field_service_agent && python main.py

# Interact via terminal
```

### Switching Between Modes

Just change the environment variable:

```bash
# WhatsApp mode
export COMMUNICATION_MODE=whatsapp

# CLI mode
export COMMUNICATION_MODE=cli

# Auto mode (detects based on credentials)
export COMMUNICATION_MODE=auto
```

---

## Troubleshooting

### Webhook Verification Failed

**Problem:** Webhook shows "Forbidden" or fails verification

**Solutions:**
1. Ensure webhook server is running before configuring in Meta
2. Check `WHATSAPP_VERIFY_TOKEN` in `.env` matches exactly what you entered in Meta
3. Ensure your webhook URL is publicly accessible (test with `curl`)
4. Check webhook server logs for error messages

### Messages Not Received

**Problem:** Sending WhatsApp messages but agents don't respond

**Solutions:**
1. Check webhook server is running (`http://localhost:8010/health`)
2. View message queue: `http://localhost:8010/queue/status`
3. Ensure phone number is verified in Meta dashboard
4. Check Meta App Dashboard → WhatsApp → Webhooks → **messages** is subscribed
5. Look for incoming webhooks in webhook server logs

### Invalid Credentials Error

**Problem:** `ValueError: WHATSAPP_ACCESS_TOKEN is required`

**Solutions:**
1. Ensure `.env` file exists (copy from `.env.example`)
2. Check `.env` has all required credentials
3. Load environment: `export $(cat .env | xargs)` or use `python-dotenv`
4. Verify access token is not expired (use permanent token for production)

### Message Sending Failed

**Problem:** `requests.exceptions.HTTPError: 400` or `403`

**Solutions:**
1. Verify access token is valid and not expired
2. Check phone number format (no +, no spaces, no dashes)
3. Ensure recipient phone number is verified in Meta dashboard (for testing)
4. Check Meta App Dashboard for error messages
5. Verify `WHATSAPP_PHONE_NUMBER_ID` is correct

### Agent-to-Agent Communication Failed

**Problem:** Field agent can't reach office agent

**Solutions:**
1. Ensure office agent is running on port 8001
2. Check firewall allows connections to port 8001
3. Verify URL in `field_service_agent/tools/send_data_to_office_agent.py`

### Interactive Buttons Not Working

**Problem:** Buttons don't appear in WhatsApp

**Solutions:**
1. Ensure using official WhatsApp app (not WhatsApp Web initially)
2. Button titles must be ≤ 20 characters
3. Maximum 3 buttons per message
4. Check Meta App settings allow interactive messages

---

## Advanced Configuration

### Handling Media Messages

The WhatsApp client supports receiving images, audio, and documents:

```python
# In webhook, media messages are stored as:
# "[IMAGE:media_id]", "[AUDIO:media_id]", etc.

# To download:
from shared.whatsapp_client import WhatsAppClient

client = WhatsAppClient()
media_url = client.get_media_url(media_id)
client.download_media(media_url, "/path/to/save/file.jpg")
```

### Custom Message Templates

For marketing messages or notifications outside 24-hour window, create message templates:

1. Go to Meta App Dashboard → WhatsApp → Message Templates
2. Create and submit template for approval
3. Use in code: `client.send(to, template_data, message_type='template')`

---

## Testing Checklist

- [ ] Webhook verification successful
- [ ] Can send message from agent to WhatsApp
- [ ] Can receive message from WhatsApp to agent
- [ ] Interactive buttons work
- [ ] Field agent → Office agent HTTP communication works
- [ ] CLI debug mode works
- [ ] Can switch between CLI and WhatsApp modes

---

## Support & Resources

- [Meta WhatsApp Cloud API Docs](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [WhatsApp Business Platform](https://business.whatsapp.com/)
- [Webhook Setup Guide](https://developers.facebook.com/docs/graph-api/webhooks/getting-started)
- [Interactive Messages](https://developers.facebook.com/docs/whatsapp/guides/interactive-messages)

---

## Security Notes

- Never commit `.env` to git (already in `.gitignore`)
- Use permanent access tokens for production (not temporary tokens)
- Enable webhook signature verification in production (set `WHATSAPP_APP_SECRET`)
- Use HTTPS for all webhook URLs (required by Meta)
- Rotate access tokens periodically
- Implement rate limiting for production deployments
