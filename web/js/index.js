// 봇의 채팅을 입력함
function botchat(idx, text) {
  var query = '<div class=\"botChatBox"> <div class="profile"> <img src="static/img/user.jpg" alt="챗봇 프로필 이미지"> </div> <div class="chat"> <span>' + text +'</span> <div class="chatSetis"> <span href="#" class="far fa-thumbs-up fa-fw" onclick=\"setis(' + idx + ')\" title="챗봇의 답변이 마음에 들어요!"></span><span href="#" onclick="unsetis(' + idx + ')" class="far fa-thumbs-down fa-fw" title="챗봇의 답변이 마음에 들지 않아요!"></span>  </div>  </div></div>';

  $("#chatBody .container").append(query);

  $('#chatBody .container').scrollTop($('#chatBody .container').prop('scrollHeight'));

  $(".navItems").slideUp();
}

// 하위 메뉴 보이기 또는 숨기기.
$(".rollUpNav").click(function() {
  $(".navItems").slideToggle();
})

$(".showList").click(function() {
  $(".navItems").slideToggle();
})

// 불만 폼 접수하기
function unsetis(idx) {
  console.log("비만족 답변 : " + idx);
  $("#setisForm").fadeIn();
}

function setis(idx) {
  console.log("만족 답변 : " + idx);
      var query = "<div class=\"userChatBox\"><div class=\"chat\">" + "답변에 만족했어." + "<\/div><\/div>";
  $("#chatBody .container").append(query);
  $('#chatBody .container').scrollTop($('#chatBody .container').prop('scrollHeight'));
  $(".navItems").slideUp();
botchat('999', "만족되었다고 기록할게요!")
}

$(".selectitems").click(function() {
  var text = this.innerHTML;
  var query = "<div class=\"userChatBox\"><div class=\"chat\">" + text + "<\/div><\/div>";
  $("#chatBody .container").append(query);
  sendQuery(text);
  $('#chatBody .container').scrollTop($('#chatBody .container').prop('scrollHeight'));
  $(".navItems").slideUp();
})

function reset() {
  var text = "처음부터";
  var query = "<div class=\"userChatBox\"><div class=\"chat\">" + text + "<\/div><\/div>";
  $("#chatBody .container").append(query);
  $('#chatBody .container').scrollTop($('#chatBody .container').prop('scrollHeight'));
  $(".navItems").slideUp();
    botchat('0', "안녕하세요, 서아키 챗봇입니다. <br> 육아, 보육 무엇이든지 물어보세요! <br><br> 만족도를 입력해주시면, 챗봇이 더 똑똑해 질거에요!");
}

function sendMessage() {
  if ($(".chatContent").val() == "") {
    alert("내용을 입력해주세요!");
    return false;
  } else {

    var query = "<div class=\"userChatBox\"><div class=\"chat\">" + $(".chatContent").val() + "<\/div><\/div>";

    $("#chatBody .container").append(query);

    sendQuery($(".chatContent").val());

    $(".chatContent").val("");

    $('#chatBody .container').scrollTop($('#chatBody .container').prop('scrollHeight'));

    $(".navItems").slideUp();
    return false;
  }
  return false;
}

function setisform() {
  if ($(".setisText").val() == "") {
    alert("내용을 입력해 주세요!");
    return false;
  } else {
    console.log($(".setisText").val());
    $("#setisForm").fadeOut();
        var query = "<div class=\"userChatBox\"><div class=\"chat\">" + "답변에 만족하지 못했어요" + "<\/div><\/div>";
  $("#chatBody .container").append(query);
  $('#chatBody .container').scrollTop($('#chatBody .container').prop('scrollHeight'));
  $(".navItems").slideUp();
      botchat('999', "답변에 만족하지 못했다고 기록할게요!")
    return false;
  }
    return false;
}

$("#setisform .background").click(function() {
  $("#setisForm").fadeOut();
})

// 쿼리를 보내는 함수
function sendQuery(text) {
  console.log(text);

  $.ajax({
    headers: {
        'Access-Control-Allow-Origin': '*',
        'Content-Type':'application/json'
    },
    url: 'https://seoakey.run.goorm.io/callNLP?company=seoulcity&system=seoakey&classgubun=ALL&var1='+text,
    method: 'GET',
    dataType: 'text',
    data: "",
    success: function(data){
        var idx = 1;
        var str = data;
        var res = str.split("@")
        console.log(res)
        if (res[1] == 3) {
            botchat(idx, res[3])
        } else if (res[1] == 2) {
            var result = "<div>네이버 블로그에서 찾은 내용이에요.</div>";
            for (var i = 0; i < 12; i+=4) {
                result += "<div class=\"test\"> <div><b>" + res[3 + i] + "</b></div> <div>" + res[4 + i] + "</div><div><a href=" + res[2 + i] +" target=\"blank\">더보기</a></div></div>"
            }

            botchat(idx, result)
        }
    },
          error: function(request, status, error) {
      console.log(request + " / " + status + " / " + error);
    }
  });

}
