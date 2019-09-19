//SCRIPT FOR RECORDING AND UPLOADING ASSIGNMENTS
///////////////////////////////////////////////////////////////////////////////


//stop start model audio
var first_click = true;
function modelPlay(task){    
    let modAudio = document.getElementById('modelAudio') 
    if (first_click){
      modAudio.src = document.getElementById('modelBtn' + task).value
      first_click = false   
    } else {
      modAudio.src = ""
      first_click = true
    }   
}

function cancel(){
    location.reload();
}

function submit(){
    $("#submit").click();    
}

//remove src of Task audio (??becasue it might mess up later recording??)
function Source(task){
    try { 
        document.getElementById('audioTask' + task).removeAttribute("src")
      }
      catch(err) {
        console.log('audio element has no source');        
      }
      finally {  
        console.log('audio source removed');      
      }   
}


//SHARING LINKS
///////////////////////////////////////////////////////////////////////////////

function saveLink(task){    
    var link = document.getElementById('linkInput' + task).value
    document.getElementById('audioData0'+ task).value = link
    document.getElementById('audioLen0' + task).value = 888
    console.log( 'link stored for task ' + task) 
    setTimeout(func, 1000)
    function func(){ $("#submit").click() }          
}


//UPLOADING FILES
///////////////////////////////////////////////////////////////////////////////
function fileValidation(task){    
    var fileInput = document.getElementById('btnUpload'+ task);
    var filePath = fileInput.value;
    var allowedExtensions = /(\.mp3|\.m4a)$/i;

    if(fileInput.files[0].size > 4400000){
        alert("File is too big!");
        location.reload()
        return false;        
    }
    else if(!allowedExtensions.exec(filePath)){
        alert('Please upload audio file: .mp3/.m4a only.');
        fileInput.value = '';
        return false;
    }    
    else{
        document.getElementById('audioData0' + task).value = "";
        document.getElementById('audioLen0' + task).value = "";
        console.dir( fileInput.files[0] );        
        document.getElementById('audioTask' + task).src = ""        
        var url = window.URL.createObjectURL(fileInput.files[0]);        
        fetch(url)
        .then(function(res){
            return res.blob();
            })
        .then(function(savedBlob){  
        
        var seconds = new Promise ((resolve,reject) =>{
            var savedBlobURL = window.URL.createObjectURL(savedBlob);
            let audio = document.getElementById('audioTask' + task);
            audio.src = savedBlobURL;
            audio.addEventListener('loadedmetadata', function() {
                var audioLen = Math.round(audio.duration);
                if (audioLen > 1){
                    document.getElementById('audioLen0' + task).value = audioLen;
                }
                else {
                    document.getElementById('audioLen0' + task).value = 0;
                }  
                console.log('seconds uploaded:' + audioLen) 
                })  
            setTimeout(func, 1000)
            function func(){ resolve ('length complete for task' + task)}
        })

        var base = new Promise ((resolve,reject) =>{
            var reader = new FileReader();
            reader.readAsDataURL(savedBlob);          
            reader.onloadend = function() {
                base64data = reader.result.split(',')[1];                        
                document.getElementById('audioData0' + task).value = base64data;
                }

            setTimeout(func, 1000)
            function func(){ resolve ('base64 complete for task ' + task)}
        }) 
        
        Promise.all([
            seconds,
            base
        ]).then((messages) => {
            console.log(messages)
            alert ('Your assignment will be updated, please wait')
            $.ajax({
                data : {
                    title : '_' + ($('#assNumber').val() + '_' + task + '_UL'),
                    base64 : base64data
                },
                type : 'POST',
                url : '/audioUpload'                    
            })
            .done(function(data) {                    
                $('#audioData0' + task).val(data.title)
                $("#submit").click();                       
                })     
        })
    })
    
    }//end else    
}//end function

