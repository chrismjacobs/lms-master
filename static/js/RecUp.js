//SCRIPT FOR RECORDING AND UPLOADING ASSIGNMENTS
///////////////////////////////////////////////////////////////////////////////

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


//RECORDING ON ANDROID PHONES AND COMPUTERS
///////////////////////////////////////////////////////////////////////////////

function AnRecord(task){
    let startBtn = document.getElementById('startAn'+ task)
    let stopBtn = document.getElementById('stopAn'+ task)
    let saveBtn = document.getElementById('saveAn'+ task)        
    var constraintObj = {audio: true, video: false };
    navigator.mediaDevices.getUserMedia(constraintObj)
    .then(function(mediaStreamObj) {     
    var mediaRecorder = new MediaRecorder(mediaStreamObj);
    var chunks = []; 
    
    startBtn.onclick = function(){
        console.log('pressed'); 
        startBtn.setAttribute('disabled', true);
        stopBtn.removeAttribute('disabled');        
        mediaRecorder.start();       
        document.getElementById('audioData0' + task).value = "";
        console.log('status:' + mediaRecorder.state);
        dnStart = Date.now()
        console.log('recording started @time: ' + dnStart);
        
        timer = setTimeout(func, 180000) //3 min = 180000 millisecs
        function func(){           
            stopAn.click()
            alert('recording stopped at 3 min ')
            console.log('terminated');  
            }       
    };

    stopBtn.onclick = function(){
        clearTimeout(timer)
        startBtn.removeAttribute('disabled')
        stopBtn.setAttribute('disabled', true);                
        saveBtn.removeAttribute('disabled')
        mediaRecorder.stop(); 
        console.log('status:' + mediaRecorder.state);
        dnStop = Date.now()
        console.log('recording stopped @time:' + dnStop);
        AudioLength = Math.round((dnStop - dnStart)/1000)
        console.log(AudioLength + ' secs recorded');
        saveBtn.innerHTML = 'Save ' + AudioLength + 's'
        startBtn.innerHTML = 'Redo'     
    };
        
    mediaRecorder.ondataavailable = function(ev) {
        chunks.push(ev.data);    
    }

    mediaRecorder.onstop = (ev)=>{
        var blob = new Blob(chunks, { 'audio' : 'audio/mpeg;' });
        console.log(blob);
        chunks = [];// here we clean out the array
        var blobURL = window.URL.createObjectURL(blob);
        document.getElementById('audioLen0' + task).value = AudioLength;
        //get the base64data string from the blob
        var reader = new FileReader();
        reader.readAsDataURL(blob); 
        reader.onloadend = function() {
        base64data = reader.result.split(',')[1]; //remove padding from beginning of string
        document.getElementById('audioData0' + task).value = base64data;
        document.getElementById('android' + task).setAttribute('controls', true)
        document.getElementById('android' + task).src = blobURL
        saveBtn.onclick = function(){
            $.ajax({
                data : {
                    title : '_' + ($('#assNumber').val() + '_' + task + '_AN'),
                    base64 : base64data
                },
                type : 'POST',
                url : '/audioUpload'                    
            })
            .done(function(data) {                    
                $('#audioData0' + task).val(data.title)
                $("#submit").click();                       
                })                        
        }//end saveBtnGR
        }//end reader.onload
    };// end media.onstop
})
.catch(function(err) {
    alert('Cannot record on this device - Please try Upload') 
    console.log(err.name, err.message);
});

}//} end function AnRecord



//UPLOADING AND SHARING LINKS
///////////////////////////////////////////////////////////////////////////////

function saveLink(task){    
    var link = document.getElementById('linkInput' + task).value
    document.getElementById('audioData0'+ task).value = link
    document.getElementById('audioLen0' + task).value = 1
    console.log( 'link stored for task ' + task) 
    setTimeout(func, 1000)
    function func(){ $("#submit").click() }          
}

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
                document.getElementById('audioLen0' + task).value = audioLen;
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

