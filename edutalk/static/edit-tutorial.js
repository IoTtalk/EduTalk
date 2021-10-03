var da_updated = false;

$(function(){

    // temporary clear local storage
    // otherwise lectures will be in wrong order
    // console.clear();

    localStorage.clear();
    sortable_init();
    cards_init();
    new_card_init();

});

function new_card_init(){
    /**
     * new-card
     **/
    $('#editmode-btn').click(function(){
      var mode = $.trim($(this).text()).toLowerCase();
      console.log(mode);
      if (mode == 'view')
      {
        var newmode = 'Edit';
        $('div.tutorial-editor').hide();
      }
      else if (mode == 'edit')
      {
        var newmode = 'View';
        $('div.tutorial-editor').show();
      }

      $(this).text(newmode);
    })
}

function cards_init(){
    /**
     * cards
     **/
    $('.rename-btn').on('click', function(){
        $(this).parent().hide();
        $(this).parent().siblings('.card-input-title').show();
    });
    $('.save-lesson-rename-btn').on('click', function(){
        rename_lecture_handler(this);
    });
    $('.cancel-lesson-rename-btn').on('click', function(){
        $(this).parent().hide();
        $(this).parent().siblings('.card-lesson-title').show();
    });

    $('#url-input').on('change', update_lecture_url_handler);
}

function update_lecture_url_handler(){
  var input_url = $('#url-input').val();
  post_json(urls.lecture.url, {url: input_url},
    function() {
      //dynamic reload iframe (preview-url)
      $('#lesson-url').prop('src', input_url);
      show_success_icon();
  });
}

function rename_lecture_handler(obj){
  //save lesson name
  $(obj).parent().hide();
  var title_text_obj = $(obj).parent().siblings('.card-lesson-title').children('.card-title-text');
  var title_obj = $(obj).parent().siblings('.card-lesson-title');
  var name = $(obj).siblings('.card-input').val();

  title_obj.show();
  post_json(urls.lecture.rename, {name: name},
    function(data) {
      title_text_obj.html(name);
      show_success_icon();
    }
  );
}

function post_json(url, data, cb, error_cb) {
  $.ajax({
    type: 'POST',
    url: url,
    data: JSON.stringify(data),
    success: cb,
    error: function(xhr, status, error) {
      res = JSON.parse(xhr.responseText);
      alert(res.reason)
      if (error_cb !== undefined)
        return error_cb();
      else
        alert('系統異常請聯絡開發人員');
    },
    contentType: 'application/json',
    dataType: 'json'
  });
}

function update_program_pane(){

    // change program pane title
    $('.ide-title > small').html(da_name);

    var success_callback = function(result){
        $('#code').val(result['code']);
    };
    get_vp_code(success_callback, lesson);

}

function update_animation_pane(){
    update_da_url();
}

function sortable_init(){
  //Using Sortable.js
  var options = {
    group: 'lesson_list',
    dataIDAttr: 'data-id',
    animation: 150,
    store: {
      /**
       * Get the order of elements. Called once during initialization.
       * @param   {Sortable}  sortable
       * @returns {Array}
       */
      get: function (sortable) {
        var order = localStorage.getItem(sortable.options.group.name);
        return order ? order.split('|') : [];
      },

      /**
       * Save the order of elements. Called onEnd (when the item is dropped).
       * @param {Sortable}  sortable
       */
      set: function (sortable) {
        var order = sortable.toArray();
        post_json(urls.lecture.reorder, {order: order},
          function(){
            localStorage.setItem(sortable.options.group.name, order.join('|'));
        });
      }
    }  // end store
  }  // end options
  Sortable.create(lessonList, options);
}


function show_success_icon(){
    $('.success-message').show();
    setTimeout(function(){ $('.success-message').fadeOut();} , 1000);

}

function show_message(obj){
    obj.show();
    setTimeout(function(){
        obj.fadeOut();
    }, 2000);
}
