var socket = io(); // WebSocket接続を初期化
var sum = 0; // 購入金額の合計
var user_id = 0; // ユーザID
var card_id = 0; // カードID
var item_id = []; // 商品のID
var price = []; // 商品の価格

// 購入商品の合計金額を計算する関数
var calculateSum = function(){
  sum = 0;
  price.forEach(function(value){
      sum += Number(value);
  });
  document.getElementById("total").innerText = sum;
};

// 商品情報のキャンセルボタンが押されると該当の商品を削除
var removeItem = function(id){
  var index = item_id.indexOf(id);
  if(index !== -1){
      item_id.splice(index, 1);
      price.splice(index, 1);
      document.getElementById(id).parentNode.remove();
      calculateSum();
  }
};

// ユーザ情報のキャンセルボタンが押されるとユーザ情報を削除
var removeUserInfo = function(){
    user_id = 0;
    card_id = 0;
    document.getElementById("card").innerHTML = '';
};
// サーバーから商品が追加されたときの処理
socket.on('item_added', function(data){
  item_id.push(data.item_id);
  price.push(data.itemPrice);
  var itemHTML = '<li id="' + data.item_id + '" class="item"><div class="item-info"><div class="item-name">' + data.itemName + '</div><div class="item-price">¥' + data.itemPrice + '</div></div><button type="button" class="remove-button" onclick="removeItem(\'' + data.item_id + '\');">キャンセル</button></li>';
  document.getElementById("items").insertAdjacentHTML('beforeend', itemHTML);
  calculateSum();
});

// サーバーからユーザ情報が更新されたときの処理
socket.on('user_info', function(data){
  user_id = data.user_id;
  card_id = data.card_id;

  // HTMLにユーザ情報を表示
  var userInfoHTML = 'ユーザID: ' + user_id + '<br>カードID: ' + card_id + '<br><button type="button" class="remove-button" onclick="removeUserInfo();">キャンセル</button>';
  document.getElementById("card").innerHTML = userInfoHTML;
});

// 購入確定ボタンが押されたときの処理
document.getElementById("confirm-purchase").addEventListener("click", function(){
  if(user_id === 0 || card_id === 0 || item_id.length === 0 || sum === 0){
      alert("商品情報またはユーザ情報が未入力です");
      return;
  }

  // サーバーに購入情報を送信
  var purchaseInfo = {
      user_id: user_id,
      card_id: card_id,
      item_id: item_id,
      price: price,
      total: sum
  };

  socket.emit('confirm_purchase', purchaseInfo);
});

// ページを初期状態に戻す関数
function resetPage() {
  // ユーザ情報と商品情報をクリア
  user_id = 0;
  card_id = 0;
  item_id = [];
  price = [];
  sum = 0;

  // HTMLの内容をクリア
  document.getElementById("items").innerHTML = '';
  document.getElementById("card").innerHTML = '';
  document.getElementById("total").innerText = '0';

  // その他のリセットに必要な処理があればここに追加
}

// サーバーから購入処理完了の通知を受け取ったときの処理
socket.on('purchase_confirmed', function(){
  alert("購入が確定されました");
  resetPage();
});
