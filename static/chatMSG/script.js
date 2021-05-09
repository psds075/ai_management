$('#chat_converse').css('display', 'block');
$('#chat_body').css('display', 'none');
$('#chat_form').css('display', 'none');
$('.chat_login').css('display', 'none');
$('.chat_fullscreen_loader').css('display', 'none');
$('#chat_fullscreen').css('display', 'none');


document.getElementById('chat_converse').scrollIntoView();
var topPosition = $("#checkpoint").offset().top;
document.getElementById('chat_converse').scrollTop = topPosition - 536;

var LASTCHATTIME = 0;

$('#prime').click(function (){
	toggleFab();
});


function appendClient(message, date) {
	var inner_tag = $("<div></div>").addClass("chat_avatar").html('<img src="../static/img/dental_hospital2.png"/>');
	var outer_tag = $("<span></span>").addClass("chat_msg_item chat_msg_item_admin");
	outer_tag.html(inner_tag);
	outer_tag.append(message);
	$("#chat_converse").append(outer_tag);
	d = new Date(date);
	var add_conv = $("<span></span>").addClass("status2").text(d.toLocaleString());
	$("#chat_converse").append(add_conv);
	document.getElementById('chat_converse').scrollIntoView();
	var topPosition = outer_tag.offset().top;
	document.getElementById('chat_converse').scrollTop = 20000;
	LASTCHATTIME = date;
}


function appendBot(message, date) {
	var add_conv = $("<span></span>").addClass("chat_msg_item chat_msg_item_user").text(message);
	$("#chat_converse").append(add_conv);
	d = new Date(date);
	var add_conv = $("<span></span>").addClass("status2").text(d.toLocaleString());
	$("#chat_converse").append(add_conv);
	document.getElementById('chat_converse').scrollIntoView();
	var topPosition = add_conv.offset().top;
	document.getElementById('chat_converse').scrollTop = 20000;
	LASTCHATTIME = date;
}


function appendChat(e) {
	var notEmpty = $(".usertext").val() != "",
		isEnterKeypress = e.type == "keypress" && e.keyCode == 13,
		isSendClick = e.type == "click";
	if (notEmpty && (isEnterKeypress || isSendClick)) {
		sendChat(filename);
		e.preventDefault();
	}
}


function sendChat(filename){
	$.ajax({
		data: {
			'filename': filename,
			'text': $("#chatSend").val()
		},
		dataType: 'JSON',
		url: '/api/v1/chat/send',
		type: 'POST',
		success: (data, textStatus, jqXHR) => {
			$("#chatSend").val("");
		}
	});
}

function receiveChat(filename){
	return $.ajax({
		data: {
			'filename': "ALL",
			'time': LASTCHATTIME,
			'read': filename,
			'read_type': "bot"
		},
		dataType: 'JSON',
		url: '/api/v1/chat/reflesh',
		type: 'POST',
		success: (data, textStatus, jqXHR) => {
			function myFunction(item, index, arr) {
				if(item['filename'] == filename){
					if(item['type'] == "bot"){
						appendBot(item['text'], item['time']);
					}
					else if(item['type'] == "user"){
						appendClient(item['text'], item['time']);
					}
					LASTCHATTIME = item['time'];
					openFab();
				}
				else{
					info_message(item["name"], item["text"], item['filename']);
					addAlarm(item['filename']);
					LASTCHATTIME = item['time'];
				}
			}
			data.forEach(myFunction);
		}
	});
}

function initChat(filename_local, interval_local, open_chat){
	filename = filename_local;
	if(interval_local != ''){
		clearInterval(interval_local);
	}
	$.ajax({
		data: {
			'filename': filename,
			'read': filename,
			'read_type': "bot"
		},
		dataType: 'JSON',
		url: '/api/v1/chat/list',
		type: 'POST',
		success: (data, textStatus, jqXHR) => {
			$("#chat_converse").html('');
			function myFunction(item, index, arr) {
				if(item['type'] == "bot"){
					appendBot(item['text'], item['time']);
				}
				else if(item['type'] == "user"){
					appendClient(item['text'], item['time']);
				}
				LASTCHATTIME = item['time'];
			}
			data.reverse().forEach(myFunction);
			if(open_chat == true){
				openFab();
			}else{
				closeFab();
			}
		}
	});
	return setInterval(receiveChat, 1000, filename);
}

$("#fab_send").click(appendChat);
$("#chatSend").keypress(appendChat);

function toggleFab() {
	$('.prime').toggleClass('zmdi-comment-outline');
	$('.prime').toggleClass('zmdi-close');
	$('.prime').toggleClass('is-active');
	$('.prime').toggleClass('is-visible');
	$('#prime').toggleClass('is-float');
	$('.chat').toggleClass('is-visible');
	$('.fab').toggleClass('is-visible');
}

function closeFab() {
	if($('#prime').hasClass('is-float')){
		toggleFab();
	}
}

function openFab() {
	if($('#prime').hasClass('is-float')){
		
	}else{
		toggleFab();
	}
}

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
});


