// function from https://halgatewood.com/how-to-customize-the-pin-it-button-for-pinterest
function pinIt()
{
  var e = document.createElement('script');
  e.setAttribute('type','text/javascript');
  e.setAttribute('charset','UTF-8');
  e.setAttribute('src','https://assets.pinterest.com/js/pinmarklet.js?r='+Math.random()*99999999);
  document.body.appendChild(e);
}

function apss_open_in_popup_window(event, url){
    event.preventDefault();
    window.open(url, 'fdadas', 'toolbars=0,width=640,height=320,left=200,top=200,scrollbars=1,resizable=1');
}

jQuery(document).ready(function ($) {
    var shortcode_profile_array = [];
    $('.apss-count').each(function () {
        var social_detail = $(this).attr('data-social-detail');
        if ($.inArray(social_detail, shortcode_profile_array) == -1) {
            shortcode_profile_array.push(social_detail);
        }
    });
    $('.apss-total-text').each(function (){$(this).text("")});
    $('.apss-shares-text').each(function (){$(this).text("megosztás")});
});