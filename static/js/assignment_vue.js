var name = document.getElementById('name').innerHTML

var ansString = document.getElementById('ansString').innerHTML
console.log(ansString);
var ansOBJ = JSON.parse(ansString)
console.log('ansOBJ', ansOBJ);

var report = navigator.userAgent
console.log(report);
var device = null
var notice = null



if (report.includes('Windows')){
  device = 'A'
  notice = 'Recording in Windows'
}
else if (report.includes('Line')){
    device = 'L'
    notice = 'WARNING - LINE APP cannot be used for recording'
}
else if (report.includes('FB')){
    device = 'FB'
    notice = 'WARNING - FACEBOOK APP cannot be used for recording'
}
else if (report.includes('Android')){
    device = 'A'
    notice = 'Recording in Android'
}
else if (report.includes('Macintosh')){
    device = 'I'
    notice = 'Recording on Mac, recording may not work on this computer'
}
else if (report.includes('iPad')){
    notice = 'Recording on iPad may not work; please upload file or use a phone/computer'
    device = 'I'
}
else if (report.includes('iPhone OS 11')){
    device = 'I'
    notice = 'Recording in iOS 11'
}
else if (report.includes('iPhone OS 12')){
  device = 'I'
  notice = 'Recording in iOS 12'
}
else if (report.includes('iPhone OS 13')){
  device = 'I'
  notice = 'Recording in iOS 13'
}
else if (report.includes('iPhone OS 14')){
  device = 'I'
  notice = 'Recording in iOS 14'
}
else if (report.includes('iPhone OS 15')){
  device = 'I'
  notice = 'Recording in iOS 15'
}
else if (report.includes('iPhone OS 16')){
  device = 'I'
  notice = 'Recording in iOS 16'
}
else if (report.includes('iPhone OS 17')){
  device = 'I'
  notice = 'Recording in iOS 17'
}
else if (report.includes('iPhone OS 18')){
  device = 'I'
  notice = 'Recording in iOS 18'
}
else {
  device = 'U'
  notice = 'Your OS may not work; if so try upload a file, share a link, or use a computer; ' + report
}
console.log('DEVICE', device);


if (name == 'Test'){
  alert('Hi Test, this is a test:  ' + device +'__'+ notice )
}

//iphone recording
window.globalFunc = function (action){
  console.log('global started');
  window.URL = window.URL || window.webkitURL;
  /**
   * Detect the correct AudioContext for the browser
   * */
  window.AudioContext = window.AudioContext || window.webkitAudioContext;
  navigator.getUserMedia  = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
  var recorder = new RecordVoiceAudios();


  if (action == 'start'){
    recorder.startRecord()
    console.log('recorder start');
  }
  else if (action == 'stop'){
    recorder.stopRecord();
  }

  function RecordVoiceAudios() {

      let encoder = null;
      let microphone;

      var audioContext;
      let processor;
      let config = {
          bufferLen: 4096,
          numChannels: 2,
          mimeType: 'audio/mpeg'
      };
      console.log('load rec voice');

      this.startRecord = function() {
        console.log('startRecord');
          audioContext = new AudioContext();
          /** Create a ScriptProcessorNode with a bufferSize of
          * 4096 and two input and output channel
          * */
          if (audioContext.createJavaScriptNode) {
              processor = audioContext.createJavaScriptNode(config.bufferLen, config.numChannels, config.numChannels);
              console.log('java processer');
          } else if (audioContext.createScriptProcessor) {
              processor = audioContext.createScriptProcessor(config.bufferLen, config.numChannels, config.numChannels);
              console.log('script processer');
          } else {
              console.log('WebAudio API has no support on this browser.');
          }
          processor.connect(audioContext.destination);
          /**
          *  ask permission of the user for use microphone or camera
          * */
          navigator.mediaDevices.getUserMedia({ audio: true, video: false })
          .then(gotStreamMethod)
          .catch('logError');
      };

      let getBuffers = (event) => {
          var buffers = [];
          for (var ch = 0; ch < 2; ++ch)
              buffers[ch] = event.inputBuffer.getChannelData(ch);
          return buffers;
      }

      let gotStreamMethod = (stream) => {

          config = {
              bufferLen: 4096,
              numChannels: 2,
              mimeType: 'audio/mpeg'
          };

          let tracks = stream.getTracks();
          /**Create a MediaStreamAudioSourceNode for the microphone **/
          microphone = audioContext.createMediaStreamSource(stream);
          /**connect the AudioBufferSourceNode to the gainNode **/
          microphone.connect(processor);
          encoder = new Mp3LameEncoder(audioContext.sampleRate, 160); //bitRate set to 160
          /** Give the node a function to process audio events **/
          processor.onaudioprocess = function(event) {
              encoder.encode(getBuffers(event));
              console.log('MP3 encoding');
          };

          stopBtnRecord = () => {
                  var stage = 1
                  console.log('stop Record');
                  audioContext.close();
                  processor.disconnect();
                  tracks.forEach(track => track.stop());
                  stage = 2
                  audioElement = document.getElementById('handler')
                  audioElement.src = URL.createObjectURL(encoder.finish());
                  stage = 3

                  globlob = audioElement.src

                    fetch(audioElement.src)
                    .then( response => response.blob() )
                    .then( blob =>{
                        var reader = new FileReader();
                        reader.readAsDataURL(blob);
                        reader.onload = function(){
                            var base64data = this.result.split(',')[1]  // <-- this.result contains a base64 data URI
                            b64d = base64data
                        }; //end reader.onload

                    })//end fetch then
                    .catch((error) => {
                      console.log(error);
                      recErrorWin(error);
                    })
                  return stage

          };// stopRecord
      }
      this.stopRecord = function() {
        try{
          var stage = stopBtnRecord()
          console.log(stage);
        }
        catch {
          recErrorWin('Apple fail before fetch');
        }

      };
  }
}


function recErrorWin (message){

  $.ajax({
    data : {
        unit : 'A',
        message : message,
        mode : notice
    },
    type : 'POST',
    url : '/recError'
    })
    .done(function(data) {
      alert('error has occured - your device is unable to record - please try to upload mp3 instead - sorry for the inconvenience')
    })
    .fail(function(){
      alert('error has occured - your device is unable to record - please try to upload mp3 instead - sorry for the inconvenience')
    });

}


//device = 'U'
let b64d = 'nothing'
let globlob = 'noURL'




startVue(ansOBJ, device)

function startVue(ansOBJ, device){

  let vue = new Vue({

    el: '#vue-app',
    delimiters: ['[[', ']]'],
    mounted: function () {
      this.audioCheck()
      if (device == 'U'){
        this.showUpload('up')
      }
    },
    data: {
        title: {
          1 : 'Task 1 Pronunciation Practice',
          2 : 'Task 2 Speaking Practice'
        },
        notice : notice,
        show: {
          1 : true,
          2 : true
        },
        audio: {
          1 : null,
          2 : null
        },
        uploadBTN : {
          1 : ['upbtn1', 'uplink1'],
          2 : ['upbtn2', 'uplink2']
        },
        ansOBJ: ansOBJ,
        device: device,
        rec1: {
            start : true,
            stop : false,
            save : false,
            cancel : false,
            timer : false,
            t_style: false,
            count : false
        },
        n1 : this.ansOBJ['3']['Notes'],
        t1 : this.ansOBJ['3']['TextOne'],
        t2 : this.ansOBJ['3']['TextTwo'],
        rec_timer : null,
        mediaRecorder : null,
        audio_source : null,
        base64data : null,
        blobURL : null,
        upload : false
    },
    methods: {
      start : function(arg){

        for (var key in vue.show){
          console.log(key, arg, vue.show);
          if (key != arg) {
            vue.show[key] = false
          }
        }

        vue.rec1.start = false
        vue.rec1.stop = true
        vue.rec1.timer = true
        vue.timer()

        if (this.device == 'A') {
        var constraintObj = {audio: true, video: false };
        navigator.mediaDevices.getUserMedia(constraintObj)
            .then(function(mediaStreamObj) {
                vue.mediaRecorder = new MediaRecorder(mediaStreamObj);
                var chunks = [];
                vue.mediaRecorder.start();
                console.log('status:' + vue.mediaRecorder.state);

              vue.mediaRecorder.ondataavailable = function(ev) {
                chunks.push(ev.data);
              }

              vue.mediaRecorder.onstop = (ev)=>{
                    try{
                      var blob = new Blob(chunks, { 'audio' : 'audio/mpeg;' });
                      console.log(blob);
                      chunks = [];// here we clean out the array
                      var blobURL = window.URL.createObjectURL(blob);
                      console.log(blobURL);
                      //get the base64data string from the blob
                      reader = new FileReader();
                      reader.readAsDataURL(blob);
                      reader.onloadend = function() {
                        vue.base64data = reader.result.split(',')[1]; //remove padding from beginning of string
                        vue.blobURL = blobURL
                      }
                    }
                    catch(err) {
                      console.log(err.message);
                      vue.recError(err.message)
                    }
                }
             })
          }
          else if (this.device == 'I'){
            // global function for iphone recording
            window.globalFunc('start')
          }
      },
      stop: function(task){

        vue.rec1.stop = false
        vue.rec1.save = true
        vue.rec1.cancel = true
        clearInterval(vue.rec_timer)
        console.log(this.device);

            if (this.device == 'A') {
              console.log('stopped');
              vue.audio[task] = 3
              vue.mediaRecorder.stop();
              console.log('status:' + vue.mediaRecorder.state);
            }
            else if (this.device == 'I'){
              // global function for iphone recording
              vue.audio[task] = 3
              window.globalFunc('stop')
              vue.blobURL = globlob
              console.log('status: mp3 rec stopped');
            }


      },
      cancel: function(){
        console.log('cancel');
        for (var key in vue.rec1){
        vue.rec1[key] = false
        }
        vue.rec1.start = true


        vue.show['1'] = true
        vue.show['2'] = true
        vue.base64data = null
        vue.blobURL = null
        this.audioCheck()
      },
      recError : function (message){

        $.ajax({
          data : {
              unit : vue.ansOBJ.Unit,
              message : message,
              mode : notice
          },
          type : 'POST',
          url : '/recError'
          })
          .done(function(data) {
            vue.showUpload('up')
            alert('error has occured - your device is unable to record - please try to upload mp3 instead - sorry for the inconvenience')
          })
          .fail(function(){
            vue.showUpload('up')
            alert('error has occured - your device is unable to record - please try to upload mp3 instead - sorry for the inconvenience')
          });
          console.log(vue.ansOBJ);
      },
      save : function (task, mark){
        if (this.device == 'I'){
          vue.base64data = b64d
        }
        let task_title
        if (task == '3'){
          task_title = 'text'
        }
        else{
          vue.ansOBJ[task]['Length'] = vue.rec1.count
          task_title = (vue.ansOBJ.Unit + '_' + task + '_' + device)
        }
        if (mark == 'link'){
          task_title = 'link'
        }

        $.ajax({
          data : {
              task : task,
              unit : vue.ansOBJ.Unit,
              title : task_title,
              base64 : vue.base64data,
              ansDict : JSON.stringify(vue.ansOBJ),
              Notes : this.n1,
              TextOne : this.t1,
              TextTwo : this.t2,
          },
          type : 'POST',
          url : '/audioUpload'
          })
          .done(function(data) {
              if (task < 3 ){
                vue.ansOBJ[task]['AudioData'] = data.title
                vue.ansOBJ[task]['Length'] = vue.rec1.count
              }
              vue.cancel()
              if (data.grade == 0){
                alert('Upload successful\r\nKeep going')
              }
              else if (data.grade == 1){
                alert('Assignment complete\r\nLate submission\r\n1 point\r\nGo back to assignments')
              }
              else if (data.grade == 2){
                alert('Assignment completed on time\r\n 2 points\r\nGo back to assignments')
              }

          })
          .fail(function(){
            alert('Upload Failed, there has been an error. Reload the page and if it happens again please tell you instructor')
          });
          console.log(vue.ansOBJ);
      },
      audioCheck : function(){
        if (this.ansOBJ['1']['AudioData'] == null){
          this.audio['1'] = 1
        }
        else{
          this.audio['1'] = 2
        }
        if (this.ansOBJ['2']['AudioData'] == null){
          this.audio['2'] = 1
        }
        else{
          this.audio['2'] = 2
        }
      },
      showUpload : function(arg){
        if (arg == 'up'){
          this.upload = true
          this.show['1'] = false
          this.show['2'] = false
        }
        else if (arg == 'rec'){
          this.upload = false
          this.show['1'] = true
          this.show['2'] = true
        }
      },
      timer : function (task){
        vue.rec_timer = setInterval(function() {
            if (vue.rec1.count) {
              console.log(vue.rec1.count);
            }
            else{
              vue.rec1.count = 0
            }

            vue.rec1.count += 1
            if (vue.rec1.count == 121){
                vue.stop(task)
                console.log('timer_terminated');
            }
            else {
                var width =  vue.rec1.count + '%'
                var color = 'indianred'
                if (vue.rec1.count > 80){
                  color = 'red'
                }
                else if (vue.rec1.count > 30){
                  color = 'mediumseagreen'
                }
                else if (vue.rec1.count > 20) {
                  color = 'khaki'
                }
                else if (vue.rec1.count > 10) {
                  color = 'coral'
                }
                vue.rec1.t_style = { height:'30px', width:width, background:color, color:'white', 'border-radius': '5px', border: '1px solid white' }
            }
          }, 1000)
      },
      playAudio : function (arg) {

        let playlist = {
          '0' : vue.blobURL,
          '1' : vue.ansOBJ['1']['AudioData'],
          '2' : vue.ansOBJ['2']['AudioData'],
          '3' : vue.ansOBJ['1']['model'],
          '4' : vue.ansOBJ['2']['model'],
        }
        player = document.getElementById('handler')

        player.src = playlist[arg]



      },
      fileValidation : function(task){
        var fileInput = document.getElementById('upbtn'+ task);
        console.log('file', fileInput)
        var filePath = fileInput.value;
        var allowedExtensions = /(\.mp3|\.m4a|\.m4v|\.mov|\.mp4|\.aac)$/i;

        if(fileInput.files[0].size > 88000000){
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
            console.dir( fileInput.files[0] );
            var url = window.URL.createObjectURL(fileInput.files[0]);
            fetch(url)
            .then(function(res){
                return res.blob();
                })
            .then(function(savedBlob){

            var seconds = new Promise ((resolve,reject) =>{
                var savedBlobURL = window.URL.createObjectURL(savedBlob);
                let audio = document.getElementById('handler');
                audio.src = savedBlobURL;
                audio.addEventListener('loadedmetadata', function() {
                    var audioLen = Math.round(audio.duration);
                    vue.rec1.count = audioLen
                    console.log('seconds uploaded: ' + vue.rec1.count)
                    })
                setTimeout(func, 1000)
                function func(){ resolve ('length complete for task' + task)}
            })

            var base = new Promise ((resolve,reject) =>{
                var reader = new FileReader();
                reader.readAsDataURL(savedBlob);
                reader.onloadend = function() {
                    vue.base64data = reader.result.split(',')[1];
                    }
                setTimeout(func, 1000)
                function func(){ resolve ('base64 complete for task ' + task)}
            })

            Promise.all([ seconds, base ])
            .then((messages) => {
                console.log(messages)
                alert ('Your assignment will be updated, please wait')
                vue.save(task)
                })
            })
        }//end else
      },//end fileValidation
      saveLink : function(task){
        vue.base64data = document.getElementById('uplink' + task).value
        vue.rec1.count = 1
        console.log( 'link stored for task ' + task)
        this.save(task, 'link')
    }
    } // end methods



})// end NEW VUE

}// endFunction



