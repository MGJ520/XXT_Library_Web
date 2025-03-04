document.querySelector('input[type="button"]').addEventListener('click', function () {
    const nickname = document.getElementById('nickname').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (password !== confirmPassword) {
        alert('Passwords do not match.');
        return;
    }

    const data = {
        nickname: nickname,
        password: b64_md5(password)
    };

    fetch('/api/update/profile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Profile updated successfully!');
                window.location.reload()
            } else {
                alert('Failed to update profile.');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
});


if (userData) {
    document.getElementById('platformNickname').textContent = userData.platformNickname;
    document.getElementById('platformEmail').textContent = userData.platformEmail;
    document.getElementById('permissionLevel').textContent = translatePermissionLevel(userData.permissionLevel);
    document.getElementById('lastLoginTime').textContent = userData.lastLoginTime;
    document.getElementById('latestLoginIp').textContent = userData.latestLoginIp;
    document.getElementById('loginCount').textContent = userData.loginCount;
    document.getElementById('loginFailureCount').textContent = userData.loginFailureCount;
} else {
    console.log('No data available');
}


function translatePermissionLevel(level) {
    switch (level) {
        case 0:
            return '用户0';
        case 1:
            return '用户1';
        case 2:
            return '用户2';
        case 3:
            return '管理员A3';
        default:
            return '未知';
    }
}
