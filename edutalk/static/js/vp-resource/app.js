csmapi.set_endpoint(urls.csm_url);

var csrftoken = $('meta[name=csrf-token]').attr('content')

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
})

/*******************************************************************/
var mac_addr = (function () {
  function s () {
      return Math.floor((1 + Math.random()) * 0x10000)
          .toString(16)
          .substring(1);
  }
  return s() + s() + s();
})();

function ida_init(){
  let url = urls.vp_bind(mac_addr);
  
  $.ajax({
    url: url,
    type: 'POST',
    headers: {'x-csrf-token': "{{ csrf_token() }}"},
    contentType: 'application/json; charset=utf-8',
    success: function() {
      console.log('device binding success')
    },
    error: function(result){
      console.log(result)
      console.log('device binding failed')
    }
  });
}

var ida = {
  'ida_init': ida_init,
}; 

/*==Basic==*/
let audio = {}

var preloadAudio = function (filename) {
  if (audio[filename] == undefined) {
    audio[filename] = new Audio('/da/vp/audio/' + filename);
  }
};

var playAudio = function (filename) {
  preloadAudio(filename);
  if (audio[filename] != undefined) {
    audio[filename].play();
  }
};

async function runprog(prog) {
  try {
    eval(prog)
    await __main__()
  } catch (err) {
    // runtime error
    console.log(err);
  }
};

var execute = function (code) {
  let options = {
    lang: 'vpython',
    version: 2.9
  };

  try {
    let js_code = glowscript_compile(code, options);
    runprog(js_code);
  } catch (err) {
    // compile error
    console.log(err);
  }

};

var fetch_code = function (url) {
  $.getJSON(url)
    .done(function (data) {
      console.log(data)
      execute(data.code)
    })
    .fail(function (jqxhr, settings, execption) {
      console.log(execption)
    });
};

window.__context = {
  glowscript_container: $('#glowscript'),
};

$(function () {
  fetch_code(urls.vp_code);
});
