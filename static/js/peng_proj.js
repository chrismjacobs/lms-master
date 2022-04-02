var ansString = document.getElementById('ansString').innerHTML
var ansOBJ = JSON.parse(ansString)
console.log('ansOBJ', ansOBJ);

var str = window.location.href
let stage = (str).split('peng/')[1].split('/')[1]


startVue(ansOBJ)

function startVue(ansOBJ){

  let vue = new Vue({

    el: '#vue-app',
    delimiters: ['[[', ']]'],
    mounted: function () {
    },
    data: {
        ansOBJ: ansOBJ,
        stage : stage,
        updateReady : true,
        pptLink : false,
        image_b64 : null,
        project: (window.location.href).split('/peng/')[1].split('/')[0],
        script: {
            Product : "What is this product",
            Features : "First, I would like to talk about some product features",
            Demo : "Now, for the demonstration",
            Extra : "Finally, what are some extra benefits of this product?",
        }

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
        imageValidation : function() {

        var fileInput = document.getElementById('image');
        //console.log('file', fileInput)
        var filePath = fileInput.value;
        //console.log(filePath);
        //console.log(vue.base64data);
        //vue.fileType = filePath.split('.')[1]
        //console.log(vue.base64data['fileType']);

        var allowedExtensions = /(\.jpeg|\.png|\.jpg)$/i;

          if(fileInput.files[0].size > 10000000){
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
                      vue.image_b64 = reader.result.split(',')[1];
                }
              })
          }//end else
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
            alert('Please wait, your plan is being updated')

            $.ajax({
              data : {
                proj : this.project,
                stage: this.stage,
                image_b64 : this.image_b64,
                ansOBJ : JSON.stringify(this.ansOBJ)
              },
              type : 'POST',
              url : '/updatePENG',
            })
            .done(function(data) {
                if (data.fail){
                    alert('Your FORM is NOT complete yet')
                }
                else{
                    vue.ansOBJ = JSON.parse(data.ansString)
                    vue.image_b64 = null
                    console.log(vue.ansOBJ)
                    document.getElementById('final_image').src = vue.ansOBJ['Image']
                    alert('Your FORM has been updated')
                }


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
                stage : this.stage,
                ansOBJ : JSON.stringify(this.ansOBJ)
              },
              type : 'POST',
              url : '/createFOOD',
            })
            .done(function(data) {
                alert('Your ppt has been created')
                vue.pptLink = data.pptLink
            })
            .fail(function(){
                alert('There has been an error. Please check that your FORM is complete or see your instructor');
            });
        },

    },
    computed : {
        imageCheck : function() {
            return this.ansOBJ['Image']
        },
    } // end methods



})// end NEW VUE

}// endFunction

