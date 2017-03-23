function get_code() {
    $.get('/code-for', {
        title: $('#title').text(),
    lang: $('#lang').val()
    }).done(function(data) {
        $('#code').text(data);
    });
}

$(function() {
    // lang switch load code template
    var lang = $('#lang');
    get_code();
    lang.change(get_code);
    // submit code
    $('#submit').on('click', function(e) {
        console.log($('#title').attr('data-pid'));
        e.preventDefault();
        $.post('/submit-code', {
            pid: $('#title').attr('data-pid'),
            lang: $('#lang').val(),
            code: $('#code').text()
        }).done(function(data) {
            alert(data);
        });
    });
});
