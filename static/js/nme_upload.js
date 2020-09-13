
var rString = document.getElementById('rString').innerHTML
var novel = document.getElementById('index').innerHTML
// var rCount = document.getElementById('rCount').innerHTML

var rObj = JSON.parse(rString)
console.log('rObj', novel, rObj)




startVue()

function startVue(){

  let vue = new Vue({

    el: '#vue-app',
    delimiters: ['[[', ']]'],
    data: {
        rObj: rObj,
        novel: novel,
        rec: {
          number: null,
          page: null,
          text: null,
          words: [null, null, null, null],
          audio: null
        },
        audio64 : {
            fileType : null,
            base64 : null,
        },
        audioPlay: null
    },
    methods: {
        goTo: function(task, index) {
            let name = document.getElementById('user').innerHTML

            var str = window.location.href


            let url = (str).split('nme')[0] + task + '/'+ index
            console.log('goTO', url);
              window.location = url
              console.log('DONE');
        },
        loadRec: function (rec) {
          this.rec.number = rec
          this.rec.page = this.rObj[rec].page
          this.rec.text = this.rObj[rec].text
          if (this.rObj[rec].words) {
            this.rec.words = this.rObj[rec].words
          }
          if (this.rObj[rec].audio) {
            this.rec.audio = this.rObj[rec].audio
          } else {
            this.rec.audio = null
          }
        },
        checkText: function () {
          let check = true
          for (let word in this.rec.words){
            console.log(word)
            if (!this.rec.text.includes(this.rec.words[word])) {
              check = false
            }
          }
          return check
        },
        submitRec: function () {
            if (!this.checkText()){
              alert('Make sure all of your words are in the text - words must be exact (including capital letters')
              return false
            }
            console.log('update via AJAX');
            let _this = this
              $.ajax({
                data : {
                  novel: this.novel,
                  rec: this.rec.number,
                  details: JSON.stringify(this.rec)
                },
                type : 'POST',
                url : '/addRec',
              })
              .done(function(data) {
                _this.rObj[_this.rec.number] = _this.rec
                rsj = JSON.stringify(vue.rObj)
                console.log(rsj)
                vue.rObj = JSON.parse(rsj)
                _this.rec.number = null
                alert('details added')
              })
              .fail(function(){
                  alert('error has occurred');
              });
        },
        storeB64 : function(key) {

            var b64data = this.audio64['base64']
            var fileType = 'mp3'
            var rec = this.rec.number
            var novel = this.novel
            let _this = this


            $.ajax({
              data : {
                b64data : b64data,
                fileType : fileType,
                novel : novel,
                rec : rec
              },
              type : 'POST',
              url : '/nme_storeB64',
            })
            .done(function(data) {
                console.log(data);
                console.log(vue.rObj, rec);
                vue.rObj[rec]['audio'] = data.audioLink
                rsj = JSON.stringify(vue.rObj)
                console.log(rsj)
                vue.rObj = JSON.parse(rsj)
                alert('audio added')
            })
            .fail(function(){
                alert('error - see instructor')
            });
        },
        resetB64 : function() {
            vue.audio64['fileType'] = false
        },
        audioValidation : function(){
            var fileInput = document.getElementById('audio');
            console.log('file', fileInput)
            var filePath = fileInput.value;
            var allowedExtensions = /(\.mp3|\.m4a|\.m4v|\.mov|\.mp4)$/i;

            // if(fileInput.files[0].size > 4400000){
            //     alert("File is too big!");
            //     location.reload()
            //     return false;
            // } else
            if(!allowedExtensions.exec(filePath)){
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

                var reader = new FileReader();
                reader.readAsDataURL(savedBlob);
                reader.onloadend = function() {
                        vue.audio64['base64'] = reader.result.split(',')[1];
                        vue.audio64['fileType'] = true
                    }
                })// end then function
            }//end else

          },//end audioValidation
          playAudio : function(key){
            this.audioPlay = key
          }
    }, // end methods



})// end NEW VUE

}// endFunction

