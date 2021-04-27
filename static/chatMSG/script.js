//hideChat(0);

$('#chat_converse').css('display', 'block');
$('#chat_body').css('display', 'none');
$('#chat_form').css('display', 'none');
$('.chat_login').css('display', 'none');
$('.chat_fullscreen_loader').css('display', 'none');
$('#chat_fullscreen').css('display', 'none');


$.ajax({
	beforeSend : function(xhr){
		xhr.setRequestHeader("accept", "application/json");
		xhr.setRequestHeader("x-access-key", "6041cb7706b927b5be29");
		xhr.setRequestHeader("x-access-secret","867c49501b63e37e20d09e8194049aa9");
	},
	url: 'https://api.channel.io/open/v3/user-chats/604112d766ff6da9d9bb/messages?limit=10',
	type: 'get',
	success: (data, textStatus, jqXHR) => {
			console.log('success');
			console.log(data);
			console.log(textStatus);
			console.log(jqXHR);
	}
});


document.getElementById('chat_converse').scrollIntoView();
var topPosition = $("#checkpoint").offset().top;
document.getElementById('chat_converse').scrollTop = topPosition - 536;

$('#prime').click(function () {
	toggleFab();
});

function appendChat(e) {
	console.log(e.target);
	var notEmpty = $(".usertext").val() != "",
		isEnterKeypress = e.type == "keypress" && e.keyCode == 13,
		isSendClick = e.type == "click";
	if (notEmpty && (isEnterKeypress || isSendClick)) {
		var add_conv = $("<span></span>").addClass("chat_msg_item chat_msg_item_user").text($("#chatSend").val());
		$("#chat_converse").append(add_conv);
		var add_conv = $("<span></span>").addClass("status2").text("Just now. Not seen yet");
		$("#chat_converse").append(add_conv);
		document.getElementById('chat_converse').scrollIntoView();
		var topPosition = add_conv.offset().top;
		document.getElementById('chat_converse').scrollTop = 20000;
		$("#chatSend").val("");
		e.preventDefault(); 
	}
}

$("#fab_send").click(appendChat);
$("#chatSend").keypress(appendChat);

//Toggle chat and links
function toggleFab() {
	$('.prime').toggleClass('zmdi-comment-outline');
	$('.prime').toggleClass('zmdi-close');
	$('.prime').toggleClass('is-active');
	$('.prime').toggleClass('is-visible');
	$('#prime').toggleClass('is-float');
	$('.chat').toggleClass('is-visible');
	$('.fab').toggleClass('is-visible');
}

$('#chat_first_screen').click(function (e) {
	hideChat(1);
});

$('#chat_second_screen').click(function (e) {
	hideChat(2);
});

$('#chat_third_screen').click(function (e) {
	hideChat(3);
});

$('#chat_fourth_screen').click(function (e) {
	hideChat(4);
});

$('#chat_fullscreen_loader').click(function (e) {
	$('.fullscreen').toggleClass('zmdi-window-maximize');
	$('.fullscreen').toggleClass('zmdi-window-restore');
	$('.chat').toggleClass('chat_fullscreen');
	$('.fab').toggleClass('is-hide');
	$('.header_img').toggleClass('change_img');
	$('.img_container').toggleClass('change_img');
	$('.chat_header').toggleClass('chat_header2');
	$('.fab_field').toggleClass('fab_field2');
	$('.chat_converse').toggleClass('chat_converse2');
	//$('#chat_converse').css('display', 'none');
	// $('#chat_body').css('display', 'none');
	// $('#chat_form').css('display', 'none');
	// $('.chat_login').css('display', 'none');
	// $('#chat_fullscreen').css('display', 'block');
});

function hideChat(hide) {
	switch (hide) {
		case 0:
			$('#chat_converse').css('display', 'none');
			$('#chat_body').css('display', 'none');
			$('#chat_form').css('display', 'none');
			$('.chat_login').css('display', 'block');
			$('.chat_fullscreen_loader').css('display', 'none');
			$('#chat_fullscreen').css('display', 'none');
			break;
		case 1:
			$('#chat_converse').css('display', 'block');
			$('#chat_body').css('display', 'none');
			$('#chat_form').css('display', 'none');
			$('.chat_login').css('display', 'none');
			$('.chat_fullscreen_loader').css('display', 'block');
			break;
		case 2:
			$('#chat_converse').css('display', 'none');
			$('#chat_body').css('display', 'block');
			$('#chat_form').css('display', 'none');
			$('.chat_login').css('display', 'none');
			$('.chat_fullscreen_loader').css('display', 'block');
			break;
		case 3:
			$('#chat_converse').css('display', 'none');
			$('#chat_body').css('display', 'none');
			$('#chat_form').css('display', 'block');
			$('.chat_login').css('display', 'none');
			$('.chat_fullscreen_loader').css('display', 'block');
			break;
		case 4:
			$('#chat_converse').css('display', 'none');
			$('#chat_body').css('display', 'none');
			$('#chat_form').css('display', 'none');
			$('.chat_login').css('display', 'none');
			$('.chat_fullscreen_loader').css('display', 'block');
			$('#chat_fullscreen').css('display', 'block');
			break;
	}
}