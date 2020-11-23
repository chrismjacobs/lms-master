//var name = document.getElementById('name').innerHTML

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
    notice = 'Rec in Android'
}
else if (report.includes('Macintosh')){
    device = 'A'
    notice = 'Recording on Mac'
}
else if (report.includes('iPad')){
    notice = 'Rec on iPad; may not work'
    device = 'I'
}
else if (report.includes('iPhone OS 11')){
    device = 'I'
    notice = 'Rec iOS 11'
}
else if (report.includes('iPhone OS 12')){
  device = 'I'
  notice = 'Rec iOS 12'
}
else if (report.includes('iPhone OS 13')){
  device = 'I'
  notice = 'Rec iOS 13'
}
else if (report.includes('iPhone OS 14')){
  device = 'I'
  notice = 'Rec iOS 14'
}
else if (report.includes('iPhone OS 15')){
  device = 'I'
  notice = 'Rec iOS 13'
}
else {
  device = 'U'
  notice = 'Your iOS will not work; if so please use a computer'
}
console.log('DEVICE', device);

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


  /// device = A or Windows
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
          // alert(audioContext)
          if (audioContext.createJavaScriptNode) {
              processor = audioContext.createJavaScriptNode(config.bufferLen, config.numChannels, config.numChannels);
              console.log('java processor');
          } else if (audioContext.createScriptProcessor) {
              processor = audioContext.createScriptProcessor(config.bufferLen, config.numChannels, config.numChannels);
              console.log('script processor');
          } else {
              console.log('WebAudio API has no support on this browser.');
          }
          processor.connect(audioContext.destination);
          /**
          *  ask permission of the user for use microphone or camera
          * */
         // alert(processor)
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





          let count = 0
          let countSpan = document.getElementById('count')
          video = document.getElementById('vid')

          // let marker = true
          processor.onaudioprocess = function(event) {
              encoder.encode(getBuffers(event));
              console.log('MP3 encoding');
              countSpan.innerHTML = count

              if (count == 1) {
                video.play()
              }
              count += 1
          };


          stopBtnRecord = () => {
                  // alert(1)
                  var stage = 1
                  console.log('stop Record');
                  audioContext.close();
                  // alert(2)
                  processor.disconnect();
                  // alert(3)
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
                      //recErrorWin(error);
                    })
                  return stage

          };// stopRecord
      }
      this.stopRecord = function() {
        // mark to see if iphone is recording or not
        try{
          var stage = stopBtnRecord()
          console.log(stage);
        }
        catch {
          alert('Video stopped')
          console.log('recErrorWin')
        }

      };
  }
}

var mString = document.getElementById('mString').innerHTML
var mData = document.getElementById('mData').innerHTML
console.log(mData)

var movieData = JSON.parse(mData)
var mObj = JSON.parse(mString)
console.log('mObj', mObj);
console.log('mData', movieData);

var str = window.location.href
let movie = str.split('nme_mov/')[1][0]

var subtitles = mObj['subtitles']
console.log('subs', subtitles)

//device = 'U'4
let b64d = 'nothing'
let globlob = 'noURL'


startVue()

function startVue(){

  let vue = new Vue({

    el: '#vue-app',
    delimiters: ['[[', ']]'],
    mounted: function () {
      video = document.getElementById('vid')
      audio = document.getElementById('aud')
      video.src = subtitles

      if (movieData['audio'] != null) {
        console.log('check audio',  movieData['audio'])
        audio.src = movieData['audio']
      }
    },
    data: {
        mObj: mObj,
        movieData: movieData,
        movie: movie,
        part: 4,
        notice : notice,
        device: device,
        videoSRC: subtitles,
        rec1: {
            start : true,
            stop : false,
            save : false,
            cancel : false,
            timer : false,
            t_style: false,
            count : false,
            load : true
        },
        mediaRecorder : null,
        audio_source : null,
        base64data : 'AAAAAAAAAAAAAAAAAA',
        blobURL : null,
        upload : false,
        rec_timer: null,
    },
    methods: {
      start : function(){
        vue.rec1.start = false
        vue.rec1.cancel = true
        vue.rec1.timer = true
        vue.timer()

        if (this.device == 'A') {
          var constraintObj = {audio: true, video: false };
          navigator.mediaDevices.getUserMedia(constraintObj, {mimeType: 'audio/webm'})
            .then(function(mediaStreamObj) {
                vue.mediaRecorder = new MediaRecorder(mediaStreamObj);
                var chunks = [];
                vue.mediaRecorder.start();
                video = document.getElementById('vid')
                video.play()
                console.log('status:' + vue.mediaRecorder.state);

              vue.mediaRecorder.ondataavailable = function(ev) {
                chunks.push(ev.data);
              }

              vue.mediaRecorder.onstop = (ev)=>{
                    try{
                      var blob = new Blob(chunks, { 'audio' : 'audio/webm' });
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
                      //vue.recError(err.message)
                    }
                }
             })
          }
          else if (this.device == 'I'){
            // global function for iphone recording
            window.globalFunc('start')
          }
      },
      stop: function(){
        video = document.getElementById('vid')
        audio = document.getElementById('aud')
        audio.pause()
        video.pause()
        video.currentTime = 0
        audio.currentTime = 0

        vue.rec1.stop = false
        vue.rec1.save = true
        vue.rec1.cancel = true
        clearInterval(vue.rec_timer)
        console.log('stopping on device', this.device);

            if (this.device == 'A') {
              console.log('stopped');
              vue.mediaRecorder.stop();
              console.log('status:' + vue.mediaRecorder.state);
            }
            else if (this.device == 'I'){
              // global function for iphone recording
              // alert('ended 2')
              window.globalFunc('stop')
              vue.blobURL = globlob
              console.log('status: mp3 rec stopped');
            }
      },
      cancel: function(){
        console.log('cancel');
        video = document.getElementById('vid')
        audio = document.getElementById('aud')
        audio.pause()
        video.pause()
        video.currentTime = 0
        audio.currentTime = 0
        if (vue.device == 'A' && vue.mediaRecorder.state == 'recording') {
          clearInterval(vue.rec_timer)
          vue.stop()
        } else if (vue.device == 'I') {
          clearInterval(vue.rec_timer)
          vue.stop()
        }
        for (var key in vue.rec1){
          vue.rec1[key] = false
        }
        vue.rec1.start = true

        vue.base64data = 'AAAAAAAAAAAAAAAAAAA'
        vue.blobURL = null
      },
      save : function (k){
        alert('data upload, please wait.....(this may take a few seconds)')
        if (this.device == 'I'){
          vue.base64data = b64d
        }
        $.ajax({
          data : {
              part: 4,
              movie: vue.movie,
              movieData: JSON.stringify(vue.movieData),
              base64 : vue.base64data,
          },
          type : 'POST',
          url : '/addMovie'
          })
          .done(function(data) {
              vue.movieData['audio'] = data.link
              audio = document.getElementById('aud')
              audio.src = data.link
              alert('Audio Saved')
              vue.cancel()
          })
          .fail(function(){
            alert('Upload Failed, there has been an error. Reload the page and if it happens again please tell you instructor')
          });

      },
      timer : function (task){
        console.log('timer')
        vue.rec_timer = setInterval(function() {
            if (vue.rec1.count) {
              console.log('count', vue.rec1.count);
            }
            else{
              vue.rec1.count = 0
              console.log('no count', vue.rec1.count);
            }

            vue.rec1.count += 1
            if (vue.rec1.count == 91){
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
                else if (vue.rec1.count > 8) {
                  color = 'coral'
                }
                vue.rec1.t_style = { height:'30px', width:width, background:color, color:'white', 'border-radius': '5px', border: '1px solid white' }
            }
          }, 1000)
      },
      playStart : function () {
        video = document.getElementById('vid')
        audio = document.getElementById('aud')
        video.play()
        audio.play()
      },
      load : function () {
        video = document.getElementById('vid')
        audio = document.getElementById('aud')
        video.play()
        video.pause()
        video.currentTime = 0
        vue.rec1.load = false
        if (device == 'I') {
          navigator.mediaDevices.getUserMedia({ audio: true, video: false })
        }
        video.onended = function() {
          // alert('video ended')
          console.log('stopping video')
          // console.log(vue.mediaRecorder.state)
          if (vue.device == 'A' && vue.mediaRecorder.state == 'recording') {
            vue.stop()
          } else if (vue.device == 'I') {
            vue.stop()
          }
        }

      },
      clip : function (arg){

        video = document.getElementById('vid')
        audio = document.getElementById('aud')

        if (arg == 'load') {
          audio.src = vue.blobURL

        }

        audio.pause()
        video.pause()
        video.currentTime = 0
        audio.currentTime = 0
        console.log('blob', vue.blobURL);


        if (arg == 'sound'){
          video.muted = false
          console.log('sound', video)
          video.play()
        }
        if (arg == 'mute'){
          video.muted = true
          console.log('mute', video)
          video.play()
        }
        if (arg == 'shadow') {
          video.muted = false
          video.play()
          audio.play()
        }
        if (arg == 'dub') {
          video.muted = true
          video.play()
          audio.play()
        }
        if (arg == 'start') {
          video.muted = true
          vue.start()
        }
      }
    } // end methods



})// end NEW VUE

}// endFunction



