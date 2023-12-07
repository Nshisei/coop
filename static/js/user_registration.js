var socket = io(); // WebSocket接続を初期化
var nfc_id = ''; // userのNFC_ID


// サーバーからユーザのNFCが追加されたときの処理
socket.on('user_nfc', function(data){
    nfc_id = data.nfc_id;
    document.getElementById("nfcId").value = nfc_id;
});