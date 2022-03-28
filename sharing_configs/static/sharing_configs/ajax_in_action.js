function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function buildHeader(){
    const csrftoken = getCookie('csrftoken');
    let headers = new Headers()    
    headers ={
        'Accept':'application/json',
        'Content-Type':'aplication-json',
        'X-Requested-With': 'XMLHttpRequest',
        "X-CSRFToken": csrftoken
    }
    return headers

}
const AJAX_SELECT = document.getElementById('id_folder')

let filesListMenu = document.getElementById("id_file_name")
filesListMenu.innerHTML = '<option value="">files in folder</option>';

let firstDivFormRow = document.getElementsByClassName("form-row")[0]
let errorNote = document.createElement("div")
errorNote.className = "input-error"
errorNote.textContent="unable to find folders"
firstDivFormRow.appendChild(errorNote)
console.log("errorNote created")

class TrackFolderMenu {
    /**
     * Constructor method.
     * @param {HTMLSelectElement} node 
     */
    constructor(node) {
        this.node = node;
        this.trackChange();
    }

    /**
     * Binds change event to callbacks.
     */
    trackChange() {
        this.node.addEventListener('change', this.update.bind(this));
    }

    /**
     * make ajax POST call to SharingConfigsImportMixin to pass user choice (folder name)
     * TODO: determine DOM elem to show error msg
     */
    update() {
        let importForm = document.getElementById("import-form")
        let importFormUrl = importForm.getAttribute('action')
        let data = {"folder":this.node.value}        
        fetch(importFormUrl,
            {
                headers:buildHeader(),
                method:"POST",
                body:JSON.stringify({"data":data})
            }        
        )
        .then(resp=> resp.json())
        .then(
            this.populateList.bind(this))
        .catch((err)=>{
            console.log(err)
            // errorMsg.innerHTML = "Unable to get folders"
        })        
    }
    /**
     * populate drop-down menu with files for a given folder if status OK
     * otherwise TODO: determine DOM elem to show error msg
     */
    populateList(data) {         
        if (data.status_code === 200) {      
        data.resp.forEach((item)=>{
            filesListMenu.innerHTML +=`<option value="${item}">${item}</option>`
            })
            
        }else{
            // errorMsg.innerHTML = "Unable to get folders"
            errorNote.textContent=`${data.status_code}`
            // errorNote.textContent="smth went wrong"
            // throw new Error("Unable to get folders");
        }         
    }
}
new TrackFolderMenu(AJAX_SELECT);

