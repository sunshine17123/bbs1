from django import forms
from django.core.exceptions import ValidationError


class LoginForm(forms.Form):
    name = forms.CharField(
        min_length=6,
        label='名字',
        error_messages={
            'required': '不能为空',
            'min_length': '最小不能少于6位',
            'invalid': '格式错误',
        },
        widget=forms.widgets.TextInput(
            attrs={
                'class': 'form-control col-md-4',
                'placeholder': '登陆用户名，不少于4个字符',

            }
        )
    )  # least 6
    pwd = forms.CharField(
        min_length=4,
        label='密码',
        widget=forms.widgets.PasswordInput(
            attrs={
                'class': 'form-control col-md-4',
                'placeholder': '至少4位，必须包含字母、数字、特殊字符',
            }
        )
    )  # least 8


class RegisterForm(forms.Form):
    name = forms.CharField(
        min_length=6,
        label='登陆名称',
        error_messages={
            'required': '不能为空',
            'min_length': '最小不能少于6位',
            'invalid': '格式错误',
        },
        widget=forms.widgets.TextInput(
            attrs={
                'class': 'form-control col-md-4',
                'name': 'username',
                'placeholder': '登陆用户名，不少于4个字符',

            }
        )
    )  # least 6
    pwd = forms.CharField(
        min_length=8,
        label='密码',
        error_messages={
            "required": "不能为空",
            "invalid": "格式错误",
            "min_length": "密码最短8位",
        },
        widget=forms.widgets.PasswordInput(
            attrs={
                'class': 'form-control col-md-4',
                'name': 'password',
                'placeholder': '至少8位，必须包含字母、数字、特殊字符',

            }
        )
    )  # least 8

    re_pwd = forms.CharField(
        label='确认密码',
        error_messages={
            "required": "不能为空",
            "invalid": "格式错误",
            "min_length": "密码最短8位",
        },
        widget=forms.widgets.PasswordInput(
            attrs={
                'class': 'form-control col-md-4',
                'name':'re_name',
                'placeholder': '请输入确认密码',

            }
        )
    )
    email = forms.CharField(
        label='邮箱',
        error_messages={
            "required": "不能为空",
            "invalid": "格式错误",
        },
        widget=forms.widgets.TextInput(
            attrs={
                'class': 'form-control col-md-4',
                'name':'email',
                'placeholder': '需要通过邮件激活账户',
                'display': 'inline-block',

            }
        )
    )
    phone = forms.CharField(
        label='手机号码',
        error_messages={
            "required": "不能为空",
            "invalid": "格式错误",
            "min_length": "用户名最短11位",
        },
        widget=forms.widgets.TextInput(
            attrs={
                'class': 'form-control col-md-4',
                'name':'phone',
                'placeholder': '激活账户需要手机短信验证',

            }
        )
    )

    nickname = forms.CharField(
        label='显示名称',
        error_messages={
            'required': '不能为空',
        },
        widget=forms.widgets.TextInput(
            attrs={
                'class': 'form-control col-md-4',
                'name':'nickname',
                'placeholder': '即昵称，不少于2个字符',

            }
        )

    )


    # 全局钩子
    def clean(self):
        pwd = self.cleaned_data.get('pwd')
        re_pwd = self.cleaned_data.get('re_pwd')
        if re_pwd and re_pwd == pwd:
            return self.cleaned_data
        else:
            self.add_error('re_pwd','两次密码不一致')
            raise ValidationError("两次密码不一致")

