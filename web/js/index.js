// 봇의 채팅을 입력함
function botchat(idx, text, ) {

}

// 하위 메뉴 보이기 또는 숨기기.
$(".rollUpNav").click(function() {
    $(".sublistContainer").slideToggle();
})

$(".showList").click(function() {
  $(".sublistContainer").slideToggle();
})

// 불만 폼 접수하기
function unsetis(idx) {
  console.log("비만족 답변 : " + idx);
  $("#setisForm").fadeIn();
}

function setis(idx) {
  console.log("만족 답변 : " + idx);
  $(this).addClass("yes");
}

function sendMessage() {
  if ($(".chatContent").val() == "") {
    alert("내용을 입력해주세요!");
    return false;
  }

  else {
    console.log($(".chatContent").val());
    $(".chatContent").val("");
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
    return false;
  }
}

$("#setisform .background").click(function() {
  $("#setisForm").fadeOut();
})
