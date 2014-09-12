var audio_context;
var recorder;
var audio_blob;

function update_table(items) {
    $('#table tbody tr').remove();
    $.each(items, function(index, item) {
        $("#table tbody").append('<tr><td class="uk-width-9-10">' + item +
            '<button style="margin-left:5px;" class="song-play-button uk-button uk-button-mini uk-button-primary uk-icon-play"></button> \
			</td><td class="uk-width-1-10"> \
			<button class="delete-button uk-button uk-button-mini uk-button-primary uk-icon-minus-circle"></button></td></tr>')
    });

    $(".delete-button").click(function(e) {
        $(this).parent().parent().fadeTo(400, 0, function() {
            $(this).remove();
        });
        $.post("/rm", {
                file: $(this).parent().parent().children().text()
            })
            .fail(function() {
                alert("can't remove")
            });
        e.preventDefault();
    });

    $(".song-play-button").click(function(e) {
        $('#audio-player').show(200);
        $('#audio-player').attr('src',
            'music/' + $(this).parent().parent().children().text()).get(0).play();

        e.preventDefault();
    });
}

function playing_state() {
    $('#prev-button').prop('disabled', false)
    $('#play-button').prop('disabled', true)
    $('#stop-button').prop('disabled', false)
    $('#next-button').prop('disabled', false)
    $('#volup-button').prop('disabled', false)
    $('#voldown-button').prop('disabled', false)
    $('.delete-button').prop('disabled', true)
    $('#remove-all-button').prop('disabled', true)
    $('#broadcast-button').prop('disabled', true)
}

function stopped_state() {
    $('#prev-button').prop('disabled', true)
    $('#play-button').prop('disabled', false)
    $('#schedule-button').prop('disabled', false)
    $('#stop-button').prop('disabled', true)
    $('#next-button').prop('disabled', true)
    $('#volup-button').prop('disabled', true)
    $('#voldown-button').prop('disabled', true)
    $('.delete-button').prop('disabled', false)
    $('#remove-all-button').prop('disabled', false)

}

function get_state() {
    $.get('/state', function(data) {
        if (data == 'playing')
            playing_state()
        else if (data == 'stopped')
            stopped_state()
        else if (data == 'schedule') {
            playing_state()
            $('#schedule-button').prop('disabled', true)
        }
    });
}

$(document).ready(function() {
    $("#play-button").click(function(e) {
        $.get("/play", get_state);
        e.preventDefault();
    });

    $("#schedule-button").click(function(e) {
        $.get("/splay", get_state);
        e.preventDefault();
    });

    $("#stop-button").click(function(e) {
        $.post("/stop", get_state);
        e.preventDefault();
    });

    $("#prev-button").click(function(e) {
        $.post("/prev");
        e.preventDefault();
    });

    $("#next-button").click(function(e) {
        $.post("/next");
        e.preventDefault();
    });

    $("#volup-button").click(function(e) {
        $.post("/volup");
        e.preventDefault();
    });

    $("#voldown-button").click(function(e) {
        $.post("/voldown");
        e.preventDefault();
    });

    $("#remove-all-button").click(function(e) {
        if (confirm("Удалить все файлы?")) {
            $.post("/rmall", function() {
                $.get("/ls", function(data) {
                    update_table(data)
                });
            });
        }
        e.preventDefault();
    });

    $("#rec-button").click(function(e) {
        recorder && recorder.record();
        $('#rec-button').prop('disabled', true)
        $('#rec-stop-button').prop('disabled', false)
        e.preventDefault();
    });

    $("#rec-stop-button").click(function(e) {
        recorder && recorder.stop();
        recorder && recorder.exportWAV(function(blob) {
            audio_blob = blob;
        });
        //recorder.clear();
        $('#rec-button').prop('disabled', false)
        $('#rec-play-button').prop('disabled', false)
        $('#rec-stop-button').prop('disabled', true)
        $.get('/state', function(data) {
            if (data == 'stopped')
                $('#broadcast-button').prop('disabled', false)
        });

        e.preventDefault();
    });

    $('#rec-play-button').click(function(e) {
        var url = URL.createObjectURL(audio_blob);
        $('#audio-player').show(200);
        $('#audio-player').attr('src', url).get(0).play();
        e.preventDefault();
    });

    $('#broadcast-button').click(function(e) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);

        var formData = new FormData();
        formData.append("theFiles", audio_blob, "record.wav");

        xhr.send(formData);
    });

    $.get("/ls", function(data) {
        update_table(data)
    });

    get_state();
});

$(function() {
    var progressbar = $("#progressbar"),
        bar = progressbar.find('.uk-progress-bar'),
        settings = {
            action: 'upload', // upload url
            param: 'theFiles',
            allow: "*",
            //allow : '*.(mp3|wma|wav|midi|mid)',
            loadstart: function() {
                bar.css("width", "0%").text("0%");
                progressbar.removeClass("uk-hidden");
            },

            progress: function(percent) {
                percent = Math.ceil(percent);
                bar.css("width", percent + "%").text(percent + "%");
            },

            allcomplete: function(response) {
                bar.css("width", "100%").text("100%");

                setTimeout(function() {
                    progressbar.addClass("uk-hidden");
                }, 250);

                $.get("/ls", function(data) {
                    update_table(data)
                });
            }
        };
    var select = $.UIkit.uploadSelect($("#upload-select"), settings),
        drop = $.UIkit.uploadDrop($("#upload-drop"), settings);
});

function startUserMedia(stream) {
    var input = audio_context.createMediaStreamSource(stream);
    //input.connect(audio_context.destination);
    //__log('Input connected to audio context destination.');
    recorder = new Recorder(input);
}

function disable_rec() {
    $('#audio-warning').show();
    $('#rec-button').hide();
    $('#rec-play-button').hide();
    $('#rec-stop-button').hide();
    $('#broadcast-button').hide();
}

$(document).ready(function() {
    alert('1')
    try {
        // webkit shim
        window.AudioContext = window.AudioContext || window.webkitAudioContext;
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;
        window.URL = window.URL || window.webkitURL;

        audio_context = new AudioContext;
        //navigator.getUserMedia
    } catch (e) {
        disable_rec();
    }

    navigator.getUserMedia({
        audio: true
    }, startUserMedia, function(e) {
        disable_rec();
    });
});