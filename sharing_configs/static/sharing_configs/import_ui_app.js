
  function importCompleted(data) {
      window.location = data["redirect"];
  }

  function importFile(event) {
      /* Import the selected file, and if succesful redirect the user to the newly created object */
      const data_name = event.target.attributes["data-name"];
      if (!data_name) {
	  return;
      }
      const file_name = data_name.value;
      const folder_name = document.querySelector('table.fileselector').attributes['data-folder'].value;
      setSpinner();
      console.log(file_name);
      console.log(folder_name);
      document.getElementById('id_folder').value = folder_name;
      document.getElementById('id_file_name').value = file_name;
      const form_data = new FormData(document.getElementById('import-form'));
      fetch('', {'method': 'POST', 'body': form_data}).then(resp => resp.json().then(json => importCompleted(json)));
  }

  function loadInFiles(folder_name, files) {
      /* Replace the app with a table of retrieved files, allowing the user to select one to import the file */
      content = '<table data-folder="' + folder_name + '" class="table table-sm fileselector"><thead><th scope="col">Name</th><th scope="col">Action</th></thead><tbody>';
      
      files['resp'].forEach((file) => {
	  content += fileTableRow(file);
      })
      content += '</tbody></table><a href="#" style="color: white;" class="btn btn-primary btn-back">Back</a>';
      document.getElementById('app').innerHTML = content;
      document.querySelectorAll('.btn-import').forEach(button =>
	  addEventListener('click', importFile)
      )
      document.querySelector('.btn-back').addEventListener('click', getFolders);
      return content;
  }

  
  function openFolder(event) {
      /* Open the selected folder, replace the app with a table of available files within the selected folder */
      setSpinner();    
      const folder_name = event.target.attributes["data-name"].value;
      fetch('files/?folder_name=' + folder_name).then(resp => resp.json().then(json => loadInFiles(folder_name, json)));
  }

  function fileTableRow(name) {
      svg_img = name.endsWith('json') ? 'icon_json.svg' : 'icon_file.svg';
      button = name.endsWith('json') ? '<a style="color: white;" href="#" data-name="' + name + '" class="btn btn-primary btn-import">Import</a>' : '';
      
      return '<tr><td><img src="/static/sharing_configs/' + svg_img + '" width="32" height="32"> ' + name + '</td><td>' + button + '</td></tr>';
  }

  function folderCard(name, permission) {
      const img_nr = name[0].charCodeAt(0) - 64; // Use the first letter to grab a Lorem Picsum image
      return '<div class="card mb-3" style="width: 18rem; max-width: 24rem;"><img class="card-img-top" src="https://picsum.photos/600/300/?image=' + img_nr + '" alt="Card image cap"> <div class="card-body"> <h5 class="card-title">' + name + '</h5><p class="card-text">' + permission + '</p><a data-name="' + name + '" href="#' + name +'" style="color: white;" class="btn btn-primary">View</a></div></div>';
  }


  function loadInFolders(folders) {
      /* Replace the app with a group of cards, one card per folder */
      content = '<div class="card-group">';
      folders['folders'].forEach((folder) => {
	  // folder["children"]?
	  content += folderCard(folder["name"], folder["permission"]);
      })
      content += "</div>";
      document.getElementById('app').innerHTML = content;
      document.querySelectorAll('.btn').forEach(button =>
	  button.addEventListener('click', openFolder)
      )
      
      return content;
  }

  function setSpinner() {
      /* Replace the main app with a spinner */
      document.getElementById('app').innerHTML = '<div class="spinner-border" role="status">';
  }
  
  function getFolders() {
      /* Load in the available folders and populate the folder cards */
      setSpinner();
      fetch('folders').then(resp => resp.json().then(json => loadInFolders(json)));
  }		   
  
getFolders();
