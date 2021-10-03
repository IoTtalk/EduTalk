"use strict";

var acc  = {};
var gyro = {};
var orient = {};
var mag = {};
var morsensor = {};
var hum = {};
var uv = {};
var alc = {};

var push_interval = 40;
var collect_data_interval = 20;

var idf_names = idf_list.map(function(x){return x[0]});

var permission_promises = [];

function sensor_handler(){
    $('.control_btn').on('click', function(){
        if($(this).text() == 'off'){
            turn_on_btn_obj($(this));
        }else{
            turn_off_btn_obj($(this));
        }
    });

    Promise.all(permission_promises).then(function(values){
        requestAnimationFrame(update_layout);
        push_sensor_value();
    });
}

function set_sensor_handler(){
    let sensor_info = {
        'Acceleration': 'accelerationIncludingGravity',
        'Gyroscope': 'rotationRate',
        'Magnetometer': 'target',
    }
    var events_setting = [
        // [Event, event listener name, [sensor list], control btn selector]
        [DeviceMotionEvent, 'devicemotion', ['Acceleration', 'Gyroscope'], '.motion_btn'],
        [DeviceOrientationEvent, 'deviceorientation', ['Orientation'], '#ori_btn']
    ]

    events_setting.forEach(setting => {
        permission_promises.push(new Promise(function(resolve, reject) {
            if(typeof setting[0].requestPermission === 'function'){
                setting[0].requestPermission()
                .then(permissionState => {
                    if (permissionState === 'granted'){
                        window.addEventListener(setting[1], (event) => {
                            setting[2].forEach(name=>{
                                event_handler(event, name);
                            });
                        });
                        turn_on_btn_obj($(setting[3]));
                        resolve();
                    }else{
                        reject();
                    }
                })
                .catch(console.error);
            }else{
                window.addEventListener(setting[1], (event) => {
                    setting[2].forEach(name=>{
                        event_handler(event, name);
                    });
                });
                turn_on_btn_obj($(setting[3]));
                resolve();
            }
        }));
    });

    function event_handler(event, name){
        if($.inArray(name + "_I",idf_names) == -1){
            return;
        }

        let tmp = event[sensor_info[name]];
        const dateTime = new Date().getTime();
        if(name == 'Acceleration'){
            acc.x = tmp.x;
            acc.y = tmp.y;
            acc.z = tmp.z;
            acc.time = dateTime;
        }else if(name == 'Gyroscope'){
            gyro.x = tmp.alpha;
            gyro.y = tmp.beta;
            gyro.z = tmp.gamma;
            gyro.time = dateTime;
        }else if(name == 'Orientation'){
            orient.x = event.alpha;
            orient.y = event.beta;
            orient.z = event.gamma;
            orient.time = dateTime;
        }else if(name == 'Magnetometer'){
            mag.x = tmp.x;
            mag.y = tmp.y;
            mag.z = tmp.z;
            mag.time = dateTime;
        }
    }

    if ( 'Magnetometer' in window ) {
        let sensor = new Magnetometer({frequency: 50});//50hz, rate=20ms
        sensor.addEventListener('reading', function(event) {
            event_handler(event, 'Magnetometer');
        });
        sensor.start();
    }

    if($.inArray('Humidity_I',idf_names) != -1 || $.inArray('UV_I',idf_names) != -1 || $.inArray('Alcohol_I',idf_names) != -1){
        setTimeout(get_morsensor_data, collect_data_interval);
    }

    function get_morsensor_data(){
        $.ajax({
            url: 'http://localhost:8080' + '/dataget',
                type: 'GET',
            })
        .done(function(data){
            const dateTime = new Date().getTime();
            morsensor.hum = data.humi;
            morsensor.uv = data.uv;
            morsensor.alc = data.alc;

            hum.x = morsensor.hum;
            hum.time = dateTime;
            uv.x = morsensor.uv;
            uv.time = dateTime;
            alc.x = morsensor.alc;
            alc.time = dateTime;

            if($(".hint-message").is(":visible")){
                $(".hint-message").hide();
                turn_on_btn_obj($(".morsensor_btn"));
            }
        })
        .fail(function(err){
            //console.log(err.statusText);
            $(".hint-message").show();
            turn_off_btn_obj($(".morsensor_btn"));
        });

        setTimeout(get_morsensor_data, collect_data_interval);
    }

    sensor_handler();
}


function push_sensor_value(){
    let name_info = [
        ['Acceleration_I', 'acc', acc, null],
        ['Gyroscope_I', 'gyr', gyro, null],
        ['Orientation_I', 'ori', orient, null],
        ['Magnetometer_I', 'mag', mag, null],
        ['Humidity_I', 'hum', hum , 'morsensor'],
        ['UV_I', 'uv', uv , 'morsensor'],
        ['Alcohol_I', 'alc', alc , 'morsensor'],
    ];

    name_info.forEach(function(info){
        push_handler(info[0], info[1], info[2], info[3]);
    });

    setTimeout(push_sensor_value, push_interval);

    function push_handler(name, btn_name, obj, type){

        if($.inArray(name, idf_names) == -1 || $('#'+ btn_name +'_btn').text() == 'off'){
            return;
        }
        if(type == 'morsensor'){
            push(name, [obj.x, obj.time]);
            return;
        }
        if(obj.x && obj.y && obj.z){
            push(name, [obj.x, obj.y, obj.z, obj.time]);
        }

    }
}

function update_layout() {
    var text_info = [
        ['Acceleration', 'A', acc, null],
        ['Gyroscope', 'G', gyro, null],
        ['Orientation', 'O', orient, null],
        ['Magnetometer', 'M',mag, null],
        ['Humidity', 'hum', hum, 'morsensor'],
        ['UV', 'uv', uv, 'morsensor'],
        ['Alcohol', 'alc', alc, 'morsensor'],
    ];

    text_info.forEach(function(info){
        update_text(info[0],info[1],info[2],info[3]);
    });

    requestAnimationFrame(update_layout);

    function update_text(name, tag, obj, type){
        if($.inArray(name + '_I', idf_names) == -1){
            return;
        }

        if(type == 'morsensor'){
            $('#'+tag+'_value').text(Number.parseFloat(obj.x).toFixed(2));
            var unixTimestamp = new Date(obj.time);
            var millisecond = unixTimestamp.getMilliseconds();
            var commonTime = unixTimestamp.toLocaleTimeString()+"."+millisecond;
            $('#'+tag+'_time').text(commonTime);
            return;
        }
        var unixTimestamp = new Date(obj.time);
//        var commonTime = unixTimestamp.toLocaleString();//Date&Time
        var millisecond = unixTimestamp.getMilliseconds();
        var commonTime = unixTimestamp.toLocaleTimeString()+"."+millisecond;//only Time(H:M:S)
        $('#'+tag+'x').text(Number.parseFloat(obj.x).toFixed(2));
        $('#'+tag+'y').text(Number.parseFloat(obj.y).toFixed(2));
        $('#'+tag+'z').text(Number.parseFloat(obj.z).toFixed(2));
        $('#'+tag+'time').text(commonTime);
    }
}

function turn_on_btn_obj(obj){
    obj.text('on');
    obj.removeClass('btn-danger').addClass('btn-success');
}

function turn_off_btn_obj(obj){
    obj.text('off');
    obj.removeClass('btn-success').addClass('btn-danger');
}
