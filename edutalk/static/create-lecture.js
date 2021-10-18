Vue.options.delimiters = ['[[', ']]'];
var csrftoken = $('meta[name=csrf-token]').attr('content')

$.ajaxSetup({
  beforeSend: function(xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken)
      }
  }
})

var app2 = new Vue({
  el: '#new-card',
  data: function(){
    return {
      lecture_name: '',
      url: '',
      odm: '',
      vp_template: 'New',
      checkboxDisabled: false,
      t_list: t_list,
      df_list: {
        'Gravity': {
          select: 'range slider',
          min: 0,
          max: 10,
          default: 5,
        },
        'Radius': {
          select: 'range slider',
          min: 0,
          max: 10,
          default: 5,
        },
        'Speed': {
          select: 'range slider',
          min: 0,
          max: 10,
          default: 5
        },
        'Friction': {
          select: 'range slider',
          min: 0,
          max: 10,
          default: 5
        },
        'Angle': {
          select: 'range slider',
          min: 0,
          max: 10,
          default: 5
        },
      },
      sm_df_list: {
        'Acceleration':{
          select: 'Smartphone Sensor',
        },
        'Gyroscope':{
          select: 'Smartphone Sensor',
        },
        'Orientation':{
          select: 'Smartphone Sensor',
        },
        'Magnetometer':{
          select: 'Smartphone Sensor',
        },
        'Humidity':{
          select: 'Morsensor',
        },
        'UV':{
          select: 'Morsensor',
        },
        'Alcohol':{
          select: 'Morsensor',
        }
      },
      checkedDF: [],
      checkedSmDF: [],
      newDFText: '',
      newDFList: [],
      err: {
        type: '',
        msg: '',
      },
      new_df_name: "",
    }
  },
  computed: {
    idm: function() {
      return this.odm + 'RC';
    },
    odfs: {
      get: function() {
        // odfs: [{'name': odf_name}, ...]
        var self = this;
        let tmp = this.checkedDF.map(function(df){
          if(self.df_list[df].hasOwnProperty('custom')){
            // new odf
            return {'name': self.odm + '_' + df};
          }else{
            return {'name': df};
          }
        });
        return tmp.concat(this.smDfInfo.map(function(x) {
          return {'name': x + '_O'};
        }));
      },
      set: function(e) {
        console.log('odf compute set:',e);
        this.checkedDF = e;
      }
    },
    idfs: function() {
      /* idfs: [{
          'name': idf_name,
          'min': min,  // optional, default is 0
          'max': max,  // optional, default is 10
          'default': rc default_value  // optional, rc default is 5, text is 0
        }, ...]
      */
      var self = this;
      var num_index = 1;
      var range_index = 1;
      var ret = this.checkedDF.map(function(odf, i) {
        var idf = self.df_list[odf]['select'];
        var ret = {};
        switch(idf) {
          case 'text':
            ret['name'] = 'Number' + num_index.toString();
            ret['default'] = 0;
            num_index++;
            break;
          case 'range slider':
            ret['name'] = 'RangeSlider' + range_index.toString();
            ret['min'] = self.df_list[odf]['min'];
            ret['max'] = self.df_list[odf]['max'];
            ret['default'] = self.df_list[odf]['default'];
            if(ret['min'] != 0 || ret['max'] != 10 || ret['custom'] == 1){
              // custom idf
              ret['name'] = self.odm + '_' + ret['name'];
            }
            range_index++;
            break;
        }
        return ret;
      });
      return ret.concat(this.smDfInfo.map(function(x) {
        return {'name': x + '_I'};
      }));
    },
    smDfInfo: {
      get: function(){
        return this.checkedSmDF;
      },
      set: function(e) {
        this.checkedSmDF = e;
      }
    },
  },
  //self-defined function for this vue object
  methods: {
    changeTemplate: function(e){
      var selected = e.target.value;
      var found = this.t_list.find(function(element){
        return element.name == selected;
      });
      var tmp_df_list = [];
      var tmp_sm_df_list = [];

      var _this = this;
      found.df_list.forEach(function(df_name){
        console.log("found each ",df_name);
        if (df_name.indexOf("_O") == -1){
          tmp_df_list.push(df_name);
        }else{
          tmp_sm_df_list.push(df_name);
        }
      });
      this.checkedDF = tmp_df_list;
      this.checkedSmDF = tmp_sm_df_list;
    },
    handleData: function(e){
      this.$set(this.dfData, e.name, e.select);
    },
    create: function(e) {
      $('#save-new-card-btn').attr('disabled', true);
      var self = this;
      $.ajax({
        url: urls.lecture.create,
        type: 'PUT',
        contentType: "application/json",
        dataType: 'json',
        processData : false,
        data: JSON.stringify({
          name: this.lecture_name,
          url: this.url,
          odm: {
            name: this.odm,
            dfs: this.odfs,
          },
          idm: {
            name: this.idm,
            dfs: this.idfs,
          },
          joins: this.idfs.map(function(x, i) {
            /*
              [idf_name, odf_name, idf_default_value]
            */ 
            return [x['name'], self.odfs[i]['name'], x['default']];
          }),
          code: self.vp_template,
        }),
        success: function(res){
          // let data = res.body;
          console.log(Date.now(), ' success');
          window.location.href = res.url;
        },
        error: function(err){
          console.log(err);
          $('#save-new-card-btn').attr('disabled', false);
          let res = err.responseJSON;
          // if (res.type === undefined)
          //   return alert(res.reason);

          // self.err.type = res.type;
          // self.err.msg = res.reason;
        }
      })
    },
    NewDF: function(e) {
      this.err.type = '';

      let new_name = this.new_df_name;
      let pass = /^[a-zA-Z](\w*)+$/i.test(new_name);
      if(!pass){
        this.err.type = 'df_name';
        this.err.msg = 'Invalid name';
        return;
      }
      if(new_name in this.df_list){
        this.err.type = 'df_name';
        this.err.msg = 'Duplicate name';
        return;
      }
      if(new_name){
        this.$set(this.df_list, new_name, {'select': 'range slider', 'min': 0, 'max': 10, 'default': 5, 'custom': 1});
        this.checkedDF.push(new_name);
      }
    }
  },
})
