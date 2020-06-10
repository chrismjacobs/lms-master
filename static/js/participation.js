var qDict = document.getElementById('qDict').innerHTML
var qOBJ = JSON.parse(qDict)
console.log('qOBJ', qOBJ)


startVue(qOBJ)

function startVue(qOBJ){ 
  
  let vue = new Vue({   

    el: '#vue-app',
    delimiters: ['[[', ']]'],
    mounted : function (){
        // start interval for ajax of participation data
        this.ansCheck()
        this.part_timer = setInterval(this.ansCheck, 30000); 
        if (this.mode == 'Reader'){
          for (var btn in this.btnToggle){
            this.btnToggle[btn] = false
          }
          for (var s in this.show){
            this.show[s] = false
          }
        }
        if (this.mode == 'Team'){
          let name_count = (this.teamnames).length 
          console.log('name_count', name_count);
          if (name_count == 1 ){          
            this.mode = 'Writer'                
          }   
          else{
            this.teamSetUp(name_count)
            this.shareAnswer(0) 
          }                   
        }
        if (this.mode == 'Instructor'){
            if (this.userID != 1 ){
              let url = (window.location.href).split('Instructor')[0] + 'Reader'
              console.log('goTO', url);               
              window.location = url
            }
            else{                            
              clearInterval(this.part_timer)
              this.classCheck()
              this.class_timer = setInterval(this.classCheck, 10000);
            } 

        var range = parseInt(this.teamcount) + 1
        for (i = 1; i < range; i++) {
            //this.leaderOBJ[i] = []
            this.leaderOBJ[i] = null
        }
        console.log('LeaderOBJ-mounted', this.leaderOBJ)
        }
    },
    data: {
      qOBJ : qOBJ,
      ansOBJ : null,
      classOBJ : null,
      leaderBar : {},
      leaderOBJ : {},  
      unit : document.getElementById('un').innerHTML,
      part : document.getElementById('pn').innerHTML,
      qs : parseInt(document.getElementById('qs').innerHTML),
      mode :  document.getElementById('mode').innerHTML,
      userID : document.getElementById('userID').innerHTML,
      user : document.getElementById('user').innerHTML,
      teamcount : document.getElementById('teamcount').innerHTML,
      teamnames : JSON.parse(document.getElementById('teamnames').innerHTML),
      TEAMNAMES : [],
      teamShow : true,
      stage : 1, 
      percent : 0, 
      part_timer : null,
      class_timer : null,
      board_timer : null,  
      seeAnswers: false,    
      btnToggle : {
        1 : true,
        2 : true,
        3 : true,
        4 : true,
        5 : true,
        6 : true,
        7 : true,
        8 : true,
      }, 
      show : {
        1 : false,
        2 : false,
        3 : false,
        4 : false,
        5 : false,
        6 : false,
        7 : false,
        8 : false,
      },      
    }, 
    methods: { 
      
      teamSetUp: function (name_count) {
        let rotator = {
          1 : { 
            2 : [0,1,0,1,0,1,0,1],
            3 : [0,1,2,0,1,2,0,1],
            4 : [0,1,2,3,0,1,2,3]
          },
          2 : { 
            2 : [1,0,1,0,1,0,1,0],
            3 : [1,2,0,1,2,0,1,2],
            4 : [1,2,3,0,1,2,3,0]
          },
          3 : { 
            2 : [0,1,0,1,0,1,0,1],
            3 : [2,0,1,2,0,1,2,0],
            4 : [2,3,0,1,2,3,0,1]
          },
          4 : { 
            2 : [1,0,1,0,1,0,1,0],
            3 : [0,2,1,0,2,1,0,2],
            4 : [3,0,1,2,3,0,1,2]
          }         
        }

        let TEAMNAMES = []
        let teamnames = this.teamnames

        if (name_count == 1 ){          
            this.mode = 'Writer'                
        }
        else{
          items = rotator[this.part][name_count]
          console.log('itemsArray', items);
            items.forEach(function(item){
              TEAMNAMES.push(teamnames[item])
            })
        }

        this.TEAMNAMES = TEAMNAMES

        if (name_count == 0 ){
          for (var i = 1; i < 5; i++){            
            this.TEAMNAMES.push(this.teamnames[0])
            this.TEAMNAMES.push(this.teamnames[1])
          }          
        }
        if (name_count == 0 ){
          for (var i = 1; i < 4; i++){
            this.TEAMNAMES.push(this.teamnames[0])
            this.TEAMNAMES.push(this.teamnames[1])
            this.TEAMNAMES.push(this.teamnames[2])
          }          
        }
        if (name_count == 0 ){
          for (var i = 1; i < 3; i++){
            this.TEAMNAMES.push(this.teamnames[0])
            this.TEAMNAMES.push(this.teamnames[1])
            this.TEAMNAMES.push(this.teamnames[2])
            this.TEAMNAMES.push(this.teamnames[3])
          }          
        }
         
        for (let btn in this.btnToggle){
          if (this.TEAMNAMES[btn - 1] != this.user){            
            this.btnToggle[btn] = false
          }
        }  
        
        console.log('TEAMNAMES ', this.TEAMNAMES);
        console.log('btnToggle ', this.btnToggle);

      },    
      showAnswers: function (key){
        if (this.show[key] == true){
          for (var s in this.show){
          this.show[s] = false
          }
        }
        else{
          for (var s in this.show){
            this.show[s] = false
          }
          this.show[key] = true            
        }  
        console.log('showAnswers pressed');     
      },
      stageCheck: function (key){
        if (this.mode == 'Reader') {
          return true
        }
        if (this.mode == 'Team') {
          return this.teamShow
        }
        else if (this.mode == 'Instructor') {
          this.seeAnswers = true
          return false
        }  
        else if (this.mode == 'Writer') {
          if (key == this.stage) {
            return true
          }
          else{
            return false
          }     
        } 
        else {
          alert('No Mode Found')
          return false
        }      
      },
      shareAnswer: function (question){
        console.log('ajax called');        
        let answer = null
        if (question == 0){
          answer = 'start_team'
          console.log(answer);
        }
        else{          
          answer = document.getElementById(question).value
          if (answer.length < 1){
            alert('answer is empty')
            return false
          }  
          this.btnToggle[question] = false      
        }
        
        $.ajax({
          data : {
              unit : this.unit,
              part : this.part,
              question : question, 
              answer : answer,
              qs : this.qs, //qs == number of questions 
                                     
          },
          type : 'POST',
          url : '/shareUpload'                    
          })
          .done(function(data) {
            if (data.action){
              alert(data.answer + ' Members: ' + vue.teamnames)
            }
            if (data.action == '2'){
              vue.teamShow = false
            }            
            vue.stage += 1                              
          })
          .fail(function(){
            alert('Failed, please reload page and try again')
          });  
      },
      ansCheck : function() {
        $.ajax({
          data : {
            unit : this.unit,
            part : this.part,
            check : 0  // signal to return one students data (not whole class)              
          },
          type : 'POST',
          url : '/getPdata',               
        })
        .done(function(data) { 
            console.log(data.dataDict);           
            vue.ansOBJ = JSON.parse(data.dataDict)            
            let count = 1 
            for (let ans in vue.ansOBJ){
              if (vue.ansOBJ[ans] != null){
                console.log(vue.ansOBJ[ans]);
                count += 1
                ///////NEW ADDITON
                vue.btnToggle[ans] = false
              }
            }
            // count starts at one and will be greater than qs 
            // after last answer submitted
            if (count > vue.qs){              
              vue.classCheck()
              vue.class_timer = setInterval(vue.classCheck, 10000);  
              vue.seeAnswers = true
              //alert('The participation has been completed by ' + vue.teamnames)
              clearInterval(vue.part_timer)                           
            }
            vue.stage = count
            console.log(count, vue.ansOBJ);
          })
          .fail(function(){
                  alert('error')
          });
      },
      classCheck : function() {
        $.ajax({
          data : {
            unit : this.unit,
            part : this.part,
            check : 1  // signal to return all class data            
          },
          type : 'POST',
          url : '/getPdata',               
        })
        .done(function(data) { 
          //console.log('classCheck ', data.dataDict);           
          vue.classOBJ = JSON.parse(data.dataDict)

          // clear leader obj back to zero
          for (let lead in vue.leaderOBJ){
            vue.leaderOBJ[lead] = []
          }
          console.log('RESET', JSON.stringify(vue.leaderOBJ));
          console.log('ClassOBJ', vue.classOBJ);


          for (let team in vue.leaderOBJ) {                        
            for (let qn in vue.classOBJ){
              let answer = vue.classOBJ[qn][team]
              if (answer != null && answer.length > 0 ){
                vue.leaderOBJ[team].push(vue.classOBJ[qn][team])                
              }              
            }
          }   
          //console.log('POST PUSH', vue.leaderOBJ);
          //console.log(vue.leaderOBJ[1].length, vue.qs);
          for (let rec in vue.leaderOBJ){
            if (vue.leaderOBJ[rec].length == 0 ){
              var width_percent = '5%'
              var background = 'red'
            } 
            else if (vue.leaderOBJ[rec].length == vue.qs) {
              var width_percent = '100%'
              var background = 'green'              
            }
            else {
              var width = ((vue.leaderOBJ[rec]).length / vue.qs ) * 100
              var width_percent = width + '%'
              var background = 'purple'
            }
            console.log('width ', width_percent);

            vue.leaderBar[rec] = { background:background,  height:'30px', width: width_percent, border: '1px solid grey', 'border-radius': '5px'}
          
            
          }
          var total = 0
          for (let team in vue.leaderOBJ){
            for (let answer in vue.leaderOBJ[team]){
              total += 1              
            }              
          }
          

          var percent_float = ( total / (vue.qs * vue.teamcount )  ) *100
          vue.percent = percent_float.toPrecision(4)
          console.log('%: qs/teamocunt/total/percent', vue.qs, vue.teamcount, total, vue.percent);
            
          })
          .fail(function(){
                  alert('error')
          });
      },
      leaderStyle_notNeeded : function(key){
        console.log('leaderOBJ.key', this.leaderOBJ[key] );
        if (this.leaderOBJ[key] == '100'){
          var bar_color = 'green'
        }
        else {
          var bar_color = 'red'
        }
          var width = this.leaderOBJ[key] + '0%'
          console.log(width);          
          this.leaderBar[key] = { background:bar_color,  height:'20px', width: width, border: '1px solid grey', 'border-radius': '5px'}
          console.log(this.leaderBar);    
      }
          
    } // end methods    
    
    
})// end NEW VUE

}// endFunction 


