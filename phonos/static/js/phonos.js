function confirm_delete_user(user_id) {
    var delete_user = confirm('Are you sure you want to delete this user?');

    if (delete_user) {
        $.ajax('/user/' + user_id, {
            method: 'DELETE',
            success: function(data, status, xhr) {
                window.location.replace('/users.html');
            }
        })
    }
};

function confirm_delete_group(group_id) {
    var delete_group = confirm('Are you sure you want to delete this group?');

    if (delete_group) {
        $.ajax('/group/' + group_id, {
            method: 'DELETE',
            success: function(data, status, xhr) {
                window.location.replace('/groups.html');
            }
        })
    }
};

var parse_timer;
function schedule_parse_cron(cron_schedule) {
    if (parse_timer) {
        clearTimeout(parse_timer);
    }
    parse_timer = setTimeout(function() {
        if (cron_schedule) {
            $.ajax('/parse_cron_schedule', {
                method: 'POST',
                data: {'cron_schedule': cron_schedule},
                success: function(data, status, xhr) {
                    $("#readable_schedule").html(data.readable_schedule);
                }
            });
        } else {
            $('#readable_schedule').empty();
        }
    }, 300);
};
