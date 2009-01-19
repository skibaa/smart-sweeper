hl_replace_main = function (element, url) {
    new Effect.Highlight(element, { startcolor: '#ffff99',endcolor: '#ffffff' });
    return replace_main (url);
}
replace_main = function (url) {
    new Effect.SlideUp('main_div', {
      duration: .3,
      afterFinish: function () {
        new Ajax.Request(url,
          {
            method:'get',
            onSuccess: function(transport){
              $('main_div').innerHTML=transport.responseText;
              new Effect.SlideDown('main_div');
            },
            onFailure: function(transport){
              $('main_div').innerHTML='<div>request to '+transport.request.url+' resulted in status '+transport.status+'</div>';
              new Effect.SlideDown('main_div');
            }
          })
      }
    });
    return false;
}
fast_replace_main = function (url) {
        new Ajax.Request(url,
          {
            method:'get',
            onSuccess: function(transport){
              $('main_div').innerHTML=transport.responseText;
              Effect.Pulsate('pulsate_me', { pulses: 5, duration: 1.5 });
            },
            onFailure: function(transport){
              $('main_div').innerHTML='<div>request to '+transport.request.url+' resulted in status '+transport.status+'</div>';
            }
          })
    return false;
}
post_replace_main = function (url, params) {
    new Effect.SlideUp('main_div', {
      duration: .3,
      afterFinish: function () {
        new Ajax.Request(url,
          {
            method:'post',
            parameters:params,
            onSuccess: function(transport){
              $('main_div').innerHTML=transport.responseText;
              new Effect.SlideDown('main_div');
            },
            onFailure: function(transport){
              $('main_div').innerHTML='<div>request to '+transport.request.url+' resulted in status '+transport.status+'</div>';
              new Effect.SlideDown('main_div');
            }
          })
      }
    });
    return false;
}
