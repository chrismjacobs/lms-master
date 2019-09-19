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
        ///////////////////////////////
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


