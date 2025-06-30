*** Settings ***
Library    SeleniumLibrary

*** Test Cases ***
测试首页
    [Documentation]    测试首页
    Open Browser    http://172.18.18.106.nip.io    chrome
    Input Text    placeholder="请输入用户名/邮箱"    admin
    Input Text    placeholder="请输入密码"    admin
    Input Text    placeholder="请输入验证码"    admin

    Click Button    data-v-de3340ce
    Wait Until Page Contains    测试框架
    Page Should Contain    测试框架
    Close Browser