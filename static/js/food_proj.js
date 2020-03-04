var ansString = document.getElementById('ansString').innerHTML
var ansOBJ = JSON.parse(ansString)
console.log('ansOBJ', ansOBJ);

var name = document.getElementById('name').innerHTML



startVue(ansOBJ)

function startVue(ansOBJ){ 
  
  let vue = new Vue({   

    el: '#vue-app',
    delimiters: ['[[', ']]'],   
    mounted: function () {        
    },    
    data: {                        
        ansOBJ: ansOBJ,
        name : name,
        updateReady : true,
        pptLink : false,
        project: (window.location.href).split('/food/')[1],       
        script: {
            ND : {
                1 : 'If Taiwan were going to vote for a national dish I would choose ', 
                2 : 'This is for three reasons', 
                3 : 'First of all,', 
                4 : 'The next reason is', 
                5 : 'The last point is',
            },        
            CV : {
                1 : 'Today I want to share with you a recipe for ', 
                2 : 'I choose this video because', 
                3 : 'Some important ingredients are...', 
                4 : 'To prepare this dish you will need...', 
                5 : 'This recipe is...',  
            },        
        },
        
    }, 
    methods: {  
        wordCount : function(mark) { 
            console.log(mark); 
            var wc = (document.getElementById(mark).value).split(' ')
            console.log(wc.length);
            if (wc.length < 8) {
                alert('This sentence seems too short - try making it longer with conjunction phrases (but/so/when/if/because..)')
            }           

            return true
        },
        style : function(mark) { 
            if (mark.includes('kw')){
                var bg = 'silver'
            }
            else if (mark.includes('dt')){
                var bg = 'darkorange'
            }           
            else if (mark.includes('Rea')){
                var bg = 'PALEVIOLETRED'
            }           
            else if (mark.includes('Int')){
                var bg = 'DARKCYAN'
            }           

            return {padding:'4px', 'font-size':'15px', background:bg, color:'white', border:'1px sold white', 'border-radius':'5px', width:'20%'}

        },
        updatePlan : function() { 
            vue.ansOBJ['Writer'] = name 
            console.log('update via AJAX');
            console.log(this.ansOBJ);
            //return false

            $.ajax({
              data : {
                proj : this.project,
                ansOBJ : JSON.stringify(this.ansOBJ)  
              },
              type : 'POST',
              url : '/updateFood',               
            })
            .done(function(data) { 
                alert('Your FORM has been updated')                
            })
            .fail(function(){
                alert('error has occurred');
            });
        },     
        createPPT : function() { 
            console.log('CreatePPT');            

            $.ajax({
              data : {
                proj : this.project,
                name : this.name,
                ansOBJ : JSON.stringify(this.ansOBJ)  
              },
              type : 'POST',
              url : '/createPPT',               
            })
            .done(function(data) { 
                if(data.error){
                    alert('There has been an error. Please check that your FORM is complete or see your instructor');
                }
                else{
                    alert('Your ppt has been created') 
                    vue.pptLink = data.pptLink
                }
                               
            })
            .fail(function(){
                alert('There has been an error. Please check that your FORM is complete or see your instructor');
            });
        }      
    }, // end methods        
    
    
    
})// end NEW VUE

}// endFunction 

