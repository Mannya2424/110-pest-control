/**
 * 110 Pest Control: website quote requests -> Google Sheet + email.
 *
 * Paste this into Extensions > Apps Script on the business's Google Sheet,
 * then Deploy > New deployment > Web app (Execute as: Me, Who has access: Anyone).
 * Each request becomes a row in the "Requests" tab. Zapier can watch that tab
 * and create a GorillaDesk lead for every new row.
 */
const NOTIFY_EMAIL = 'pestcontrol110@outlook.com';
const SHEET_NAME = 'Requests';
const HEADERS = ['Date', 'Language', 'Name', 'Phone', 'Email', 'City or ZIP', 'Pest', 'Message', 'Wants emails'];

function doPost(e) {
  const p = (e && e.parameter) || {};
  if (p._honey) return done_();   // spam bot filled the hidden field
  if (!p.name || !p.phone) return done_();

  const sheet = getSheet_();
  const row = [new Date(), p.lang || 'en', p.name, p.phone, p.email || '', p.location || '',
               p.pest || '', p.message || '', p.optin ? 'Yes' : 'No'];
  sheet.appendRow(row.map(clean_));

  const lines = HEADERS.map((h, i) => `<tr><td style="padding:4px 12px 4px 0;color:#666">${h}</td><td style="padding:4px 0"><b>${escape_(String(row[i]))}</b></td></tr>`);
  MailApp.sendEmail({
    to: NOTIFY_EMAIL,
    replyTo: p.email || NOTIFY_EMAIL,
    subject: (p.lang === 'es' ? 'Nueva solicitud de presupuesto: ' : 'New quote request: ') + p.name,
    htmlBody: `<table style="font-family:Arial,sans-serif;font-size:14px">${lines.join('')}</table>`
  });
  return done_();
}

function getSheet_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

// Stop spreadsheet formula injection (values starting with = + - @).
function clean_(v) {
  return typeof v === 'string' && /^[=+\-@]/.test(v) ? "'" + v : v;
}

function escape_(s) {
  return s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

function done_() {
  return ContentService.createTextOutput(JSON.stringify({ ok: true })).setMimeType(ContentService.MimeType.JSON);
}
