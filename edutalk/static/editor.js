var editor;
var dm_name;

CodeMirror.commands.autocomplete = function(cm) {
    CodeMirror.showHint(cm, CodeMirror.hint.html);
}

var mac_addr = null;
var ida= null;

function get_vp_code(cb , lec_id) {
  IDE_ajax_send_data(urls.vp_code, 'GET' , {success_callback: cb});
  return 'ok';
}

function set_code_mirror(){

    editor = CodeMirror.fromTextArea(document.getElementById("code"), {
        mode: {name: "python",
               version: 3,
               singleLineStringErrors: false},

        theme: "twilight",
        indentUnit: 4,
        lineWrapping: true,
        lineNumbers: true,
        styleActiveLine: true,
        matchBrackets: true,

        extraKeys: {
          "Ctrl-Space": "autocomplete"
        },
        value: "<!doctype html>\n<html>\n  " + document.documentElement.innerHTML + "\n</html>"
    });

}

function update_code_mirror(new_code){

    $('#code').show();
    if(new_code){
        $('#code').val(new_code);
    }

    $('.CodeMirror-wrap').remove();
    set_code_mirror();
    $('#code').hide();

}

function editor_init(){

    var success_callback = function(result) {
        var content = $('<textarea></textarea>', {'id': 'code', 'name':'code'}).val(result['code']);
        content.appendTo('#IDE');
        $('#code').hide();
    };
    get_vp_code(success_callback, lesson);

}

window.__context = {
  glowscript_container: $('#glowscript'),
};

function dai(profile) {
  //dummy
}

function csmPull(df, handler){
  //dummy
}

function preloadAudio(filename){
  //dummy
}

function playAudio(filename){
  //dummy
}

var error_flag;
async function runprog(prog) {
    error_flag=false;
    try {
        eval(prog);
        await __main__()
    } catch(err) {
        console.log('runtime error: ', err.message);
            $('#error-content').text(err.message);
            $('#error-type').text('Runtime Error');
            $('#error-message').show();
            error_flag=true;
    }
};

function execute (code) {
  var options = {
    lang: 'vpython',
    version: 2.9
  };
  var js_code, program;

  try {
      js_code = glowscript_compile(code, options);
      runprog(js_code);
  } catch(err){
    console.log('compile error: ', err.message);
    var re = /line\s\d+/;
    // Knowing case: Windows 10 64-bit ; Chrome 68.0.3440.106  64-bit
    // err.message like this: "compile error: Line 7: cannot import from vpython"
    // Original Testing case:
    //      FreeBSD 11.0-release-p1 desktop firefox 56.0.2 (64-bit) case: "compile error: line 7: cannot import from vpython"
    //
    // with "line"/ "Line" in differece cases making regex matching error
    err.message = err.message.toLowerCase();
    var newstr = err.message.match(re)[0];
    newstr = newstr.replace(/(\d+)/, function($1){ return $1-1;});
    err.message = err.message.replace(re, newstr);
    $('#error-content').text(err.message);
    $('#error-type').text('Compile Error');
    $('#error-message').show();
    error_flag=true;
  }
  if(error_flag){
    return false;

  }else{
    $('#error-message').hide();
    return true;
  }

};

function save_code(callback){
    new_code = editor.getValue();
    $('#code').val(new_code);

    success_flag = execute(new_code);
    var options = {
        data: {'code': new_code},
        success_callback: function(result) {
            if(callback && success_flag){
                callback();
            }
        }
    };
    IDE_ajax_send_data(urls.vp_code, 'POST', options);
}

function set_as_default(){
    // save code first
    var callback = function(){
        // send set as default request to server
        console.log('set as default')
        IDE_ajax_send_data(urls.vp_default, 'POST');
    }
    save_code(callback);
}


function try_it(){
    window.location.href = '/Python_Edu/'+dm_name;
}

function reset_code(){
  console.log(urls.vp_reset);
  var options = {
      success_callback: function(result){
          update_code_mirror(result['code']);
          /*
            * Need to refactor this.
            * set_code_mirror will hide #IDE for /tutorial page
            * to prevent #IDE from missing after clicking reset btn, we use $('#IDE').show() here.
            * */
          $('#IDE').show();
      }
  };
  IDE_ajax_send_data(urls.vp_reset, 'POST', options);
}

var csrftoken = $('meta[name=csrf-token]').attr('content')

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
})

function IDE_ajax_send_data(ajax_url, type, options){
  if (options === undefined)
    var options = {
      data: {},
    }

  $.ajax({
    url: ajax_url,
    type: type,
    dataType: 'json',
    headers: {'x-csrf-token': "{{ csrf_token() }}"},
    contentType: 'application/json; charset=utf-8',
    data: JSON.stringify(options.data),
    success: function(result){
      if(options.success_callback) {
        options.success_callback(result);
      }
      else {
        console.log('success: ', ajax_url);
      }
    },
    error: function(result) {
      console.log('error: ', ajax_url);
      console.log('result: ', result.status, result.statusText);
      console.log(result)
    }
  });
}
