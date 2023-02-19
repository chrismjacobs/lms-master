
let unit_number = document.getElementById('unit').innerHTML
console.log(unit_number)

let fullString = document.getElementById('fullDict').innerHTML
let fullOBJ = JSON.parse(fullString)
let info = JSON.parse(fullOBJ['info']) 


let publish = JSON.parse(fullOBJ['publish']) 
let imageLink = publish['imageLink']
let title = publish['title']
console.log(imageLink);


// check revison has been done
let revise = JSON.parse(fullOBJ['revise']) 

let revised = revise['revised']
if (revised == null){
    console.log('No data')
    alert('Please wait for instructors revision')
    window.location = (window.location.href).split('work')[0] + 'work/topic' + '/' + unit_number   
}

let text = revise['text']

startVue(info, revised)

function startVue(info, revised){ 
    let app = new Vue({   

    el: '#vue-app',
    delimiters: ['[[', ']]'],
    mounted : function (){ 
        document.getElementById('final_image').src = imageLink   
    },     
    data: {
        publish : revised,       
        info : info, 
        base64data : null, 
        fileType : null, 
        title : title,        
        save : false,
        imageLink : imageLink,        
        theme : { color : info['theme'],  display:'inline-block', 'font-size': '25px'}    
    }, 
    methods: { 
        selectText: function(id){
            console.log(id)            
            document.getElementById(id).setAttribute('class', 'input2')          
        },
        deSelect: function(id, start){
            if (start!='start') {
                this.save = true
                }    
            
            console.log('SAVE', this.revText );            
              
            let textBox = document.getElementById(id)
            console.log('Height', textBox.scrollHeight)
            textBox.setAttribute('class', 'input3') 
            textBox.setAttribute('style', 'height:' + textBox.scrollHeight +'px !important')            
        },  
        image: function () {
            selectedFile = document.getElementById('pic').files[0]

            console.log(selectedFile)
            var form_data = new FormData();

            form_data.append('image', document.getElementById('pic').files[0])
            form_data.append()
            console.log(form_data);
            sendImage(form_data)       
        }, 
        fileValidation : function(){    
          var fileInput = document.getElementById('pic');        
          console.log('file', fileInput)
          var filePath = fileInput.value;
          console.log(filePath);
          app.fileType = filePath.split('.')[1]

          var allowedExtensions = /(\.jpeg|\.png|\.jpg)$/i;
      
            if(fileInput.files[0].size > 4400000){
                alert("File is too big!"); 
                fileInput.value = '';             
                return false;        
            }
            else if(!allowedExtensions.exec(filePath)){
                alert('Please upload image: .jpeg/.png only.');
                fileInput.value = '';
                return false;
            }    
            else{            
                console.dir( fileInput.files[0] );    
                var url = window.URL.createObjectURL(fileInput.files[0]);        
                fetch(url)
                .then(function(res){
                    return res.blob();
                    })
                .then(function(savedBlob){
                    var reader = new FileReader();
                    reader.readAsDataURL(savedBlob);          
                    reader.onloadend = function() {
                        app.base64data = reader.result.split(',')[1];  
                        console.log(app.base64data); 
                        setTimeout(app.uploadImage() , 10000)
                        
                        } 
                })  
            }//end else
              
        },//end fileValidation  
        uploadImage: function (){
            console.log()
            $.ajax({    
                type : 'POST',
                data : {
                    unit : document.getElementById('unit').innerHTML, 
                    b64String : app.base64data,
                    fileType : app.fileType                                       
                          
                },
                url : '/sendImage',    
            })
            .done(function(data) {              
                if (data) {
                    console.log(data.imageLink);    
                    app.imageLink = data.imageLink  
                    document.getElementById('final_image').src = app.imageLink    
                }
            });
        },
        sendData: function (){            
            $.ajax({    
                type : 'POST',
                data : {
                    unit : document.getElementById('unit').innerHTML, 
                    obj : null,
                    final : app.publish,
                    title : app.title, 
                    imageLink : app.imageLink,
                    stage : 5,                     
                    work : 'publish'           
                },
                url : '/storeData',    
            })
            .done(function(data) {              
                if (data) {                
                    alert('Thank you ' + data.name + ', your ' + data.work + ' has been saved')
                    window.location = (window.location.href).split('work')[0] + 'work/topic' + '/' + unit_number         
                }
            });
        },
        readRefs: function(){             
            this.sendData(this.revText) 
            alert('Please wait a moment while your writing is being updated') 
        }, 
        cancel: function(){
            alert('You have cancelled so your changes will not be saved')
            window.location = (window.location.href).split('work')[0] + 'work/topic' + '/' + unit_number         
        }      
    }
    
})// end NEW VUE

}// end start vue function