var quill = undefined;
var is_saved = false;
$('#save').click(function() {
    let title = $('#title-edit').val();
    let content = JSON.stringify(quill.getContents());
    let content_text = quill.getText();
    let csrf_token = $('#csrf_token').val();
    let method = is_saved? 'PATCH': 'POST';
    let urlpath = (post_uri === undefined)? '/api/posts/': `/api/posts/${post_uri}`;
    $.ajax({
        type: method,
        url: urlpath,
        headers: {'X-CSRFToken': csrf_token},
        data: JSON.stringify({'title': title, 'body': content, 'body_text': content_text}),
        success: function(data) {
            is_saved = true;
            let new_post_uri = encodeURI(data['post_uri']) || undefined;
            if (post_uri !== new_post_uri) {
                let re = new RegExp(`(${post_uri}|new-post)`);
                new_href = location.href.replace(re, new_post_uri);
                if (!new_href.includes('?edit=1')) {
                    new_href += '?edit=1';
                }
                location = new_href;
            }
        },
        error: function(error) {console.log(error);},
        contentType: 'application/json',
        dataType: 'json'
    });
});

$('#delete').click(function() {
    let title = $('#title').val();
    let content = quill.getContents();
    let csrf_token = $('#csrf_token').val();
    $.ajax({
        type: 'DELETE',
        url: `/api/posts/${post_uri}`,
        headers: {'X-CSRFToken': csrf_token},
        data: JSON.stringify({'title': title, 'body': content}),
        success: function() {
            let pos = location.href.indexOf(post_uri) - 1;
            location = location.href.slice(0, pos);
        },
        error: function(error) {console.log(error);},
        contentType: 'application/json',
        dataType: 'json'
    });
});

$('#discard').click(function() {
    let referrer = document.referrer || '/';
    location = referrer;
});

$('#edit').click(function() {
    $('#edit').hide();
    $('#view').show();
    $('#save').show();
    $('#title-edit').show();
    $('#title-edit').val($('#title').text());
    $('#title').hide();
    $('#body').css('border', '1px solid #ccc');
    $('.ql-toolbar').show();
    quill.enable();
});

$('#view').click(function() {
    $('#edit').show();
    $('#view').hide();
    $('#save').hide();
    $('#title-edit').hide();
    $('#title').show();
    $('#title').text($('#title-edit').val());
    $('#body').css('border', '0px');
    $('.ql-toolbar').hide();
    quill.disable();
});

let csrf_token = $('#csrf_token').val();
let path_parts = location.pathname.split('/');
//post
if (path_parts.length == 3) {
    var post_uri = path_parts[2];
    $.ajax({
        type: 'GET',
        url: `/api/posts/${post_uri}`,
        headers: { 'X-CSRFToken': csrf_token },
        contentType: 'application/json',
        success: function (data) {
            $('#title').text(data['title']);
            let body = $('#body');
            quill = new Quill(body[0], {
                modules: {
                    toolbar: true
                },
                theme: 'snow'
            });
            quill.setContents(JSON.parse(data['body']));
            $('#post-date').text(moment(data['created_on'] * 1000).format('YYYY-MM-DD'));
            let url = new URL(location.href);
            if (url.searchParams.get('edit') !== "1") {
                $('.ql-toolbar').hide();
                quill.disable();
            }
            else {
                $('#edit').click();
            }
            is_saved = true;
        },
        error: function(error) {console.log(error);},
        dataType: 'json'
    });
}
//new post
else {
    quill =  new Quill('#editor', {
        modules: { toolbar: true },
        theme: 'snow'
    });
}

//comments
$.ajax({
    type: 'GET',
    url: `/api/comments?post_uri=${post_uri}`,
    headers: {
        'X-CSRFToken': csrf_token
    },
    success: function (data) {
        let comments = data['comments'];
        comments.forEach(function(comment) {
            let tmp = document.getElementById('comment-template').content.cloneNode(true);
            $(tmp).find('.commenter').text(comment['author']);
            $(tmp).find('.commenter').href = `/@${comment['author']}`;
            $(tmp).find('.meta-info').text(moment(comment['comment_on']).format('YYYY-MM-DD HH:mm:ss'));
            $(tmp).find('.comment-content').text(comment['content']);
            $('#comments').append(tmp);
        });
    },
    error: function (error) {
        console.log(error);
    },
    contentType: 'application/json',
    dataType: 'json'
});

$('#submit-comment').click(function() {
    let comment = $('#write-comment').val();
    if (comment === '') {
        return ;
    }
    $.ajax({
        type: 'POST',
        url: `/api/comments?post_uri=${post_uri}`,
        headers: {
            'X-CSRFToken': csrf_token
        },
        data: JSON.stringify({content: comment}),
        success: function() {
            let tmp = document.getElementById('comment-template').content.cloneNode(true);
            $(tmp).find('.commenter').text($('#user-setting-dropdown').text());
            $(tmp).find('.commenter').href = `/@${comment['author']}`;
            $(tmp).find('.meta-info').text(moment().format('YYYY-MM-DD'));
            $(tmp).find('.comment-content').text(comment);
            $('#comments').append(tmp);
            $('#write-comment').val('');
        },
        error: function(error) {console.log(error);},
        contentType: 'application/json',
        dataType: 'json'
    });
});