/*
 * tutorial.js is the main JS file for Tutotrial Page
 *
 */

/*
 * <current>
 * current specifies the state where the user currently stays
 * It changes when user clicks another pane/ state
 */
var current = 'lecture';
var current_mode = 'read-only';
var sidebar_hidden_flag = false;

/*
 * <position>
 * position is for lecture pane
 * The following program will save the browsing y index position before the user change state.
 * It is used to go back to the previous position when the user come back to the lecture pane
 */
var position;
var main_height;
var ide_height = 600;
var isFirefox = navigator.userAgent.toLowerCase().indexOf('firefox') > -1;

var cyber_device_url = urls.vp_index;
var remote_control_url = window.location.origin + '/da/rc/'+ da_name + '.html';



$(function(){

    //initial();
    $('#lecture-btn').on('click', show_lecture_pane );
    $('#program-btn').on('click', show_program_pane );
    $('#animation-btn').on('click', show_animation_pane );

    $('.edit').on('click', edit_mode );
    // console.log('current mode', current_mode);

    // temporary trigger click for developer
    $('.edit').trigger('click');

    console.log('cyber_device', cyber_device_url);
    console.log('remote_control', remote_control_url);

});

function initial(){
    /*
     * todo
     * There's somewhere else hide the CodeMirror after the page loaded,
     * for CodeMirror is loading too slow !!
     * Need to fix this
     * */

    var init_state = localStorage.getItem('state');
    console.log('init_state', init_state);
    if(init_state == 'program'){
        show_program_pane();
    }else if(init_state == 'animation'){
        show_animation_pane();
    }


}

function show_lecture_pane(){

    if(current == 'lecture'){
        return;
    }
    if(current_mode =='edit'){
        $("#wrapper").addClass("toggled");
    }

    set_current_state('lecture');
    $('.main-div').animate({'height': main_height}, 1, function(){
        /**
        using animate since $(window).scrollTop(position) doesn't work in firefox
        firefox seems to load iframe much more longer than chrome, which make scrollTop position failed.
        following code detects browser to filter firefox and use show() callback to fix this case.
        **/
        $('html,body').scrollTop(position);
        if(isFirefox){
            $('#lecture-content').show(function(){
                $('.main-div').height('auto');
            });
        }else{
            $('#lecture-content').show();
            $('.main-div').height('auto');
        }
    });
}

function show_program_pane(){

    if(current == 'program'){
        return;
    }

    $("#wrapper").removeClass("toggled");
    save_current_lecture_position();
    // save lecture position before changing .main-div height
    $('.main-div').height(ide_height);
    // change .mian-div height for Program, or it will have unnecessary scrolling
    set_current_state('program');
    $('.ide-title').show();

    /* For now we update code mirror every time when a user click Program Pane
     * Don't know why for now, but if we use var da_updated = true / false to tell wether
     * CodeMirror need to update or not, it has the problem of being black a while and load slowly.
     * This problem was found when CodeMirror can't find textarea when textarea's status is hide .
     * */
    update_code_mirror();

}

function show_animation_pane_event_handler(){
    $("#wrapper").removeClass("toggled");
    save_current_lecture_position();
    set_current_state('animation');
}

function show_animation_pane(){

    console.log('current', current);

    if(current == 'animation'){
        return;
    }else if(current == 'program' && da_name != ''){
        /*
         * this way is a little bit wierd
         * need to refactor
         * */
        save_code(show_animation_pane_event_handler);
    }else{
        show_animation_pane_event_handler();
    }

}

function update_da_url(){
    /*
    *  used in edit-tutorial.js
    */
    // cyber_device_url = window.location.origin + '/da/vp/web_py_index.html#'+ da_name;
    remote_control_url = window.location.origin + '/da/Remote_control_'+ da_name;

}

function set_iframe_url(target){
    /*
     * Since DA keeps pulling data from iottalk server,
     * which makes browser busy sending HTTP Requests,
     * we create a function that make DA shut up by removing the iframe url
     *
     * */

    if(target == 'animation') {
        $('#device-iframe').attr('src', cyber_device_url);
        $('#remote-control-iframe').attr('src', remote_control_url);
    }
    else {
        $('#device-iframe').attr('src', '');
        $('#remote-control-iframe').attr('src', '');
        $.ajax({
        url: urls.lecture.unbind,
        type: 'GET',
        }).done(function(data){
            console.log('testunbind start');
            console.log(data);
            console.log('testunbind end');
        })
    }

}


function save_current_lecture_position(){
    if(current == 'lecture'){
        position = $(window).scrollTop();
        main_height = $('.main-div').height();
    }
}

function set_current_state(target){  

    /* set_navigation_bar
     * 1. make target 'active' by adding class
     * 2. add IDE button on top of navbar when pane is 'Program'
     */
    set_navigation_bar(target);
    set_iframe_url(target); // set iframe url if pane is 'Animation'

    localStorage.setItem('state', target);
    current = target;

    if(target == 'lecture'){
		$('#IDE').hide();
        $('#animation-content').hide();
        $.ajax({
        url: urls.lecture.unbind,
        type: 'GET',
        }).done(function(data){
            console.log('testunbind start');
            console.log(data);
            console.log('testunbind end');
        })
    }else if(target == 'program'){
		$('#lecture-content').hide();
        $('#animation-content').hide();
        $.ajax({
        url: urls.lecture.unbind,
        type: 'GET',
        }).done(function(data){
            console.log('testunbind start');
            console.log(data);
            console.log('testunbind end');
        })

        $('#IDE').show();
        $(window).scrollTop(0);
    }else{// target == 'animation'
		$('#IDE').hide();
		$('#lecture-content').hide();

        $('#animation-content').show();
        $(window).scrollTop(0);
        $.ajax({
        url: urls.lecture.bind,
        type: 'GET',
        }).done(function(data){
            console.log('testbind start');
            console.log(data);
            console.log('testbind end');
        })
    }

}


function set_navigation_bar(target){

    /*
     * 1. set target as active on navigation bar
     * */
    var previous_id = '#'+ current+'-btn';
    var target_id = '#'+target+'-btn';

    $(previous_id).removeClass('active');
    $(target_id).addClass('active');

    /*
     * 2. show extra buttons if in 'Program' state
     * */

    if(target == 'program'){
        $('.editor-btn').show();
    }else{// target is 'animation' or 'lecture'
        $('.editor-btn').hide();
    }

    if(target == 'animation'){
        $('#show-qr-btn').show();
        $('#show-dw-btn').show();
        $('#show-menu-btn').show();
        //$('#show-qr-btn').on('click',show_QRcode);
    }else{
        $('#show-qr-btn').hide();
        $('#show-dw-btn').hide();
        $('#show-menu-btn').hide();
    }

}
function toggle_menu(){
    if( !$('#wrapper').hasClass('toggled')){ // side bar is hide right now
        sidebar_hidden_flag=true;
        $('#menu-toggle').trigger('click');
    }else{
        sidebar_hidden_flag=false;
    }
}
function edit_mode(){

    if(current_mode == 'read-only'){
    //read-only => edit
        if(current == 'lecture'){
            toggle_menu();
        }
        $('.edit').html('View');
        current_mode = 'edit';
    }else{
    //edit => read-only
        if(lesson == 'None'){//you are in add new lecture page
            window.location.href = '/';
        }
        if(current == 'lecture'){
            if(sidebar_hidden_flag == true){
                $('#menu-toggle').trigger('click');
            }
        }
        $('.edit').html('Edit');
        current_mode = 'read-only';
    }

    $('.tutorial-editor').toggleClass('show');
    $('#add-new-course').toggleClass('show');
    $('.iottalk-link-block').toggleClass('show');

}
