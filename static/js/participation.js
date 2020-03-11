var qDict = document.getElementById('qDict').innerHTML
var qOBJ = JSON.parse(qDict)
console.log('qOBJ', qOBJ);


startVue(qOBJ)

function startVue(qOBJ){ 
  
  let vue = new Vue({   

    el: '#vue-app',
    delimiters: ['[[', ']]'],
    mounted : function (){
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
            this.leaderOBJ[i] = []
            this.leaderOBJ[i] = null
        }
        console.log('TEST', this.leaderOBJ)
                         
            

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
      teamcount : document.getElementById('teamcount').innerHTML,
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
        this.btnToggle[question] = false
        let answer = document.getElementById(question).value
        if (answer.length < 1){
          alert('answer is empty')
          return false
        }
        
        $.ajax({
          data : {
              unit : this.unit,
              part : this.part,
              question : question, 
              answer : answer,
              qs : this.qs,
                                     
          },
          type : 'POST',
          url : '/shareUpload'                    
          })
          .done(function(data) {
            if (data.action){
              alert(data.answer)
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
            check : 0  // signal to return all class data              
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
              }
            }
            // count starts at one and will be greater than qs 
            // after last answer submitted
            if (count > vue.qs){
              
              vue.classCheck()
              vue.class_timer = setInterval(vue.classCheck, 10000);  
              vue.seeAnswers = true
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
          console.log('POST PUSH', vue.leaderOBJ);

          for (let rec in vue.leaderOBJ){

            var width = ((vue.leaderOBJ[rec]).length / vue.qs ) * 100
            var width_percent = width + '%'
            console.log(width);
            vue.leaderBar[rec] = { background:'red',  height:'20px', width: width_percent, border: '1px solid grey', 'border-radius': '5px'}
          
            
          }
          var total = 0
          for (let team in vue.leaderOBJ){
            console.log('TEAM', vue.leaderOBJ[team]);
            total += 1
          }
          

          var percent_float = ( total / (vue.qs * vue.teamcount )  ) *100
          vue.percent = percent_float.toPrecision(4)
          console.log('%: qs/teamocunt/total/percent', vue.qs, vue.teamcount, total, vue.percent);
            
          })
          .fail(function(){
                  alert('error')
          });
      },
      leaderStyle : function(key){
          var width = this.leaderOBJ[key] + '0%'
          console.log(width);          
          this.leaderBar[key] = { background:'red',  height:'20px', width: width, border: '1px solid grey', 'border-radius': '5px'}
          console.log(this.leaderBar);    
      }
          
    } // end methods    
    
    
})// end NEW VUE

}// endFunction 


