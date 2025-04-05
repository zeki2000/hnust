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
