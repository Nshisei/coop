var itemListPath = firebase.database().ref("/item"); //firebaseで商品情報を保持しているパス
var userPath = firebase.database().ref("/user"); //firebaseでユーザ情報を保持しているパス
var errorBarcodePath = firebase.database().ref("/error/barcode"); //firebaseでバーコード関係のエラー情報を保持しているパス
var errorFelicaPath = firebase.database().ref("/error/felica"); //firebaseでfelica関係のエラー情報を保持しているパス
var key = []; //商品のfirebase登録キーを保持
var price = []; //商品の価格を保持
var insert = []; //商品情報を表示するために生成するHTMLタグを保持
var sum = 0; //購入金額の合計
var user_id = 0; //ユーザID
var card_id = 0; //カードID
var item_id = []; //商品のID
var discountProbability = 0; //割引確率
var discountedPrice = []; //割引適用後の価格


//購入商品の合計金額を計算する関数
var calculateSum = function(){
  sum = 0;
  price.forEach(function(value){
    sum += Number(value);
  });
  document.getElementById("summary-price").innerText = '¥' + sum;
}

//barcode関係のエラー情報をクリアする
var barcodeErrorClear = function(){
  firebase.database().ref("/error/barcode/").set({unregistered_error:0});
}

//Felica関係のエラー情報をクリアする
var felicaErrorClear = function(){
  firebase.database().ref("/error/felica/").set({unregistered_error:0});
}

//Firebase データベース内のアイテムのリストを取得するために使用。最初の一回はパスに存在する全ての要素に対してトリガーされる。以降は、パスに新しい子が追加されるたびに、その子のみに対し再びトリガーされる。
itemListPath.on("child_added", function(snapshot){
  key.push(snapshot.key);
  price.push(snapshot.val().itemPrice);
  item_id.push(snapshot.val().item_id);
  insert.push('<li class="item"><div class="item-info"><div class="table"><div class="removeButton table-style"><button id=' + snapshot.key + ' type="button" class="remove-button" onclick="removeItem(this.id);">キャンセル</button></div><div class="item-name table-style">'+ snapshot.val().itemName +'</div><div class="item-price table-style">¥'+ snapshot.val().itemPrice +'</div></div></div></li>');
  document.getElementById("insertItem").insertAdjacentHTML('beforeend', insert[insert.length - 1]);
  calculateSum();
  barcodeErrorClear();
  document.getElementById("insertBuyError").innerHTML = '';
  console.log("Add");
  console.log(item_id);
})

//firebaseのitem要素が削除された際にトリガーされ、削除された分のHTMLタグを削除
itemListPath.on("child_removed", function(snapshot){
  var index = key.indexOf(snapshot.key);
  insert.splice(index,1);
  price.splice(index,1);
  item_id.splice(index,1);
  key.splice(index,1);
  document.getElementById("insertItem").textContent = ''; //itemListをクリーン
  insert.forEach(function(value){
    document.getElementById("insertItem").insertAdjacentHTML('beforeend', value);
  });
  calculateSum();
  console.log("remove");
  console.log(item_id);
})


//商品情報のキャンセルボタンが押されるとfirebaseの特定の要素を削除
var removeItem = function(id){
  firebase.database().ref("/item/" + id).remove();
};

//ユーザ情報のキャンセルボタンが押されるとfirebaseの特定の要素を削除
var removeUserInfo = function(){
  firebase.database().ref("/user").remove();
};

//var audio_flg = true;

var postInfo = function(){
	var user_id_text = user_id;
	var card_id_text = card_id;
	var item_id_text = "";
	var price_text = "";
	var fixedDatas = new FormData();
	var XHR = new XMLHttpRequest();
	var win_flg = false;
	var str;
	XHR.open("POST","coop.php",false);
	if(Math.random() * 100 <= discountProbability){ //アタリ
		for(var i=0; i<item_id.length; i++){
			item_id_text += item_id[i] + ",";
			if(price[i] < 0){ //価格がマイナス、つまり入金処理を行っている場合は当選しても0円にしない
				price_text += price[i] + ",";
			}else{
				price_text += "0" + ",";
			}
		}
		win_flg = true;
	}else{ //ハズレ
		for(var i=0; i<item_id.length; i++){
			item_id_text += item_id[i] + ",";
			price_text += price[i] + ",";
		}
	}
	item_id_text = item_id_text.slice(0, -1);
	price_text = price_text.slice(0, -1);
	// 購入するための情報の入力が不十分な場合は購入できない
	if(user_id_text == 0 || card_id_text == 0 || item_id_text == "" || price_text == ""){
		document.getElementById("buy-button").blur();
		document.getElementById("insertBuyError").innerHTML = '<div class="errorContainer table-style"><div class="errorMessage">商品情報もしくはカード情報が未入力です。</div></div>';
		return false;
	}
	if(win_flg) {
//		document.getElementById("ok_sound").play();
		str = 'おめでとうございます！あたりなので今回の購入は無料です！ありがとうございました。';
	} else {
//		document.getElementById("win_sound").play();
		str = '購入処理が完了しました。ありがとうございました。';
	}
	fixedDatas.append("user_id",user_id_text);
	fixedDatas.append("card_id",card_id_text);
	fixedDatas.append("item_id",item_id_text);
	fixedDatas.append("price",price_text);
	XHR.send(fixedDatas);//データを送信。送信に対するACKが帰ってきたら以下の処理を実行。
	document.getElementById("insertBuyError").innerHTML = '';
	firebase.database().ref("/").remove();
//	while(audio_flg);
//	audio_flg = true;
	alert(str);

};

/*
var audioEnded = function(){
	audio_flg = false;
};


document.getElementById("ok_sound").addEventListener("ended",audioEnded,false); // 終了イベント処理関数設定
document.getElementById("win_sound").addEventListener("ended",audioEnded,false); // 終了イベント処理関数設定
*/

//firebaseのユーザ情報を取得する。最初に一回トリガーされる。以降はユーザ情報に変更が発生した場合にトリガーされる。
userPath.on("value", function(snapshot){
  if(snapshot.exists()){ //ユーザ情報がfirebaseにある場合
    user_id = snapshot.val().user_id;
    card_id = snapshot.val().card_id;
    discountProbability = snapshot.val().probability;
    document.getElementById("insertUserInfo").innerHTML = '<div class="removeButton table-style ebutton"><button type="button" class="remove-button" onclick="removeUserInfo();">キャンセル</button></div><div id="" class="table-style  e1">カード名義人</div><div id="userInfo" class="table-style  e2">' + snapshot.val().name + '<br>' + snapshot.val().grade + '</div><div id="" class="table-style  e3">支払い方法</div><div id="" class="table-style  e4"><div class="table"><img src="felica.png" class="table-style felica"><div class="table-style smallText" ><div>プリペイド/ポストペイ<br></div><div id="IDm">'+ snapshot.val().felicaID +'</div></div></div></div><div class="table-style  e5">残高</div><div id="balance" class="table-style  e6">' + '¥' + snapshot.val().balance + '</div>';
    document.getElementById("balance").innerText = '¥' + snapshot.val().balance;
    felicaErrorClear();
    document.getElementById("insertBuyError").innerHTML = '';
  }else{  ////ユーザ情報がfirebaseにない場合
    user_id = 0;
    card_id = 0;
    discountProbability = 0;
    document.getElementById("insertUserInfo").innerHTML = '';
  }
  console.log("userChange");
})

//firebaseのバーコード関係のエラー情報を取得する。最初に一回トリガーされる。以降はエラー情報に変更が発生した場合にトリガーされる。
errorBarcodePath.on("value", function(snapshot){
  if(snapshot.exists() && snapshot.val().unregistered_error == 1){ //エラー処理
    document.getElementById("insertBarcodeError").innerHTML = '<div class="errorContainer"><div class="errorMessage">入力されたバーコードは登録されていません。</div></div>';
    console.log(snapshot.val().unregistered_error);
  }else{
    document.getElementById("insertBarcodeError").innerHTML = '';
  }
})

//firebaseのFelica関係のエラー情報を取得する。最初に一回トリガーされる。以降はエラー情報に変更が発生した場合にトリガーされる。
errorFelicaPath.on("value", function(snapshot){
  if(snapshot.exists() && snapshot.val().unregistered_error == 1){ //エラー処理
    document.getElementById("insertFelicaError").innerHTML = '<div class="errorContainer"><div class="errorMessage">入力されたカード情報は登録されていません。</div></div>';
    removeUserInfo();
    console.log(snapshot.val().unregistered_error);
  }else{
    document.getElementById("insertFelicaError").innerHTML = '';
  }
})
