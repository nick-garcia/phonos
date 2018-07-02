function confirm_delete_user(user_id) {
    var delete_user = confirm('Are you sure you want to delete his user?');

    if (delete_user) {
        $.ajax('/user/' + user_id, {
            method: 'DELETE',
            success: function(data, status, xhr) {
                window.location.replace('/users.html');
            }
        })
    }
}

