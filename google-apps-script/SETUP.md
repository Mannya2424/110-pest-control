# Quote requests → Google Sheet → GorillaDesk

## Part 1: Google Sheet (do this on a computer, about 10 minutes)

1. Sign in to the business Google account and create a new Google Sheet named **110 Pest Control - Website Requests**.
2. In the sheet, open **Extensions → Apps Script**.
3. Delete the sample code, paste in everything from `Code.gs` (in this folder), and click **Save**.
4. Click **Deploy → New deployment**. Click the gear next to "Select type" and choose **Web app**.
   - Description: `Website form`
   - Execute as: **Me**
   - Who has access: **Anyone**
5. Click **Deploy**, then **Authorize access**. Pick the business account. If Google says the app isn't verified, click **Advanced → Go to (project name)** and **Allow**. This is your own script, so that warning is expected.
6. Copy the **Web app URL**. It starts with `https://script.google.com/macros/s/` and ends in `/exec`.
7. Send that URL to whoever maintains the website. It goes in the `action="..."` of the quote form on both `index.html` and `es/index.html`, replacing `APPS_SCRIPT_URL`.

After that, every quote request adds a row to the **Requests** tab and emails pestcontrol110@outlook.com.
The **Wants emails** column shows who checked the newsletter box. Only email those people.

## Part 2: GorillaDesk (once their account is set up)

1. Sign in at zapier.com with the business email.
2. **Create Zap**:
   - Trigger: **Google Sheets → New Spreadsheet Row**. Pick the sheet and the **Requests** tab.
   - Action: **GorillaDesk → Create Lead** (connect the GorillaDesk account when asked).
   - Map the fields: Name, Phone, Email, City or ZIP, and put Pest + Message in the notes.
3. Test it, then turn the Zap **on**.

## If you change Code.gs later

Use **Deploy → Manage deployments → Edit → Version: New version → Deploy** so the web app URL stays the same.
