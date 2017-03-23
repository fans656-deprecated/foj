$(function() {
    var not_empties = $('.not_empty');
    not_empties.focus(function(e) {
        $(this).removeClass('invalid');
    });
    $('#submit').on('click', function(e) {
        e.preventDefault();
        var title = $('#title');
        var desc = $('#desc');
        var testcases = $('#testcases');
        var invalid = false;
        for (var i = 0; i < not_empties.length; ++i) {
            if ($(not_empties[i]).val().length == 0) {
                $(not_empties[i]).toggleClass('invalid');
                invalid = true;
            }
        }
        if (invalid) return;
        $.post('submit-problem', {
            title: title.val(),
            desc: desc.val(),
            testcases: testcases.val(),
        }).done(function() {
            alert('Submitted');
        }).fail(function() {
            alert('Submition failed');
        });
    });
});
