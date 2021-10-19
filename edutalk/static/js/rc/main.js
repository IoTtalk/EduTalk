var idf_data = {};

$(function () {
  var csrftoken = $('meta[name=csrf-token]').attr('content')

  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken)
          }
      }
  })
  $('#permission_modal').modal('show', { backdrop: 'static', keyboard: false });
  $('#permission_modal').bind('click', function () {
    $('#permission_modal').modal('hide');
    set_sensor_handler();
  });
  input_num_handler();
  slider_handler();

  idfs = [];
  idf_list.forEach(idf => {
    idfs.push(idf[0])
  });

  idf_list.forEach(idf => {
    idf[0] = new Function(
      "return function " + idf[0] + "() {\
        let data = idf_data[arguments.callee.name];\
        if (data) {return data;}\
      }")();
  });
  csmapi.set_endpoint(urls.csm_url);

  var profile = {
      'dm_name': dm_name,          
      'idf_list': idfs,
      'odf_list':[],
      'd_name': dev,
  };

  var mac_addr = (function () {
    function s () {
        return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
    }
    return s() + s() + s();
  })();
  
  function ida_init(){
    let url = urls.rc_bind(mac_addr);
    
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
  
  dai(profile, mac_addr, ida)

//   const da = new iottalkjs.DAI({
//     apiUrl: urls.csm_url,
//     deviceModel: dm_name,
//     deviceName: dev,
//     idfList: idf_list,
//     odfList: [],
//     pushInterval: 0.02,
//     onRegister: onRegister,
//   });
//   da.run();
// });

// function onRegister() {
//   url = urls.rc_bind(this.appID)
//   $.post(url, {
//     dataType: 'json',
//   })
//     .done(function () {
//       console.log('device binding success')
//     })
//     .fail(function () {
//       console.log('device binding failed')
//     })
// }

function input_num_handler() {
  $('.submit-btn').on('click', function () {
    $(this).siblings('.error-msg').hide();
    let idf = $(this).parent().attr('name');
    let current_value = $(this).siblings('.input-num').val();
    console.log('current value', current_value);
    // check because mobile input type=num can still type in text
    if (current_value) {
      dan.push(idf, parseFloat(current_value));
    } else {
      $(this).siblings('.error-msg').show();
    }
  });
}

function slider_handler() {
  $('input[type="range"]').rangeslider({
    // Feature detection the default is `true`.
    // Set this to `false` if you want to use
    // the polyfill also in Browsers which support
    // the native <input type="range"> element.
    polyfill: false,

    // Default CSS classes
    rangeClass: 'rangeslider',
    disabledClass: 'rangeslider--disabled',
    horizontalClass: 'rangeslider--horizontal',
    verticalClass: 'rangeslider--vertical',
    fillClass: 'rangeslider__fill',
    handleClass: 'rangeslider__handle',

    // Callback function
    onInit: function () {
      this.output = $('<output class="column has-text-centered">').insertAfter(this.$range).html(this.$element.val());
    },
    // Callback function
    onSlide: function (position, value) {
      //console.log('onSlide:',position,value);
      this.output.html(value);
    },
    // Callback function
    onSlideEnd: function (position, value) {
      console.log('onSlideEnd:', this.identifier, value);
      let idf = this.$element.attr('data-idf-name');
      console.log(typeof(idf))
      dan.push(idf, [parseFloat(value)]);
    }
  });
}

// Shared function
function push(idf_name, data, callback) {
  console.log('push idf_name ', idf_name, data);
  if (!(data instanceof Array))
    data = [data];
  idf_data[idf_name] = data;
}
})