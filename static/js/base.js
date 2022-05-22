// 导航栏状态
$(function () {
    $(".menu-link").click(function () {
        $(".menu-link").removeClass("is-active");
        $(this).addClass("is-active");
    });
});

// 搜索栏
$(".search-bar input")
    .focus(function () {
        $(".header").addClass("wide");
    })
    .blur(function () {
        $(".header").removeClass("wide");
    });

// 返回首页
$('#close-details').on('click', function() {
    window.location.href = '/';
});


