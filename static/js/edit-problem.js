$(function() {
    $('#submit').click(function(e) {
        e.preventDefault();
        $.post('/submit-problem', {
            data: JSON.stringify({
                pid: $('#pid').text(),
                title: $('#title').val(),
                tags: $('#tags').val(),
                desc: $('#desc').val(),
                snippets: $('.snippet').map(function() {
                    var v = $(this);
                    return {lang: v.attr('data-lang'), code: v.val()};
                }).toArray(),
                testcodes: $('.testcode').map(function(v) {
                    var v = $(this);
                    return {lang: v.attr('data-lang'), code: v.val()};
                }).toArray()
            })
        }).done(function(data) {
            data = JSON.parse(data);
            if (data['result'] == 'ok') {
                window.location.href = data['redirect'];
            } else {
                alert(data['message']);
            }
        });
    });
});
