/**
 * Prode Mundial 2026 – Backend en Google Apps Script
 * 
 * INSTRUCCIONES DE DEPLOY:
 * 1. Abrí script.google.com y creá un nuevo proyecto
 * 2. Pegá este código reemplazando el contenido
 * 3. Guardá (Ctrl+S)
 * 4. Extensiones → Crear una planilla de cálculo (o usá una existente)
 *    - En el código, reemplazá SPREADSHEET_ID con el ID de tu planilla
 *    - El ID está en la URL: docs.google.com/spreadsheets/d/ESTE_ES_EL_ID/edit
 * 5. Implementar → Nueva implementación → Aplicación web
 *    - Ejecutar como: Yo
 *    - Quién tiene acceso: Cualquier usuario
 * 6. Copiá la URL de la implementación (termina en /exec)
 * 7. Pegá esa URL en index.html donde dice SHEETS_URL = ''
 */

// ─── CONFIGURACIÓN ───────────────────────────────────────────────────────────
var SPREADSHEET_ID = ''; // <-- pegá acá el ID de tu Google Sheet
var SHEET_NAME     = 'Pronosticos';

// ─── Helpers ─────────────────────────────────────────────────────────────────
function getSheet() {
  var ss = SPREADSHEET_ID
    ? SpreadsheetApp.openById(SPREADSHEET_ID)
    : SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow(['nombre', 'datos', 'ultima_actualizacion']);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function findRow(sheet, name) {
  var values = sheet.getDataRange().getValues();
  for (var i = 1; i < values.length; i++) {  // i=1 salta el header
    if (values[i][0] === name) return i + 1;  // 1-indexed para sheet.getRange
  }
  return -1;
}

function getAllData(sheet) {
  var values = sheet.getDataRange().getValues();
  var result = {};
  for (var i = 1; i < values.length; i++) {
    var name = values[i][0];
    if (!name) continue;
    try { result[name] = JSON.parse(values[i][1] || '{}'); }
    catch(e) { result[name] = {}; }
  }
  return result;
}

// ─── doGet: leer datos ───────────────────────────────────────────────────────
function doGet(e) {
  try {
    var sheet = getSheet();
    var action = (e && e.parameter && e.parameter.action) || 'getAll';

    if (action === 'getAll') {
      var data = getAllData(sheet);
      return output({ ok: true, data: data });
    }

    if (action === 'getOne') {
      var name = e.parameter.name || '';
      var row  = findRow(sheet, name);
      if (row < 0) return output({ ok: true, data: {} });
      var cell = sheet.getRange(row, 2).getValue();
      try { return output({ ok: true, data: JSON.parse(cell || '{}') }); }
      catch(ex) { return output({ ok: true, data: {} }); }
    }

    return output({ ok: false, error: 'acción desconocida' });
  } catch(ex) {
    return output({ ok: false, error: ex.message });
  }
}

// ─── doPost: guardar datos ───────────────────────────────────────────────────
function doPost(e) {
  try {
    var payload = JSON.parse(e.postData.contents);
    var name    = payload.name;
    var data    = JSON.stringify(payload.data || {});
    var ts      = new Date().toISOString();

    if (!name) return output({ ok: false, error: 'falta nombre' });

    var sheet = getSheet();
    var row   = findRow(sheet, name);

    if (row > 0) {
      sheet.getRange(row, 2).setValue(data);
      sheet.getRange(row, 3).setValue(ts);
    } else {
      sheet.appendRow([name, data, ts]);
    }

    return output({ ok: true });
  } catch(ex) {
    return output({ ok: false, error: ex.message });
  }
}

function output(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
