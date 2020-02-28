var ansString = document.getElementById('ansDict').innerHTML
var ansOBJ = JSON.parse(ansString)
console.log('ansOBJ', ansOBJ);

var testString = document.getElementById('testDict').innerHTML
var testOBJ = JSON.parse(testString)
console.log('testOBJ', testOBJ);

var teamMembers = document.getElementById('teamMembers').innerHTML
var teamOBJ = JSON.parse(teamMembers)
console.log('teamOBJ', teamOBJ);




startVue(ansOBJ, teamOBJ,)

function startVue(ansOBJ, teamOBJ){ 
  
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
        unit: (window.location.href).split('/qna/')[1].split('/')[0],
        team: (window.location.href).split('/qna/')[1].split('/')[1],        
        
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
        edit : function(question) {
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
        qStyle : function(key) {            
            return this.buttonColor[this.marker[key]]  
        },
        updateAnswers : function() {  
            console.log('update via AJAX');

            $.ajax({
              data : {
                unit : this.unit,
                team : this.team  
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
        resetMarkers : function(q) {             
            for (var mark in vue.marker) {
                if (vue.marker[mark] == 3){
                    if (mark == q) {      
                        alert('Your team member has just edited this question')
                        vue.marker[mark] = 2
                    }
                    else {
                        vue.marker[mark] = 2
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
                ansOBJ : JSON.stringify(this.ansOBJ),                     
                question : key,
                total : total  
              },
              type : 'POST',
              url : '/storeQNA',               
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
    computed : {        

    }
    
    
    
})// end NEW VUE

}// endFunction 

