function buildHeader() {
    let headers = new Headers()
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'aplication-json',
        'X-Requested-With': 'XMLHttpRequest',
    }
    return headers
}

const AJAX_SELECT = document.getElementById('id_folder')

let filesListMenu = document.getElementById("id_file_name")
filesListMenu.innerHTML = '<option value="">files in folder</option>';

// error generation
let firstDivFormRow = document.getElementsByClassName("form-row")[0]
let errorUl = document.createElement("ul")
let emptyDiv = document.createElement("div")
firstDivFormRow.appendChild(emptyDiv)
firstDivFormRow.appendChild(errorUl)
let errorLi = document.createElement("li")
errorUl.appendChild(errorLi)
errorUl.className = "errorlist"
// get jax url from form attr


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
        let importFormUrlAjax = importForm.getAttribute('data-action')
        let folder = this.node.value
        let param = { folder_name: folder }
        // /admin/auth/user/fetch/files/?folder_name=folder_two
        let importFormUrl = `${importFormUrlAjax}?` + new URLSearchParams(param)
        fetch(importFormUrl,
            {
                headers: buildHeader(),
                method: "GET"
            }
        )
            .then(resp => resp.json())
            .then((data) => {
                this.populateList(data)
            })
            //this.populateList.bind(this))
            .catch((err) => {
                // url in ajax request is not correct                       
                this.populateList(data)

            })
    }
    /**
     * populate drop-down menu with files for a given folder if status OK
     * otherwise TODO: determine DOM elem to show error msg
     */
    populateList(data) {
        if (data.status_code === 200) {
            // reset drop-down menu for list of files  
            filesListMenu.innerHTML = '<option value="">files in folder</option>';
            data.resp.forEach((item) => {
                filesListMenu.innerHTML += `<option value="${item}">${item}</option>`
            })

        } else if (data.status_code == 400) {
            errorLi.textContent = `${data.error}`
            throw new Error("Status response 400. Unable to get files");
        } else {
            errorLi.textContent = "Sorry.The url does not exist.Unable to get list of files \
            for this folder.."
            throw new Error("Error. The url does not exist");

        }
    }
}
new TrackFolderMenu(AJAX_SELECT);

