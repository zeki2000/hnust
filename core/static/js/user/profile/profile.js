// 身份证验证函数
function validateIdNumber(id) {
    if (!/^\d{17}[\dXx]$/.test(id)) return false;
    
    const weights = [7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2];
    const checksum = ['1','0','X','9','8','7','6','5','4','3','2'];
    
    let sum = 0;
    for (let i = 0; i < 17; i++) {
        sum += parseInt(id.charAt(i)) * weights[i];
    }
    
    const mod = sum % 11;
    return id.charAt(17).toUpperCase() === checksum[mod];
}

// 实名认证表单验证
$(document).ready(function() {
    $('#realNameForm').submit(function(e) {
        if (!validateIdNumber($('input[name="id_number"]').val())) {
            showAlert('danger', '身份证号码无效，请检查后重新输入');
            e.preventDefault();
        }
    });

    // 短信验证码倒计时
    $('#sendCodeBtn').click(function() {
        let countdown = 60;
        const btn = $(this);
        btn.prop('disabled', true);
        
        const timer = setInterval(function() {
            btn.text(countdown + '秒后重试');
            countdown--;
            
            if (countdown < 0) {
                clearInterval(timer);
                btn.text('获取验证码').prop('disabled', false);
            }
        }, 1000);
        
        // 发送验证码AJAX请求
        $.ajax({
            url: '/send_verification_code/',
            method: 'POST',
            data: {
                phone: $('input[name="new_phone"]').val()
            },
            success: function(response) {
                if (!response.success) {
                    showAlert('danger', response.message);
                    clearInterval(timer);
                    btn.text('获取验证码').prop('disabled', false);
                }
            }
        });
    });
});

// 从用户门户复用的显示消息函数
function showAlert(type, message) {
    const alertDiv = $(`
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
    `);
    
    $('.alert-container').prepend(alertDiv);
    setTimeout(() => {
        alertDiv.alert('close');
    }, 5000);
}

// 头像上传预览和处理
$(document).ready(function() {
    
    // 头像上传预览
    $('#avatar-upload').change(function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        // 验证文件类型和大小
        if (!file.type.match('image/jpeg|image/png')) {
            showAlert('danger', '只支持JPEG/PNG格式图片');
            return;
        }
        if (file.size > 2 * 1024 * 1024) {
            showAlert('danger', '图片大小不能超过2MB');
            return;
        }

        const reader = new FileReader();
        reader.onload = function(event) {
            $('#avatar-preview').attr('src', event.target.result);
        };
        reader.readAsDataURL(file);
    });

    // 日期格式转换函数
    function normalizeDate(dateStr) {
        
        const match = dateStr.match(/^(\d{4})\.(\d{1,2})(\d{2})日?$/);
        if (match) {
            const year = match[1];
            const month = match[2].padStart(2, '0');
            const day = match[3];
            return `${year}-${month}-${day}`;
        }
        return dateStr; // 返回原值或标准格式
    }

    // AJAX表单提交
    $('#profile-form').submit(function(e) {
        e.preventDefault();
        
        const form = $(this);
        const formData = new FormData(this);
        
        const submitBtn = form.find('button[type="submit"]');
        
        // 禁用提交按钮防止重复提交
        submitBtn.prop('disabled', true);
        
        $.ajax({
            url: this.action,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(data) {
                if (data.success) {
                    showAlert('success', '资料更新成功');
                    // 更新页面上的头像显示
                    if (data.avatar_url) {
                        $('#avatar-preview').attr('src', data.avatar_url);
                        $('.navbar .avatar img').attr('src', data.avatar_url);
                    }
            // 更新导航栏用户信息
            if (data.success) {
                console.log('Full AJAX response:', data);
                // 头像更新
                if (data.avatar_url) {
                    console.log('Updating avatar in navbar');
                    $('.navbar .avatar img').attr('src', data.avatar_url);
                }
                // 更新昵称
                if (data.nickname) {
                    console.log('Updating nickname from response:', data.nickname);
                    $('.navbar .profile span').text(data.nickname);
                }
                    } else {
                        console.error('Profile update failed:', data.message || 'Unknown error');
                    }
                } else {
                    showAlert('danger', data.message || '更新失败');
                }
            },
            error: function(xhr) {
                let message = '网络错误，请重试';
                if (xhr.responseJSON && xhr.responseJSON.message) {
                    message = xhr.responseJSON.message;
                }
                showAlert('danger', message);
            },
            complete: function() {
                submitBtn.prop('disabled', false);
            }
        });
    });
});
