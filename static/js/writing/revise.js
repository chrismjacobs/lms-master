
let unit_number = document.getElementById('unit').innerHTML
console.log(unit_number)

let partner = document.getElementById('partner').innerHTML
console.log('partner', partner)

let user = document.getElementById('user').innerHTML
console.log('user', user)

$.ajax({
    type : 'POST',
    url : '/getHTML/' + unit_number
})
.done(function(data) {
        console.log(data);
        if (data.stage < 3){
        console.log('No data')
        alert('Please wait for instructors revision')
        window.location = (window.location.href).split('work')[0] + 'work/topic' + '/' + unit_number
        }
        let revise_obj = JSON.parse(data.revise)
        let info = JSON.parse(data.info)
        let html = revise_obj['html']
        let text = revise_obj['text']
        console.log('START VUE', info)
        startVue(info, html, text)
});




startVue(info, html, text)


function startVue(info, html, text){
    let app = new Vue({

    el: '#vue-app',
    delimiters: ['[[', ']]'],
    mounted: function(){
        //this.revHTML = this.revHTML.replace('n&lt;', '>');
        //this.revHTML = this.revHTML.replace('&lt;', '<');
        console.log(this.revHTML);
        for (let s of document.getElementsByTagName('span')){
            s.setAttribute("class", "revise");
        }
        this.deSelect('text', 'start')
    },
    data: {
        partner : partner,
        user: user,
        original : text,
        revText : text, // updated by v-model
        revHTML : html,
        exampleHTML : "<span style='background-color: yellow;'>Student can fix</span>&emsp;&emsp;<span style='background-color: orange;'>Form Mistake (V/Vs/Vpt/Ving/N/Ns)</span>&emsp;&emsp;<span style='background-color: springgreen;'>Instructor fixed</span><br><span style='background-color:cyan;'>Complicated fix</span>&emsp;&emsp;<span style='background-color:plum;'>Punctuation ( . / , / no space / new sentence)</span>&emsp;&emsp;<span style='background-color:tomato;'>Delete</span>",
        infoOBJ : info,
        save : false,
        status : info['stage'],
        theme : { 'color' : info['theme'] }
    },
    methods: {
        getBG: function () {
            if (this.user == this.partner) {
                return {background:'#AB47BC'}
            }
        },
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
        readRefs: function(){
            this.sendData(this.revText) // revText connected by v-model
            alert('Please wait a moment while your writing is being updated')
        },
        sendData: function (revised){
            console.log(revised)
            $.ajax({
                type : 'POST',
                data : {
                    unit : document.getElementById('unit').innerHTML,
                    obj : revised,
                    stage : 4,
                    work : 'revise'
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
        cancel: function(){
            alert('You have cancelled so your changes will not be saved')
            window.location = (window.location.href).split('work')[0] + 'work/topic' + '/' + unit_number
        }
    }

})// end NEW VUE

}// end start vue function