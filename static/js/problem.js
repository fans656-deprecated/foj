function set_code() {
    var lang = $('#lang').val();
    var code_last = $('.last-submission-codes[data-lang="' + lang + '"]').text();
    var code = $('.snippet[data-lang="' + lang + '"]').text();
    //console.log(lang + ' ' + code);
    $('#code').val(code_last != '' ? code_last : code);
}

$(function() {
    // lang switch load code template
    set_code();
    $('#lang').change(set_code);
    // submit code
    $('#submit').on('click', function(e) {
        console.log('sumbiting ' + $('#title').attr('data-pid'));
        e.preventDefault();
        $('.submission-state').text('');
        // submit
        var pid = $('#title').attr('data-pid');
        var title = $('#title').text();
        var lang = $('#lang').val();
        var code = $('#code').val();
        console.log('submit code: ' + title);
        $.post('/submit-code', {
            pid: pid,
            title: title,
            lang: lang,
            code: code
        }).done(function(data) {
            data = JSON.parse(data);
            if (data['result'] == 'ok') {
                var sid = data['sid'];
                var source = new EventSource('/submission-state/' + sid);
                source.onmessage = function(ev) {
                    console.log(ev.data);
                    var data = JSON.parse(ev.data);
                    var state = data['state'];
                    console.log('changing #submission-state to ' + data['state']);
                    $('#submission-state').attr('data-state', state);
                    $('#submission-state').attr('href', '/submission/' + sid);
                    if (data['state'] != 'pending') {
                        ev.target.close();
                    }
                    $('#submission-state').text(data['name']);
                    $('#submission-info').text(data['info']);
                };
            } else if (data['result'] == 'failed') {
                alert(data['message']);
            }
        });
        // change last submission code
        $('.last-submission-codes[data-lang="' + lang + '"]').text(code);
    });
    $('#reset-snippet').on('click', function(e) {
        console.log('reset snippet');
        e.preventDefault();
        var code = $('.snippet[data-lang="' + $('#lang').val() + '"]').text();
        console.log(code);
        $('#code').val(code);
    });
    $('#use-last-submission').on('click', function(e) {
        console.log('use last submission code');
        e.preventDefault();
        var code = $('.last-submission-codes[data-lang="' + $('#lang').val() + '"]').text();
        console.log(code);
        $('#code').val(code);
    });
    var source = null;
});
