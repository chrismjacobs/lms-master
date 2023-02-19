topJS = document.getElementById('topics').innerHTML
topOBJ = JSON.parse(topJS)
console.log('topOBJ', topOBJ);
       
startVue(topOBJ)
 


function startVue(topOBJ){ new Vue({   

    el: '#vue-app',
    delimiters: ['[[', ']]'],  
    data: {
        topOBJ: topOBJ                      
    }, 
    methods: {
        barStyle: function(theme, stage){   
            if (stage==5){
                return {background: theme, width : '90%', height : '15px', display : 'inline-block', border : '2px solid white' }  
            }       
            var stage_bar = {
                0 : '2%', 
                1 : '20%', 
                2 : '35%', 
                3 : '55%', 
                4 : '75%'
            }            
            var width = stage_bar[stage] 
            return {background: theme, width : width, height : '15px', display : 'inline-block' }        
        }, 
        goTo: function(key){
            window.location = (window.location.href).split('topic_list')[0] + 'work/topic/' + key   
        }
                  
    }     

    
})// end NEW VUE

}
