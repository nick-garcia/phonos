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
}

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
}


