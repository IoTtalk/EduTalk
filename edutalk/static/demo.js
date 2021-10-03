// define animation related variables
var cyber_device_url = vp_index;
//var remote_control_url = window.location.origin + '/da/rc/'+ da_name + '.html';

$(function(){
    // Initialize
    if(cyber_device_url!=""){
        $('#device-iframe').attr('src', cyber_device_url);
    }
});