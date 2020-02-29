var ansString = document.getElementById('ansDict').innerHTML
var ansOBJ = JSON.parse(ansString)
console.log('ansOBJ', ansOBJ);

//var testString = document.getElementById('testDict').innerHTML
//var testOBJ = JSON.parse(testString)
//console.log('testOBJ', testOBJ);

var teamMembers = document.getElementById('teamMembers').innerHTML
var teamOBJ = JSON.parse(teamMembers)
console.log('teamOBJ', teamOBJ);

var report = navigator.userAgent
var device = null
var notice = null

if (report.includes('Windows')){
  device = 'A'
  notice = 'Recording in Windows'
}
else if (report.includes('Android')){
    device = 'A'
    notice = 'Recording in Android'
}
else if (report.includes('Macintosh')){
    device = 'A'
    notice = 'Recording on Mac'
}
else if (report.includes('iPad')){
    notice = 'Recording on iPad may not work; please upload file, share a link or use a phone/computer'
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
else {
  device = 'U'
  notice = 'Your iOS may not work; if so try upload a file, share a link, or use a computer'
}
console.log('DEVICE', device);

//device = 'U'
let b64d = 'nothing'
let globlob = 'noURL'


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
              console.log('stop Record');
              audioContext.close();
              processor.disconnect();
              tracks.forEach(track => track.stop());

              audioElement = document.getElementById('handler')   
              audioElement.src = URL.createObjectURL(encoder.finish());   
              globlob = audioElement.src              
                fetch(audioElement.src)
                .then( response => response.blob() )
                .then( blob =>{
                    var reader = new FileReader();
                    reader.readAsDataURL(blob);	
                    reader.onload = function(){ 
                        b64d = this.result.split(',')[1]  // <-- this.result contains a base64 data URI; set to gloabl variable                                                                  
                    }; //end reader.onload
                
                })//end fetch      
          };// stopRecord          
      }
      this.stopRecord = function() {
          stopBtnRecord();
      }; 
  }
}




startVue(ansOBJ, device, notice)

function startVue(ansOBJ, device, notice){ 
  
  let vue = new Vue({   

    el: '#vue-app',
    delimiters: ['[[', ']]'],   
    mounted: function () { 
      if (device == 'U'){
        this.showUpload('up')
      }     
      
    },   
    data: {
        ansOBJ: ansOBJ, 
        device: device,
        notice : notice,
        addReady : false,        
        unit: (window.location.href).split('/snl/')[1].split('/')[0],
        team: (window.location.href).split('/snl/')[1].split('/')[1], 
        edit: false,
        show: {
          1 : true          
        },
        audio: {
          1 : null          
        },
        uploadBTN : {
          1 : ['upbtn1', 'uplink1']          
        },          
        rec1: {          
            start : true,
            stop : false, 
            save : false, 
            cancel : false, 
            timer : false,
            t_style: false,  
            count : false 
        },   
        base64data : {
          image_b64 : null,            
          fileType : null, 
          audio_b64 : null,           
          word : null, 
          sentence : null
        },     
        rec_timer : null,
        mediaRecorder : null,
        audio_source : null,        
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
                  var blob = new Blob(chunks, { 'audio' : 'audio/mpeg;' });
                  console.log(blob);
                  chunks = [];// here we clean out the array
                  var blobURL = window.URL.createObjectURL(blob);
                  console.log(blobURL);         
                  //get the base64data string from the blob
                  reader = new FileReader();
                  reader.readAsDataURL(blob); 
                  reader.onloadend = function() {
                    vue.base64data['audio_b64'] = reader.result.split(',')[1]; //remove padding from beginning of string
                    vue.blobURL = blobURL 
                    vue.ready()           
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
          vue.mediaRecorder.stop();           
          console.log('status:' + vue.mediaRecorder.state);
        }
        else if (this.device == 'I'){
          // global function for iphone recording
          window.globalFunc('stop')
          vue.blobURL = globlob;    
          vue.base64data['audio_b64'] = b64d      
          //console.log('status: mp3 rec stopped', vue.base64data['audio_b64']); 

        }
        vue.ready()        
      },  
      cancel: function(){
        console.log('cancel');
        for (var key in vue.rec1){
        vue.rec1[key] = false          
        }
        vue.rec1.start = true 
        

        vue.show['1'] = true
        vue.show['2'] = true
        vue.base64data['audio_b64'] = null
        vue.blobURL = null  
        vue.ready()       
      },
      editor: function(){
        console.log('test');        
        this.edit =  !this.edit        
      },
      updateWord: function(){        
        vue.base64data['word'] = document.getElementById('word').value
        vue.base64data['sentence'] = document.getElementById('sentence').value
        this.ready() 
        console.log(vue.base64data);
      },
      deleteWord : function(key){
        $.ajax({
          data : {              
              unit : vue.unit,
              team : vue.team,
              word : key             
          },
          type : 'POST',
          url : '/deleteWord'                    
          })
          .done(function(data) {
            alert('Your team answers have been updated. You now have ' + data.qCount + ' words');
            vue.ansOBJ = JSON.parse(data.newDict)
            // reset base64data
            for (var key in vue.base64data) {
              vue.base64data[key] = null
              }  
            vue.edit = false
          })
          .fail(function(){
            alert('Upload Failed, there has been an error. Reload the page and if it happens again please tell you instructor')
          });           
          console.log(vue.ansOBJ);       
      },
      addWord : function (){        
        var user = document.getElementById('user').value
        for (var key in vue.base64data) {
          if (vue.base64data[key] == null) {
            alert (key + ' is not complete')
            return false
          }         
        }  

        $.ajax({
          data : {              
              unit : vue.unit,
              team : vue.team,
              user : user,
              b64String : JSON.stringify(vue.base64data),              
          },
          type : 'POST',
          url : '/addWord'                    
          })
          .done(function(data) {
            console.log(data.word + ' has been succesfully added');
            vue.ansOBJ = JSON.parse(data.newDict)
            // reset base64data
            for (var key in vue.base64data) {
              vue.base64data[key] = null
              }  
          })
          .fail(function(){
            alert('Upload Failed, there has been an error. Reload the page and if it happens again please tell you instructor')
          });           
          console.log(vue.ansOBJ);
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
                else if (vue.rec1.count > 10) {
                  color = 'coral'
                }
                vue.rec1.t_style = { height:'30px', width:width, background:color, color:'white', 'border-radius': '5px', border: '1px solid white' }                
            }
          }, 1000)
      },
      playAudio : function (arg) { 
        let playlist = {
          '0' : vue.blobURL          
        }
        player = document.getElementById('handler')        
        player.src = playlist[arg]
       
      },
      fileValidation : function(task){    
        var fileInput = document.getElementById('upbtn'+ task);        
        console.log('file', fileInput)
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
        this.ready() 
      },//end fileValidation 
      imageValidation : function(){    
        var fileInput = document.getElementById('image');        
        //console.log('file', fileInput)
        var filePath = fileInput.value;
        //console.log(filePath);
        //console.log(vue.base64data);
        vue.base64data['fileType'] = filePath.split('.')[1]
        //console.log(vue.base64data['fileType']);

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
                      vue.base64data['image_b64'] = reader.result.split(',')[1];  
                      //vue.base64data[image_file] = 'T' + vue.team + '_U' + vue.unit;  
                      //console.log(vue.base64data['image_b64']); 
                      //setTimeout(vue.uploadImage() , 10000)
                      
                      } 
              })  
          }//end else
          vue.ready()
            
      },
      ready : function() {
        console.log('checking ready');        
        for (var key in this.base64data) {
          if (this.base64data[key] == null) {
            this.addReady = false
            return false
          }
        }
        this.addReady = true
        return true
                     
    }, // end methods  
    
          

    }  
    
    
    
})// end NEW VUE

}// endFunction 




