function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);
    
    // Data transaksi berupa Array of Items
    for (var i = 0; i < data.length; i++) {
      sheet.appendRow([
        data[i].timestamp,
        data[i].item,
        data[i].qty,
        data[i].subtotal,
        data[i].payment_method
      ]);
    }
    
    return ContentService.createTextOutput(JSON.stringify({"status": "SUCCESS"}))
                         .setMimeType(ContentService.MimeType.JSON);
  } catch(error) {
    return ContentService.createTextOutput(JSON.stringify({"status": "ERROR", "message": error.toString()}))
                         .setMimeType(ContentService.MimeType.JSON);
  }
}
