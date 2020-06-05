var ansString = document.getElementById('ansDict').innerHTML
var ansOBJ = JSON.parse(ansString)
console.log('ansOBJ', ansOBJ);

var testString = document.getElementById('testDict').innerHTML
var testOBJ = JSON.parse(testString)
console.log('testOBJ', testOBJ);

var teamMembers = document.getElementById('teamMembers').innerHTML
var teamOBJ = JSON.parse(teamMembers)
console.log('teamOBJ', teamOBJ);

const mode = (window.location.href).split('/abc/')[1].split('/')[0]
const unit = (window.location.href).split('/abc/')[1].split('/')[1]
const team = (window.location.href).split('/abc/')[1].split('/')[2]
console.log(mode, unit, team);


startVue()

function startVue(){ 
  
  let vue = new Vue({   

    el: '#vue-app',
    delimiters: ['[[', ']]'],   
    mounted: function () {
        setInterval(function(){
            vue.updateAnswers()
        }, 15000)
        setTimeout(function(){
           vue.checkMarkers()
        }, 2000);
        

    },    
    data: {                        
        ansOBJ: ansOBJ,         
        teamOBJ: teamOBJ,
        testOBJ: testOBJ, 
        mode: mode, 
        unit: unit,
        team: team,  
        marker:{
            1 : 1, 
            2 : 1, 
            3 : 1, 
            4 : 1, 
            5 : 1, 
            6 : 1, 
        },
        buttonColor:{
            3 : {background: 'dodgerblue', padding: '5px'},             
            2 : {background: 'mediumseagreen', padding: '5px'},             
            1 : {background: 'lightcoral', padding: '5px'}   
        }
    }, 
    methods: {  
        editMarkers : function(question) {
            if (this.marker[question] == 3 ) {
                this.checkMarkers()
            }
            else{
                this.checkMarkers()
                this.marker[question] = 3 
                let testString = JSON.stringify(this.ansOBJ[question])
                this.testOBJ[question] = JSON.parse(testString) 
            }   
        },
        resetMarkers : function(q) {             
            for (var mark in vue.marker) {
                if (vue.marker[mark] == 3){
                    if (mark == q) {      
                        alert('Your team member has just edited this question')
                        vue.marker[mark] = 2
                    }
                    else {
                        console.log('Your team mate just updated question ' + mark)
                    }
                }
                else {
                    vue.marker[mark] = 2
                }                
            }
        },
        checkMarkers : function() {
            for (var mark in vue.marker) {
                if (this.ansOBJ[mark]['writer']){
                    vue.marker[mark] = 2                    
                }
                else {
                    vue.marker[mark] = 1
                }                               
            }
        },        
        qStyle : function(key) {            
            return this.buttonColor[this.marker[key]]  
        },
        updateAnswers : function() {  
            console.log('update via AJAX');

            $.ajax({
              data : {
                unit : this.unit,
                team : this.team,  
                mode : this.mode,  
              },
              type : 'POST',
              url : '/updateAnswers',               
            })
            .done(function(data) { 
                var newOBJ = JSON.parse(data.ansString) 
                for (var q in vue.ansOBJ){
                    if (   JSON.stringify(newOBJ[q]) != JSON.stringify(vue.ansOBJ[q])   ){
                        //alert(JSON.stringify(newOBJ[q]))
                        vue.ansOBJ = newOBJ
                        vue.resetMarkers(q) 
                    }
                }  
            })
            .fail(function(){
                console.log('error has occurred');
            });
        },
        storeData : function(key) {            
            this.ansOBJ[key]['writer'] = document.getElementById(key + 'w').innerHTML          
            this.ansOBJ[key]['answer'] = document.getElementById(key + 'a').value          
            this.ansOBJ[key]['question'] = document.getElementById(key + 'q').value         
            this.ansOBJ[key]['topic'] = document.getElementById(key + 't').value        
            //console.log(this.ansOBJ);
            
            console.log(this.ansOBJ.values);
            //reset the testOBJ
            this.testOBJ = testOBJ
            this.checkMarkers()   
            
            var total = 0
            for (var mark in this.marker){
                total += this.marker[mark]
            }
            console.log(total);

            $.ajax({
              data : {
                unit : this.unit,
                team : this.team,
                mode : this.mode,
                ansOBJ : JSON.stringify(this.ansOBJ),                     
                question : key,
                total : total  
              },
              type : 'POST',
              url : '/storeAnswer',               
            })
            .done(function(data) { 
                console.log(data); 
                alert('Question ' + data.question + ' updated') 
                vue.updateAnswers()         
            })
            .fail(function(){
                alert('error - see instructor')
            });
        }
                    
    }, // end methods        
    
    
    
})// end NEW VUE

}// endFunction 

