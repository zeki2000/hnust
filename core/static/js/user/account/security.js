// 获取CSRF token的全局函数
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 显示全局提示
function showAlert(message, type = 'danger') {
    $('.global-alert').remove();
    const alertHtml = `
        <div class="alert alert-${type} global-alert alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
    `;
    $('body').prepend(alertHtml);
    setTimeout(() => $('.global-alert').alert('close'), 5000);
}

$(document).ready(function() {
    // 检查用户密码状态
    $.get('/api/security/password_status/', function(response) {
        if (response.has_password) {
            $('#password-action-btn').text('修改密码')
                .addClass('btn-success')
                .removeClass('btn-primary');
        } else {
            $('#password-action-btn').text('设置密码')
                .addClass('btn-primary')
                .removeClass('btn-success');
        }
    }).fail(function() {
        // 默认假设用户有密码
        $('#password-action-btn').text('修改密码')
            .addClass('btn-success')
            .removeClass('btn-primary');
    });

    // 初始化模态框
    $('.modal').modal({
        show: false
    });

    // 绑定主操作按钮事件
    $('#password-action-btn').off('click').on('click', function() {
        if ($(this).text().includes('设置')) {
            $('#setPasswordModal').modal('show');
        } else {
            $('#changePasswordModal').modal('show');
        }
    });

    $('#phone-action-btn').click(function() {
        openPhoneModal();
    });

    $('#auth-action-btn').click(function() {
        openAuthModal();
    });

    $('#delete-action-btn').click(function() {
        openDeleteModal();
    });

    // 绑定表单提交按钮
    $('#submitChangePassword').click(changePassword);
    $('#submitSetPassword').click(setPassword);

    // 密码验证函数
    function validatePassword() {
        // 获取当前显示的模态框中的密码输入框
        const $activeModal = $('.modal.in');
        const $newPassword = $activeModal.find('input[name="new_password"]');
        const $confirmPassword = $activeModal.find('input[name="confirm_password"]');
        const newPass = $newPassword.val();
        const confirmPass = $confirmPassword.val();
        
        const pattern = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,12}$/;
        
        // 验证新密码格式
        if (newPass) {
            const isValid = pattern.test(newPass);
            const helpText = $newPassword.closest('.form-group').find('.form-text');
            
            if (!isValid) {
                helpText.addClass('text-danger');
                helpText.text('密码需为6-12位字母和数字组合');
            } else {
                helpText.removeClass('text-danger');
                helpText.text('');
            }
        }
        
        // 验证两次密码是否一致
        if (newPass && confirmPass) {
            const $confirmGroup = $confirmPassword.closest('.form-group');
            const $confirmHelp = $confirmGroup.find('.form-text');
            
            if (newPass !== confirmPass) {
                $confirmHelp.addClass('text-danger');
                $confirmHelp.text('两次输入的密码不一致');
            } else {
                $confirmHelp.removeClass('text-danger');
                $confirmHelp.text('');
            }
        }
    }

    // 使用防抖处理密码验证
    let passwordTimeout;
    $(document).on('blur', 'input[name="new_password"], input[name="confirm_password"]', function() {
        clearTimeout(passwordTimeout);
        passwordTimeout = setTimeout(validatePassword, 300);
    });
});

function openPasswordModal() {
    $('#changePasswordModal').modal('show');
}

function openPhoneModal() {
    $('#verifyOldPhoneModal').modal('show');
    // 显示当前绑定的手机号
    $.get('/api/user/get-phone/', function(response) {
        $('#old-phone').val(response.phone);
    });
}

function openAuthModal() {
    $('#authModal').modal('show');
}

function openDeleteModal() {
    $('#deleteAccountModal').modal('show');
}

// 修改密码 - 用于已设置密码的用户
function changePassword() {
    const $form = $('#changePasswordForm');
    const oldPassword = $form.find('input[name="old_password"]').val();
    const newPassword = $form.find('input[name="new_password"]').val();
    const confirmPassword = $form.find('input[name="confirm_password"]').val();

    // 清除旧提示
    $('.global-alert').remove();

    // 基础验证
    if (!oldPassword || !newPassword || !confirmPassword) {
        showAlert('请填写所有密码字段');
        return;
    }

    if (newPassword.length < 6 || newPassword.length > 12) {
        showAlert('密码长度需为6-12位');
        return;
    }
    if (!/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,12}$/.test(newPassword)) {
        showAlert('密码需包含字母和数字组合');
        return;
    }

    if (newPassword !== confirmPassword) {
        showAlert('两次输入的新密码不一致');
        return;
    }

    const csrftoken = getCookie('csrftoken');

    // 发送请求
    $.ajax({
        url: '/api/security/change_password/',
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        data: JSON.stringify({
            old_password: oldPassword,
            new_password: newPassword,
            confirm_password: confirmPassword
        }),
        success: function(response) {
            console.log('密码修改成功:', response);
            showAlert('密码修改成功！', 'success');
            $('#changePasswordModal').modal('hide');
            // 更新UI状态
            $('#password-display').text('已设置');
            $('#password-action-btn').text('修改密码')
                .removeClass('btn-primary')
                .addClass('btn-success');
        },
        error: function(xhr) {
            console.error('密码修改失败:', xhr.status, xhr.responseText);
            const errorMsg = xhr.responseJSON?.message || 
                `操作失败 (${xhr.status} ${xhr.statusText})`;
            showAlert(errorMsg);
        }
    });
}

// 设置密码 - 用于未设置密码的用户
function setPassword(e) {
    const $form = $('#setPasswordForm');

    // 阻止表单默认提交行为
    if (e && e.preventDefault) {
        e.preventDefault();
    }

    const $newPassword = $form.find('input[name="new_password"]');
    const $confirmPassword = $form.find('input[name="confirm_password"]');
    const newPassword = $newPassword.val();
    const confirmPassword = $confirmPassword.val();

    // 清除之前的提示
    $('.alert').alert('close');
    $('.is-invalid').removeClass('is-invalid');

    // 基础验证
    if (!newPassword || !confirmPassword) {
        console.log('验证失败: 密码字段未填写完整');
        showAlert('请填写所有密码字段');
        $form.find('.form-control').addClass('is-invalid');
        return;
    }

    if (newPassword.length < 6 || newPassword.length > 12) {
        showAlert('密码长度需为6-12位');
        $form.find('input[name="new_password"]').addClass('is-invalid');
        return;
    }

    if (!/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,12}$/.test(newPassword)) {
        showAlert('密码需包含字母和数字组合');
        $form.find('input[name="new_password"]').addClass('is-invalid');
        return;
    }

    if (newPassword !== confirmPassword) {
        showAlert('两次输入的新密码不一致');
        $form.find('input[name="confirm_password"]').addClass('is-invalid');
        return;
    }

    const formData = {
        new_password: newPassword,
        confirm_password: confirmPassword,
        csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
    };
    
    // 获取CSRF token
    const csrftoken = getCookie('csrftoken');
    
    $.ajax({
        url: '/api/security/set_password/',
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        data: JSON.stringify({
            new_password: newPassword,
            confirm_password: confirmPassword
        }),
        beforeSend: function() {
            $('#submitSetPassword').prop('disabled', true).html('<i class="fa fa-spinner fa-spin"></i> 处理中...');
        },
        success: function(response) {
            showAlert('密码设置成功！', 'success');
            // 关闭模态框
            $('#setPasswordModal').modal('hide');
            // 更新状态文本
            $('#password-display').text('已设置');
            // 更新按钮状态
            $('#password-action-btn').text('修改密码')
                .removeClass('btn-primary')
                .addClass('btn-success');
            // 重置表单
            $('#setPasswordForm')[0].reset();
        },
        error: function(xhr) {
            $('#setPasswordBtn').prop('disabled', false).text('设置密码');
            const errorMsg = xhr.responseJSON?.message || '密码设置失败，请稍后重试';
            showAlert(errorMsg);
            
            // 高亮显示错误字段
            if (xhr.responseJSON?.errors) {
                Object.keys(xhr.responseJSON.errors).forEach(field => {
                    $(`[name="${field}"]`).addClass('is-invalid');
                });
            }
        },
    });
}

// 打开密码模态框
function openPasswordModal(type) {
    if (type === 'change') {
        $('#changePasswordModal').modal('show');
    } else {
        $('#setPasswordModal').modal('show');
    }
}

// 获取手机验证码
// 获取原手机验证码
function getOldPhoneCode() {
    $.ajax({
        url: '/api/security/send_phone_code/',
        method: 'POST',
        success: function(response) {
            showAlert('验证码已发送到原手机', 'success');
            startCountdown('#sendOldPhoneCodeBtn');
        },
        error: function(xhr) {
            showAlert(xhr.responseJSON?.message || '验证码发送失败');
        }
    });
}

// 获取新手机验证码
function getNewPhoneCode() {
    const phone = $('#new-phone').val();
    
    if (!phone || !/^1[3-9]\d{9}$/.test(phone)) {
        showAlert('请输入有效的手机号码');
        return;
    }

    $.ajax({
        url: '/api/user/send-new-phone-code/',
        method: 'POST',
        data: {
            phone: phone
        },
        success: function(response) {
            showAlert('验证码已发送到新手机', 'success');
            startCountdown('#sendNewPhoneCodeBtn');
        },
        error: function(xhr) {
            showAlert(xhr.responseJSON?.message || '验证码发送失败');
        }
    });
}

// 验证原手机号
function verifyOldPhone() {
    const code = $('#old-phone-code').val();

    if (!code || !/^\d{6}$/.test(code)) {
        showAlert('请输入6位验证码');
        return;
    }

    $.ajax({
        url: '/api/user/verify-old-phone/',
        method: 'POST',
        data: {
            code: code
        },
        success: function(response) {
            $('#verifyOldPhoneModal').modal('hide');
            $('#changePhoneModal').modal('show');
        },
        error: function(xhr) {
            showAlert(xhr.responseJSON?.message || '验证失败');
        }
    });
}

// 更换手机号
function changePhone() {
    const phone = $('#new-phone').val();
    const code = $('#new-phone-code').val();

    if (!phone || !/^1[3-9]\d{9}$/.test(phone)) {
        showAlert('请输入有效的手机号码');
        return;
    }

    if (!code || !/^\d{6}$/.test(code)) {
        showAlert('请输入6位验证码');
        return;
    }

    $.ajax({
        url: '/api/security/change_phone/',
        method: 'POST',
        data: {
            phone: phone,
            code: code
        },
        success: function(response) {
            showAlert('手机号更换成功', 'success');
            $('#changePhoneModal').modal('hide');
            resetPhoneForm();
            location.reload(); // 刷新页面更新显示
        },
        error: function(xhr) {
            showAlert(xhr.responseJSON?.message || '手机号更换失败');
        }
    });
}

// 提交实名认证
function submitAuth() {
    const realName = $('#real-name').val();
    const idNumber = $('#id-number').val();

    if (!realName || realName.length < 2) {
        showAlert('请输入有效的真实姓名');
        return;
    }

    if (!idNumber || !/(^\d{15}$)|(^\d{17}(\d|X|x)$)/.test(idNumber)) {
        showAlert('请输入有效的身份证号码');
        return;
    }

    $.ajax({
        url: '/api/security/submit_auth/',
        method: 'POST',
        data: {
            real_name: realName,
            id_number: idNumber
        },
        success: function(response) {
            showAlert('实名认证成功', 'success');
            $('#authModal').modal('hide');
            location.reload(); // 刷新页面更新状态
        },
        error: function(xhr) {
            showAlert(xhr.responseJSON?.message || '实名认证失败');
        }
    });
}

// 注销账号
function deleteAccount() {
    if (!confirm('确定要注销账号吗？此操作不可撤销！')) {
        return;
    }

    $.ajax({
        url: '/api/security/delete_account/',
        method: 'POST',
        success: function(response) {
            window.location.href = '/'; // 注销后跳转首页
        },
        error: function(xhr) {
            showAlert(xhr.responseJSON?.message || '账号注销失败');
        }
    });
}

// 验证码倒计时
function startCountdown(btnSelector) {
    let countdown = 60;
    const $btn = $(btnSelector);
    const originalText = $btn.text();
    
    $btn.prop('disabled', true);
    
    const timer = setInterval(function() {
        $btn.text(`${countdown}秒后重试`);
        countdown--;
        
        if (countdown < 0) {
            clearInterval(timer);
            $btn.text(originalText).prop('disabled', false);
        }
    }, 1000);
}
