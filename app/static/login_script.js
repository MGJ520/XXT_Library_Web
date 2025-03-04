

function pustSignIn() {
    event.preventDefault();

    const email_login_local = document.getElementById('email_login_local').value.trim();
    let password_login_local = document.getElementById('password_login_local').value.trim();
    password_login_local=hashPassword(password_login_local);
    // 检查邮箱和密码是否为空
    if (!email_login_local || !password_login_local) {
        document.getElementById('login_error').innerText = '邮箱和密码不能为空。';
        return; // 如果为空，则停止执行并显示错误信息
    }

    const data = { email_login_local, password_login_local };

    fetch('/api/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/index';
            } else {
                document.getElementById('login_error').innerText = data.error;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('login_error').innerText = '登录请求失败，请稍后再试。';
        });
}

function postSignUp() {
    event.preventDefault();

    const username_register_local = document.getElementById('username_register_local').value.trim();
    const email_register_local = document.getElementById('email_register_local').value.trim();
    let password_register_local = document.getElementById('password_register_local').value.trim();
    password_register_local=hashPassword(password_register_local);
    // 检查用户名、邮箱和密码是否为空
    if (!username_register_local || !email_register_local || !password_register_local) {
        document.getElementById('register_error').innerText = '用户名、邮箱和密码不能为空。';
        return; // 如果任一为空，则停止执行并显示错误信息
    }

    const data = { username_register_local, email_register_local, password_register_local };
    console.log(data);
    fetch('/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('成功注册');
                window.location.href = '/login';
            } else {
                document.getElementById('register_error').innerText = data.error;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('register_error').innerText = '注册请求失败，请稍后再试。';
        });
}


document.addEventListener('DOMContentLoaded', function() {
    const logoImage = document.getElementById('logo-image');
    logoImage.onload = function() {
        logoImage.style.animationPlayState = 'running';
    };
});


function signUp() {
    document.querySelector('.sign-in').classList.toggle('is-hidden');
    document.querySelector('.sign-up').classList.toggle('is-hidden');  
}

function backSighIn() {
    document.querySelector('.sign-in').classList.toggle("is-hidden")
    document.querySelector('.sign-up').classList.toggle("is-hidden")
}


function hashPassword(message) {
    // 输出最终哈希值
    return b64_md5(message);
}