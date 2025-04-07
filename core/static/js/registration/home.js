document.addEventListener('DOMContentLoaded', function() {
    // 登录/注册标签切换
    const authTabs = document.getElementById('authTabs');
    if (authTabs) {
        const tabLinks = authTabs.querySelectorAll('.nav-link');
        tabLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const tabId = this.getAttribute('href');
                showTab(tabId);
            });
        });
    }

    // 显示错误消息
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    });

    // 表单验证反馈
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = this.querySelectorAll('input');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    isValid = false;
                } else {
                    input.classList.remove('is-invalid');
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });
});

function showTab(tabId) {
    // 隐藏所有标签内容
    const tabContents = document.querySelectorAll('.tab-pane');
    tabContents.forEach(content => {
        content.classList.remove('show', 'active');
    });

    // 取消所有标签的活动状态
    const tabLinks = document.querySelectorAll('.nav-link');
    tabLinks.forEach(link => {
        link.classList.remove('active');
    });

    // 显示选中的标签内容
    const selectedTab = document.querySelector(tabId);
    if (selectedTab) {
        selectedTab.classList.add('show', 'active');
    }

    // 设置当前标签为活动状态
    const activeLink = document.querySelector(`[href="${tabId}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

// 个人资料页功能
document.addEventListener('DOMContentLoaded', function() {
    // 头像上传预览
    const avatarInput = document.getElementById('avatar-upload');
    if (avatarInput) {
        avatarInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    document.getElementById('avatar-preview').src = event.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // AJAX表单提交
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('success', '资料更新成功');
                } else {
                    showAlert('danger', data.message || '更新失败');
                }
            })
            .catch(error => {
                showAlert('danger', '网络错误，请重试');
            });
        });
    }
});

function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;
    
    const container = document.querySelector('.alert-container');
    if (container) {
        container.prepend(alertDiv);
        setTimeout(() => {
            alertDiv.classList.add('fade');
            setTimeout(() => alertDiv.remove(), 150);
        }, 3000);
    }
}